#!/usr/bin/env python3
"""check-readme — the README must link every document, or it is no longer an entry point.

The owner asked that the README be kept current during work rather than at the end. A promise is
not a check, so this is a check: every Markdown file under docs/ must be reachable from README.md.
Round packs, syntheses and audits included - if a document exists and the front page does not
mention it, a reader will not find it.

    python lab/check-readme.py            # exit 1 listing the unlinked documents
    python lab/check-readme.py --warn     # report only, always exit 0

Exempt: nothing. A document nobody links is a document nobody reads.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DOCS = ROOT / "docs"


def linked_targets(readme_text: str) -> set:
    """Every relative link and every bare path mentioned in the README."""
    out = set()
    for target in re.findall(r"\]\(([^)]+)\)", readme_text):
        target = target.split("#", 1)[0].strip()
        if target and not target.startswith(("http://", "https://", "mailto:")):
            out.add(target.lstrip("./"))
    for bare in re.findall(r"docs/[A-Za-z0-9._/-]+\.md", readme_text):
        out.add(bare)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true")
    a = ap.parse_args()

    text = README.read_text(encoding="utf-8")
    linked = linked_targets(text)
    linked_names = {Path(t).name for t in linked}

    missing = []
    for doc in sorted(DOCS.glob("*.md")):
        if doc.name not in linked_names:
            missing.append(doc.relative_to(ROOT).as_posix())

    print(f"docs: {len(list(DOCS.glob('*.md')))}, linked from README: "
          f"{len(list(DOCS.glob('*.md'))) - len(missing)}")
    for m in missing:
        print(f"unlinked  {m}")
    if not missing:
        print("RESULT: ok")
        return 0
    print("RESULT:", "warn" if a.warn else "fail")
    return 0 if a.warn else 1


if __name__ == "__main__":
    sys.exit(main())
