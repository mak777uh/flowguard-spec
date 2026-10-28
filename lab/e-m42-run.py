"""E-M42: re-run the eleven breaks an independent adversarial agent found, against the patched gate.

The attack suite is kept as a regression: if one of these ever returns a strong verdict again, this
harness fails. Inputs are reconstructed here rather than read from the attacker scratch directory, so
the suite survives a clean checkout.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PY = sys.executable
V = "tools/fg_verify.py"
A = Path(__file__).resolve().parent.parent / "fixtures" / "attack"
# --self-test plants a wrong expectation and requires the suite to go red.
SELF_TEST = os.environ.get("FG_ATTACK_SELFTEST") == "1"

# Expected refusal codes per case: declared here so the suite states its intent, and so
# lab/check-refusal-coverage.py can see which code each attack is supposed to trigger.
EXPECTED = {
    "B1 one path, weak claim": ["EVIDENCE_TIER_UNSUPPORTED"],
    "B2 report says core empty": ["EVIDENCE_TIER_UNSUPPORTED"],
    "B3 eight copies of one path": ["COVERAGE_BASIS_TOO_SMALL"],
    "B4 truncation without label": ["MISSING_EVIDENCE"],
    "B5 refuted confirmation": ["EVIDENCE_TIER_UNSUPPORTED"],
    "B6 attribution sources [null]": ["CLAIM_EXCEEDS_EVIDENCE", "EVIDENCE_TIER_UNSUPPORTED"],
    "B7 growth declared": ["POLICY_CEILING_EXCEEDED"],
    "B8 empty commit": ["MISSING_EVIDENCE"],
    "B9 density deleted": ["THIN_DB_LOGIC_COVERAGE", "EVIDENCE_TIER_UNSUPPORTED"],
    "B10 observed DELETE as prose": ["REPORT_BUNDLE_INCONSISTENT"],
    "B10 control stmt:DELETE": ["UNENUMERABLE_PATH"],
    "A13 not independent": ["E_NO_INDEPENDENT_CLOSURE"],
    "B11 lenient policy": ["POLICY_UNTRUSTED"],
}
CASES = [
    ("B1 one path, weak claim", ["--claim", A / "k-consistent.json", "--inventory", A / "a4-inv.json"]),
    ("B2 report says core empty", ["--claim", A / "k-scoped.json", "--inventory", A / "a11-inv.json",
                                   "--report", A / "a12-report.json"]),
    ("B3 eight copies of one path", ["--claim", A / "a1-claim.json", "--inventory", A / "a1-inv.json"]),
    ("B4 truncation without label", ["--claim", A / "k-proven.json", "--inventory", A / "a5-inv.json"]),
    ("B5 refuted confirmation", ["--claim", A / "k-proven.json", "--inventory", A / "a3-inv.json"]),
    ("B6 attribution sources [null]", ["--claim", A / "k-proven.json", "--inventory", A / "a2-inv.json"]),
    ("B7 growth declared", ["--claim", A / "k-proven.json", "--inventory", A / "a9-inv.json"]),
    ("B8 empty commit", ["--claim", A / "k-commit-empty.json", "--inventory", A / "a10-inv.json"]),
    ("B9 density deleted", ["--claim", A / "k-proven.json", "--inventory", A / "a6-inv.json"]),
    ("B10 observed DELETE as prose", ["--claim", A / "a7-claim.json", "--inventory", A / "a7-inv.json"]),
    ("B10 control stmt:DELETE", ["--claim", A / "a7-claim.json", "--inventory", A / "a7b-inv.json"]),
    ("B11 lenient policy", ["--claim", A / "a4-claim.json", "--inventory", A / "a4-inv.json",
                            "--policy", A / "a4-policy.json"]),
    ("C1 tier as string", ["--claim", A / "c1-claim.json", "--inventory", A / "a4-inv.json"]),
]

bad = 0
for name, args in CASES:
    args = [str(x) for x in args]
    if SELF_TEST and name == "B1 one path, weak claim":
        # Deliberately wrong expectation: if the suite still reports green, the suite is a comment.
        EXPECTED[name] = ["THIS_CODE_NEVER_FIRES"]
    missing = [x for x in args if x.startswith(str(A)) and not Path(x).exists()]
    if missing:
        print(f"{name:32} SKIP (missing {[Path(m).name for m in missing]})")
        continue
    r = subprocess.run([PY, V] + args, capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
    except Exception:
        print(f"{name:32} NO JSON (exit {r.returncode}) traceback={'Traceback' in r.stderr}")
        bad += 1
        continue
    codes = sorted({e["code"] for e in out.get("errors", [])})
    want = EXPECTED.get(name, [])
    missing_expected = [c for c in want if c not in codes]
    strong = out["verdict"] in ("PROVEN", "SCOPED_ASSURANCE")
    flag = "STILL BREAKS" if strong else ("NO EXPECTED CODE" if missing_expected else "blocked")
    if strong or missing_expected:
        bad += 1
    print(f"{name:32} {out['verdict']:20} {flag:14} {codes[:3]}")

print(f"\nstill breaking: {bad}")
sys.exit(1 if bad else 0)
