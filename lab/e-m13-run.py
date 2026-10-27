#!/usr/bin/env python3
"""E-M13 harness: attribution from a call graph, end to end through the merger and the verifier."""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E11 = ROOT / "lab" / "e-m11-run.py"
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"
CALLS = ROOT / "enumerators" / "pgcalls" / "fg_enum_pgcalls.py"
MERGE = ROOT / "tools" / "merge_inventory.py"
VERIFY = ROOT / "tools" / "fg_verify.py"
CP = "function:bank.transfer"
THRESHOLD = {"attributed": (2, 2), "false_attribution": (0, 9)}


def sh(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"step failed: {cmd[1]}")
    return r.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", default="fgfix")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    # fixture comes from the E-M11 harness, which builds and loads it
    subprocess.run([sys.executable, str(E11), "--psql", a.psql, "--port", str(a.port),
                    "--user", a.user, "--db", a.db], capture_output=True, text=True)

    g, c = tmp / "g.json", tmp / "c.json"
    sh([sys.executable, GRANTS, "--psql", a.psql, "--port", a.port, "--user", a.user,
        "--db", a.db, "--schema", "bank", "--table", "accounts", "--out", g,
        "--target-lock", "fgfix@e-m13"])
    sh([sys.executable, CALLS, "--psql", a.psql, "--port", a.port, "--user", a.user,
        "--db", a.db, "--schema", "bank", "--control", "transfer", "--out", c,
        "--target-lock", "fgfix@e-m13"])
    m = tmp / "m.json"
    sh([sys.executable, MERGE, g, c, "--out", m])

    man = json.loads(m.read_text(encoding="utf-8"))
    attributed = [p for p in man["paths"] if (p.get("attribution") or {}).get("to") == CP]
    entries = {p["entry"] for p in attributed}
    decoy = [p for p in man["paths"] if "transfer_fast" in p["entry"]]
    decoy_ok = decoy and not (decoy[0].get("attribution") or {}).get("to")

    print(f"paths: {man['paths_total']}, attributed to {CP}: {len(attributed)}")
    for e in sorted(entries):
        print(f"  in core: {e}")
    print(f"decoy transfer_fast not attributed: {bool(decoy_ok)}")

    need_attr, total_attr = THRESHOLD["attributed"]
    print(f"attribution {len(attributed)}/{total_attr} (need {need_attr})")
    print(f"false attribution: {0 if decoy_ok else 1}/{THRESHOLD['false_attribution'][1]}")

    claim = tmp / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": "E-M13", "target_lock": {"commit": "fgfix@e-m13"},
        "declared_control_point": CP, "declared_level": "CONSISTENT_DECLARED",
        "claimed_coverage": round(len(attributed) / man["paths_total"], 3), "excluded": [],
        "not_claimed": ["NC-01", "NC-02"],
    }), encoding="utf-8")
    out = sh([sys.executable, VERIFY, "--claim", claim, "--inventory", m])
    v = json.loads(out)
    print(f"verdict: {v['verdict']}, coverage {v['computed_coverage']}")

    ok = len(attributed) >= need_attr and decoy_ok and (v["computed_coverage"] or 0) > 0 and not v["errors"]
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
