#!/usr/bin/env python3
"""E-M35: a truncated inventory is refused as a coverage denominator.

A cap is necessary (E-M34: 480 paths is unreadable) and dangerous (a ratio over a truncated list is a
ratio over an unknown subset). The rule: truncation is allowed for reading, refused for arithmetic.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"
MERGE = ROOT / "tools" / "merge_inventory.py"
VERIFY = ROOT / "tools" / "fg_verify.py"


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    out = tmp / "trunc.json"
    r = subprocess.run([sys.executable, str(GRANTS), "--psql", a.psql, "--port", str(a.port),
                        "--user", a.user, "--db", "fg_scale", "--schema", "bank", "--table", "target",
                        "--max-paths", "100", "--out", str(out), "--target-lock", "scale@e-m35"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 1
    doc = json.loads(out.read_text(encoding="utf-8"))
    trunc = doc.get("truncated") or {}
    print(f"paths kept {len(doc['paths'])}, truncated {trunc}, claim {doc['completeness_claim']}")
    print(f"summary matches the published list: {sum(doc['summary']['by_kind'].values()) == len(doc['paths'])}")

    man = tmp / "m.json"
    subprocess.run([sys.executable, str(MERGE), str(out), "--out", str(man)],
                   capture_output=True, text=True)
    claim = tmp / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": "E-M35", "target_lock": {"commit": "scale@e-m35"},
        "declared_control_point": "function:bank.target", "declared_level": "CONSISTENT_DECLARED",
        "claimed_coverage": 0.5, "excluded": [], "evidence_tier": 1,
        "not_claimed": ["NC-01", "NC-02"]}), encoding="utf-8")
    v = subprocess.run([sys.executable, str(VERIFY), "--claim", str(claim), "--inventory", str(man)],
                       capture_output=True, text=True)
    out_doc = json.loads(v.stdout)
    codes = [e["code"] for e in out_doc.get("errors", [])]
    refused = "MISSING_EVIDENCE" in codes and any(
        e["subject"] == "coverage_basis" for e in out_doc.get("errors", []))
    print(f"coverage refused on a truncated source: {refused} (codes {codes[:4]})")

    ok = (len(doc["paths"]) == 100 and trunc.get("omitted", 0) > 0
          and doc["completeness_claim"] == "partial" and refused)
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
