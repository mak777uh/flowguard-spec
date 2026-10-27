#!/usr/bin/env python3
"""E-M25 harness: an overload makes a name-based attribution a guess.

All three round-8 reviews named the same class: joining sources by bare function name is not an
identity. PostgreSQL allows overloads, so `transfer` can be two different functions - one the control
point, one a direct writer.

This harness builds exactly that shape, then checks that the merger refuses to attribute the route
and says why.

    python lab/e-m25-run.py --psql <psql> --port 54329
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E11 = ROOT / "lab" / "e-m11-run.py"
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"
CALLS = ROOT / "enumerators" / "pgcalls" / "fg_enum_pgcalls.py"
ROUTES = ROOT / "enumerators" / "routes-json" / "fg_enum_routes.py"
MERGE = ROOT / "tools" / "merge_inventory.py"
VERIFY = ROOT / "tools" / "fg_verify.py"

OVERLOAD = """
CREATE OR REPLACE FUNCTION bank.transfer(src integer, dst integer, amt numeric, note text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $fn$
BEGIN
  UPDATE bank.accounts SET balance = balance + amt WHERE id = dst;
END $fn$;
GRANT EXECUTE ON FUNCTION bank.transfer(integer, integer, numeric, text) TO app_rw;
"""

ROUTE = {
    "service": "bank-api",
    "target_lock": "bank-api@e-m25",
    "routes": [
        {"method": "POST", "path": "/transfer", "handler": "api_transfer",
         "writes": ["accounts"], "calls": ["transfer"]}
    ],
}


def sh(cmd, check=True):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"step failed: {Path(str(cmd[1])).name}")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", default="fgfix")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    sh([sys.executable, str(E11), "--psql", a.psql, "--port", str(a.port),
        "--user", a.user, "--db", a.db], check=False)

    sql = tmp / "overload.sql"
    sql.write_text(OVERLOAD, encoding="utf-8")
    sh([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", a.db,
        "-q", "-f", str(sql)])

    lock = "fgfix@e-m25"
    g, c, rt = tmp / "g.json", tmp / "c.json", tmp / "r.json"
    sh([sys.executable, str(GRANTS), "--psql", a.psql, "--port", a.port, "--user", a.user,
        "--db", a.db, "--schema", "bank", "--table", "accounts", "--out", g, "--target-lock", lock])
    sh([sys.executable, str(CALLS), "--psql", a.psql, "--port", a.port, "--user", a.user,
        "--db", a.db, "--schema", "bank", "--control", "transfer", "--out", c, "--target-lock", lock])
    manifest = tmp / "routes.json"
    manifest.write_text(json.dumps(ROUTE), encoding="utf-8")
    sh([sys.executable, str(ROUTES), "--manifest", manifest, "--schema", "bank",
        "--table", "accounts", "--control", "transfer", "--out", rt, "--target-lock", lock])

    m = tmp / "m.json"
    out = sh([sys.executable, str(MERGE), g, c, rt, "--out", m]).stdout
    doc = json.loads(m.read_text(encoding="utf-8"))

    route = [p for p in doc["paths"] if p["kind"] == "http_entry"][0]
    attr = route.get("attribution")
    conflict = route.get("attribution_conflict")

    names = sorted({p["entry"].rsplit(".", 1)[-1] for p in doc["paths"]
                    if p["entry"].startswith("function:")})
    print(f"functions in the schema: {', '.join(names)}")
    print(f"route {route['entry']}: attribution={attr} conflict={conflict}")

    claim = tmp / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": "E-M25", "target_lock": {"commit": lock},
        "declared_control_point": "function:bank.transfer",
        "declared_level": "SCOPED_ASSURANCE", "claimed_coverage": 0.9,
        "excluded": [], "not_claimed": ["NC-01", "NC-02", "NC-04", "NC-05"],
    }), encoding="utf-8")
    pr = sh([sys.executable, str(VERIFY), "--claim", claim, "--inventory", m], check=False)
    verdict = json.loads(pr.stdout)
    codes = [e["code"] for e in verdict.get("errors", [])]
    print(f"verdict: {verdict['verdict']} codes={codes}")
    print(f"level_upgrade_allowed: {verdict['perimeter'].get('level_upgrade_allowed')}")

    ambiguous_caught = conflict is not None and attr is None
    blocked = verdict["perimeter"].get("level_upgrade_allowed") is False
    ok = ambiguous_caught and blocked
    print(f"\nambiguous attribution detected: {ambiguous_caught}")
    print(f"upgrade blocked: {blocked}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
