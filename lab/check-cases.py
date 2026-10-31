#!/usr/bin/env python3
"""check-cases — a case is five sections and one sentence, or it is not a case.

The format exists so that a person who did not write this repository can produce a result without reading its
source. A format nobody checks becomes three variants by the second author, so this guard enforces the parts
that make the format useful:

  * folder name `NNN-slug`, `NNN` three digits, `slug` lowercase words
  * the five sections, in order: Claim, Evidence, Reproduce, Verdict, Limits
  * `**Verdict:**` carrying one of the three allowed words
  * the title giving one sentence, not a paragraph
  * Evidence naming at least one artifact
  * Limits with at least one line — a case with no limits claims more than it can
  * the registry matching the folders (delegated to build-case-registry.py --check)

    python lab/check-cases.py
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
NAME = re.compile(r"^\d{3}-[a-z0-9-]+$")
VERDICTS = ("confirmed", "not confirmed", "could not tell")
SECTIONS = ("Claim", "Evidence", "Reproduce", "Verdict", "Limits")


def main() -> int:
    problems = []
    folders = sorted(p for p in CASES.iterdir() if p.is_dir() and p.name != "TEMPLATE")

    for d in folders:
        if not NAME.match(d.name):
            problems.append(f"{d.name}: folder does not match NNN-slug")
            continue
        readme = d / "README.md"
        if not readme.exists():
            problems.append(f"{d.name}: no README.md")
            continue
        text = readme.read_text(encoding="utf-8")
        lines = text.splitlines()

        heads = [l for l in lines if l.startswith("## ")]
        order = [h[3:].strip().split()[0] for h in heads if h[3:].strip()]
        if tuple(order[:5]) != SECTIONS:
            problems.append(f"{d.name}: sections are {order[:5]}, expected {list(SECTIONS)}")

        title = next((l for l in lines if l.startswith("# ")), "")
        sentence = re.sub(r"^#\s*\d{3}\s*[—-]\s*", "", title).strip()
        if not sentence:
            problems.append(f"{d.name}: no title sentence")
        elif len(sentence) > 220:
            problems.append(f"{d.name}: the title is {len(sentence)} characters — one sentence, not a paragraph")

        verdict_line = next((l for l in lines if l.strip().startswith("**Verdict:**")), "")
        verdict = verdict_line.split("**")[-1].strip().lower() if verdict_line else ""
        if verdict not in VERDICTS:
            problems.append(f"{d.name}: verdict {verdict!r} is not one of {list(VERDICTS)}")

        body = text.split("## Limits", 1)
        if len(body) == 2 and not body[1].strip():
            problems.append(f"{d.name}: Limits is empty — a case with no limits claims more than it can")

        evidence = text.split("## Evidence", 1)
        if len(evidence) == 2:
            chunk = evidence[1].split("## ", 1)[0]
            if not re.search(r"(https?://|`[^`]+`|\b[0-9a-f]{7,64}\b|\./|\w+\.\w{2,4})", chunk):
                problems.append(f"{d.name}: Evidence names no artifact")

    registry = subprocess.run([sys.executable, str(ROOT / "lab" / "build-case-registry.py"), "--check"],
                              capture_output=True, text=True)
    if registry.returncode != 0:
        problems.append("registry: " + (registry.stdout or "stale").strip().splitlines()[-1])

    print(f"cases: {len(folders)}, problems: {len(problems)}")
    for p in problems[:12]:
        print(f"  {p}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
