#!/usr/bin/env python3
"""fg-enum-pgcalls — attribute PL/pgSQL functions to a declared control point.

Contributes `attributions`, not `paths` (ADR-0007 as amended by ADR-0009). The distinction matters:
the grants enumerator says *what can write*; this one says *whether that writer goes through the
declared control point*. Merging the two turns a list of doors into a covered set.

    python fg_enum_pgcalls.py --psql <path> --host 127.0.0.1 --port 5432 --user postgres \
        --db mydb --schema bank --control transfer --out attributions.json
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL = HERE / "attribution.sql"

COVERS = [
    "functions whose body calls the control point by name",
    "transitive reachability through the call graph, up to depth 8",
]
BLIND_SPOTS = [
    "dynamic SQL: EXECUTE with a function name built at runtime",
    "calls through variables, records or string concatenation",
    "C-language functions and extension code",
    "calls made from outside the database (application code, scheduled jobs)",
    "depth beyond 8 in a deep call chain",
    "overloads: resolution is by name, not by signature",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-lock", default="")
    a = ap.parse_args()

    cmd = [a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user, "-d", a.db,
           "-v", "ON_ERROR_STOP=1", "-v", f"schema={a.schema}", "-v", f"control={a.control}",
           "-tAF|", "-f", str(SQL)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(f"psql failed: {r.returncode}")

    attributions = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) != 4:
            raise SystemExit(f"unexpected row: {line!r}")
        entry, to, method, confidence = parts
        attributions.append({
            "entry": entry, "attributed_to": to, "method": method, "confidence": confidence,
        })

    source = {
        "source_id": "pgcalls-v0.1",
        "enumerates": "calls",
        "kind": "static",
        "tool": {"name": "fg-enum-pgcalls", "version": "0.1.0",
                 "digest": "sha256:" + sha256(SQL.read_bytes()).hexdigest()},
        "run": {"target_lock": a.target_lock,
                "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "environment": f"postgres via psql {a.host}:{a.port}/{a.db}",
                "scope": f"{a.schema}.{a.control}"},
        "covers": COVERS,
        "blind_spots": BLIND_SPOTS,
        "paths": [],
        "control_points": [],
        "attributions": attributions,
        "completeness_claim": "exhaustive_within_covers",
    }
    Path(a.out).write_text(json.dumps(source, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"attributions: {len(attributions)} function(s) reach {a.schema}.{a.control} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
