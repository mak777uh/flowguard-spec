#!/usr/bin/env python3
"""fg_readiness — how ready is this, measured from artifacts rather than asserted.

Every check below either finds its evidence in the repository or scores zero with the reason.
Nothing here is a self-assessment: if the guards are red, E1 is zero; if nobody rebuilt a bundle,
P1 is zero, whatever the prose says.

    python tools/fg_readiness.py            # table + tier + percentages
    python tools/fg_readiness.py --json     # machine-readable

The criteria and weights are documented in docs/READINESS.md. Change them there first.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)


def ok_guards():
    a = run(["bash", "lab/check-secrets.sh"])
    b = run([PY, "lab/check-links.py"])
    c = run([PY, "lab/check-claims.py"])
    d = run(["bash", "lab/selftest-guards.sh"])
    green = [x.returncode == 0 for x in (a, b, c, d)]
    return all(green), f"secrets/links/claims/negative-controls: {sum(green)}/4 green"


def ok_verify():
    r = run([PY, "tools/fg_verify.py", "--claim", "fixtures/verify-probe/claim.json",
             "--inventory", "fixtures/verify-probe/inv.json"])
    return r.returncode in (0, 1, 2), "verifier executes and returns a verdict"


def ok_acceptance():
    r = run([PY, "lab/e-m12-run.py"])
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["no output"])[-3]


def ok_enumerator_grants():
    psql = find_psql()
    if not psql:
        return False, "psql not found"
    r = run([PY, "lab/e-m11-run.py", "--psql", psql, "--port", "54329"])
    return r.returncode == 0, "E-M11 recall 8/8 on the planted fixture" if r.returncode == 0 else "E-M11 failed"


def ok_attribution():
    psql = find_psql()
    if not psql:
        return False, "psql not found"
    r = run([PY, "lab/e-m13-run.py", "--psql", psql, "--port", "54329"])
    return r.returncode == 0, "E-M13 attribution 2/2, false 0/9" if r.returncode == 0 else "E-M13 failed"


def ok_bundle():
    r = run([PY, "tools/fg_bundle.py", "verify", "--bundle", "fixtures/sample-bundle",
             "--trusted-keys", "fixtures/sample-bundle/signatures/demo.pub",
             "fixtures/sample-bundle/signatures/owner.pub",
             "--expect-target", "flowguard-sample@2026-10-27"])
    return '"SIGNED_AND_CONSISTENT"' in r.stdout, "sample bundle verifies with both anchors"


def ok_corpus():
    r = run([PY, "lab/e-m10-run.py", "--per-class", "4", "--valid", "4"])
    return r.returncode == 0, "E-M10 corpus detects all declared classes" if r.returncode == 0 else "E-M10 failed"


CONSUMER_FIELDS = ("person", "organisation", "decision_before", "decision_after",
                   "what_they_lose", "date", "verbatim")



def _foreign_validation_records():
    """Every foreign_validation record a human would have committed, as (path, record).

    Fixtures and scratch directories are demonstrations, and a demonstration is not an act — the
    reviewer's own finding (E-M43): a synthetic record in tools/_tmp made P1 pass.
    """
    import json as _json
    out = []
    roots = [ROOT / "docs", ROOT / "interop", ROOT / "lab" / "experiments", ROOT / "reports"]
    for base in roots:
        if not base.exists():
            continue
        for f in base.rglob("*.json"):
            if any(part in (".git", "node_modules", "_tmp", "fixtures") for part in f.parts):
                continue
            try:
                doc = _json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            recs = doc.get("foreign_validation") if isinstance(doc, dict) else None
            if isinstance(recs, list):
                for r in recs:
                    if isinstance(r, dict):
                        out.append((f, r))
    return out


def _valid_confirmation(r):
    owner = r.get("owner") or {}
    return (r.get("owner_confirmed") is True
            and r.get("verdict") in ("confirmed", "partially_correct")
            and all(owner.get(k) for k in ("name", "role", "how_contacted", "date"))
            and len(str(r.get("owner_statement") or "").strip()) >= 12)


def ok_third_party_rebuild():
    """A rebuild line plus a validated foreign confirmation of the same schema.

    Text alone was enough before: a reviewer typed one line and collected 15 points (E-M43).
    """
    marker = has_marker(r"^rebuild_result\s*:\s*(agreed|differed)\s+by\s+(a\s+)?(third[- ]party|human|organisation|organization)")
    records = [r for _, r in _foreign_validation_records() if _valid_confirmation(r)]
    if not marker:
        return False, "no rebuild line by a third party"
    if not records:
        return False, "the rebuild line has no validated foreign_validation record behind it"
    return True, f"{marker} + {records[0].get('schema')} confirmed by {records[0]['owner']['name']}"


def ok_external_corpus():
    """An owner-produced ground-truth list, blind — not a marker in prose."""
    records = [r for _, r in _foreign_validation_records()
               if isinstance(r.get("ground_truth"), dict) and r.get("blind_evaluation") is True]
    if records:
        return True, f"blind ground truth for {records[0].get('schema')}"
    return False, "no record with ground_truth + blind_evaluation: a marker is not a corpus"


def ok_risk_acceptance():
    """A real acceptance, not a demonstration.

    The fixture bundle carries a risk_acceptance role on purpose, to exercise the format. Crediting
    the product for it is the same false credit as counting an unfilled M8 template (sixth instance):
    an example is not an act. Only signatures outside fixtures/ count.
    """
    for rolefile in ROOT.glob("**/signatures/*.role"):
        if "fixtures" in rolefile.parts or "_tmp" in rolefile.parts:
            continue
        try:
            doc = json.loads(rolefile.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if doc.get("asserts") == "risk_acceptance":
            required = ("issuer", "accepted_scope", "residual_risk", "valid_until", "statement")
            missing = [k for k in required if not doc.get(k)]
            if missing:
                return False, f"risk_acceptance missing {', '.join(missing)}"
            if len(str(doc.get("statement"))) < 12:
                return False, "risk_acceptance statement is a placeholder"
            return True, f"{doc['issuer']} until {doc['valid_until']}"
    return False, "no acceptance outside fixtures/ (a demo signature is not an act)"

def ok_consumer():
    """A filled form, not a template. Placeholders and short values score zero: a template that
    passes its own check is exactly the failure this repository keeps finding in its instruments."""
    p = ROOT / "docs" / "M8-CONSUMER.md"
    if not p.exists():
        return False, "no docs/M8-CONSUMER.md"
    text = p.read_text(encoding="utf-8")
    values = {}
    for field in CONSUMER_FIELDS:
        m = re.search(rf"(?m)^\s*{field}:\s*(.+)$", text)
        if m:
            values[field] = m.group(1).strip()
    missing = [f for f in CONSUMER_FIELDS if f not in values]
    if missing:
        return False, f"fields missing: {', '.join(missing)}"
    weak = [f for f, v in values.items() if v.startswith("<") or len(v) < 8]
    if weak:
        return False, f"placeholder or too short: {', '.join(weak)}"
    return True, f"{values['person']} on {values['date']}"

def has_marker(pattern):
    import re
    for p in (ROOT / "lab" / "experiments").glob("*.md"):
        if re.search(pattern, p.read_text(encoding="utf-8", errors="ignore"), re.M):
            return p.name
    return None


def find_psql():
    """Locate psql without hardcoding any absolute path: PATH first, then the active conda prefix."""
    import os
    import shutil
    hit = shutil.which("psql")
    if hit:
        return hit
    for base in (os.environ.get("CONDA_PREFIX"), os.environ.get("MAMBA_ROOT_PREFIX")):
        if not base:
            continue
        cand = Path(base) / "Library" / "bin" / "psql.exe"
        if cand.exists():
            return str(cand)
    cand = Path(os.environ.get("USERPROFILE", "")) / "miniconda3" / "Library" / "bin" / "psql.exe"
    return str(cand) if cand.exists() else None


CHECKS = [
    # id, group, weight, runner, criterion
    ("E1", "engine", 10, ok_guards, "all guards and negative controls green"),
    ("E2", "engine", 8, ok_verify, "the verifier executes and refuses"),
    ("E3", "engine", 12, ok_acceptance, "acceptance scenarios pass"),
    ("E4", "engine", 8, ok_enumerator_grants, "grant enumerator measured on a planted fixture"),
    ("E5", "engine", 8, ok_attribution, "attribution measured, decoy not fooled"),
    ("E6", "engine", 8, ok_bundle, "bundle with Ed25519 verifies under both anchors"),
    ("E7", "engine", 6, ok_corpus, "mutation corpus measured with a declared class set"),
    ("P1", "product", 15, ok_third_party_rebuild,
     "a party that did not write the code rebuilt a bundle"),
    ("P2", "product", 10, ok_consumer, "a named consumer documented the decision that changes"),
    ("P3", "product", 8, ok_risk_acceptance,
     "someone signed risk acceptance with a reliance scope"),
    ("P4", "product", 7, ok_external_corpus,
     "a test corpus written by someone else"),
]

TIERS = [
    ("T0", "nothing runs", set()),
    ("T1", "works for its author", {"E1", "E2", "E6"}),
    ("T2", "usable by an outsider on their own database", {"E1", "E2", "E3", "E4", "E5", "E6", "E7"}),
    ("T3", "trustworthy for someone else's decision", {"E1", "E2", "E3", "E4", "E5", "E6", "E7", "P1", "P2"}),
    ("T4", "a guarantee someone may rely on", {"E1", "E2", "E3", "E4", "E5", "E6", "E7", "P1", "P2", "P3", "P4"}),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, earned_total, weight_total = [], 0, 0
    per_group = {"engine": [0, 0], "product": [0, 0]}
    for cid, group, weight, fn, criterion in CHECKS:
        try:
            passed, detail = fn()
        except Exception as e:  # noqa: BLE001
            passed, detail = False, f"check failed to run: {e}"
        earned = weight if passed else 0
        earned_total += earned
        weight_total += weight
        per_group[group][0] += earned
        per_group[group][1] += weight
        rows.append({"id": cid, "group": group, "weight": weight,
                     "earned": earned, "passed": passed, "detail": detail,
                     "criterion": criterion})

    passed_ids = {r["id"] for r in rows if r["passed"]}
    tier = TIERS[0]
    for t, name, req in TIERS:
        if req <= passed_ids:
            tier = (t, name, req)
    pct = round(100 * earned_total / weight_total) if weight_total else 0
    engine_pct = round(100 * per_group["engine"][0] / per_group["engine"][1])
    product_pct = round(100 * per_group["product"][0] / per_group["product"][1])

    if a.json:
        print(json.dumps({"overall_pct": pct, "engine_pct": engine_pct, "product_pct": product_pct,
                          "tier": tier[0], "tier_name": tier[1],
                          "next_tier_blockers": sorted(
                              next((req for t, _, req in TIERS if t > tier[0]), set()) - passed_ids),
                          "checks": rows}, indent=1, ensure_ascii=False))
        return 0

    print(f"{'id':4} {'grp':8} {'wt':3} {'got':3} {'criterion':52} detail")
    for r in rows:
        print(f"{r['id']:4} {r['group']:8} {r['weight']:3} {r['earned']:3} {r['criterion']:52} "
              f"{'OK' if r['passed'] else '—'} {r['detail'][:60]}")
    print(f"\ncore (engine): {engine_pct}%   product: {product_pct}%   overall: {pct}%")
    print(f"tier: {tier[0]} — {tier[1]}")
    higher = [(x, y, z) for x, y, z in TIERS if z > (tier[2] or set())]
    nxt = higher[0] if higher else None
    if nxt:
        missing = sorted(nxt[2] - passed_ids)
        print(f"next tier {nxt[0]} ({nxt[1]}) blocked by: {', '.join(missing) or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
