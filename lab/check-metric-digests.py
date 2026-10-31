#!/usr/bin/env python3
"""check-metric-digests — every digest in docs/METRICS.md must name a file that exists.

A metric row carries the sha256 of the log it was extracted from. Four rows carried digests that
matched no file at all: the numbers reproduced, the digests had never been computed from a captured
run. That is worse than no digest, because it *looks* like a trail (hostile review, E-M43).

    python lab/check-metric-digests.py           # exit 1 on a digest that resolves to nothing
    python lab/check-metric-digests.py --fix-hint
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "docs" / "METRICS.md"
LOGS = ROOT / "lab" / "logs"
DIGEST = re.compile(r"`([0-9a-f]{64})`")


def log_digests():
    out = {}
    for p in LOGS.glob("*"):
        if p.is_file():
            out[hashlib.sha256(p.read_bytes()).hexdigest()] = p.name
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-hint", action="store_true")
    ap.add_argument("--cards", action="store_true",
                    help="also check the sha256 a trailing Log section on each experiment card")
    a = ap.parse_args()

    known = log_digests()
    rows, unresolved, no_log = 0, [], 0
    by_digest: dict[str, set[str]] = {}
    for lineno, line in enumerate(METRICS.read_text(encoding="utf-8").splitlines(), 1):
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        rows += 1
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        experiment = (re.match(r"(E-M\d+)", cells[1]) or [None, "?"])
        experiment = experiment.group(1) if hasattr(experiment, "group") else "?"
        found = DIGEST.findall(line)
        if "`no-log`" in line:
            no_log += 1
        for digest in found:
            by_digest.setdefault(digest, set()).add(experiment)
            if digest not in known:
                unresolved.append((lineno, cells[0], digest[:12]))

    # One sha256 is one log. The same digest under two different experiments means a cell was copied;
    # 49 rows carried a single digest until 2026-10-31, which is how the placeholder was visible at all.
    shared = sorted((d, sorted(ids)) for d, ids in by_digest.items() if len(ids) > 1)
    for digest, ids in shared:
        print(f"  digest {digest[:12]}… is claimed by {len(ids)} experiments: {', '.join(ids)} — one log, one row")
    unresolved.extend((0, "shared", d[:12]) for d, _ in shared)

    card_bad = []
    if a.cards:
        for card in sorted((ROOT / "lab" / "experiments").glob("*.md")):
            # INDEX.md is generated and carries the word "digest" in prose; it is not a card (E-M79)
            if card.name in ("INDEX.md", "README.md"):
                continue
            text = card.read_text(encoding="utf-8", errors="ignore")
            for dig in DIGEST.findall(text):
                if dig not in known:
                    card_bad.append((card.name.split("-")[0], dig[:12]))
        unresolved.extend((0, f"card {cid}", pref) for cid, pref in card_bad)

    print(f"metric rows: {rows}, rows with a captured log: {rows - no_log}, rows marked no-log: {no_log}, "
          f"log files: {len(known)}, unresolved digests: {len(unresolved)}")
    for lineno, num, prefix in unresolved:
        where = f" (line {lineno})" if lineno else ""
        print(f"  {num}{where}: {prefix}… matches no file in lab/logs/")
    if unresolved and a.fix_hint:
        print("\nfix: re-run the row's command into lab/logs/<id>-<date>.log and put the new sha256 in the cell,")
        print("     or mark the row `no-log` and let the count of uncaptured runs stand in the open.")
    print("RESULT:", "ok" if not unresolved else "fail")
    return 0 if not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
