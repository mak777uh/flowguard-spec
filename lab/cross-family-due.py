#!/usr/bin/env python3
"""cross-family-due — should we spend tokens on an external-model attack this round?

Cross-family attacks cost real money per run, so they run on **change**, not on a schedule. This
tracks the digest of the files that decide verdicts; when they change, the next attack is due, and it
stays due until someone records a run.

    python lab/cross-family-due.py            # print state, exit 0 if due, 1 if not
    python lab/cross-family-due.py --record   # mark a run as done at the current digest
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "lab" / "state" / "cross-family.json"
WATCHED = [
    "tools/fg_verify.py",
    "tools/fg_coverage.py",
    "tools/fg_bundle.py",
    "schemas/claim-0.1.json",
    "schemas/inventory-0.1.json",
    "enumerators/grants-pg/enumerate.sql",
]


def digest() -> str:
    h = hashlib.sha256()
    for rel in WATCHED:
        p = ROOT / rel
        h.update(rel.encode())
        h.update(p.read_bytes() if p.exists() else b"-")
    return h.hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()

    now = digest()
    STATE.parent.mkdir(parents=True, exist_ok=True)
    try:
        prev = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        prev = {}

    last = prev.get("digest")
    runs = int(prev.get("runs", 0))
    due = last != now

    if a.record:
        STATE.write_text(json.dumps({"digest": now, "runs": runs + 1,
                                     "last_run_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                                     .strftime("%Y-%m-%dT%H:%M:%SZ")}, indent=1),
                         encoding="utf-8")
        print(f"recorded cross-family run #{runs + 1} at digest {now}")
        return 0

    print(f"gate digest now {now}, last attack at {last or 'never'} ({runs} run(s))")
    if due:
        print("cross-family attack is DUE: the files that decide verdicts changed")
        print("run it once, verify the findings, then: python lab/cross-family-due.py --record")
    else:
        print("cross-family attack is NOT due: nothing that decides verdicts has changed")
    print("RESULT:", "due" if due else "not-due")
    return 0 if due else 1


if __name__ == "__main__":
    sys.exit(main())
