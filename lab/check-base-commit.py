#!/usr/bin/env python3
"""check-base-commit — every card must anchor itself to a tree that exists.

`base_commit` is the anchor of a card: the tree the run started from. Without it a card is a story with a
timestamp, and the whole evidence chain of this repository rests on being able to open that tree.

The check is deliberately absolute: `git cat-file -e <sha>^{commit}` has to succeed for every card. There is no
allowlist and no waiver. An earlier draft of this file carried a map of "unverifiable but disclosed" anchors;
it was written against a shallow clone, where none of the 38 shas resolved, and the first CI run showed the
rows reported as stale — the objects were there all along. A waiver list that only exists because the checking
tool looked at a partial repository is exactly the failure this project is about, so it is gone.

    python lab/check-base-commit.py
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = ROOT / "lab" / "experiments"
CARD_RE = re.compile(r'(?m)^base_commit:\s*"?' + r"([0-9a-f]{7,40})")


def resolves(sha: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        print("git is not available: cannot resolve any base_commit")
        return 2

    if subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT,
                      capture_output=True, text=True).stdout.strip() == "true":
        # A shallow clone resolves nothing and would report every card as broken. That is how this guard
        # first produced a false alarm; say it instead of inventing a defect.
        print("this is a shallow clone: run `git fetch --unshallow` before checking base_commit")
        return 2

    checked, problems = 0, []
    for p in sorted(CARDS.glob("*.md")):
        if p.name in ("INDEX.md", "README.md") or "-" not in p.name:
            continue
        m = CARD_RE.search(p.read_text(encoding="utf-8", errors="ignore"))
        if not m:
            continue
        card, sha = "-".join(p.name.split("-")[:2]), m.group(1)
        checked += 1
        if not resolves(sha):
            problems.append(f"{card}: base_commit {sha} is not a commit in this repository")

    print(f"cards checked: {checked}, problems: {len(problems)}")
    for p in problems[:12]:
        print(f"  {p}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
