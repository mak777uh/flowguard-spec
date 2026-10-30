#!/usr/bin/env python3
"""fg_decompose — turn a spec, or the claimant's text of intentions, into checkable units.

The request this answers: take prose, split it into precise units, and hand those units on to a defended core.
The honest version of that cannot be "understand the text". It can be: **classify every sentence into a unit with
a known fate**, and name the ones that can never become a unit. That is what this does, deterministically.

    python tools/fg_decompose.py --text spec.md --out draft.json

Each sentence becomes one unit with a kind:

    measured    names an action and an object - it can become a path and a claim about it
    assumption  states a condition the system relies on, without naming who verifies it
    requirement must / may not - a statement about policy, not about code
    absolute    "secure", "guaranteed", "always", "never" - cannot become a unit at all, by construction
    unmapped    none of the above; kept, marked, never silently dropped

Exit 0 when every sentence has a kind and there is at least one `measured` unit; 1 when an `absolute` is present
(the text claims something no artifact can support); 2 on usage.

What it does not do: it does not decide whether a `measured` unit is TRUE, does not resolve pronouns, and does not
read a document it cannot split into sentences. Those are printed as limits, not hidden.
"""
import argparse
import json
import pathlib
import re
import sys

# A unit needs an action a program can perform, and an object it performs it on. These are the verbs the
# enumerators can actually follow: they are the ones that appear in a path's `how`.
ACTION_VERBS = {
    "write",
    "writes",
    "insert",
    "inserts",
    "update",
    "updates",
    "delete",
    "deletes",
    "transfer",
    "transfers",
    "move",
    "moves",
    "read",
    "reads",
    "grant",
    "grants",
    "call",
    "calls",
    "execute",
    "executes",
    "create",
    "creates",
    "drop",
    "drops",
    "encrypt",
    "encrypts",
    "decrypt",
    "decrypts",
    "log",
    "logs",
    "emit",
    "emits",
    "запис",
    "пиш",
    "перевод",
    "перевод",
    "чита",
    "вызов",
    "созда",
    "удал",
    "обновл",
    "встав",
    "предостав",
    "шифр",
    "расшифр",
    "логир",
    "отправ",
}

ABSOLUTES = {
    "secure",
    "provably safe",
    "fully secure",
    "guaranteed",
    "guarantee",
    "always",
    "never",
    "impossible",
    "cannot be bypassed",
    "cannot fail",
    "unhackable",
    "безопасн",
    "гарантир",
    "всегда",
    "никогда",
    "невозможно",
}

REQUIREMENT = ("must ", "shall ", "may not", "must not", "required to", "должен", "обязан", "не вправе")
ASSUMPTION = ("assume", "assumes", "provided that", "assuming", "given that", "предполага", "при условии")

SENTENCE = re.compile(r"(?<=[.!?])\s+|\n{2,}")


def words(text: str) -> set[str]:
    return set(re.findall(r"[\w-]+", text.lower()))


def classify(sentence: str) -> tuple[str, str]:
    """(kind, reason). Order matters: an absolute disqualifies a sentence before anything else is read."""
    # hyphens and spaces must not decide a refusal: "provably-safe" and "provably safe" are the same claim
    low = sentence.lower().replace("-", " ").replace("\u2011", " ")
    for token in ABSOLUTES:
        if token in low:
            return "absolute", f"contains {token!r}: no artifact can support it"
    if any(low.startswith(p) or f" {p}" in low for p in REQUIREMENT):
        return "requirement", "states a policy, not an observation about a system"
    if any(p in low for p in ASSUMPTION):
        return "assumption", "states a condition; nobody is named as verifying it"
    # Substring match, not set intersection: Russian verbs are stems, so 'запис' must match 'записать'.
    toks = words(sentence)
    acts = {v for v in ACTION_VERBS if any(v in w for w in toks)}
    if acts:
        return "measured", f"names an action ({', '.join(sorted(acts)[:3])}) with an object"
    return "unmapped", "no action a program can follow"


def decompose(text: str) -> dict:
    sentences = [s.strip() for s in SENTENCE.split(text) if s and s.strip()]
    units = []
    for i, s in enumerate(sentences, 1):
        kind, reason = classify(s)
        units.append({"id": f"U{i}", "text": s, "kind": kind, "reason": reason,
                      "needs": ("a target table and a control point" if kind == "measured"
                                else "a human decision" if kind in ("requirement", "assumption")
                                else "rewriting: this sentence cannot become a unit")})
    by_kind = {}
    for u in units:
        by_kind[u["kind"]] = by_kind.get(u["kind"], 0) + 1
    draft = {
        "decompose_version": "1",
        "units": units,
        "counts": by_kind,
        "claim": {
            "claim_id": "<set by a human>",
            "target_lock": {"commit": "<the source this text describes>"},
            "declared_control_point": "<from the measured units; the tool will not invent it>",
            "declared_level": "CONSISTENT_DECLARED",
            "claimed_coverage": 0.0,
            "evidence_tier": 0,
            "not_claimed": ["NC-01", "NC-02"],
        },
        "limits": [
            "a 'measured' unit is an action, not a fact: it becomes a path, and a path is only as true as the "
            "enumerator that found it",
            "pronouns and cross-sentence references are not resolved",
            "an 'absolute' sentence is refused, not weakened: rewriting it is the claimant's act",
        ],
    }
    return draft


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()

    try:
        text = pathlib.Path(a.text).read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"cannot read {a.text}: {e}")
        return 2

    draft = decompose(text)
    out = json.dumps(draft, indent=1, ensure_ascii=False)
    if a.out:
        pathlib.Path(a.out).write_text(out + "\n", encoding="utf-8")

    for u in draft["units"]:
        print(f"  {u['id']:4} {u['kind']:11} {u['text'][:70]}")
    print()
    for k, v in sorted(draft["counts"].items()):
        print(f"  {k:11} {v}")
    absolutes = draft["counts"].get("absolute", 0)
    measured = draft["counts"].get("measured", 0)
    if a.out:
        print(f"\nwritten: {a.out}")
    print("RESULT:", "refused" if absolutes else ("ok" if measured else "nothing measurable"))
    return 1 if absolutes else (0 if measured else 1)


if __name__ == "__main__":
    sys.exit(main())
