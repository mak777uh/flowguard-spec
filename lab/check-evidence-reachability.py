#!/usr/bin/env python3
"""check-evidence-reachability — a card, a note or an audit that nothing indexes is a file nobody will find.

volna's cross-audit (2026-10-29, F-1) put it exactly: `lab/check-readme.py` promises "every document" and scans
`docs/` only — 124 of 188 tracked Markdown files escape it, including every experiment card and every interop
note. The step name was true of the guard's docstring and false of the step.

This is the missing half. It does not require a link from README to every card (that would swamp the README); it
requires each evidence file to be named in its directory's index, and each index to be linked from README:

    lab/experiments/INDEX.md   every card in lab/experiments/
    interop/README.md          every note in interop/ (and interop/reviews/, interop/reviews/LEDGER.md)
    cross-audit/README.md      every review we receive or write

    python lab/check-evidence-reachability.py            # exit 1 on an unindexed file
    python lab/check-evidence-reachability.py --list     # show the counts per index
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

INDEXES = {
    "lab/experiments": ROOT / "lab" / "experiments" / "INDEX.md",
    "interop": ROOT / "interop" / "README.md",
    "cross-audit": ROOT / "cross-audit" / "README.md",
}


def tracked(prefix: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", f"{prefix}/*.md"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if f]


def index_mentions(path: pathlib.Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"[\w./-]+\.md", text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    problems = []
    for prefix, index in INDEXES.items():
        files = tracked(prefix)
        if not files:
            continue
        named = index_mentions(index)
        if not index.exists():
            problems.append((prefix, index, "the index itself is missing"))
            continue
        missing = [f for f in files
                   if pathlib.Path(f).name not in named and f not in named
                   and not f.endswith("README.md") and not f.endswith("INDEX.md")]
        if a.list:
            print(f"{prefix:18} files: {len(files):3}  indexed: {len(files) - len(missing):3}  index: {index.name}")
        for f in missing:
            problems.append((prefix, index, f))

    total = sum(len(tracked(p)) for p in INDEXES)
    print(f"evidence files covered by an index: {total}")
    for prefix, index, item in problems[:40]:
        print(f"  unindexed  {item}   (index: {index.relative_to(ROOT)})")
    if len(problems) > 40:
        print(f"  ... and {len(problems) - 40} more")
    print(f"problems: {len(problems)}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
