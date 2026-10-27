#!/usr/bin/env python3
"""Acceptance scenarios for the verifier: the round-7 T1-T10 table plus two exclusion cases.

T1-T10 were written by a round-7 reviewer who had not seen the implementation. T11-T12 were added
after the exclusion hole was found: `excluded` used to be free-text, so a claim could exclude
invented identifiers or even the covered core, and still pass.

Note on history: the original harness used placeholder exclusion strings ("x0", "x1"). When
exclusions became bound to real inventory paths those scenarios failed, correctly. They now exclude
real paths with reasons, which is what a real claim does. See lab/experiments/E-M14-exclusions.md.
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


REQUIRED = {
    "CONSISTENT_DECLARED": ["NC-01", "NC-02"],
    "SCOPED_ASSURANCE": ["NC-01", "NC-02", "NC-04", "NC-05"],
    "PROVEN": ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10"],
}


def claim(level="SCOPED_ASSURANCE", coverage=0.8, excluded=None, target="abc123", control=CORE,
          not_claimed=None):
    return {"claim_id": "C1", "flow": "balance_transfer", "target_lock": {"commit": target},
            "declared_control_point": control, "declared_level": level,
            "claimed_coverage": coverage, "excluded": excluded or [],
            "not_claimed": REQUIRED[level] if not_claimed is None else not_claimed}


def real_exclusions(m, n, reason="documented out of scope"):
    """n real outside paths, each with a reason - the only shape a valid exclusion can take."""
    outs = [p for p in m["paths"] if not p.get("control_point")]
    return [{"path_id": p["path_id"], "reason": reason} for p in outs[:n]]


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
    return pr.returncode, json.loads(pr.stdout)


def scenarios():
    def t1():
        m = manifest()
        return m, claim(excluded=real_exclusions(m, 1)), None, None, 1

    def t5():
        m = manifest(8, 6)
        return m, claim(excluded=real_exclusions(m, 5)), None, None, 1

    def t11():
        m = manifest()
        return m, claim(excluded=[{"path_id": "wp_invented", "reason": "looks plausible"}]), None, None, 1

    def t12():
        m = manifest()
        return m, claim(excluded=[{"path_id": "wp_core0", "reason": "we decided it is fine"}]), None, None, 1

    return [
        ("T1", "correct claim, full declared scope", t1,
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
        ("T5", "unjustified exclusion beyond the ceiling", t5,
         lambda c, o: any(e["code"] == "POLICY_CEILING_EXCEEDED" for e in o["errors"])),
        ("T6", "policy source untrusted",
         lambda: (manifest(), claim(), None, {"policy_id": "p", "trusted": False}, 1),
         lambda c, o: c == 2 and any(e["code"] == "POLICY_UNTRUSTED" for e in o["errors"])),
        ("T7", "new external path appeared this run",
         lambda: (manifest(delta={"new_paths": 2, "closed_paths": 0, "net_change": 2}, growth=True),
                  claim(), None, None, 1),
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
        ("T11", "exclusion names a path that does not exist", t11,
         lambda c, o: any(e["code"] == "UNKNOWN_OR_UNBOUND_PATH" for e in o["errors"])),
        ("T12", "exclusion names a path inside the covered core", t12,
         lambda c, o: any(e["code"] == "REPORT_BUNDLE_INCONSISTENT" for e in o["errors"])),
        ("T13", "not_claimed is prose instead of vocabulary",
         lambda: (manifest(), claim(not_claimed=["results may vary"]), None, None, 1),
         lambda c, o: any(e["code"] == "REPORT_BUNDLE_INCONSISTENT" for e in o["errors"])),
        ("T14", "claimed level without its required not_claimed codes",
         lambda: (manifest(10, 0), claim(level="PROVEN", coverage=1.0,
                                         not_claimed=["NC-01", "NC-02"]), None, None, 1),
         lambda c, o: any(e["code"] == "MISSING_EVIDENCE" and e["subject"] == "not_claimed" for e in o["errors"])),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.parse_args()

    passed = 0
    print(f"{'id':4} {'scenario':46} result")
    with tempfile.TemporaryDirectory() as tmp:
        items = scenarios()
        for sid, text, build, check in items:
            m, c, r, pol, attempts = build()
            code, out = run(tmp, m, c, r, pol, attempts)
            ok = check(code, out)
            passed += ok
            print(f"{sid:4} {text:46} {'PASS' if ok else 'FAIL'}")
            if not ok or "--verbose" in sys.argv:
                print("     ", json.dumps({"exit": code, **out}, ensure_ascii=False)[:400])

    total = len(items)
    print(f"\nscenarios passed: {passed}/{total}")
    print("threshold (pre-registered): all of them")
    print(f"RESULT: {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
