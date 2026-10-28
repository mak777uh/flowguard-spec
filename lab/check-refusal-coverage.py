#!/usr/bin/env python3
"""check-refusal-coverage — every refusal code must be exercised by a test.

A refusal code that nothing triggers is a comment. After the independent attack (E-M42) closed eleven
breaks, the risk is the opposite one: a code is added, the gate is trusted, and no test ever fires it,
so the next refactor can delete the check silently.

This scans the refusal-code table in docs/37-REFUSAL-CODES.md and requires each code to appear in at
least one of: the attack suites (lab/e-m36-run.py, lab/e-m42-run.py), fixtures/attack, or an
experiment card's declared expectations.

    python lab/check-refusal-coverage.py            # exit 1 on an unexercised code
    python lab/check-refusal-coverage.py --list     # show which test covers which code
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "37-REFUSAL-CODES.md"
CODE = re.compile(r"`([A-Z][A-Z0-9_]{4,})`")

CARRIERS = [
    ROOT / "lab" / "e-m36-run.py",
    ROOT / "lab" / "e-m42-run.py",
    ROOT / "lab" / "e-m12-run.py",
    ROOT / "lab" / "e-m33-run.py",
    ROOT / "lab" / "selftest-guards.sh",
]


def documented_codes():
    text = DOC.read_text(encoding="utf-8")
    # only codes that appear in the refusal table rows, not in prose examples
    codes = set()
    for line in text.splitlines():
        if line.startswith("|") and "`" in line:
            cells = line.strip().strip("|").split("|")
            if cells and CODE.search(cells[0]):
                codes.add(CODE.search(cells[0]).group(1))
    return codes


def carriers():
    out = {}
    for path in CARRIERS:
        if path.exists():
            out[path.name] = path.read_text(encoding="utf-8", errors="ignore")
    attack = ROOT / "fixtures" / "attack"
    if attack.exists():
        blob = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                         for p in attack.glob("*.json"))
        out["fixtures/attack"] = blob
    for card in (ROOT / "lab" / "experiments").glob("*.md"):
        out.setdefault("cards", "")
        out["cards"] += card.read_text(encoding="utf-8", errors="ignore")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    want = documented_codes()
    have = carriers()
    covered, uncovered = {}, []
    for code in sorted(want):
        where = [name for name, blob in have.items() if code in blob]
        if where:
            covered[code] = where
        else:
            uncovered.append(code)

    if a.list:
        for code, where in covered.items():
            print(f"{code:28} exercised in: {', '.join(where[:3])}")
    print(f"refusal codes documented: {len(want)}, exercised by a test: {len(covered)}, "
          f"unexercised: {len(uncovered)}")
    for code in uncovered:
        print(f"  no test fires {code}")
    print("RESULT:", "ok" if not uncovered else "fail")
    return 0 if not uncovered else 1


if __name__ == "__main__":
    sys.exit(main())
