#!/usr/bin/env python3
"""E-M26 harness: classify a perimeter change instead of blocking every change.

Round-8 review, all three: blanket-blocking any perimeter change rewards stagnation, because deleting
a dead path is also a change. The classified delta is:

  additive      new surface (shape not seen before)  -> blocks an upgrade
  substitutive  a new path replacing a vanished one of the same shape -> re-attest, may upgrade
  subtractive   removal with no replacement          -> never blocks

Three real states of the same database are measured here.

    python lab/e-m26-run.py --psql <psql> --port 54329
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
MERGE = ROOT / "tools" / "merge_inventory.py"
VERIFY = ROOT / "tools" / "fg_verify.py"

ADD = """
CREATE OR REPLACE FUNCTION bank.settle_batch(rows integer[]) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER AS $fn$
DECLARE r integer;
BEGIN
  FOREACH r IN ARRAY rows LOOP
    UPDATE bank.accounts SET balance = balance WHERE id = r;
  END LOOP;
END $fn$;
GRANT EXECUTE ON FUNCTION bank.settle_batch(integer[]) TO app_rw;
"""

DROP = "DROP FUNCTION IF EXISTS bank.settle_batch(integer[]);"


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

    state = {"n": 0}

    def snapshot(tag):
        state["n"] += 1
        sql = tmp / f"{tag}.sql"
        out = tmp / f"g-{tag}.json"
        if tag == "added":
            sql.write_text(ADD, encoding="utf-8")
            sh([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", a.db, "-q", "-f", str(sql)])
        if tag == "removed":
            sql.write_text(DROP, encoding="utf-8")
            sh([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", a.db, "-q", "-f", str(sql)])
        sh([sys.executable, str(GRANTS), "--psql", a.psql, "--port", a.port, "--user", a.user,
            "--db", a.db, "--schema", "bank", "--table", "accounts", "--out", out,
            "--target-lock", "fgfix@e-m26"])
        return out

    g0 = snapshot("base")
    m0 = tmp / "m0.json"
    sh([sys.executable, str(MERGE), g0, "--out", m0])

    g1 = snapshot("added")
    m1 = tmp / "m1.json"
    sh([sys.executable, str(MERGE), g1, "--previous", m0, "--out", m1])

    g2 = snapshot("removed")
    m2 = tmp / "m2.json"
    sh([sys.executable, str(MERGE), g2, "--previous", m1, "--out", m2])

    def read(p):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        return d.get("delta_since_previous") or {}, d.get("perimeter_growth")

    d1, growth1 = read(m1)
    d2, growth2 = read(m2)
    print("after adding a writer:   classification=%s growth=%s" % (d1.get("classification"), growth1))
    print("after removing it:       classification=%s growth=%s" % (d2.get("classification"), growth2))

    claim = tmp / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": "E-M26", "target_lock": {"commit": "fgfix@e-m26"},
        "declared_control_point": "function:bank.transfer",
        "declared_level": "SCOPED_ASSURANCE", "claimed_coverage": 0.2,
        "excluded": [], "not_claimed": ["NC-01", "NC-02", "NC-04", "NC-05"],
    }), encoding="utf-8")
    v1 = json.loads(sh([sys.executable, str(VERIFY), "--claim", claim, "--inventory", m1],
                       check=False).stdout)
    v2 = json.loads(sh([sys.executable, str(VERIFY), "--claim", claim, "--inventory", m2],
                       check=False).stdout)
    print("upgrade allowed while additive: %s" % v1["perimeter"].get("level_upgrade_allowed"))
    print("upgrade allowed after removal:  %s" % v2["perimeter"].get("level_upgrade_allowed"))

    ok = (
        (d1.get("classification") or {}).get("additive", 0) >= 1
        and growth1 is True
        and v1["perimeter"].get("level_upgrade_allowed") is False
        and (d2.get("classification") or {}).get("subtractive", 0) >= 1
        and growth2 is False
        and v2["perimeter"].get("perimeter_growth") is False
    )
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
