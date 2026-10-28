#!/usr/bin/env python3
"""fg_status — generate docs/STATUS-v0.md from the tools that measure the repository.

The status file was edited by hand for weeks and accumulated contradictions a hostile reviewer could
list: "M1 absent" and "M1 present" in one file, 84 links against 122, "three guards" against six CI
steps, a 7/7 headline beside a table that said 5/7. Every one of those came from editing a row and not
the rest of the page (E-M43, E-M44).

A status page is a derived artifact. This generates it, and fails the build when it is stale.

    python tools/fg_status.py            # write docs/STATUS-v0.md
    python tools/fg_status.py --check    # exit 1 if the file disagrees with the tools
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "STATUS-v0.md"


def run(cmd, timeout=900):
    try:
        # Child output is UTF-8; without this, the em dash in the readiness line decodes to mojibake
        # and the tier regex silently fails (found while generating this page the first time).
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                              encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        class R:
            returncode = 1
            stdout = ""
            stderr = str(e)
        return R()


def kit():
    r = run([sys.executable, "lab/check-interop.py"])
    rows, total = [], None
    for line in r.stdout.splitlines():
        m = re.match(r"^(M\d)\s+(.+?)\s{2,}(present|absent)\s+(.*)$", line)
        if m:
            rows.append((m.group(1), m.group(2).strip(), m.group(3), m.group(4).strip()))
        m2 = re.search(r"kit conformance:\s*(\d+)/(\d+)", line)
        if m2:
            total = f"{m2.group(1)}/{m2.group(2)}"
    return rows, total or "?"


def readiness():
    r = run([sys.executable, "tools/fg_readiness.py"])
    out = r.stdout
    pct = re.search(r"core \(engine\): (\d+)%\s+product: (\d+)%\s+overall: (\d+)%", out)
    tier = re.search(r"(?m)^tier:\s*(T\d)\s*[—–-]\s*(.+)$", out)
    nxt = re.search(r"next tier (T\d) \((.+?)\) blocked by: (.+)", out)
    checks = []
    for line in out.splitlines():
        m = re.match(r"^([EP]\d)\s+(engine|product)\s+(\d+)\s+(\d+)\s+(.+?)\s{2,}(OK|—)", line)
        if m:
            checks.append((m.group(1), m.group(5).strip(), m.group(4), m.group(3)))
    return {
        "engine": pct.group(1) if pct else "?",
        "product": pct.group(2) if pct else "?",
        "overall": pct.group(3) if pct else "?",
        "tier": tier.group(1) if tier else "?",
        "tier_name": tier.group(2).strip() if tier else "?",
        "next": (nxt.group(1), nxt.group(2), nxt.group(3)) if nxt else None,
        "checks": checks,
    }


def counts():
    metrics = [l for l in (ROOT / "docs" / "METRICS.md").read_text(encoding="utf-8").splitlines()
               if re.match(r"^\|\s*\d+\s*\|", l)]
    cards = list((ROOT / "lab" / "experiments").glob("*.md"))
    verdicts = {}
    for c in cards:
        t = c.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^verdict:\s*(\S+)", t, re.M)
        if m:
            verdicts[m.group(1)] = verdicts.get(m.group(1), 0) + 1
    adrs = list((ROOT / "lab" / "decisions").glob("ADR-*.md"))
    links = run([sys.executable, "lab/check-links.py"]).stdout
    m = re.search(r"links checked: (\d+), broken: (\d+)", links)
    return {
        "metrics": len(metrics),
        "cards": len(cards),
        "verdicts": verdicts,
        "adrs": len(adrs),
        "links": (m.group(1), m.group(2)) if m else ("?", "?"),
        "commit": run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
    }


def open_items():
    """Open findings named by the most recent experiment cards."""
    items = []
    for card in sorted((ROOT / "lab" / "experiments").glob("*.md"))[-3:]:
        t = card.read_text(encoding="utf-8", errors="ignore")
        block = re.search(r"## Still open[^\n]*\n(.*?)(\n## |\Z)", t, re.S)
        if not block:
            continue
        for line in block.group(1).splitlines():
            line = line.strip()
            if line.startswith("- **"):
                items.append((card.name.split("-")[0], line[2:]))
    return items


def build() -> str:
    rows, kit_total = kit()
    r = readiness()
    c = counts()
    openers = open_items()
    stamp = run(["git", "log", "-1", "--format=%cI"]).stdout.strip()[:16].replace("T", " ") + " UTC"

    L = []
    A = L.append
    A("# STATUS — generated, not edited")
    A("")
    A(f"*Produced by `python tools/fg_status.py` at {stamp} from commit `{c['commit']}`. Editing this file by")
    A("hand is what produced the contradictions a reviewer found (M1 absent and present in one page, 84 links")
    A("against 122, three guards against six CI steps). Regenerate it instead; the build fails when it is stale.*")
    A("")
    A("## Where it stands")
    A("")
    A("```")
    A(f"engine (the tool)     {r['engine']}%")
    A(f"product (reliance)    {r['product']}%")
    A(f"overall               {r['overall']}%")
    A(f"tier                  {r['tier']} — {r['tier_name']}")
    if r["next"]:
        A(f"next tier             {r['next'][0]} ({r['next'][1]}), blocked by {r['next'][2]}")
    A("```")
    A("")
    A("The product half is zero because nobody outside has confirmed a finding, rebuilt the bundle as a")
    A("third party, or signed an acceptance. That is not modesty, it is the measured state.")
    A("")
    A("## What exists, counted")
    A("")
    A(f"| artifacts | count |")
    A(f"|---|---|")
    A(f"| metric rows, each with a command | {c['metrics']} |")
    A(f"| experiment cards | {c['cards']} ({', '.join(f'{k} {v}' for k, v in sorted(c['verdicts'].items()))}) |")
    A(f"| decisions | {c['adrs']} |")
    A(f"| markdown links checked | {c['links'][0]}, broken {c['links'][1]} |")
    A("")
    A("## Method kit")
    A("")
    A(f"Conformance measured by `lab/check-interop.py`: **{kit_total}**")
    A("")
    A("| item | state | evidence |")
    A("|---|---|---|")
    for mid, name, state, detail in rows:
        A(f"| {mid} {name} | {state} | {detail[:90]} |")
    A("")
    A("## Readiness checks")
    A("")
    A("| check | what it verifies | earned / weight |")
    A("|---|---|---|")
    for cid, name, got, wt in r["checks"]:
        A(f"| {cid} | {name[:80]} | {got} / {wt} |")
    A("")
    if openers:
        A("## Open findings, from the cards")
        A("")
        for card_id, line in openers:
            A(f"- {card_id}: {line}")
        A("")
    A("## What this page is not")
    A("")
    A("- Not a claim of security. Every verdict carries `NC-01`…`NC-11`; the vocabulary is in")
    A("  [NOT-CLAIMED.md](NOT-CLAIMED.md) and the verifier refuses a claim that omits its required codes.")
    A("- Not a review. Reviews come from outside: [the exchange protocol](../interop/REVIEW-EXCHANGE.md) and")
    A("  [the ledger](../interop/reviews/LEDGER.md).")
    A("- Not written by hand. `python tools/fg_status.py --check` fails when this file and the tools disagree.")
    A("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = build()
    if a.check:
        def _body(s):
            # The stamp names the commit the page was generated from, so the file is always one commit
            # behind itself. Compare content, not the stamp: the content is what must not drift.
            return re.sub(r"\*Produced by [^*]*\*", "STAMP", s, count=1)

        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if _body(current) != _body(text):
            print("STATUS-v0.md is stale — run python tools/fg_status.py")
            return 1
        print("STATUS-v0.md is current")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
