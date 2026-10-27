#!/usr/bin/env python3
"""E-M41: an independent oracle for the same question, compared against the enumerator.

Reviewer В6: "to test false negatives, you need a ground-truth list built independently". On a real
schema nobody will produce one, so the next best thing is a SECOND implementation that answers the
same question by a different route and disagrees loudly.

The enumerator asks: which database objects can write this table?
  - functions whose body matches a write verb within 200 characters of the table name;
  - triggers, rules, policies, privileges.

This oracle asks with different logic, deliberately allowing itself to be looser:
  - any function whose body mentions the table at all, plus the object identity of every trigger;
  - every trigger whose function writes the table, regardless of how the trigger is attached;
  - foreign keys with a cascade that can delete or null rows in the target.

Disagreement is the output. Oracle-only objects are candidate false negatives; enumerator-only
objects are candidate false positives.

    python lab/e-m41-run.py --psql <psql> --port 54329 --db fg_gitlab --schema public --table projects
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRANTS = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"

ORACLE_SQL = """
with fns as (
  select p.oid, p.proname, p.prosrc
  from pg_proc p join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = :'schema'
),
writers as (
  select oid, proname from fns
  where prosrc ~* ('(update|insert[[:space:]]+into|delete[[:space:]]+from)[\\s\\S]*' || :'table')
),
trig as (
  select c.relname as on_table, t.tgname, p.proname as fn,
         (p.oid in (select oid from writers)) as fn_writes
  from pg_trigger t
  join pg_class c on c.oid = t.tgrelid
  join pg_namespace n on n.oid = c.relnamespace
  join pg_proc p on p.oid = t.tgfoid
  where n.nspname = :'schema' and not t.tgisinternal
),
fk as (
  select con.conname, cl.relname as child, confrel.relname as parent,
         con.confdeltype, con.confupdtype
  from pg_constraint con
  join pg_class cl on cl.oid = con.conrelid
  join pg_class confrel on confrel.oid = con.confrelid
  join pg_namespace n on n.oid = cl.relnamespace
  where con.contype = 'f' and n.nspname = :'schema'
    and (cl.relname = :'table' or confrel.relname = :'table')
)
select 'writer', proname, '' from writers
union all
select 'trigger', on_table || ' -> ' || tgname, fn from trig where fn_writes
union all
select 'fk', child || ' -> ' || parent, conname || ' del=' || confdeltype::text
  from fk where confdeltype in ('c', 'n', 'd') or confupdtype in ('c', 'n', 'd')
order by 1, 2;
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--port", type=int, default=54329)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", default="fg_gitlab")
    ap.add_argument("--schema", default="public")
    ap.add_argument("--table", default="projects")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    out = tmp / "enum.json"
    r = subprocess.run([sys.executable, str(GRANTS), "--psql", a.psql, "--port", str(a.port),
                        "--user", a.user, "--db", a.db, "--schema", a.schema, "--table", a.table,
                        "--out", str(out), "--target-lock", f"{a.db}@e-m41"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return 1
    enum = json.loads(out.read_text(encoding="utf-8"))

    sql = tmp / "oracle.sql"
    sql.write_text(ORACLE_SQL, encoding="utf-8")
    o = subprocess.run([a.psql, "-h", "127.0.0.1", "-p", str(a.port), "-U", a.user, "-d", a.db,
                        "-v", "ON_ERROR_STOP=1", "-v", f"schema={a.schema}", "-v", f"table={a.table}",
                        "-t", "-A", "-F", "|", "-f", str(sql)], capture_output=True, text=True)
    if o.returncode != 0:
        sys.stderr.write(o.stderr)
        return 1
    oracle = []
    for line in o.stdout.splitlines():
        parts = line.split("|")
        if len(parts) == 3:
            oracle.append(tuple(parts))

    enum_fns = {p["entry"].split(".")[-1] for p in enum["paths"] if p["kind"] == "function"}
    enum_trig = {p["entry"] for p in enum["paths"] if p["kind"] == "trigger_chain"}
    oracle_fns = {name for kind, name, _ in oracle if kind == "writer"}
    oracle_trig_fns = {fn for kind, _, fn in oracle if kind == "trigger"}
    oracle_trig_all = {(name.split(" -> ")[0], name.split(" -> ")[1]) for kind, name, _ in oracle
                       if kind == "trigger"}
    oracle_fk = [(name, extra) for kind, name, extra in oracle if kind == "fk"]

    print(f"enumerator: {len(enum['paths'])} paths "
          f"({len(enum_fns)} functions, {len(enum_trig)} trigger chains)")
    print(f"oracle:     {len(oracle_fns)} writer functions, {len(oracle_trig_fns)} trigger functions, "
          f"{len(oracle_fk)} cascading keys")

    # The declared control point is reported as a control_point, not as a path: it is the door
    # everything is supposed to pass through, and counting it as a missed writer would be wrong.
    cp_names = {c["entry"].split(".")[-1] for c in enum.get("control_points", [])}
    oracle_fns = oracle_fns - cp_names
    only_oracle_fns = sorted(oracle_fns - enum_fns)
    only_enum_fns = sorted(enum_fns - oracle_fns)
    enum_trig_fns = {e.split("trigger:")[1].split(" ")[0] for e in enum_trig if "trigger:" in e}

    print(f"\nfunctions found only by the oracle (candidate false negatives): {only_oracle_fns or 'none'}")
    print(f"functions found only by the enumerator (candidate false positives): {only_enum_fns or 'none'}")
    # A trigger function that writes the table is already reported as a plain writer; only count it
    # as missed when the enumerator does not mention it at all.
    missed_triggers = sorted(oracle_trig_fns - enum_trig_fns - enum_fns)
    print(f"trigger functions the enumerator missed entirely: {missed_triggers or 'none'}")
    # Only keys where the target is the CHILD are writes into it; the rest cascade out of it.
    oracle_fk_in = [x for x in oracle_fk if x[0].split(" -> ")[0] == a.table]
    # Normalise direction: the enumerator writes `parent -> child`, the oracle `child -> parent`.
    enum_fk = set()
    for p_ in enum["paths"]:
        if p_["kind"] == "fk_cascade":
            parts = p_["entry"].replace("fk:", "").split(" -> ")
            if len(parts) == 2:
                enum_fk.add(parts[0] + "|" + parts[1])
    oracle_fk_keyed = {x[0].split(" -> ")[1] + "|" + x[0].split(" -> ")[0]: x[0]
                       for x in oracle_fk_in}
    missing_fk = [name for key, name in oracle_fk_keyed.items() if key not in enum_fk]
    print(f"cascading keys INTO the target: oracle {len(oracle_fk_in)}, enumerator {len(enum_fk)}")
    print(f"  missed by the enumerator: {missing_fk or 'none'}")
    print(f"cascading keys OUT of the target (not writers of it): {len(oracle_fk) - len(oracle_fk_in)}")

    fn_gap = len(only_oracle_fns)
    trig_gap = len(missed_triggers)
    fk_gap = len(missing_fk)
    ok = fn_gap == 0 and trig_gap == 0 and fk_gap == 0
    print(f"\nRESULT: {'PASS' if ok else 'FAIL — disagreement found'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
