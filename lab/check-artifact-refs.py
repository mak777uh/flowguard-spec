#!/usr/bin/env python3
"""check-artifact-refs — every backticked repository path must exist.

Adapted from VecDHT's `lab/check-artifact-refs.py` (their note 2, 2026-10-27): "a reference to a
path that does not exist is worse than it looks — the reader checks the name, not the tree".

Our markdown-link checker covers links; it does not cover the far more common habit of naming a file
in backticks inside prose. Those drift silently.

    python lab/check-artifact-refs.py            # exit 1 on a dangling reference
    python lab/check-artifact-refs.py --list     # print every reference found

Allowances live in `lab/artifact-ref-allowances.txt`, one per line: `path  # why it is allowed`.
An allowance whose path now EXISTS is itself a finding, because the list must not rot in the other
direction (their rule, kept).
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW = ROOT / "lab" / "artifact-ref-allowances.txt"

PREFIXES = ("docs/", "lab/", "tools/", "enumerators/", "fixtures/", "interop/", "policies/",
            "articles/", ".github/")
SCAN = ["*.md", "docs/*.md", "lab/**/*.md", "enumerators/**/*.md", "tools/*.md",
        "interop/*.md", "fixtures/**/*.md", "articles/*.md", "policies/*.md"]

BACKTICK = re.compile(r"`([^`\n]+)`")


def candidates():
    seen = []
    for pattern in SCAN:
        seen.extend(ROOT.glob(pattern))
    return sorted({p for p in seen if p.is_file()})


def looks_like_path(token: str) -> bool:
    token = token.strip()
    if not token or token.startswith(("http://", "https://", "<", "$")):
        return False
    if any(ch in token for ch in "*?<>{}\"'| ") and "/" not in token:
        return False
    if token.startswith(PREFIXES):
        return True
    # a bare filename with an extension is only checked when it sits under a known directory
    return False


def load_allowances():
    allow = {}
    if ALLOW.exists():
        for line in ALLOW.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            path, _, why = line.partition("#")
            allow[path.strip()] = why.strip()
    return allow


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    allow = load_allowances()
    total, dangling, details = 0, [], []
    for doc in candidates():
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for m in BACKTICK.finditer(text):
            token = m.group(1).strip()
            if not looks_like_path(token):
                continue
            total += 1
            target = token.split("#", 1)[0].rstrip("/")
            target = re.sub(r":\d+(-\d+)?$", "", target)  # `file.py:211` names a line, not another file
            if any(c in target for c in "<>*?"):  # templates and globs are not references
                continue
            if a.list:
                details.append(f"{doc.relative_to(ROOT).as_posix()}: {token}")
            if target in allow:
                continue
            # cards and docs are cited both as `docs/X.md` and as `docs/X`; accept either form
            if not ((ROOT / target).exists() or (ROOT / (target + ".md")).exists()):
                dangling.append((doc.relative_to(ROOT).as_posix(), token))

    stale = [p for p in allow if (ROOT / p).exists()]

    if a.list:
        print("\n".join(details))
    print(f"backticked paths checked: {total}, dangling: {len(dangling)}, "
          f"allowances: {len(allow)}, stale allowances: {len(stale)}")
    for doc, token in dangling[:20]:
        print(f"  dangling  {doc}: `{token}`")
    for p in stale[:10]:
        print(f"  stale allowance (path now exists): {p}")
    ok = not dangling and not stale
    print("RESULT:", "ok" if ok else "fail")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
