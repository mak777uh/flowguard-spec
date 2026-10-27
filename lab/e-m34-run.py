#!/usr/bin/env python3
"""E-M34: does the output stay usable when the schema is not a toy?

A reviewer warned: "a schema with four hundred functions may produce a list nobody reads, which is a
different failure and is not measured here." This measures it.

Pre-registered shape: 50 tables, 400 functions writing the target table in a dozen different ways,
30 triggers, 10 roles with grants. Pre-registered thresholds: the enumerator finishes in under 60
seconds, reports every planted writer, and — the point — the flat list is either small enough to
read (<= 120 paths) or the output carries a triage summary that makes the reading possible.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"

TABLES = 50
FUNCS = 400
TRIGGERS = 30
ROLES = 10

SHAPES = [
    "UPDATE bank.target SET v = v + 1 WHERE id = 1;",
    "INSERT INTO bank.target(id, v) VALUES (1, 1);",
    "DELETE FROM bank.target WHERE id = 1;",
    "PERFORM bank.helper(1);",
    "EXECUTE format('UPDATE bank.target SET v = %s', 1);",
]


def build_sql():
    parts = [
        "DROP SCHEMA IF EXISTS bank CASCADE;",
        "CREATE SCHEMA bank;",
        "CREATE TABLE bank.target (id int primary key, v int);",
        "CREATE FUNCTION bank.helper(x int) RETURNS int LANGUAGE sql AS $$ SELECT x + 1 $$;",
    ]
    for r in range(ROLES):
        parts.append(f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='app_r{r}') "
                     f"THEN CREATE ROLE app_r{r}; END IF; END $$;")
        parts.append(f"GRANT INSERT, UPDATE ON bank.target TO app_r{r};")
    for t in range(TABLES):
        parts.append(f"CREATE TABLE bank.t{t} (id int primary key, v int);")
    for i in range(FUNCS):
        body = SHAPES[i % len(SHAPES)]
        secdef = "SECURITY DEFINER" if i % 7 == 0 else "SECURITY INVOKER"
        parts.append(
            f"CREATE OR REPLACE FUNCTION bank.f{i}(a int) RETURNS void LANGUAGE plpgsql {secdef} AS "
            f"$$ BEGIN {body} END $$;")
        parts.append(f"GRANT EXECUTE ON FUNCTION bank.f{i}(int) TO app_r{i % ROLES};")
    for t in range(TRIGGERS):
        parts.append(
            f"CREATE OR REPLACE FUNCTION bank.trg{t}() RETURNS trigger LANGUAGE plpgsql AS "
            f"$$ BEGIN UPDATE bank.target SET v = v + 1 WHERE id = NEW.id; RETURN NEW; END $$;")
        parts.append(f"CREATE TRIGGER t{t} AFTER INSERT ON bank.t{t} FOR EACH ROW EXECUTE FUNCTION bank.trg{t}();")
    return "\n".join(parts)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    sql = tmp / "scale.sql"
    sql.write_text(build_sql(), encoding="utf-8")

    def psql(*args, sql_text=None):
        cmd = [a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", "fg_scale", "-q"] + list(args)
        if sql_text:
            cmd += ["-c", sql_text]
        return subprocess.run(cmd, capture_output=True, text=True)

    subprocess.run([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", "postgres",
                    "-q", "-c", "DROP DATABASE IF EXISTS fg_scale;"], capture_output=True, text=True)
    subprocess.run([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", "postgres",
                    "-q", "-c", "CREATE DATABASE fg_scale;"], capture_output=True, text=True)
    load = psql("-f", str(sql))
    errors = [l for l in (load.stderr or "").splitlines() if "ERROR" in l]
    print(f"generated schema: {FUNCS} functions, {TABLES} tables, {TRIGGERS} triggers, {ROLES} roles, "
          f"{len(errors)} load errors")

    out = tmp / "scale.json"
    t0 = time.time()
    r = subprocess.run([sys.executable, str(GRANTS), "--psql", a.psql, "--port", str(a.port),
                        "--user", a.user, "--db", "fg_scale", "--schema", "bank", "--table", "target",
                        "--out", str(out), "--target-lock", "scale@e-m34"],
                       capture_output=True, text=True)
    seconds = time.time() - t0
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 1
    doc = json.loads(out.read_text(encoding="utf-8"))
    paths = doc["paths"]
    kinds = {}
    for p in paths:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    distinct = len({p["entry"] for p in paths})

    print(f"runtime: {seconds:.1f}s, paths reported: {len(paths)}, distinct entries: {distinct}")
    print(f"kinds: {kinds}")
    summary = doc.get("summary") or {}
    print(f"summary present: {bool(summary)} -> {summary.get('reading_note')}")
    print(f"by kind: {summary.get('by_kind')}, by control-point status: {summary.get('by_control_point_status')}")

    under_time = seconds < 60
    # 80 of the planted functions deliberately do not write the table (PERFORM helper), so the
    # correct expectation is the number of writers, not the number of functions.
    non_writers = sum(1 for i in range(FUNCS) if SHAPES[i % len(SHAPES)] == "PERFORM bank.helper(1);")
    expected_writers = FUNCS - non_writers
    found_writers = len({p["entry"] for p in paths if p["entry"].startswith("function:bank.f")})
    found_all = found_writers >= expected_writers
    reviewable = len(paths) <= 120 or bool(summary)
    print(f"\nunder 60s: {under_time}   writers expected {expected_writers}, reported {found_writers}: "
          f"{found_all}   reviewable: {reviewable}")
    ok = under_time and found_all and reviewable
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
