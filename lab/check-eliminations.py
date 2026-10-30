#!/usr/bin/env python3
"""check-eliminations — the registry must match the cards, and every elimination needs a revival condition.

Two failures worth guarding, both from `mak777uh/-`:

1. a `refutes` card that is not in `docs/ELIMINATIONS.md` — the hypothesis can quietly return;
2. an entry whose revival condition is missing — "an entry without a revival condition is not an elimination,
   it is an opinion".

It also refuses the reverse: a registry row whose card no longer exists or is no longer `refutes`.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "build-eliminations.py"), "--check"],
                       capture_output=True, text=True)
    problems = []
    if r.returncode != 0:
        problems.append((r.stdout or "stale").strip())

    text = (ROOT / "docs" / "ELIMINATIONS.md").read_text(encoding="utf-8") if \
        (ROOT / "docs" / "ELIMINATIONS.md").exists() else ""
    if "missing — add it" in text:
        problems.append("an elimination has no revival condition")

    # every refutes card present?
    refutes = []
    for p in sorted((ROOT / "lab" / "experiments").glob("*.md")):
        if p.name in ("INDEX.md", "README.md") or "-" not in p.name:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^verdict:\s*(\S+)", t, re.M)
        if m and m.group(1) == "refutes":
            refutes.append(p.name.split("-")[0] + "-" + p.name.split("-")[1])
    for cid in refutes:
        if cid not in text:
            problems.append(f"{cid} is refuted but missing from the registry")

    for p in problems:
        print(f"  {p}")
    print(f"refuted cards: {len(refutes)}, problems: {len(problems)}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
