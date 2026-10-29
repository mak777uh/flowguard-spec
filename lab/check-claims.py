#!/usr/bin/env python3
"""Claim linter — enforces the rule behind docs/CLAIMS.md:
a claim may not be worded more strongly than its evidence type permits,
and the artifacts it cites must be traceable.

Structural problems (bad type, duplicate id, dangling claim reference) are errors.
A cited artifact that does not exist yet is a warning: the repository is pre-code,
and a warning here is the to-do list, not a lie.

    python lab/check-claims.py            # warnings allowed, structural errors fail
    python lab/check-claims.py --strict   # missing artifacts also fail (pre-release)
"""
import pathlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ROOT / "docs" / "CLAIMS.md"
TYPES = {"proof", "test", "statistics", "observation", "judgment", "withdrawn", "not established", "false as stated"}
RESERVED = ("PROVEN", "ENFORCED_TESTED", "guarantee")
ROW = re.compile(r"^\|\s*(C-\d{2})\s*\|")
CLAIM_REF = re.compile(r"(?<!corpus )\bC-\d{2}\b")
ARTIFACT = re.compile(r"`([^`]+(?:/|\.md|\.json|\.ps1|\.sh|\.py)[^`]*)`")


NUMBER = re.compile(r"(?<![\w./-])(\d{2,6})(?![\w./-])")


def numbers_in(text: str) -> set[str]:
    """Counts a sentence can assert: two digits or more, not part of an identifier or a path."""
    return set(NUMBER.findall(text))


def artifact_text(paths: list[str]) -> set[str]:
    blob = []
    for rel in paths:
        candidate = pathlib.Path(rel)
        if not candidate.is_absolute():
            candidate = pathlib.Path(__file__).resolve().parent.parent / rel
        if candidate.is_file():
            try:
                blob.append(candidate.read_text(encoding="utf-8", errors="ignore"))
            except Exception:  # noqa: BLE001
                continue
    return numbers_in("\n".join(blob))

strict = "--strict" in sys.argv
errors, warnings = [], []

if not CLAIMS.exists():
    print(f"error: {CLAIMS} missing")
    sys.exit(1)

ids, rows = [], {}
for line in CLAIMS.read_text(encoding="utf-8").splitlines():
    m = ROW.match(line)
    if not m:
        continue
    cid = m.group(1)
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3:
        errors.append(f"{cid}: row has {len(cells)} cells, expected at least 3")
        continue
    ids.append(cid)
    claim_type = cells[2].strip("*` ").lower()
    rows[cid] = {"type": claim_type, "line": line}

# 1. types
for cid, r in rows.items():
    t = r["type"]
    if t not in TYPES and not any(t.startswith(x) for x in TYPES):
        errors.append(f"{cid}: unknown evidence type '{t}'")

# 1b. the wording ceiling, actually enforced.
# Until this existed the rule was stated in this file's docstring and in docs/CLAIMS.md and checked
# by nobody - the seventh "declared, not enforced" instance in this repository. VecDHT's note 2 asked
# for the wording to be DERIVED from the evidence type rather than written freely; this is that.
CEILING = {
    "proof":         {"reserved_ok": True},
    "test":          {"reserved_ok": True},
    # For weaker types the reserved words are forbidden outright in the wording column, with no
    # negation exception: "may not be called a guarantee" is a comment about the claim, and it
    # belongs in the refutation column, not in the sentence the claim is allowed to say.
    "statistics":    {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
    "observation":   {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
    "judgment":      {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
    "withdrawn":     {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
    "not established": {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
    "false as stated": {"reserved_ok": False, "deny": ["guaranteed", "always holds", "never fails"]},
}
wording_checked = 0
for cid, r in rows.items():
    cells = [c.strip() for c in r["line"].strip().strip("|").split("|")]
    if len(cells) < 4:
        errors.append(f"{cid}: no wording column, so the ceiling cannot be checked")
        continue
    wording = cells[3].strip("*` ")
    cur = wording.lower()
    wording_checked += 1
    rule = CEILING.get(r["type"], {"reserved_ok": False})
    for word in RESERVED:
        if word in cells[3] and not rule.get("reserved_ok"):
            errors.append(f"{cid}: wording uses the reserved word '{word}' while typed '{r['type']}'")
    for bad in rule.get("deny", []):
        if bad in cur:
            errors.append(f"{cid}: typed '{r['type']}' may not say '{bad}'")

# 2. duplicate ids
for cid in {i for i in ids if ids.count(i) > 1}:
    errors.append(f"{cid}: duplicate id")

# 3. cited artifacts
cited = 0
for cid, r in rows.items():
    for path in ARTIFACT.findall(r["line"]):
        cited += 1
        target = ROOT / path
        if not target.exists():
            msg = f"{cid}: cites missing artifact {path}"
            (errors if strict else warnings).append(msg)

# 4. dangling claim references across docs
known = set(ids)
for md in list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md")):
    for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        for ref in CLAIM_REF.findall(line):
            if ref not in known:
                errors.append(f"{md.relative_to(ROOT)}:{lineno}: references unknown claim {ref}")

# 5. reserved words must be backed by a proof/test claim of the same document
reserved_hits = 0
surface = list((ROOT / "reports").glob("*.md")) if (ROOT / "reports").exists() else []
for md in surface:
    text = md.read_text(encoding="utf-8")
    for word in RESERVED:
        if word not in text:
            continue
        reserved_hits += 1
        if md.name in {"CLAIMS.md", "eliminations.md"}:
            continue
        if not CLAIM_REF.search(text):
            warnings.append(f"{md.relative_to(ROOT)}: uses reserved word '{word}' without citing a claim")

# 4b. the value, not only the ceiling (herness, 2026-10-29): every count of two or more digits in a claim's
# sentence must appear in the text of the artifacts it cites, or the document and its evidence disagree.
for _cid, row in rows.items():
    cells = [c.strip() for c in row["line"].strip().strip("|").split("|")]
    if len(cells) < 2:
        continue
    sentence, cited_files = cells[1], ARTIFACT.findall(row["line"])
    if not cited_files:
        continue
    claimed_numbers = numbers_in(sentence)
    if not claimed_numbers:
        continue
    missing = sorted(claimed_numbers - artifact_text(cited_files), key=int)
    if missing:
        errors.append(f"{cells[0]}: the sentence asserts {', '.join(missing)}, which appear in none of "
                      f"its artifacts ({', '.join(cited_files[:2])})")

print(f"claims: {len(ids)}  wording ceilings checked: {wording_checked}  artifacts cited: {cited}  reserved-word files: {reserved_hits}")
for w in warnings:
    print(f"warn  {w}")
for e in errors:
    print(f"ERROR {e}")
print("RESULT:", "fail" if errors else ("fail (strict)" if strict and warnings else "ok"))
sys.exit(1 if errors or (strict and warnings) else 0)
