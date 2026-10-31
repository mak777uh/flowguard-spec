#!/usr/bin/env python3
"""check-base-commit — a card must name a tree that exists, or say why it cannot.

Every experiment card carries `base_commit`: the tree the run started from. That is the anchor of the whole
evidence chain — a card whose anchor cannot be inspected is a story with a timestamp.

This repository was published as one squashed commit, so 38 cards name trees that are not git objects here.
Leaving that implicit is the one defect this project exists to prevent, so the gap is written down in
`lab/commit-map.tsv` and this guard keeps the disclosure honest in both directions:

  * a card whose `base_commit` does not resolve and has no row      -> fail
  * a card whose sha differs from the sha in its row                -> fail
  * a row for a card that no longer exists                          -> fail
  * a row whose sha resolves now (the disclosure has rotted)        -> fail
  * a row with no status or no reason                               -> fail

    python lab/check-base-commit.py
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = ROOT / "lab" / "experiments"
MAP = ROOT / "lab" / "commit-map.tsv"

CARD_RE = re.compile(r'(?m)^base_commit:\s*"?' + r"([0-9a-f]{7,40})")


def resolves(sha: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def card_shas() -> dict[str, str]:
    out = {}
    for p in sorted(CARDS.glob("*.md")):
        if p.name in ("INDEX.md", "README.md") or "-" not in p.name:
            continue
        m = CARD_RE.search(p.read_text(encoding="utf-8", errors="ignore"))
        if m:
            out["-".join(p.name.split("-")[:2])] = m.group(1)
    return out


def rows() -> dict[str, tuple[str, str, str]]:
    out = {}
    if not MAP.exists():
        return out
    for line in MAP.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [c.strip() for c in line.split("\t")]
        if len(parts) < 4:
            parts += [""] * (4 - len(parts))
        card, sha, status, note = parts[:4]
        out[card] = (sha, status, note)
    return out


def main() -> int:
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        print("git is not available: cannot resolve any base_commit")
        return 2

    cards, mapped = card_shas(), rows()
    problems = []

    for card, sha in sorted(cards.items()):
        if resolves(sha):
            continue
        row = mapped.get(card)
        if not row:
            problems.append(f"{card}: base_commit {sha} does not resolve and has no row in lab/commit-map.tsv")
            continue
        row_sha, status, note = row
        if row_sha != sha:
            problems.append(f"{card}: map says {row_sha}, the card says {sha}")
        if not status:
            problems.append(f"{card}: the map row has no status")
        if not note:
            problems.append(f"{card}: the map row has no reason — a row without a reason is a waiver")

    for card, (sha, _status, _note) in sorted(mapped.items()):
        if card not in cards:
            problems.append(f"{card}: row in lab/commit-map.tsv, but no card names a base_commit")
        elif resolves(sha):
            problems.append(f"{card}: the row is stale — {sha} resolves now, remove the row")

    unresolved = sum(1 for s in cards.values() if not resolves(s))
    print(f"cards with base_commit: {len(cards)}, disclosed as unavailable: {unresolved}, "
          f"map rows: {len(mapped)}, problems: {len(problems)}")
    for p in problems[:12]:
        print(f"  {p}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
