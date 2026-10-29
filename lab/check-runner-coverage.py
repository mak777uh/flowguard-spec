#!/usr/bin/env python3
"""check-runner-coverage — every experiment runner must be run by CI or declared not-to-be.

volna's cross-audit (F-2): 26 `lab/e-m*-run.py` runners exist, CI runs 2, and the dossier cites the other 24 as
evidence. The honest answers are two, and both are acceptable — but one of them has to be written down:

1. the runner is in `.github/workflows/guards.yml`;
2. the runner is in `lab/runners-not-in-ci.txt` with the reason it cannot be (a live PostgreSQL, a GPU, a
   network call), in which case `lab/round-check.sh` runs it locally and the reason says why.

A runner that is in neither list is a runner whose number in a card nobody can reproduce.

    python lab/check-runner-coverage.py            # exit 1 on an undeclared runner
    python lab/check-runner-coverage.py --list     # show the split
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "guards.yml"
DECLARED = ROOT / "lab" / "runners-not-in-ci.txt"


def runners() -> list[str]:
    out = subprocess.run(["git", "ls-files", "lab/e-m*-run.py"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return sorted(pathlib.Path(f).name for f in out if f)


def declared() -> set[str]:
    if not DECLARED.exists():
        return set()
    out = set()
    for line in DECLARED.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line.split()[0])
    return out


def in_ci(name: str, workflow: str) -> bool:
    return name in workflow


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    workflow = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    decl = declared()
    undeclared, ci, excused = [], [], []
    for name in runners():
        if in_ci(name, workflow):
            ci.append(name)
        elif name in decl:
            excused.append(name)
        else:
            undeclared.append(name)

    if a.list:
        print(f"in CI: {len(ci)}  declared-not-in-CI: {len(excused)}  undeclared: {len(undeclared)}")
        for name in ci:
            print(f"  ci        {name}")
        for name in excused:
            print(f"  declared  {name}")

    # A declared runner must have its declaration checked: `local-ritual` means the ritual runs it, and
    # that is a claim about lab/round-check.sh which this guard can verify instead of trusting.
    ritual_text = (ROOT / "lab" / "round-check.sh").read_text(encoding="utf-8") \
        if (ROOT / "lab" / "round-check.sh").exists() else ""
    unverified = [name for name in excused
                  if "local-ritual" in DECLARED.read_text(encoding="utf-8").split(name, 1)[1].splitlines()[0]
                  and name not in ritual_text]

    print(f"runners: {len(runners())}, in CI: {len(ci)}, declared not-in-CI: {len(excused)}, "
          f"undeclared: {len(undeclared)}, declared-but-not-run-by-the-ritual: {len(unverified)}")
    for name in unverified:
        print(f"  declaration is false  {name}  (lab/runners-not-in-ci.txt says local-ritual; the ritual does not run it)")
    for name in undeclared:
        print(f"  undeclared  {name}  (add it to the workflow, or to lab/runners-not-in-ci.txt with a reason)")
    ok = not undeclared and not unverified
    print("RESULT:", "ok" if ok else "fail")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
