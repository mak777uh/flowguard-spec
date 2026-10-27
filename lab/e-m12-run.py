#!/usr/bin/env python3
"""E-M12 harness: the ten acceptance scenarios from round 7, run against fg_verify.

The scenarios come from review 1 of round 7 (the T1-T10 table). They were written by that reviewer
without seeing our verifier, which makes them a genuine acceptance suite rather than a test written
to match the implementation.

Thresholds are pre-registered in lab/experiments/E-M12-claim-refusal.md.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "tools" / "fg_verify.py"

CORE = "function:bank.transfer"


def manifest(core=8, outside=2, independent=True, conflicts=None, target="abc123",
             delta=None, growth=False, kinds=("grants",), sources=None):
    paths = []
    for i in range(core):
        paths.append({"path_id": f"wp_core{i}", "entry": f"table:core{i}", "kind": "function",
                      "control_point": CORE, "confidence": "catalog", "found_by": ["grants-pg-v0.1"]})
    for i in range(outside):
        paths.append({"path_id": f"wp_out{i}", "entry": f"table:out{i}", "kind": "privilege",
                      "control_point": "", "confidence": "catalog", "found_by": ["grants-pg-v0.1"]})
    return {
        "manifest_version": "inventory/0.1",
        "target_lock": target,
        "sources": sources or [{"source_id": "grants-pg-v0.1", "kind": k, "covers": [], "blind_spots": ["declared"]}
                               for k in kinds],
        "independent_of_agent": independent,
        "paths": paths,
        "conflicts": conflicts or [],
        "delta_since_previous": delta,
        "perimeter_growth": growth,
    }


def claim(level="SCOPED_ASSURANCE", coverage=0.8, excluded=1, target="abc123", control=CORE):
    return {"claim_id": "C1", "flow": "balance_transfer", "target_lock": {"commit": target},
            "declared_control_point": control, "declared_level": level,
            "claimed_coverage": coverage, "excluded": [f"x{i}" for i in range(excluded)]}


def run(tmp, m, c, r=None, pol=None, attempts=1):
    files = {}
    for name, doc in (("m", m), ("c", c), ("r", r), ("p", pol)):
        if doc is None:
            continue
        f = Path(tmp) / f"{name}.json"
        f.write_text(json.dumps(doc, indent=1), encoding="utf-8")
        files[name] = str(f)
    cmd = [sys.executable, str(VERIFY), "--claim", files["c"], "--inventory", files["m"],
           "--attempts", str(attempts)]
    if "r" in files:
        cmd += ["--report", files["r"]]
    if "p" in files:
        cmd += ["--policy", files["p"]]
    pr = subprocess.run(cmd, capture_output=True, text=True)
    out = json.loads(pr.stdout)
    return pr.returncode, out


SCENARIOS = [
    ("T1", "correct claim, full declared scope", lambda: (manifest(), claim(), None, None, 1),
     lambda c, o: o["verdict"] == "SCOPED_ASSURANCE" and not o["errors"]),
    ("T2", "claims proven at coverage 0.6",
     lambda: (manifest(6, 4), claim(level="PROVEN", coverage=0.6), None, None, 1),
     lambda c, o: o["verdict"] != "PROVEN" and any(e["code"] == "CLAIM_EXCEEDS_EVIDENCE" for e in o["errors"])),
    ("T3", "one required path missing, claim says full coverage",
     lambda: (manifest(8, 2), claim(coverage=1.0), None, None, 1),
     lambda c, o: any(e["code"] == "CLAIM_EXCEEDS_EVIDENCE" for e in o["errors"])),
    ("T4", "report and bundle agree but different commits",
     lambda: (manifest(target="abc123"), claim(target="def456"), None, None, 1),
     lambda c, o: c == 2 and o["verdict"] == "INVALID"),
    ("T5", "unjustified exclusion beyond the ceiling",
     lambda: (manifest(), claim(excluded=5), None, None, 1),
     lambda c, o: any(e["code"] == "POLICY_CEILING_EXCEEDED" for e in o["errors"])),
    ("T6", "policy source untrusted",
     lambda: (manifest(), claim(), None, {"policy_id": "p", "trusted": False}, 1),
     lambda c, o: c == 2 and any(e["code"] == "POLICY_UNTRUSTED" for e in o["errors"])),
    ("T7", "new external path appeared this run",
     lambda: (manifest(delta={"new_paths": 2, "closed_paths": 0, "net_change": 2}, growth=True), claim(), None, None, 1),
     lambda c, o: o["perimeter"]["perimeter_growth"] is True and o["perimeter"]["level_upgrade_allowed"] is False),
    ("T8", "path moved into core without new evidence",
     lambda: (manifest(7, 3), claim(level="PROVEN", coverage=1.0), None, None, 1),
     lambda c, o: o["verdict"] != "PROVEN"),
    ("T9", "evidence removed, verdict must not strengthen",
     lambda: (manifest(7, 3), claim(level="SCOPED_ASSURANCE", coverage=0.8), None, None, 1),
     lambda c, o: o["verdict"] in ("CONSISTENT_DECLARED", "SCOPED_ASSURANCE") and o["computed_coverage"] == 0.7),
    ("T10", "resubmission after refusal exceeds the retry budget",
     lambda: (manifest(), claim(), None, None, 4),
     lambda c, o: c == 2 and any(e["code"] == "RETRY_BUDGET_EXCEEDED" for e in o["errors"])),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.parse_args()

    passed = 0
    print(f"{'id':4} {'scenario':46} result")
    with tempfile.TemporaryDirectory() as tmp:
        for sid, text, build, check in SCENARIOS:
            m, c, r, pol, attempts = build()
            code, out = run(tmp, m, c, r, pol, attempts)
            ok = check(code, out)
            passed += ok
            print(f"{sid:4} {text:46} {'PASS' if ok else 'FAIL'}")
            if not ok or "--verbose" in sys.argv:
                print("     ", json.dumps({"exit": code, **out}, ensure_ascii=False)[:400])

    total = len(SCENARIOS)
    print(f"\nscenarios passed: {passed}/{total}")
    print("threshold (pre-registered): 10/10")
    print(f"RESULT: {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
