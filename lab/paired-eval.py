"""E-M73 — the paired evaluation: does our artifact help an agent answer better than a bare catalogue?

This is the measurement the product half has never made. Two arms, the same model, the same questions, one
difference: arm A receives the catalogue (tables, functions, triggers, grants); arm B receives our inventory and
verdict. Ground truth is written from the catalogue by hand, not from our tool — otherwise the tool grades itself.

Pre-registered threshold, before any call:

  arm B must find strictly more true bypass paths than arm A, and must not introduce more false ones.
  Anything else is reported as it comes out, including "no difference" and "arm B is worse".

    python lab/paired-eval.py --model qwen3.8-flash --dry-run   # show the questions and ground truth
    python lab/paired-eval.py --model qwen3.8-flash             # run both arms

The model calls go through the harness's own agent(), so this file is a specification plus a scorer; the run
itself is driven from the session, and the transcript is stored next to the card.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "migrations-sample"
INVENTORY = ROOT / "inbox" / "paired-inventory.json"

# ---------------------------------------------------------------- the catalogue (arm A's world)
CATALOGUE = """
Schema: sample

Tables
  sample.accounts(id bigserial PK, balance numeric NOT NULL DEFAULT 0, updated_at timestamptz NOT NULL DEFAULT now())

Functions
  sample.update_updated_at_column() RETURNS trigger            -- sets NEW.updated_at = now()
  sample.apply_transfer(p_from bigint, p_to bigint, p_amount numeric) RETURNS void
      -- UPDATE sample.accounts SET balance = balance - p_amount WHERE id = p_from;
      -- UPDATE sample.accounts SET balance = balance + p_amount WHERE id = p_to;

Triggers
  sample_accounts_updated_at BEFORE UPDATE ON sample.accounts
      FOR EACH ROW EXECUTE FUNCTION sample.update_updated_at_column()

Grants
  GRANT INSERT, UPDATE ON sample.accounts TO app_rw

Declared control point for this exercise: the function sample.review_transfer(), which is supposed to be the
only way money moves. It exists in the application code and is called by the HTTP handler for transfers.
"""

# ---------------------------------------------------------------- ground truth, from the catalogue
QUESTIONS = [
    {
        "id": "q1",
        "question": "Which functions can change sample.accounts.balance without calling sample.review_transfer()?",
        "truth": ["sample.apply_transfer"],
        "kind": "function_bypass",
    },
    {
        "id": "q2",
        "question": "Can a role write sample.accounts directly, without going through any function?",
        "truth": ["app_rw (GRANT INSERT, UPDATE)"],
        "kind": "grant_bypass",
    },
    {
        "id": "q3",
        "question": "Does an update to sample.accounts reach any code that the transfer control point does not see?",
        "truth": ["yes: the trigger sample_accounts_updated_at runs update_updated_at_column() on every UPDATE"],
        "kind": "trigger_bypass",
    },
    {
        "id": "q4",
        "question": "If sample.review_transfer() is the only allowed path, how many independent ways around it exist?",
        "truth": ["three: apply_transfer(), the app_rw grant, and the trigger"],
        "kind": "count",
    },
    {
        "id": "q5",
        "question": "Which of those bypasses would a grader accept as 'the control point covers every write'?",
        "truth": ["none: each bypass alone falsifies that claim"],
        "kind": "judgement",
    },
]

ANSWER_FORMAT = """Answer with JSON only:
{"answers": [{"id": "q1", "answer": "...", "bypasses": ["..."]}, ...]}
List every bypass you believe exists; an empty list is a valid answer."""


def inventory_text() -> str:
    """Arm B's world: what our tool says, in the same words the bundle would carry."""
    if not INVENTORY.exists():
        return "(inventory not generated yet: run the enumerator first)"
    doc = json.loads(INVENTORY.read_text(encoding="utf-8"))
    lines = ["Inventory of write paths for sample.accounts", ""]
    for p in doc.get("paths", []):
        lines.append(f"  {p['path_id']}  {p['kind']:14} {p['entry']}")
        lines.append(f"      target: {p.get('target')}")
        lines.append(f"      verbs:  {', '.join(p.get('verbs', []))}")
        lines.append(f"      how:    {p.get('how', '')}")
        attr = (p.get("attribution") or {}).get("to")
        lines.append(f"      attributed to control point: {attr or 'none'}")
        lines.append("")
    lines.append("Verdict for the claim 'review_transfer covers every write to accounts': CONSISTENT_DECLARED")
    lines.append("Coverage: 0.0 (no path reaches the declared control point)")
    lines.append("Not claimed: NC-01 (the inventory may be incomplete), NC-02 (nothing outside the scope is safe)")
    return "\n".join(lines)


def prompt(arm: str, q: dict) -> str:
    world = CATALOGUE if arm == "A" else CATALOGUE + "\n\n" + inventory_text()
    return f"""You are analysing a Postgres schema. Use only what is below.

{world}

QUESTION ({q['id']}): {q['question']}

{ANSWER_FORMAT}"""


def score(answer: str, q: dict) -> dict:
    """Set agreement on the bypasses, which is the part a machine can score without judgement."""
    try:
        doc = json.loads(answer[answer.find("{"):answer.rfind("}") + 1])
        got = " ".join(str(x).lower() for x in doc.get("answers", [])[0].get("bypasses", []))
    except Exception:  # noqa: BLE001
        return {"parse": False, "hits": 0, "false": 0}
    truth = [t.lower() for t in q["truth"]]
    hits = sum(1 for t in truth if any(word in got for word in t.split()[:2]))
    false = 0 if got.strip() in ("", "[]") else max(0, len(got.split(",")) - hits)
    return {"parse": True, "hits": hits, "false": false}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.8-flash")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--arm", choices=["A", "B"])
    a = ap.parse_args()

    if a.dry_run:
        print(f"model: {a.model}\nquestions: {len(QUESTIONS)}, arms: 2, calls: {2 * len(QUESTIONS)}\n")
        for q in QUESTIONS:
            print(f"[{q['id']}] {q['question']}")
            print(f"     truth: {q['truth']}")
        print("\n--- arm A prompt (first question) ---")
        print(prompt("A", QUESTIONS[0])[:900])
        print("\n--- arm B prompt (first question, inventory part) ---")
        print(inventory_text()[:900])
        return 0

    # a single arm, printed as JSON so the session can call the model and feed the answer back
    if a.arm:
        out = [{"id": q["id"], "prompt": prompt(a.arm, q)} for q in QUESTIONS]
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return 0

    print("run one arm at a time from the session: --arm A | --arm B, then score with --score FILE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
