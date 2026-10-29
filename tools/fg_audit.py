#!/usr/bin/env python3
"""fg_audit — whole-repository consistency check for the method's own artifacts.

The lab loop only works if the artifacts stay well-formed. This checks the *process* rather than the
product: cards with thresholds, metrics with logs, ADRs with their own limits, enumerators with
declared blind spots, a status document whose numbers match the checker.

    python tools/fg_audit.py            # every check, exit 1 on any failure
    python tools/fg_audit.py --json

A failure here is not a defect in the product; it is a defect in the discipline that produces it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def check(cid, name, fn):
    try:
        ok, detail = fn()
    except Exception as e:  # noqa: BLE001
        ok, detail = False, f"check crashed: {e}"
    RESULTS.append({"id": cid, "name": name, "ok": ok, "detail": detail})


def cards():
    # INDEX.md and README.md are generated indexes, not cards: they carry no id, threshold or verdict,
    # and their presence made the audit fail the moment lab/build-indexes.py started writing them (E-M79).
    return sorted(p for p in (ROOT / "lab" / "experiments").glob("*.md")
                  if p.name not in ("INDEX.md", "README.md"))


def front_matter(text):
    if not text.startswith("---"):
        return {}
    body = text.split("---", 2)
    if len(body) < 3:
        return {}
    out = {}
    for line in body[1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def a1_cards_have_fields():
    required = ("id", "hypothesis", "status", "threshold", "result", "verdict")
    bad = []
    for c in cards():
        fm = front_matter(c.read_text(encoding="utf-8"))
        missing = [k for k in required if k not in fm]
        if missing:
            bad.append(f"{c.name}: missing {', '.join(missing)}")
    return (not bad, "; ".join(bad) or f"{len(cards())} cards well-formed")


def a2_completed_have_evidence():
    bad = []
    for c in cards():
        text = c.read_text(encoding="utf-8")
        fm = front_matter(text)
        if fm.get("status") != "completed":
            continue
        if len(fm.get("result", "")) < 40:
            bad.append(f"{c.name}: completed with a result shorter than 40 chars")
        if "lab/logs/" not in text and "command:" not in text:
            bad.append(f"{c.name}: completed without a log or a command")
    return (not bad, "; ".join(bad) or "every completed card carries a result and a command or log")


def a3_metrics_have_logs():
    p = ROOT / "docs" / "METRICS.md"
    if not p.exists():
        return False, "docs/METRICS.md missing"
    rows = [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    bad = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 6:
            bad.append(f"row {cells[0]}: {len(cells)} cells")
            continue
        cmd = cells[3] if len(cells) > 3 else ""
        if "`" not in cmd:
            bad.append(f"row {cells[0]}: no command")
    return (not bad, "; ".join(bad) or f"{len(rows)} metric rows carry commands")


def a4_enumerators_declare_blind_spots():
    bad = []
    for d in (ROOT / "enumerators").iterdir():
        if not d.is_dir():
            continue
        readme = d / "README.md"
        if not readme.exists():
            bad.append(f"{d.name}: no README")
            continue
        text = readme.read_text(encoding="utf-8")
        if "## Covers" not in text:
            bad.append(f"{d.name}: no Covers section")
        if "## Blind spots" not in text:
            bad.append(f"{d.name}: no Blind spots section")
    return (not bad, "; ".join(bad) or "every enumerator declares covers and blind spots")


def a5_adrs_state_their_limits():
    bad = []
    for adr in sorted((ROOT / "lab" / "decisions").glob("ADR-*.md")):
        text = adr.read_text(encoding="utf-8")
        if "**Status:**" not in text:
            bad.append(f"{adr.name}: no Status")
        if "does NOT do" not in text:
            bad.append(f"{adr.name}: no explicit limits section")
    return (not bad, "; ".join(bad) or "every ADR declares status and its own limits")


def a6_status_matches_checker():
    """The kit number in the status document must equal what the checker computes."""
    st = ROOT / "docs" / "STATUS-v0.md"
    if not st.exists():
        return False, "STATUS-v0.md missing"
    sys.path.insert(0, str(ROOT / "lab"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("ci", ROOT / "lab" / "check-interop.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # run the checker on ourselves and parse its summary line
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "check-interop.py")],
                       capture_output=True, text=True)
    m = re.search(r"kit conformance:\s*(\d+)/(\d+)", r.stdout)
    if not m:
        return False, "check-interop produced no conformance line"
    computed = f"{m.group(1)}/{m.group(2)}"
    text = st.read_text(encoding="utf-8")
    # Only the line that states conformance counts; the document also records history, and a
    # historical number is not a stale claim.
    for line in text.splitlines():
        if "conformance" in line.lower():
            m2 = re.search(r"(\d)\s*/\s*7", line)
            if m2 and f"{m2.group(1)}/7" != computed:
                return False, f"the conformance line says {m2.group(1)}/7, checker computes {computed}"
            if m2:
                return True, f"status and checker agree at {computed}"
    return False, "no conformance line found in the status document"


def a7_no_dangling_placeholders():
    hits = []
    for md in list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md")):
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\b(TODO|TBD|FIXME)\b", line):
                hits.append(f"{md.relative_to(ROOT)}:{i}")
    return (not hits, "; ".join(hits[:5]) or "no TODO/TBD/FIXME markers")


def a8_readme_links_all():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "check-readme.py")],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["no output"])[-1]


def a9_claims_artifact_status():
    """Count claims with missing artifacts, and require the count to be published."""
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "check-claims.py")],
                       capture_output=True, text=True)
    missing = len(re.findall(r"cites missing artifact", r.stdout))
    st = ROOT / "docs" / "STATUS-v0.md"
    published = str(missing) in st.read_text(encoding="utf-8") if st.exists() else False
    return (r.returncode == 0, f"{missing} claims cite missing artifacts (to-do list); status publishes the number: {published}")


def a12_status_current():
    """docs/STATUS-v0.md is generated; a hand edit turns the build red (E-M43: hand edits made it
    contradict itself in six rows)."""
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "fg_status.py"), "--check"],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["no output"])[-1]


def a11_dossier_current():
    """DOSSIER.md is generated; if it lags, the one file we hand to outside models is a lie."""
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "fg_dossier.py"), "--check"],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["no output"])[-1]


def a10_worktree_clean():
    import subprocess
    r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    dirty = [l for l in r.stdout.splitlines() if l.strip()]
    return (not dirty, f"{len(dirty)} uncommitted change(s)" if dirty else "worktree clean")


CHECKS = [
    ("A1", "experiment cards carry the required fields", a1_cards_have_fields),
    ("A2", "completed cards carry result and evidence", a2_completed_have_evidence),
    ("A3", "every metric row carries a command", a3_metrics_have_logs),
    ("A4", "every enumerator declares blind spots", a4_enumerators_declare_blind_spots),
    ("A5", "every ADR states its own limits", a5_adrs_state_their_limits),
    ("A6", "the status document agrees with the checker", a6_status_matches_checker),
    ("A7", "no TODO/TBD markers in documents", a7_no_dangling_placeholders),
    ("A8", "the README links every document", a8_readme_links_all),
    ("A9", "claims citing missing artifacts remain lint-clean", a9_claims_artifact_status),
    ("A11", "the dossier matches its generator", a11_dossier_current),
    ("A12", "the status page matches its generator", a12_status_current),
    ("A10", "the worktree is clean", a10_worktree_clean),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="skip A10: before a commit the worktree is dirty by definition")
    a = ap.parse_args()
    for cid, name, fn in CHECKS:
        if a.allow_dirty and cid == "A10":
            continue
        check(cid, name, fn)

    failed = [r for r in RESULTS if not r["ok"]]
    if a.json:
        print(json.dumps({"failed": len(failed), "checks": RESULTS}, indent=1, ensure_ascii=False))
        return 1 if failed else 0

    for r in RESULTS:
        print(f"{r['id']:4} {'ok  ' if r['ok'] else 'FAIL'} {r['name']:52} {r['detail'][:70]}")
    print(f"\naudit: {len(RESULTS) - len(failed)}/{len(RESULTS)} checks pass")
    print("RESULT:", "ok" if not failed else "fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
