#!/usr/bin/env python3
"""fg_enum_migrations — the paths a migration file creates, without a database.

Why this enumerator exists: the grants and pgcalls enumerators read a **live** database. A repository's
migration directory says what a database will become, and most of an application's write logic is defined there:
`CREATE FUNCTION` with a body that inserts, `CREATE TRIGGER` that fires on update, backfills that touch every row.
Nothing in the previous two enumerators looks at a file.

    python enumerators/migrations/fg_enum_migrations.py --dir migrations --schema public \\
        --control function:public.audit_write --out migrations.json --target-lock t@1

What it reports, and what it refuses to report:

- **functions**: name, whether the body writes (INSERT/UPDATE/DELETE/TRUNCATE/COPY), whether it uses dynamic SQL
  (`EXECUTE` with a non-literal), and which tables it names. Verbs are taken from the body's statements.
- **triggers**: the function they call and the table they fire on, as a `trigger_chain` path: a write to the table
  can reach the trigger body without passing the declared control point.
- **grants**: `GRANT ... ON <table>` gives a role a write path with no function in between.
- **backfills**: `INSERT INTO`/`UPDATE` runs inside the migration itself. Reported as `observed_write` with
  `completeness_claim: partial`, because a migration is a one-off script, not a path that exists afterwards.

It does not claim to be complete: a body built by string concatenation is reported with
`completeness_claim: partial` and a reason, never silently dropped.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

WRITE_VERBS = ("INSERT", "UPDATE", "DELETE", "TRUNCATE", "COPY", "MERGE")
FUNC_HEAD_RE = re.compile(r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([\w.\"]+)", re.I)
DOLLAR_RE = re.compile(r"AS\s+\$(\w*)\$", re.I)
TRIGGER_RE = re.compile(
    r"CREATE\s+(?:CONSTRAINT\s+)?TRIGGER\s+([\w\"]+)\s+.*?ON\s+([\w.\"]+).*?EXECUTE\s+(?:PROCEDURE|FUNCTION)\s+([\w.\"]+)",
    re.I | re.S)
GRANT_RE = re.compile(r"GRANT\s+(.*?)\s+ON\s+(?:TABLE\s+)?([\w.\"]+)\s+TO\s+([\w\"]+)", re.I | re.S)
TABLE_RE = re.compile(r"\b(?:FROM|INTO|UPDATE|JOIN|TABLE)\s+([\w.\"]+)", re.I)


def strip_ident(name: str) -> str:
    return name.replace('"', "").strip()


def verbs_in(body: str) -> list[str]:
    found = []
    for verb in WRITE_VERBS:
        if re.search(rf"\b{verb}\b", body, re.I):
            found.append(verb)
    if re.search(r"\bEXECUTE\b\s+[^'\"]", body, re.I):
        found.append("CALL:dynamic")
    if re.search(r"\bFOR\s+\w+\s+IN\s+EXECUTE\b", body, re.I):
        found.append("CALL:cursor")
    return sorted(set(found))


def tables_in(text: str) -> list[str]:
    out = []
    for m in TABLE_RE.finditer(text):
        name = strip_ident(m.group(1))
        if not name or not (name[0].isalpha() or name[0] == "_"):
            # "UPDATE new.updated_at = 1" and friends: not a table
            continue
        if name.split(".")[0].lower() in {"new", "old", "excluded"}:
            continue
        if name.upper() in {"SELECT", "SET", "VALUES", "WHERE", "ON", "OF", "FOR", "TABLE",
                            "NEW", "OLD", "EXCLUDED", "CURRENT_DATE", "NOW"}:
            continue
        if "." not in name:
            name = f"public.{name}"
        out.append(name)
    return sorted(set(out))


def paths_from_file(path: Path, schema: str, control: str, lock: str) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    paths: list[dict] = []
    stems = path.name.split("__", 1)
    migration = stems[1].replace(".sql", "") if len(stems) == 2 else path.stem

    for m in FUNC_HEAD_RE.finditer(text):
        fname = strip_ident(m.group(1))
        if "." not in fname:
            fname = f"{schema}.{fname}"
        # parameters may contain brackets and commas, so the body starts at the dollar quote that
        # follows the head, not at the first closing bracket (which found 1 of 4 functions)
        head = text[m.end():m.end() + 2000]
        dollar = DOLLAR_RE.search(head)
        if not dollar:
            continue
        body = head[dollar.end():]
        vs = verbs_in(body)
        writes = [v for v in vs if v in WRITE_VERBS]
        if not writes:
            continue
        pid = "wp_mig_" + hashlib.sha256(f"{path.name}|{fname}".encode()).hexdigest()[:12]
        paths.append({
            "path_id": pid,
            "entry": f"function:{fname}",
            "target": tables_in(body)[0] if tables_in(body) else f"table:{schema}.*",
            "kind": "function",
            "how": f"defined in migration {migration}; body uses " + ", ".join(writes),
            "verbs": [f"stmt:{v}" for v in writes] + [f"stmt:{v}" for v in vs if v == "CALL"],
            "dynamic_sql": "EXECUTE" in body,
            "completeness_claim": "exhaustive_within_covers" if "EXECUTE" not in body
                                  else "partial",
            "not_covered_reason": None if "EXECUTE" not in body
                                  else "dynamic SQL: the body cannot be read as text",
            "attribution": {
                "to": control if control and control.split(":")[-1] == fname else "none",
                "method": "migration_text",
                "sources": ["migrations"],
            },
            "vanished": False,
        })

    for m in TRIGGER_RE.finditer(text):
        tname, table = strip_ident(m.group(1)), strip_ident(m.group(2))
        fn = strip_ident(m.group(3))
        if "." not in table:
            table = f"{schema}.{table}"
        if "." not in fn:
            fn = f"{schema}.{fn}"
        pid = "wp_mig_" + hashlib.sha256(f"{path.name}|trigger|{tname}".encode()).hexdigest()[:12]
        paths.append({
            "path_id": pid,
            "entry": f"trigger:{tname}",
            "target": f"table:{table}",
            "kind": "trigger_chain",
            "how": f"trigger on {table} executes {fn}; a write to the table reaches the body "
                   f"without passing the declared control point",
            "verbs": ["stmt:UPDATE", "stmt:INSERT"],
            "completeness_claim": "exhaustive_within_covers",
            "not_covered_reason": None,
            "attribution": {"to": "none", "method": "migration_text", "sources": ["migrations"]},
            "vanished": False,
        })

    for m in GRANT_RE.finditer(text):
        privs, table, role = m.group(1).upper(), strip_ident(m.group(2)), strip_ident(m.group(3))
        if not any(p in privs for p in ("INSERT", "UPDATE", "DELETE", "ALL")):
            continue
        if "." not in table:
            table = f"{schema}.{table}"
        pid = "wp_mig_" + hashlib.sha256(f"{path.name}|grant|{role}|{table}".encode()).hexdigest()[:12]
        paths.append({
            "path_id": pid,
            "entry": f"role:{role}",
            "target": f"table:{table}",
            "kind": "privilege",
            "how": f"GRANT {privs} ON {table} TO {role} in migration {migration}",
            "verbs": [f"stmt:{p.strip()}" for p in privs.split(",") if p.strip()],
            "completeness_claim": "exhaustive_within_covers",
            "not_covered_reason": None,
            "attribution": {"to": "none", "method": "migration_text", "sources": ["migrations"]},
            "vanished": False,
        })

    # writes performed by the migration itself
    for verb, pattern in (("INSERT", r"INSERT\s+INTO\s+([\w.\"]+)"),
                          ("UPDATE", r"\bUPDATE\s+([\w.\"]+)\s+SET\b")):
        for m in re.finditer(pattern, text, re.I):
            table = strip_ident(m.group(1))
            if "." not in table:
                table = f"{schema}.{table}"
            pid = "wp_mig_" + hashlib.sha256(f"{path.name}|script|{verb}|{table}".encode()).hexdigest()[:12]
            paths.append({
                "path_id": pid,
                # the page requires an observed_write entry to be a statement, not a script name
                "entry": f"stmt:{verb} {table}",
                "target": f"table:{table}",
                "kind": "observed_write",
                "how": f"the migration script itself runs {verb} on {table}",
                "verbs": [f"stmt:{verb}"],
                "completeness_claim": "partial",
                "not_covered_reason": "a migration runs once; it is not a path that exists afterwards",
                "attribution": {"to": "none", "method": "migration_text", "sources": ["migrations"]},
                "vanished": False,
            })
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--schema", default="public")
    ap.add_argument("--control", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-lock", required=True)
    a = ap.parse_args()

    root = Path(a.dir)
    files = sorted(root.glob("*.sql"))
    if not files:
        print(f"no .sql files under {root}")
        return 1

    paths: list[dict] = []
    for f in files:
        paths.extend(paths_from_file(f, a.schema, a.control, a.target_lock))

    # one path per path_id: the same function redefined in a later migration is one function
    seen: dict[str, dict] = {}
    for p in paths:
        seen.setdefault(p["path_id"], p)
    paths = list(seen.values())

    writes = sum(1 for p in paths if any(v.startswith("stmt:") for v in p["verbs"]))
    doc = {
        "manifest_version": "inventory/0.1",
        "target_lock": a.target_lock,
        "independent_of_agent": False,
        "sources": [{
            "source_id": "migrations",
            "kind": "static",
            "what": f"{len(files)} migration files read as text",
            "completeness_claim": "partial" if any(
                p["completeness_claim"] == "partial" for p in paths) else "exhaustive_within_covers",
            "notes": "a migration directory is not a database: what a later ALTER drops is still here",
        }],
        "paths": paths,
    }
    Path(a.out).write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"files: {len(files)}, paths: {len(paths)} ({writes} with write verbs) -> {a.out}")
    for kind in ("function", "trigger_chain", "privilege", "observed_write"):
        n = sum(1 for p in paths if p["kind"] == kind)
        if n:
            print(f"  {kind:16} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
