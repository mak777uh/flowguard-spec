#!/usr/bin/env python3
"""E-M36: attack the verdict gate. Two of them worked.

The point of this harness is not that the tool now refuses these two - it is that they were possible
until someone tried. A gate nobody attacks is a gate nobody has tested.

    python lab/e-m36-run.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "tools" / "fg_verify.py"
CORE = "function:bank.transfer"
LEVEL_CODES = ["NC-01", "NC-02", "NC-04", "NC-05", "NC-11"]


def source(covers=("tables",), blind=("everything else",), kind="grants"):
    return {"source_id": "s", "kind": kind, "covers": list(covers), "blind_spots": list(blind),
            "completeness_claim": "exhaustive_within_covers"}


def path(i, entry, cp="", attribution=None):
    p = {"path_id": "wp_%016d" % i, "entry": entry, "kind": "privilege", "control_point": cp}
    if attribution:
        p["attribution"] = attribution
    return p


def manifest(paths, kind="grants"):
    return {"manifest_version": "inventory/0.1", "target_lock": "t@1",
            "sources": [source(kind=kind)], "independent_of_agent": True, "paths": paths}


def claim(level="SCOPED_ASSURANCE", coverage=1.0, tier=1):
    return {"claim_id": "atk", "target_lock": {"commit": "t@1"}, "declared_control_point": CORE,
            "declared_level": level, "claimed_coverage": coverage, "excluded": [],
            "evidence_tier": tier, "not_claimed": LEVEL_CODES}


ATTACKS = [
    ("A1 one path, coverage 1.0",
     lambda: manifest([path(1, "table:bank.accounts", CORE)]),
     lambda: claim(), {"COVERAGE_BASIS_TOO_SMALL", "UNSUPPORTED_CONTROL_POINT_CLAIM"}),
    ("A2 two paths, coverage 1.0",
     lambda: manifest([path(1, "table:a", CORE), path(2, "table:b", CORE)]),
     lambda: claim(), {"COVERAGE_BASIS_TOO_SMALL", "UNSUPPORTED_CONTROL_POINT_CLAIM"}),
    ("A3 every path declares itself in-core",
     lambda: manifest([path(i, f"table:t{i}", CORE) for i in range(1, 12)]),
     lambda: claim(), {"UNSUPPORTED_CONTROL_POINT_CLAIM"}),
    ("A4 attribution with no source",
     lambda: manifest([path(i, f"table:t{i}", CORE, {"to": CORE, "method": "direct", "sources": []})
                       for i in range(1, 12)]),
     lambda: claim(), {"UNSUPPORTED_CONTROL_POINT_CLAIM"}),
    ("A5 empty not_claimed",
     lambda: manifest([path(i, f"table:t{i}", CORE, {"to": CORE, "method": "direct",
                                                     "sources": ["s"]}) for i in range(1, 12)]),
     lambda: {**claim(), "not_claimed": []}, {"MISSING_EVIDENCE"}),
    ("A6 PROVEN at tier 0",
     lambda: manifest([path(i, f"table:t{i}", CORE, {"to": CORE, "method": "direct",
                                                     "sources": ["s"]}) for i in range(1, 12)]),
     lambda: claim(level="PROVEN", tier=0), {"CLAIM_EXCEEDS_EVIDENCE"}),
    ("A7 witness-only inventory",
     lambda: manifest([path(i, f"table:t{i}", CORE, {"to": CORE, "method": "direct",
                                                     "sources": ["s"]}) for i in range(1, 12)],
                      kind="runtime"),
     lambda: claim(), {"MISSING_EVIDENCE"}),
    ("A8 excluded everything",
     lambda: manifest([path(i, f"table:t{i}", CORE, {"to": CORE, "method": "direct",
                                                     "sources": ["s"]}) for i in range(1, 12)]),
     lambda: claim(coverage=1.0), {"REPORT_BUNDLE_INCONSISTENT"}),
]


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    for i, (stmt, inv_fn, claim_fn, code) in enumerate([a for a in ATTACKS if a[0].startswith("A8")]):
        pass
    passed, rows = 0, []
    for name, inv_fn, claim_fn, expected in ATTACKS:
        inv, cl = inv_fn(), claim_fn()
        if name.startswith("A8"):
            cl = {**cl, "excluded": [{"path_id": f"wp_{i:016d}", "reason_code": "OWNER_ACCEPTS",
                                      "accepted_by": "x", "valid_until": "2027-01-01",
                                      "reason": "everything"} for i in range(1, 12)]}
        ci = tmp / "c.json"
        mi = tmp / "m.json"
        ci.write_text(json.dumps(cl), encoding="utf-8")
        mi.write_text(json.dumps(inv), encoding="utf-8")
        r = subprocess.run([sys.executable, str(VERIFY), "--claim", str(ci), "--inventory", str(mi)],
                           capture_output=True, text=True)
        out = json.loads(r.stdout)
        codes = {e["code"] for e in out.get("errors", [])}
        blocked = bool(codes & expected) and out["verdict"] != "PROVEN"
        passed += blocked
        rows.append((name, out["verdict"], sorted(codes)[:3], blocked))
        print(f"{name:38} {out['verdict']:20} {sorted(codes)[:2]}")

    print(f"\nattacks blocked: {passed}/{len(ATTACKS)}")
    print(f"RESULT: {'PASS' if passed == len(ATTACKS) else 'FAIL'}")
    return 0 if passed == len(ATTACKS) else 1


if __name__ == "__main__":
    sys.exit(main())
