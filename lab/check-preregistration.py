#!/usr/bin/env python3
"""check-preregistration — a card written after the run is a story, not an experiment.

Taken from `mak777uh/-` (morphogenesis), which pre-registers every experiment with the criteria committed before
the run, **including the branch structure of possible outcomes**, and reports "the test did not reach the effect"
rather than "there is no effect".

This guard applies to cards written from 2026-10-31 onward. The older cards are not retrofitted - rewriting 69
cards after the fact would produce exactly the artefact this guard exists to prevent - but their absence is
counted and printed, so the debt is visible rather than hidden.

Required in the front matter of every new card:

    sensitivity   what difference this design can produce, as a number
    branches      confirm / refute / inconclusive, each as a number
    stop_rule     when to stop early, and when to stop without a result
    analysis_plan which figure comes from which artifact, and by which command

    python lab/check-preregistration.py            # exit 1 on a new card missing a field
    python lab/check-preregistration.py --list     # show every card's status
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = ROOT / "lab" / "experiments"
CUTOFF = "2026-10-31"
FIELDS = ("sensitivity", "branches", "stop_rule", "analysis_plan")


def front_matter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end > 0 else ""


def card_date(text: str) -> str:
    m = re.search(r'^started:\s*"?(\d{4}-\d{2}-\d{2})', text, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^finished:\s*\"?(\d{4}-\d{2}-\d{2})", front_matter(text), re.M)
    return m.group(1) if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    new_cards, old_cards, bad = [], [], []
    for path in sorted(CARDS.glob("*.md")):
        if path.name in ("INDEX.md", "README.md") or "-" not in path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        fm = front_matter(text)
        date = card_date(text)
        if date and date >= CUTOFF:
            new_cards.append(path.name)
            missing = [f for f in FIELDS if not re.search(rf"^{f}:", fm, re.M)]
            if missing:
                bad.append((path.name, missing))
        else:
            old_cards.append(path.name)

    if a.list:
        for name in new_cards:
            print(f"  new  {name}")
        print(f"  old  {len(old_cards)} cards, exempt (written before {CUTOFF})")

    print(f"cards under the rule: {len(new_cards)}, exempt: {len(old_cards)}, "
          f"missing a pre-registered field: {len(bad)}")
    for name, missing in bad:
        print(f"  {name}: no {', '.join(missing)}")
    print("RESULT:", "ok" if not bad else "fail")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
