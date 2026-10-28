#!/usr/bin/env python3
"""fg-init — one command from a schema dump to a verdict.

Reviewer finding (E-M43): the readiness tier T2 says "an outsider can install and reproduce", but there was
no install procedure at all: the harnesses assumed a running PostgreSQL, a database, and a hand-written
claim. This does the whole path once, in the open, and prints what it did.

    python tools/fg_init.py --psql <psql> --dump schema.sql --db fg_try \
                            --schema public --table projects --control function:public.audit

What it does, in order, and stops at the first failure:

1. creates the database if it is absent (and says so)
2. loads the dump with ON_ERROR_STOP=1
3. counts tables and functions, and prints the **db_logic_density band** before any claim is made, because a
   thin database cannot carry a strong verdict and the user should learn that before reading one
4. runs the two enumerators that exist (grants, calls) into a temporary directory
5. merges them into an inventory, with the target lock derived from the dump's digest
6. writes a claim template — CONSISTENT_DECLARED, coverage 0 — never a strong one
7. runs the verifier and prints the verdict, its refusals and the next steps
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", required=True)
    ap.add_argument("--dump", required=True)
    ap.add_argument("--schema", default="public")
    ap.add_argument("--table", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    work = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="fg-init-"))
    work.mkdir(parents=True, exist_ok=True)
    base = [a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user]

    def say(step, detail=""):
        print(f"[{step}] {detail}" if detail else f"[{step}]")

    # 1. database
    rc, out, err = sh(base + ["-d", "postgres", "-tAc",
                              f"SELECT 1 FROM pg_database WHERE datname='{a.db}'"])
    if out.strip() != "1":
        rc, out, err = sh(base + ["-d", "postgres", "-c", f'CREATE DATABASE "{a.db}"'])
        if rc != 0:
            print("cannot create the database:", err.strip()[:200])
            return 1
        say("1/7 database", f"{a.db} created")
    else:
        say("1/7 database", f"{a.db} already exists")

    # 2. load
    rc, out, err = sh(base + ["-d", a.db, "-v", "ON_ERROR_STOP=1", "-q", "-f", a.dump])
    if rc != 0:
        print("the dump did not load:", (err or out).strip()[:300])
        return 1
    say("2/7 dump loaded", f"{Path(a.dump).name}, {Path(a.dump).stat().st_size} bytes")

    # 3. how much logic is in the database at all
    def scalar(sql):
        rc, out, _ = sh(base + ["-d", a.db, "-tAc", sql])
        try:
            return int(out.strip() or 0)
        except ValueError:
            return 0

    tables = scalar("select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace "
                    f"where n.nspname='{a.schema}' and c.relkind in ('r','p')")
    funcs = scalar("select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                   f"where n.nspname='{a.schema}'")
    writing = scalar("select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                     f"where n.nspname='{a.schema}' and p.prosrc ~* '(update|insert[[:space:]]+into|delete[[:space:]]+from)'")
    density = round(writing / funcs, 3) if funcs else None
    band = (None if density is None else
            "thin" if density < 0.15 else "mixed" if density < 0.40 else "dense")
    say("3/7 scope", f"{tables} tables, {funcs} functions, {writing} writing "
                     f"(density {density}, band {band})")
    if band == "thin":
        print("     note: most write logic is outside the database; a strong verdict is refused on such a "
              "system by the verifier, and this run will not be an exception")

    lock = f"{a.db}@{hashlib.sha256(Path(a.dump).read_bytes()).hexdigest()[:12]}"

    # 4. enumerate
    grants = work / "grants.json"
    calls = work / "calls.json"
    rc, out, err = sh([sys.executable, str(ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"),
                       "--psql", a.psql, "--port", str(a.port), "--user", a.user, "--db", a.db,
                       "--schema", a.schema, "--table", a.table, "--out", str(grants),
                       "--target-lock", lock])
    if rc != 0:
        print("the grants enumerator failed:", (err or out).strip()[:300])
        return 1
    say("4/7 enumerated", out.strip().splitlines()[-1] if out.strip() else "grants")

    control_name = a.control.split(":")[-1].split(".")[-1]
    rc, out, err = sh([sys.executable, str(ROOT / "enumerators" / "pgcalls" / "fg_enum_pgcalls.py"),
                       "--psql", a.psql, "--port", str(a.port), "--user", a.user, "--db", a.db,
                       "--schema", a.schema, "--control", control_name, "--out", str(calls),
                       "--target-lock", lock])
    if rc != 0:
        print("note: the call enumerator did not run ({}) — coverage will be zero, which is honest".format(
            (err or out).strip()[:120]))
        sources = [grants]
    else:
        say("5/7 callers enumerated", out.strip().splitlines()[-1] if out.strip() else "calls")
        sources = [grants, calls]

    # 5. merge
    inv = work / "inventory.json"
    rc, out, err = sh([sys.executable, str(ROOT / "tools" / "merge_inventory.py"), *[str(s) for s in sources],
                       "--out", str(inv)])
    if rc != 0:
        print("merge failed:", (err or out).strip()[:300])
        return 1
    say("6/7 inventory", f"{inv} ({len(json.loads(inv.read_text(encoding='utf-8')).get('paths', []))} paths)")

    # 6. a claim that claims nothing it has not earned
    claim = work / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": f"first-run-{a.db}",
        "target_lock": {"commit": lock},
        "declared_control_point": a.control,
        "declared_level": "CONSISTENT_DECLARED",
        "claimed_coverage": 0.0,
        "excluded": [],
        "evidence_tier": 0,
        "not_claimed": ["NC-01", "NC-02", "NC-04", "NC-05", "NC-11"],
    }, indent=1), encoding="utf-8")

    # 7. verdict
    rc, out, err = sh([sys.executable, str(ROOT / "tools" / "fg_verify.py"),
                       "--claim", str(claim), "--inventory", str(inv)])
    try:
        doc = json.loads(out)
    except Exception:  # noqa: BLE001
        print("the verifier did not answer:", (err or out).strip()[:300])
        return 1
    say("7/7 verdict", doc["verdict"])
    for e in doc.get("errors", []):
        print(f"     {e['code']}: {e.get('next_action', '')}")
    print()
    print("what this run produced:")
    for name, path in (("inventory", inv), ("claim", claim)):
        print(f"  {name:10} {path}")
    print()
    print("next steps, in order of what they buy:")
    print("  1. read the inventory: every path is a way to write the table without the control point")
    print("  2. raise the claim only when the evidence raises it - the verifier refuses a claim above it")
    print("  3. to bind the result to a party, create a bundle: python tools/fg_bundle.py create --help")
    return 0


if __name__ == "__main__":
    sys.exit(main())
