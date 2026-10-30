#!/usr/bin/env python3
"""check-doc-numbers — two documents must not share a number.

Eight collisions were created in one session: each new study took the next free-looking number in `docs/` without
checking, and `docs/30` through `docs/37` already belonged to round syntheses, the spec audit, the refusal codes and
the inventory design. A reader who cites "docs/34" then has two candidates, and the repository has no way to say
which one was meant.

    python lab/check-doc-numbers.py            # exit 1 on a duplicate number
    python lab/check-doc-numbers.py --list     # show the numbering
"""
import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    by_number = collections.defaultdict(list)
    for path in sorted(DOCS.glob("*.md")):
        stem = path.name.split("-")[0]
        if stem.isdigit():
            by_number[stem].append(path.name)

    dups = {k: v for k, v in by_number.items() if len(v) > 1}
    if a.list:
        for number in sorted(by_number, key=int):
            print(f"  {number:>3}  {', '.join(by_number[number])}")

    print(f"numbered documents: {len(by_number)}, duplicates: {len(dups)}")
    for number, names in sorted(dups.items(), key=lambda kv: int(kv[0])):
        print(f"  {number}: {', '.join(names)}")
    print("RESULT:", "ok" if not dups else "fail")
    return 0 if not dups else 1


if __name__ == "__main__":
    sys.exit(main())
