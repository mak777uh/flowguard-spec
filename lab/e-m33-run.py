#!/usr/bin/env python3
"""E-M33: the verifier is consumed by a machine, so a malformed input must be a refusal, not a crash.

An agent integrating with this tool sends JSON and parses JSON. A traceback on stderr is not a
verdict: it is a signal to the caller to retry, guess, or give up, and none of those is a decision.

The harness throws 16 malformed or hostile inputs at `fg_verify` and requires, for every one:
  * the process exits with 1 or 2 (never 0, never a crash-only 1 with no verdict),
  * stdout is parseable JSON containing a `verdict` field,
  * stderr contains no `Traceback`.

    python lab/e-m33-run.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "tools" / "fg_verify.py"

GOOD_CLAIM = {
    "claim_id": "fuzz", "target_lock": {"commit": "t@1"},
    "declared_control_point": "function:f", "declared_level": "CONSISTENT_DECLARED",
    "claimed_coverage": 0.0, "excluded": [], "not_claimed": ["NC-01", "NC-02"],
    "evidence_tier": 1,
}
GOOD_INV = {
    "manifest_version": "inventory/0.1", "target_lock": "t@1",
    "sources": [{"source_id": "s", "kind": "grants"}],
    "independent_of_agent": True, "paths": [],
}


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    good_claim = tmp / "good-claim.json"
    good_inv = tmp / "good-inv.json"
    good_claim.write_text(json.dumps(GOOD_CLAIM), encoding="utf-8")
    good_inv.write_text(json.dumps(GOOD_INV), encoding="utf-8")

    cases = []

    def add(name, claim_text=None, inv_text=None, claim_path=None, inv_path=None):
        c = tmp / f"{name}-claim.json"
        i = tmp / f"{name}-inv.json"
        if claim_path is None:
            c.write_text(claim_text, encoding="utf-8")
        else:
            c = claim_path
        if inv_path is None:
            i.write_text(inv_text, encoding="utf-8")
        else:
            i = inv_path
        cases.append((name, c, i))

    add("empty", "", json.dumps(GOOD_INV))
    add("not-json", "{nope", json.dumps(GOOD_INV))
    add("array-claim", "[]", json.dumps(GOOD_INV))
    add("claim-is-string", '"hello"', json.dumps(GOOD_INV))
    add("missing-id", json.dumps({k: v for k, v in GOOD_CLAIM.items() if k != "claim_id"}),
        json.dumps(GOOD_INV))
    add("coverage-is-string", json.dumps({**GOOD_CLAIM, "claimed_coverage": "lots"}), json.dumps(GOOD_INV))
    add("unknown-level", json.dumps({**GOOD_CLAIM, "declared_level": "TOTALLY_PROVEN"}), json.dumps(GOOD_INV))
    add("excluded-is-object", json.dumps({**GOOD_CLAIM, "excluded": {"a": 1}}), json.dumps(GOOD_INV))
    add("not-claimed-is-string", json.dumps({**GOOD_CLAIM, "not_claimed": "NC-01"}), json.dumps(GOOD_INV))
    add("target-lock-is-string", json.dumps({**GOOD_CLAIM, "target_lock": "t@1"}), json.dumps(GOOD_INV))
    add("tier-is-string", json.dumps({**GOOD_CLAIM, "evidence_tier": "two"}), json.dumps(GOOD_INV))
    add("inventory-empty", json.dumps(GOOD_CLAIM), "")
    add("inventory-no-paths", json.dumps(GOOD_CLAIM),
        json.dumps({k: v for k, v in GOOD_INV.items() if k != "paths"}))
    add("inventory-paths-is-object", json.dumps(GOOD_CLAIM),
        json.dumps({**GOOD_INV, "paths": {"a": 1}}))
    add("inventory-path-missing-entry", json.dumps(GOOD_CLAIM),
        json.dumps({**GOOD_INV, "paths": [{"path_id": "wp_1"}]}))
    add("deep-nesting", json.dumps({**GOOD_CLAIM, "flow": "[" * 400 + "]" * 400}), json.dumps(GOOD_INV))
    add("huge-claim", json.dumps({**GOOD_CLAIM, "flow": "x" * 200000}), json.dumps(GOOD_INV))

    passed, failures = 0, []
    for name, claim, inv in cases:
        r = subprocess.run([sys.executable, str(VERIFY), "--claim", str(claim), "--inventory", str(inv)],
                           capture_output=True, text=True, timeout=120)
        ok_json = False
        verdict = None
        try:
            out = json.loads(r.stdout)
            ok_json = "verdict" in out
            verdict = out.get("verdict")
        except Exception:  # noqa: BLE001
            pass
        traceback = "Traceback" in (r.stderr or "")
        ok = ok_json and not traceback and r.returncode in (1, 2)
        passed += ok
        if not ok:
            failures.append({"case": name, "exit": r.returncode, "json": ok_json,
                             "verdict": verdict, "traceback": traceback})
        print(f"{name:28} exit={r.returncode} json={'yes' if ok_json else 'NO '} "
              f"traceback={'YES' if traceback else 'no '} verdict={verdict}")

    print(f"\ncases: {len(cases)}, handled as a verdict: {passed}")
    print("threshold (pre-registered): every case")
    for f in failures:
        print("  failure:", f)
    print(f"RESULT: {'PASS' if passed == len(cases) else 'FAIL'}")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
