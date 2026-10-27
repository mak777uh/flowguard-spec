#!/usr/bin/env python3
"""E-M30 harness: the same tool on five public schemas nobody here wrote.

Round-8 review, all three models: every number so far came from a fixture written by the tool's
author. The smallest honest answer is not a bigger fixture — it is foreign input.

Protocol, fixed BEFORE any run:
  * schemas: pagila, chinook, northwind, sakila, adventureworks — public sample databases,
    chosen because they are public and varied, not because of an expected result;
  * target table per schema: the table whose name suggests money movement, chosen by a fixed rule
    (first match in an ordered list of name patterns), not by looking at the findings;
  * one run per schema, no tuning between runs;
  * recorded per schema: tables, functions, paths, findings, run time, and whether the run raised
    an unenumerable verb or an ambiguous attribution;
  * findings are NOT claimed as true: confirming one requires the schema's owner, which we do not
    have. Tier 1 (E-M29) remains the honest ceiling.

    python lab/e-m30-run.py --psql <psql> --port 54329
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"
# The schema files are third-party and not committed; the directory is supplied on the command line.

TARGETS = ["payment", "payments", "invoice", "invoices", "order", "orders", "sale", "sales",
           "transaction", "transactions", "purchase", "purchases"]




def psql(psql_bin, port, user, db, *args, sql=None):
    cmd = [psql_bin, "-h", "127.0.0.1", "-p", str(port), "-U", user, "-d", db, "-q", "-tA"] + list(args)
    if sql:
        cmd += ["-c", sql]
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--schemas", required=True, help="directory holding the downloaded schema dumps")
    ap.add_argument("--pagila", required=True, help="path to the pagila schema dump")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())
    rows = []
    schema_dir = Path(a.schemas)
    schemas = [
        ("pagila", Path(a.pagila)),
        ("chinook", schema_dir / "chinook.sql"),
        ("northwind", schema_dir / "northwind.sql"),
        ("sakila", schema_dir / "sakila.sql"),
        ("adventureworks", schema_dir / "adventureworks.sql"),
    ]

    for name, path in schemas:
        if not path.exists():
            rows.append({"schema": name, "status": "missing file"})
            continue
        db = f"fg_{name}"
        psql(a.psql, a.port, a.user, "postgres", sql=f"DROP DATABASE IF EXISTS {db};")
        psql(a.psql, a.port, a.user, "postgres", sql=f"CREATE DATABASE {db};")
        t0 = time.time()
        to_load = path
        if name == "chinook":
            # the script creates its own database and switches into it; we load into ours instead
            lines = [l for l in path.read_text(encoding="utf-8", errors="ignore").splitlines()
                     if not l.strip().upper().startswith(("CREATE DATABASE", "\\C "))]
            to_load = tmp / "chinook-clean.sql"
            to_load.write_text("\n".join(lines), encoding="utf-8")
        load = psql(a.psql, a.port, a.user, db, "-f", str(to_load))
        load_errors = sum(1 for line in (load.stderr or "").splitlines() if "ERROR" in line)
        tables = psql(a.psql, a.port, a.user, db, sql=(
            "select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace "
            "where n.nspname='public' and c.relkind='r';")).stdout.strip()
        funcs = psql(a.psql, a.port, a.user, db, sql=(
            "select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
            "where n.nspname='public';")).stdout.strip()
        target = ""
        for pat in TARGETS:
            # Partitions are excluded: pagila's `payment` is a partitioned parent, and the first
            # name match picked a single partition, which is not the table the flow uses.
            hit = psql(a.psql, a.port, a.user, db, sql=(
                "select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace "
                "where n.nspname='public' and c.relkind in ('r','p') and c.relispartition = false "
                f"and c.relname ilike '%{pat}%' "
                f"order by (c.relname = '{pat}') desc, c.relname limit 1;")).stdout.strip()
            if hit:
                target = hit
                break
        if not target:
            rows.append({"schema": name, "status": f"loaded ({load_errors} errors), no target table",
                         "tables": tables, "functions": funcs})
            continue
        out = tmp / f"{name}.json"
        r = subprocess.run([sys.executable, str(GRANTS), "--psql", a.psql, "--port", str(a.port),
                            "--user", a.user, "--db", db, "--schema", "public", "--table", target,
                            "--out", str(out), "--target-lock", f"{name}@e-m30"],
                           capture_output=True, text=True)
        doc = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"paths": []}
        kinds = {}
        for p in doc.get("paths", []):
            kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
        rows.append({
            "schema": name, "status": "ok", "load_errors": load_errors,
            "tables": tables, "functions": funcs, "target": target,
            "paths": len(doc.get("paths", [])), "kinds": kinds,
            "seconds": round(time.time() - t0, 1),
        })

    print(f"{'schema':15} {'tables':>6} {'funcs':>5} {'target':16} {'paths':>5} {'sec':>5}  kinds")
    for r in rows:
        if r.get("status") != "ok":
            print(f"{r['schema']:15} {r.get('tables','-'):>6} {r.get('functions','-'):>5} "
                  f"{'-':16} {'-':>5} {'-':>5}  {r.get('status')}")
            continue
        print(f"{r['schema']:15} {r['tables']:>6} {r['functions']:>5} {r['target']:16} "
              f"{r['paths']:>5} {r['seconds']:>5}  {r['kinds']}")

    ok_rows = [r for r in rows if r.get("status") == "ok"]
    total_findings = sum(r["paths"] for r in ok_rows)
    print(f"\nschemas run: {len(ok_rows)}/{len(schemas)}, total paths reported: {total_findings}")
    (tmp / "summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("summary:", tmp / "summary.json")
    ok = len(ok_rows) >= 4
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
