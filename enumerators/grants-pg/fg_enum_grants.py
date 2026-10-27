#!/usr/bin/env python3
"""fg-enum-grants — enumerate the write paths to a Postgres table and emit a SourceRecord.

Read-only: every query goes through psql against the system catalogue. Nothing is written to the
target database. The output is a SourceRecord per ADR-0007, with mandatory declared blind spots.

    python fg_enum_grants.py --psql <path-to-psql> --host 127.0.0.1 --port 54329 \
        --user postgres --db fgfix --schema bank --table accounts --out source.json
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL = HERE / "enumerate.sql"

# Declared before any run. A source that cannot say what it is blind to is not admissible.
COVERS = [
    "table privileges granted to roles",
    "functions whose body mentions the table",
    "trigger state on the table (enabled / disabled)",
    "INSTEAD OF triggers on views that write the table",
    "triggers on other tables whose body mentions the table",
]
BLIND_SPOTS = [
    "dynamic SQL where the table name is assembled at runtime and never appears literally",
    "writes from other databases, foreign data wrappers, dblink, or a different service",
    "application-level checks that the database never sees",
    "privileges inherited through role membership chains and column-level grants",
    "writes performed by extensions or by superuser sessions outside these catalogues",
    "attribution of a write path to a declared control point - this needs a call graph, so coverage",
    "    computed from this source alone stays at 0 and the verdict stays capped",
]


def stable_id(kind: str, entry: str, control_point: str, detail: str = "") -> str:
    # detail is part of identity: an INSERT grant and an UPDATE grant are two different paths
    # to the same table, and collapsing them would silently drop one (found by E-M11 run 1).
    return "wp_" + sha256(f"{kind}|{entry}|{control_point}|{detail}".encode()).hexdigest()[:16]


def run_psql(a) -> list[list[str]]:
    cmd = [
        a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user, "-d", a.db,
        "-v", "ON_ERROR_STOP=1", "-v", f"schema={a.schema}", "-v", f"table={a.table}",
        "-tAF|", "-f", str(SQL),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(f"psql failed with {r.returncode}")
    rows = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) != 6:
            raise SystemExit(f"unexpected row shape ({len(parts)} cols): {line!r}")
        rows.append(parts)
    return rows


def count_functions(a) -> int:
    """Total functions in the schema: the denominator of db_logic_density."""
    cmd = [a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user, "-d", a.db, "-tAc",
           "select count(*) from pg_proc p join pg_namespace n on n.oid = p.pronamespace "
           f"where n.nspname = '{a.schema}'"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return int((r.stdout or "0").strip() or 0)
    except ValueError:
        return 0

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-lock", default="unset")
    ap.add_argument("--max-paths", type=int, default=0,
                    help="keep at most N paths, highest-value kinds first; a truncated source is "
                         "declared partial and cannot serve as a coverage denominator")
    a = ap.parse_args()

    rows = run_psql(a)
    paths, control_points = [], []
    for item_kind, kind, entry, control_point, detail, confidence in rows:
        record = {
            "path_id": stable_id(kind, entry, control_point, detail),
            "kind": kind,
            "entry": entry,
            "control_point": control_point,
            "detail": detail,
            "confidence": confidence,
        }
        (paths if item_kind == "path" else control_points).append(record)

    # How much of the write logic lives in the database at all. On GitLab's public schema only 36
    # of 558 functions contain a write statement: the report then covers a thin slice, and nothing
    # used to say so (E-M37, E-M40).
    funcs_total = count_functions(a) or 0
    funcs_writing = len({p["entry"] for p in paths if p["entry"].startswith("function:")})
    density = round(funcs_writing / funcs_total, 3) if funcs_total else None

    # A flat list is fine for a machine and useless for a reader: on a 400-function schema this
    # produced 480 paths (E-M34). The summary comes first so a human can triage, and the full list
    # stays for the machine.
    truncated = None

    if a.max_paths and len(paths) > a.max_paths:
        # Order matters: a truncated list must keep the paths a reader can act on first.
        priority = {"dynamic_sql": 0, "disabled_control": 1, "view_trigger": 2, "trigger_chain": 3,
                    "function": 4, "privilege": 5}
        ordered = sorted(paths, key=lambda q: (priority.get(q["kind"], 9), q["entry"]))
        kept = ordered[: a.max_paths]
        truncated = {"total": len(paths), "kept": len(kept), "omitted": len(paths) - len(kept)}
        paths = kept

    # Counters are computed on what is actually published: a summary that describes the list before
    # truncation would contradict the list beside it (found while verifying E-M35).
    by_kind = {}
    by_cp = {"inside": 0, "outside": 0}
    for p_ in paths:
        by_kind[p_["kind"]] = by_kind.get(p_["kind"], 0) + 1
        by_cp["inside" if p_.get("control_point") else "outside"] += 1

    source = {
        "summary": {
            "db_logic_density": density,
            "functions_total": funcs_total,
            "functions_writing": funcs_writing,
            "paths_total": len(paths),
            "distinct_entries": len({p_["entry"] for p_ in paths}),
            "by_kind": by_kind,
            "by_control_point_status": by_cp,
            "reading_note": ("more than 120 paths: read the summary first"
                             if len(paths) > 120 else "short enough to read in full"),
        },
        "source_id": "grants-pg-v0.1",
        "kind": "grants",
        "tool": {
            "name": "fg-enum-grants",
            "version": "0.1.0",
            "digest": "sha256:" + sha256(SQL.read_bytes()).hexdigest(),
        },
        "run": {
            "target_lock": a.target_lock,
            "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "environment": f"postgres via psql {a.host}:{a.port}/{a.db}",
            "scope": f"{a.schema}.{a.table}",
        },
        "covers": COVERS,
        "blind_spots": BLIND_SPOTS,
        "paths": paths,
        "control_points": control_points,
        "completeness_claim": "partial" if truncated else "exhaustive_within_covers",
        "truncated": truncated,
    }
    Path(a.out).write_text(json.dumps(source, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"source: {len(paths)} paths, {len(control_points)} control point(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
