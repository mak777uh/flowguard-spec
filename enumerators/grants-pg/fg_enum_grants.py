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

    source = {
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
        "completeness_claim": "exhaustive_within_covers",
    }
    Path(a.out).write_text(json.dumps(source, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"source: {len(paths)} paths, {len(control_points)} control point(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
