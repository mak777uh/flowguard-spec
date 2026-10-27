#!/usr/bin/env python3
"""fg-enum-runtime — which writes to a table actually happened, according to the server log.

A different mechanism from the catalogue enumerators: it does not read what is declared, it reads
what executed. That is the point — two sources that both read the catalogue can share a blind spot;
a source that reads the log cannot share the *catalogue's* blind spot, and brings its own instead.

    python fg_enum_runtime.py --psql <path> --host 127.0.0.1 --port 5432 --user postgres \
        --db mydb --schema bank --table accounts --log <server.log> --workload <script.sql> \
        --out runtime.json

The workload is executed with `log_statement = all` for that session; the statements are then read
back out of the server log. Nothing is written to the target database beyond what the workload does.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

COVERS = [
    "writes to the table that were actually executed in the observed window",
    "the statement text of each write, including the caller that reached it",
]
BLIND_SPOTS = [
    "paths not exercised during the window - absence of evidence, not evidence of absence",
    "writes from other sessions, other databases or other services, unless they share this log",
    "parameterised statements whose table name is bound at execution and not logged literally",
    "COPY, and statements truncated or rotated out of the log",
    "attribution: the log shows the statement, not which control point the caller went through",
    "writes performed INSIDE a function reached by SELECT: only the outer SELECT is logged, so a",
    "    legitimate write through a control point is invisible - this source UNDER-counts",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--log", required=True, help="server log file written by the running instance")
    ap.add_argument("--workload", required=True, help="SQL script to execute and observe")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-lock", default="")
    a = ap.parse_args()

    log_path = Path(a.log)
    before = log_path.stat().st_size if log_path.exists() else 0

    # log_statement=all for this session, then run the workload
    sql = f"SET log_statement = 'all';\n\\i {a.workload}\n"
    tmp = Path(a.out).with_suffix(".workload.sql")
    tmp.write_text(sql, encoding="utf-8")
    r = subprocess.run([a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user, "-d", a.db,
                        "-v", "ON_ERROR_STOP=1", "-q", "-f", str(tmp)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"workload failed: {r.returncode}")
    tmp.unlink(missing_ok=True)

    # read only what was appended during the run
    with log_path.open("rb") as f:
        f.seek(before)
        chunk = f.read().decode("utf-8", errors="replace")

    write_re = re.compile(
        rf"\b(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(?:\w+\.)?(?P<tbl>\w+)", re.I)
    target = a.table
    counts, stmts = {}, []
    for line in chunk.splitlines():
        if "statement:" not in line:
            continue
        stmt = line.split("statement:", 1)[1].strip()
        m = write_re.search(stmt)
        if not m or m.group("tbl").lower() != target.lower():
            continue
        verb = re.sub(r"\s+", " ", m.group(1).upper())
        counts[verb] = counts.get(verb, 0) + 1
        stmts.append({"verb": verb, "statement": stmt[:200]})

    paths = []
    for verb, n in sorted(counts.items()):
        paths.append({
            "path_id": "wp_" + sha256(f"runtime|{verb}|{a.schema}.{target}".encode()).hexdigest()[:16],
            "kind": "observed_write",
            "entry": f"stmt:{verb} {a.schema}.{target}",
            "control_point": "",
            "detail": f"{n} occurrence(s) in the observed window",
            "confidence": "runtime",
        })

    source = {
        "source_id": "runtime-pg-v0.1",
        "kind": "runtime",
        "tool": {"name": "fg-enum-runtime", "version": "0.1.0",
                 "digest": "sha256:" + sha256(Path(__file__).read_bytes()).hexdigest()},
        "run": {"target_lock": a.target_lock,
                "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "environment": f"postgres log {log_path.name} via psql {a.host}:{a.port}/{a.db}",
                "scope": f"{a.schema}.{a.table}"},
        "covers": COVERS,
        "blind_spots": BLIND_SPOTS,
        "paths": paths,
        "control_points": [],
        "attributions": [],
        "observed_statements": stmts,
        "completeness_claim": "exhaustive_within_covers",
    }
    Path(a.out).write_text(json.dumps(source, indent=1, ensure_ascii=False), encoding="utf-8")
    total = sum(counts.values())
    print(f"runtime: {total} write statement(s) to {a.schema}.{a.table}, "
          f"{len(paths)} distinct verb(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
