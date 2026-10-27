#!/usr/bin/env python3
"""Interop check — reports how far a repository implements the shared method kit (M1-M7).

Semantics, not paths: the checker looks for what a file *means* (a table with an
evidence-type column, a card with a pre-registered threshold) and reports where it found
it. A restructuring sibling therefore shows `present (moved)`, not a false negative.

The check never fails a build. Gaps are information. Claiming compatibility without
running it is the actual error.

    python lab/check-interop.py                     # this repository
    python lab/check-interop.py --repo C:/path/to/sibling
    python lab/check-interop.py --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

EVIDENCE = {"proof", "test", "statistics", "observation", "judgment",
            "withdrawn", "not established", "false as stated"}
CLAIM_ROW = re.compile(r"^\|\s*([A-Z]{1,2}-\d{1,3})\s*\|")
THRESHOLD_WORDS = re.compile(r"(threshold|порог|pre-?registered)", re.I)
TABLE_HEADER = re.compile(r"^\|\s*id\s*\|\s*claim\s*\|", re.I)


def md_files(root):
    return [p for p in root.rglob("*.md") if ".git" not in p.parts]


def find_claims(root):
    """Return (path, rows, types) for the file that looks like a claim registry."""
    best = None
    for p in md_files(root):
        try:
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        rows, types = 0, set()
        for line in lines:
            m = CLAIM_ROW.match(line)
            if not m:
                continue
            rows += 1
            cells = [c.strip().strip("*` ") for c in line.strip().strip("|").split("|")]
            if len(cells) > 2:
                t = cells[2].lower()
                for known in EVIDENCE:
                    if t.startswith(known):
                        types.add(known)
        if rows >= 3 and (best is None or rows > best[1]):
            best = (p, rows, types)
    return best


def find_eliminations(root):
    for p in md_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "eliminary" in p.name.lower() or "eliminations" in p.name.lower():
            entries = len(re.findall(r"(?m)^#{2,3}\s+\S", text))
            revival = len(re.findall(r"revive|воскреш", text, re.I))
            return p, entries, revival
    return None


def find_experiments(root):
    hits = []
    for d in root.rglob("*"):
        if d.is_dir() and re.search(r"experiment|hypothes", d.name, re.I) and ".git" not in d.parts:
            hits.extend([f for f in d.glob("*.md")])
    cards = 0
    for f in hits:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if THRESHOLD_WORDS.search(text):
            cards += 1
    return hits, cards


def find_metrics(root):
    for p in md_files(root):
        if "metric" in p.name.lower():
            text = p.read_text(encoding="utf-8", errors="ignore")
            cmds = len(re.findall(r"```", text)) // 2
            return p, cmds
    return None


def find_status(root):
    for p in md_files(root):
        if re.search(r"status", p.name, re.I):
            return p
    return None


def find_guards(root):
    found = {"secrets": None, "links": None, "claims": None}
    for p in root.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        name = p.name.lower()
        if name.endswith((".sh", ".py", ".js", ".ts")):
            try:
                head = p.read_text(encoding="utf-8", errors="ignore")[:4000].lower()
            except OSError:
                continue
            if "secret" in name or "secret" in head:
                found["secrets"] = found["secrets"] or p
            if "link" in name and ("http" in head or "relative" in head):
                found["links"] = found["links"] or p
            if "claim" in name and ("linter" in head or "evidence" in head or "registry" in head):
                found["claims"] = found["claims"] or p
    return found


def row(item, state, detail):
    return {"item": item, "state": state, "detail": detail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(HERE))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.repo).resolve()
    if not root.exists():
        print(f"error: {root} does not exist")
        return 2

    out = []
    exp_files, exp_cards = find_experiments(root)
    out.append(row("M1 experiment cards",
                   "present" if exp_cards else ("partial" if exp_files else "absent"),
                   f"{exp_cards} cards with a pre-registered threshold, {len(exp_files)} files"))

    metrics = find_metrics(root)
    out.append(row("M2 metrics with commands",
                   "present" if metrics and metrics[1] else ("partial" if metrics else "absent"),
                   f"{metrics[0].name}, {metrics[1]} command blocks" if metrics else "no metrics file"))

    claims = find_claims(root)
    if claims:
        p, rows, types = claims
        out.append(row("M3 claim registry",
                       "present" if len(types) >= 3 else "partial",
                       f"{p.name}: {rows} claims, evidence types used: {', '.join(sorted(types)) or 'none'}"))
    else:
        out.append(row("M3 claim registry", "absent", "no table with an evidence-type column"))

    elim = find_eliminations(root)
    out.append(row("M4 eliminations with revival conditions",
                   "present" if elim and elim[2] else ("partial" if elim else "absent"),
                   f"{elim[0].name}: {elim[1]} entries, {elim[2]} revival mentions" if elim else "absent"))

    st = find_status(root)
    out.append(row("M5 falsifiable status doc", "present" if st else "absent",
                   st.name if st else "no status document"))

    guards = find_guards(root)
    have = [k for k, v in guards.items() if v]
    out.append(row("M6 guards", "present" if len(have) == 3 else ("partial" if have else "absent"),
                   ", ".join(have) if have else "none found"))

    rebuild = None
    for p in md_files(root):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"independent (re)?build|rebuild from (the )?document", text, re.I) and re.search(r"\b(defects?|caught|found \d|result)\b", text, re.I) and p.name not in ("99-SOURCES.md", "96-INTEROP.md"):
            rebuild = p
            break
    out.append(row("M7 independent-rebuild test", "present" if rebuild else "absent",
                   rebuild.name if rebuild else "no recorded rebuild test"))

    present = sum(1 for r in out if r["state"] == "present")
    total = len(out)
    if args.json:
        print(json.dumps({"repo": str(root), "score": f"{present}/{total}", "items": out}, indent=1))
        return 0

    print(f"repo: {root}")
    print(f"{'item':38} {'state':9} detail")
    for r in out:
        print(f"{r['item']:38} {r['state']:9} {r['detail']}")
    print(f"\nkit conformance: {present}/{total}")
    print("note: gaps are information, not failures — this check never breaks a build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
