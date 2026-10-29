#!/usr/bin/env python3
"""claims-map — the M3 dimension: every claim tied to an evidence type and a witness.

The other side calls this M3 and marks us `partial`: our claims registry ties a claim to a wording
ceiling, but not to the kind of evidence behind it. Without that dimension a sentence grows faster than
what supports it, because nothing checks the two against each other.

Here the evidence type is **derived**, not typed:

    proof-like      a card whose verdict is `supports` AND which names a captured log
    measured        a card whose verdict is `supports`
    refuted         a card whose verdict is `refutes` (the claim may only cite it as a refutation)
    assertion       no card at all - the claim rests on prose

and the strongest allowed wording follows from the type:

    proof-like -> "proven", "verified", "guaranteed"
    measured   -> "measured", "shown", numbers
    refuted    -> only "refuted", "failed", "does not hold"
    assertion  -> no strong word at all

    python lab/claims-map.py            # exit 1 when a claim outruns its evidence
    python lab/claims-map.py --table    # print the derived map
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "lab" / "experiments"
CLAIMS = ROOT / "docs" / "CLAIMS.md"

STRONG = ("proven", "verified", "guaranteed", "proof", "guarantee")
MEDIUM = ("measured", "shown", "demonstrated")
REFUTE_ONLY = ("refuted", "failed", "does not hold", "contradicted")

CEILING = {"proof-like": STRONG + MEDIUM, "measured": MEDIUM, "refuted": REFUTE_ONLY,
           "assertion": ()}


def cards():
    out = {}
    for f in sorted(CARDS.glob("*.md")):
        # INDEX.md and README.md are indexes, not cards: the generated index has no hyphen and crashed the
        # id parser the moment it appeared (found by the ritual, not by reading).
        if f.name in ("INDEX.md", "README.md") or "-" not in f.name:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^verdict:\s*(\S+)", text, re.M)
        has_log = bool(re.search(r"sha256\s+`[0-9a-f]{64}`|lab/logs/", text))
        cid = f.name.split("-")[0] + "-" + f.name.split("-")[1]
        out[cid] = (m.group(1) if m else "none", has_log)
    return out


def claims():
    """Rows of the claim registry: | C-01 | ... | type | wording | artifact |"""
    rows = []
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*C-\d+", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        rows.append(cells)
    return rows


def evidence_type(cells, known):
    # A withdrawn claim is not a claim: its sentence is the wording being retired, so the strong word
    # in it is the thing being taken back, not something asserted (E-M63).
    if "withdrawn" in " ".join(cells[2:4]).lower():
        return "withdrawn", []
    text = " ".join(cells)
    ids = re.findall(r"E-M\d+", text)
    found = [known[i] for i in ids if i in known]
    if any(v == "refutes" for v, _ in found):
        return "refuted", ids
    if any(v == "supports" and log for v, log in found):
        return "proof-like", ids
    if found:
        return "measured", ids
    return "assertion", ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()
    known = cards()
    rows = claims()
    problems = []
    print(f"{'claim':6} {'type':11} {'may say':34} artifact")
    for cells in rows:
        cid, text = cells[0], " ".join(cells[1:])
        etype, ids = evidence_type(cells, known)
        allowed = CEILING.get(etype, ())
        lowered = text.lower()
        used = [w for w in STRONG + MEDIUM if w in lowered]
        bad = [w for w in used if w not in allowed]
        if etype == "withdrawn":
            bad = []
        if bad:
            problems.append((cid, etype, bad))
        print(f"{cid:6} {etype:11} {', '.join(allowed)[:32] or '-':34} {','.join(ids) or '-'}")

    for cid, etype, bad in problems:
        print(f"  OUTRUNS: {cid} is {etype} but says {', '.join(bad)}")
    print(f"claims: {len(rows)}, outrunning their evidence: {len(problems)}")
    print("RESULT:", "ok" if not problems else "fail")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
