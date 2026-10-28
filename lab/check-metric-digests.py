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
    rows, unresolved = 0, []
    for lineno, line in enumerate(METRICS.read_text(encoding="utf-8").splitlines(), 1):
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        rows += 1
        for digest in DIGEST.findall(line):
            if digest not in known:
                cell = [c.strip() for c in line.strip().strip("|").split("|")]
                unresolved.append((lineno, cell[0], digest[:12]))

    card_bad = []
    if a.cards:
        for card in sorted((ROOT / "lab" / "experiments").glob("*.md")):
            text = card.read_text(encoding="utf-8", errors="ignore")
            for dig in DIGEST.findall(text):
                if dig not in known:
                    card_bad.append((card.name.split("-")[0], dig[:12]))
        unresolved.extend((0, f"card {cid}", pref) for cid, pref in card_bad)

    print(f"metric rows: {rows}, log files: {len(known)}, unresolved digests: {len(unresolved)}")
    for lineno, num, prefix in unresolved:
        where = f" (line {lineno})" if lineno else ""
        print(f"  {num}{where}: {prefix}… matches no file in lab/logs/")
    if unresolved and a.fix_hint:
        print("\nfix: re-run the row's command into lab/logs/<id>-<date>.log and put the new sha256 in the cell,")
        print("     or replace the cell with `-` and say in the row that the run was not captured.")
    print("RESULT:", "ok" if not unresolved else "fail")
    return 0 if not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
