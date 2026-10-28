#!/usr/bin/env python3
"""xrepo-sweep — the channel state, read from the repositories instead of remembered.

Coordination kept in a document drifts the moment somebody pushes. This sweeps the sibling checkouts that exist
on this machine and reports, per project: the last commit, whether their `interop/` carries a note addressed to
us, and whether our last note to them has been answered. A project with no checkout is reported as such, not
skipped — "nobody looked" must not read like "nothing to see".

    python lab/cross-repo/sweep.py
    python lab/cross-repo/sweep.py --json
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

# parents: [cross-repo, lab, spec, <workspace>] - siblings live next to this repository, not inside it.
HOME = pathlib.Path(__file__).resolve().parents[3]
OURS = "flowguard"

# Where a sibling checkout lives on this machine. A missing directory is a reported fact, not an error.
SIBLINGS = {
    "lexspec": HOME / "lexspec-review",
    "VecDHT": HOME / "VecDHT",
    "cases": HOME / "cases",
    "lean-agent-verify": HOME / "lean-agent-verify",
    "modelproof": HOME / "modelproof",
    "pharos-agent-arena": HOME / "pharos-agent-arena",
    "morphogenesis": HOME / "-",
}


def git(repo: pathlib.Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return (r.stdout or "").strip() if r.returncode == 0 else ""


def notes_to_us(repo: pathlib.Path) -> list[str]:
    d = repo / "interop"
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.md")):
        stem = f.name.lower()
        if "to-flowguard" in stem or "to_flowguard" in stem:
            out.append(f.name)
    return out


def mentions(repo: pathlib.Path, needle: str) -> int:
    """How many files under interop/ or docs/ mention a string - our finding ids, for instance."""
    n = 0
    for base in ("interop", "docs", "lab"):
        d = repo / base
        if not d.is_dir():
            continue
        for f in d.rglob("*.md"):
            try:
                if needle in f.read_text(encoding="utf-8", errors="ignore"):
                    n += 1
            except Exception:  # noqa: BLE001
                continue
    return n


def sweep() -> list[dict]:
    rows = []
    for name, path in SIBLINGS.items():
        row = {"project": name, "checkout": str(path), "present": path.is_dir()}
        if row["present"]:
            row["head"] = git(path, "log", "--oneline", "-1")
            row["last_date"] = git(path, "log", "-1", "--format=%cI")
            row["notes_to_us"] = notes_to_us(path)
            # do they mention our two open findings?
            row["mentions_f3_1"] = mentions(path, "F-3-1")
            row["mentions_f4_1"] = mentions(path, "F-4-1")
        rows.append(row)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = sweep()
    if a.json:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
        return 0

    print(f"{'project':22} {'checkout':10} {'note to us':26} last commit")
    for r in rows:
        if not r["present"]:
            print(f"{r['project']:22} {'absent':10} {'-':26} no checkout on this machine")
            continue
        notes = ", ".join(r["notes_to_us"]) or "-"
        print(f"{r['project']:22} {'present':10} {notes[:26]:26} {r['head'][:44]}")
        if r["mentions_f3_1"]:
            print(f"{'':22} {'':10} our finding F-3-1 is mentioned in {r['mentions_f3_1']} file(s)")
        if r["mentions_f4_1"]:
            print(f"{'':22} {'':10} our finding F-4-1 is mentioned in {r['mentions_f4_1']} file(s)")

    present = [r for r in rows if r["present"]]
    answered = [r for r in present if r["mentions_f3_1"] or r["mentions_f4_1"]]
    print(f"\ncheckouts: {len(present)}/{len(rows)}, findings acknowledged: {len(answered)}")
    print("RESULT:", "ok" if present else "no sibling checkouts found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
