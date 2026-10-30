#!/usr/bin/env python3
"""queue — a claimable work queue for campaigns over many targets.

Taken from the PutnamBench harness (`harness/pb.py`, "work queue" section), where 672 problems were solved by a
fleet of agents on one host. The four ideas worth copying, and this file is all four:

1. **One human-readable TSV**, one row per target, mutated only under an exclusive lock on a sidecar file, written
   atomically (temp + replace), so readers never see a partial table and any number of workers can claim safely.
2. **A claim records the owning PID.** Liveness is decided by that PID, never by elapsed time: a long analysis is
   expected to take hours, and reaping it on age would hand the same target to a second worker.
3. **`reap`** returns abandoned rows to `todo` when the owner is gone - the failure mode that actually happens.
4. **Retry is explicit.** `claim` only takes `todo` rows, so a target that failed is never retried automatically;
   `requeue` is what turns a pass@1 sweep into pass@2.

Differences from theirs, on purpose: no `variant` column (our campaigns vary in kind, not in two fixed variants),
and a `kind` column for what sort of work the row is (a repo audit, a schema enumeration, a model attack).

    python lab/queue.py init --file lab/state/audit-queue.tsv --rows repos.txt
    python lab/queue.py claim --owner lead
    python lab/queue.py release <target> --status done --note "audit written"
    python lab/queue.py reap
    python lab/queue.py status
"""
import argparse
import datetime
import os
import pathlib
import sys

try:                                    # POSIX
    import fcntl
except ImportError:                     # Windows: no flock, so the lock is a create-exclusive file
    fcntl = None

COLUMNS = ["target", "kind", "status", "owner", "pid", "claimed_at", "finished_at", "note"]
STATUSES = {"todo", "running", "done", "failed", "skipped"}
DEFAULT = pathlib.Path(__file__).resolve().parent / "state" / "queue.tsv"


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


class Lock:
    """Exclusive lock on a sidecar file; a spin file where flock does not exist."""

    def __init__(self, path: pathlib.Path, shared: bool = False):
        self.path = path
        self.shared = shared
        self.fh = None
        self.spin = path.with_suffix(path.suffix + ".spin")

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if fcntl:
            self.fh = open(self.path.with_suffix(self.path.suffix + ".lock"), "a+")
            fcntl.flock(self.fh, fcntl.LOCK_SH if self.shared else fcntl.LOCK_EX)
            return self
        import time
        for _ in range(600):            # 60 s
            try:
                self.spin.touch(exist_ok=False)
                return self
            except FileExistsError:
                time.sleep(0.1)
        raise SystemExit(f"could not acquire {self.spin}")

    def __exit__(self, *exc):
        if fcntl and self.fh:
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()
        elif self.spin.exists():
            self.spin.unlink()
        return False


def read_rows(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        parts = line.split("\t")
        if i == 0 and parts[0] == "target":
            continue
        parts += [""] * (len(COLUMNS) - len(parts))
        rows.append(dict(zip(COLUMNS, parts[:len(COLUMNS)])))
    return rows


def write_rows(path: pathlib.Path, rows: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    body = ["\t".join(COLUMNS)]
    for r in rows:
        body.append("\t".join((r.get(c) or "").replace("\t", " ").replace("\n", " ")
                              for c in COLUMNS))
    tmp.write_text("\n".join(body) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def pid_alive(pid: str) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (ValueError, ProcessLookupError):
        return False
    except PermissionError:
        return True


def reap(rows: list[dict]) -> int:
    """Return `running` rows whose owner is gone. Age is never the criterion."""
    n = 0
    for r in rows:
        if r["status"] != "running":
            continue
        if r["pid"] and pid_alive(r["pid"]):
            continue
        r.update(status="todo", owner="", pid="", claimed_at="",
                 note="reaped (owner gone)")
        n += 1
    return n


def cmd_init(a) -> int:
    path = pathlib.Path(a.file)
    with Lock(path):
        rows = read_rows(path)
        existing = {r["target"] for r in rows}
        added = 0
        for line in pathlib.Path(a.rows).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            target, _, kind = line.partition("\t")
            if target in existing:
                continue
            rows.append({"target": target, "kind": kind or "audit", "status": "todo",
                         "owner": "", "pid": "", "claimed_at": "", "finished_at": "", "note": ""})
            added += 1
        rows.sort(key=lambda r: r["target"])
        write_rows(path, rows)
    print(f"{path}: {len(rows)} rows ({added} new)")
    return 0


def cmd_claim(a) -> int:
    path = pathlib.Path(a.file)
    with Lock(path):
        rows = read_rows(path)
        if not rows:
            print("queue is empty - run init first", file=sys.stderr)
            return 2
        reap(rows)
        pick = next((r for r in rows if r["status"] == "todo"
                     and (not a.kind or r["kind"] == a.kind)), None)
        if pick is None:
            write_rows(path, rows)
            print("nothing to claim", file=sys.stderr)
            return 1
        pick.update(status="running", owner=a.owner, pid=str(a.pid or os.getpid()),
                    claimed_at=now(), finished_at="", note="")
        write_rows(path, rows)
    print(f"{pick['target']}\t{pick['kind']}")
    return 0


def cmd_release(a) -> int:
    if a.status not in STATUSES:
        print(f"bad status; one of {sorted(STATUSES)}", file=sys.stderr)
        return 2
    path = pathlib.Path(a.file)
    with Lock(path):
        rows = read_rows(path)
        for r in rows:
            if r["target"] == a.target:
                r.update(status=a.status, finished_at=now(), pid="", note=a.note or "")
                break
        else:
            print(f"{a.target} not in the queue", file=sys.stderr)
            return 1
        write_rows(path, rows)
    print(f"{a.target} -> {a.status}")
    return 0


def cmd_reap(a) -> int:
    path = pathlib.Path(a.file)
    with Lock(path):
        rows = read_rows(path)
        n = reap(rows)
        write_rows(path, rows)
    print(f"reaped {n}")
    return 0


def cmd_requeue(a) -> int:
    path = pathlib.Path(a.file)
    with Lock(path):
        rows = read_rows(path)
        n = 0
        for r in rows:
            if r["status"] in a.status and r["status"] != "done" or (a.force and r["status"] in a.status):
                r.update(status="todo", owner="", pid="", claimed_at="", finished_at="",
                         note=f"requeued from {r['status']}")
                n += 1
        write_rows(path, rows)
    print(f"requeued {n}")
    return 0


def cmd_status(a) -> int:
    path = pathlib.Path(a.file)
    with Lock(path, shared=True):
        rows = read_rows(path)
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(f"{path}  {len(rows)} rows")
    for s in ("done", "running", "todo", "failed", "skipped"):
        if by.get(s):
            print(f"  {s:8} {by[s]:4}")
    if a.verbose:
        for r in rows:
            if a.status and r["status"] != a.status:
                continue
            print(f"  {r['target'][:40]:42} {r['kind']:8} {r['status']:8} {r['owner'][:12]:12} {r['note'][:30]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(DEFAULT))
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init"); i.add_argument("--rows", required=True); i.set_defaults(fn=cmd_init)
    c = sub.add_parser("claim"); c.add_argument("--owner", required=True)
    c.add_argument("--pid", type=int); c.add_argument("--kind"); c.set_defaults(fn=cmd_claim)
    r = sub.add_parser("release"); r.add_argument("target")
    r.add_argument("--status", required=True); r.add_argument("--note"); r.set_defaults(fn=cmd_release)
    sub.add_parser("reap").set_defaults(fn=cmd_reap)
    q = sub.add_parser("requeue"); q.add_argument("--status", nargs="+", default=["failed"])
    q.add_argument("--force", action="store_true"); q.set_defaults(fn=cmd_requeue)
    s = sub.add_parser("status"); s.add_argument("-v", "--verbose", action="store_true")
    s.add_argument("--status"); s.set_defaults(fn=cmd_status)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
