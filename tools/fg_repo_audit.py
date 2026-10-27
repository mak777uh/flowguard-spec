#!/usr/bin/env python3
"""fg_repo_audit — the repository and the method, measured rather than described.

Two questions:
  1. Is the repository coherent — no dead weight, no contradictory documents, no stale claims?
  2. Is the development method working — do its own instruments catch its own errors?

    python tools/fg_repo_audit.py            # human report
    python tools/fg_repo_audit.py --json
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "tools/_tmp"}


def tracked_files():
    r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return [ROOT / line for line in r.stdout.splitlines() if line.strip()]


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout


def section_inventory(files):
    by_ext = Counter()
    sizes = []
    for f in files:
        if not f.exists() or f.is_dir():
            continue
        by_ext[f.suffix.lower() or "(none)"] += 1
        sizes.append((f.stat().st_size, f.relative_to(ROOT).as_posix()))
    sizes.sort(reverse=True)
    return {
        "files": len(files),
        "by_extension": dict(by_ext.most_common(12)),
        "largest": [{"path": p, "kb": round(s / 1024, 1)} for s, p in sizes[:8]],
        "total_mb": round(sum(s for s, _ in sizes) / 1024 / 1024, 2),
    }


def section_documents(files):
    docs = [f for f in files if f.suffix == ".md" and f.parent.name in ("docs", "lab", "articles", "interop")
            or f.name in ("README.md", "DOSSIER.md")]
    superseded = []
    for f in docs:
        if not f.exists():
            continue
        head = f.read_text(encoding="utf-8", errors="ignore")[:1500].upper()
        if "SUPERSEDED" in head or "LEGACY" in head or "PRE-PIVOT" in head:
            superseded.append(f.relative_to(ROOT).as_posix())
    titles = Counter()
    for f in docs:
        if f.exists():
            m = re.search(r"^#\s+(.+)$", f.read_text(encoding="utf-8", errors="ignore"), re.M)
            if m:
                titles[m.group(1).strip().lower()] += 1
    dup_titles = {t: n for t, n in titles.items() if n > 1}
    return {
        "documents": len(docs),
        "marked_superseded": sorted(superseded),
        "duplicate_titles": dup_titles,
    }


def section_cards():
    cards = sorted((ROOT / "lab" / "experiments").glob("*.md"))
    rows = []
    for c in cards:
        text = c.read_text(encoding="utf-8", errors="ignore")
        fm = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            for line in parts[1].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
        rows.append({"file": c.name, "id": fm.get("id"), "status": fm.get("status"),
                     "verdict": fm.get("verdict"), "has_log": "lab/logs/" in text})
    return {
        "cards": len(rows),
        "by_verdict": dict(Counter(r["verdict"] for r in rows)),
        "without_log": [r["id"] for r in rows if not r["has_log"]],
        "planned": [r["id"] for r in rows if r["status"] == "planned"],
    }


def section_metrics():
    p = ROOT / "docs" / "METRICS.md"
    rows = [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    commands = sum(1 for r in rows if "`" in "".join(r.split("|")[4:5]))
    logs = sum(1 for r in rows if re.search(r"`[0-9a-f]{16,}`", r))
    return {"rows": len(rows), "with_command": commands, "with_log_hash": logs}


def section_guards():
    sel = (ROOT / "lab" / "selftest-guards.sh").read_text(encoding="utf-8")
    controls = len(re.findall(r"# ---- control", sel))
    ci = (ROOT / ".github" / "workflows" / "guards.yml")
    steps = len(re.findall(r"^\s+- name:", ci.read_text(encoding="utf-8"), re.M)) if ci.exists() else 0
    return {"negative_controls": controls, "ci_steps": steps,
            "checks": sorted(p.name for p in (ROOT / "lab").glob("check-*.py"))}


def section_method():
    """Does the method find its own errors? Count the recorded catches."""
    patterns = [r"found by [A-Z]-M\d+", r"caught by", r"false positive", r"declared, not enforced",
                r"фикстур\w* автора", r"one commit late", r"did not fire"]
    hits = Counter()
    evidence = []
    for f in tracked_files():
        if f.suffix not in (".md", ".py", ".sh", ".sql") or not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in patterns:
            for m in re.finditer(pat, text, re.I):
                hits[pat] += 1
                if len(evidence) < 12:
                    line = text[:m.start()].count("\n") + 1
                    evidence.append(f"{f.relative_to(ROOT).as_posix()}:{line}: {m.group(0)}")
    return {"catches_recorded": dict(hits), "total": sum(hits.values()), "examples": evidence}


def section_claims():
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "check-claims.py")],
                       cwd=ROOT, capture_output=True, text=True)
    missing = len(re.findall(r"cites missing artifact", r.stdout))
    total = re.search(r"claims: (\d+)", r.stdout)
    return {"claims": int(total.group(1)) if total else None,
            "citations_without_artifact": missing}


def section_history():
    commits = git("rev-list", "--count", "HEAD").strip()
    last = git("log", "-1", "--format=%cI %s").strip()
    authors = Counter(git("log", "--format=%an").splitlines())
    return {"commits": int(commits or 0), "last": last, "authors": dict(authors)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    files = tracked_files()
    report = {
        "inventory": section_inventory(files),
        "documents": section_documents(files),
        "cards": section_cards(),
        "metrics": section_metrics(),
        "guards": section_guards(),
        "claims": section_claims(),
        "method": section_method(),
        "history": section_history(),
    }

    if a.json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return 0

    inv, docs, cards, met = report["inventory"], report["documents"], report["cards"], report["metrics"]
    g, cl, meth, hist = report["guards"], report["claims"], report["method"], report["history"]

    print("== repository ==")
    print(f"files tracked        {inv['files']}  ({inv['total_mb']} MB)")
    print(f"by extension         {inv['by_extension']}")
    print(f"largest              {', '.join('%s %sKB' % (x['path'].split('/')[-1], x['kb']) for x in inv['largest'][:4])}")
    print(f"documents            {docs['documents']}, marked superseded: {len(docs['marked_superseded'])}")
    if docs["duplicate_titles"]:
        print(f"duplicate titles     {docs['duplicate_titles']}")
    print(f"experiment cards     {cards['cards']}  by verdict {cards['by_verdict']}")
    print(f"cards without log    {cards['without_log'] or 'none'}")
    print(f"metric rows          {met['rows']}, with command {met['with_command']}, with log hash {met['with_log_hash']}")
    print(f"claims               {cl['claims']}, citing artifacts not yet built: {cl['citations_without_artifact']}")
    print(f"commits              {hist['commits']}, authors {hist['authors']}")

    print("\n== method ==")
    print(f"negative controls    {g['negative_controls']}, CI steps {g['ci_steps']}")
    print(f"checkers             {', '.join(g['checks'])}")
    print(f"recorded catches     {meth['total']} mentions — {meth['catches_recorded']}")
    for e in meth["examples"][:6]:
        print(f"  {e}")

    print("\n== questions the numbers raise ==")
    if cards["planned"]:
        print(f"- {len(cards['planned'])} card(s) still planned: {cards['planned']}")
    if met["rows"] != met["with_command"]:
        print(f"- {met['rows'] - met['with_command']} metric row(s) lack a command")
    if cl["citations_without_artifact"]:
        print(f"- {cl['citations_without_artifact']} claim citation(s) point at artifacts that do not exist")
    if docs["marked_superseded"]:
        print(f"- {len(docs['marked_superseded'])} superseded document(s) still linked as current material")
    print("RESULT: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
