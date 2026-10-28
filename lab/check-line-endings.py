#!/usr/bin/env python3
"""check-line-endings — no CRLF in scripts, and a shell script that parses.

Three times now a script written through a Windows tool acquired CRLF and bash refused it:
`set: pipefail: invalid option name`, then `$'\\r': command not found`. Each time the failure surfaced
somewhere else — readiness E1 dropped to zero and the reason was invisible. `.gitattributes` only
normalises at checkout and commit; the working tree can still be wrong while tests run.

    python lab/check-line-endings.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = (".sh", ".py", ".yml", ".yaml", ".json")


def resolve_bash():
    """`bash` on Windows can be WSL's, which fails on a Git-style path and reports in UTF-16."""
    candidates = [r"C:\Program Files\Git\bin\bash.exe", "/bin/bash", "/usr/bin/bash"]
    for c in candidates:
        if Path(c).exists():
            return c
    return "bash"


def main() -> int:
    listed = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    bad = []
    for name in listed:
        p = ROOT / name
        if not p.is_file() or p.suffix not in SUFFIXES:
            continue
        if "fixtures" in p.parts:
            continue
        data = p.read_bytes()
        if b"\r\n" in data:
            bad.append((p.relative_to(ROOT).as_posix(), "CRLF"))

    # a shell script must at least parse: a CRLF file fails here with a readable message
    bash = resolve_bash()
    for sh in sorted(ROOT.glob("lab/*.sh")):
        r = subprocess.run([bash, "-n", str(sh)], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append((sh.relative_to(ROOT).as_posix(), "does not parse: " + (r.stderr.strip()[:80])))

    for path, why in bad:
        print(f"  {path}: {why}")
    print(f"files with CRLF or a parse error: {len(bad)}")
    print("RESULT:", "ok" if not bad else "fail")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
