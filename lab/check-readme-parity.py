#!/usr/bin/env python3
"""check-readme-parity — the Russian mirror may omit a number, and may never contradict one.

LexSpec's cross-audit (2026-10-29, F-2) named this gap and gave it to us in ready form: the repository declares
`README.md` as canon and `README.ru.md` as a mirror, and nothing compares them. Prose may legitimately differ
between languages; a count may not — if the canon says "17 codes" and the mirror says "16", one of them is wrong
and a reader has no way to know which.

The rule is **subset, not equality**: README.ru.md declares itself a summary ("Русское зеркало … при расхождении
верен [канон]"), so it may leave numbers out — and must never state one the canon does not. Equality would turn a
summary into a translation, which is a different document with a different promise.

Only integers of two or more digits count, with fenced code, inline code and enumeration markers stripped: those
are the numbers in this document that make claims. A number present in the mirror and absent from the canon is a
contradiction and fails the check; a number only in the canon is reported as information.

    python lab/check-readme-parity.py            # exit 1 when the number sets differ
    python lab/check-readme-parity.py --list     # show both sets
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANON = ROOT / "README.md"
MIRROR = ROOT / "README.ru.md"

# Integers only, and only those standing alone: `0.15` is not the number 0 or 15, `#L24` is not a count,
# `e-m70` is an identifier. Fenced code blocks are stripped first, because commands contain versions,
# ports and paths that are not claims.
FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
NUMBER = re.compile(r"(?<![\w.#/-])(\d{2,6})(?![\w./-])")
# A line that starts with "1." or "1)" is an enumeration, not a count.
ENUM_HEAD = re.compile(r"^\s*\d+[.)]\s", re.M)


def numbers(path: pathlib.Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    text = FENCE.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = ENUM_HEAD.sub(" ", text)
    return set(NUMBER.findall(text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    for path in (CANON, MIRROR):
        if not path.exists():
            print(f"missing: {path.name}")
            return 1

    canon, mirror = numbers(CANON), numbers(MIRROR)
    only_canon = sorted(canon - mirror, key=int)   # information: the summary omitted it
    only_mirror = sorted(mirror - canon, key=int)  # contradiction: the summary invented it

    if a.list:
        print("canon :", " ".join(sorted(canon, key=int)))
        print("mirror:", " ".join(sorted(mirror, key=int)))

    print(f"numbers in {CANON.name}: {len(canon)}, in {MIRROR.name}: {len(mirror)}")
    if only_canon:
        print(f"  only in the canon (the summary may omit these): {' '.join(only_canon)}")
    if only_mirror:
        print(f"  only in the mirror (contradiction): {' '.join(only_mirror)}")

    ok = not only_mirror
    print("RESULT:", "ok" if ok else "fail")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
