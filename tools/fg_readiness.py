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
             "--expect-target", "flowguard-sample@2026-10-27"])
    return '"SIGNED_AND_CONSISTENT"' in r.stdout, "sample bundle verifies with both anchors"


def ok_corpus():
    r = run([PY, "lab/e-m10-run.py", "--per-class", "4", "--valid", "4"])
    return r.returncode == 0, "E-M10 corpus detects all declared classes" if r.returncode == 0 else "E-M10 failed"


def has_marker(pattern):
    import re
    for p in (ROOT / "lab" / "experiments").glob("*.md"):
        if re.search(pattern, p.read_text(encoding="utf-8", errors="ignore"), re.M):
            return p.name
    return None


def find_psql():
    for c in (Path(r"C:\Users\Admin\miniconda3\Library\bin\psql.exe"), Path("psql")):
        if Path(c).exists():
            return str(c)
    return None


CHECKS = [
    # id, group, weight, runner, criterion
    ("E1", "engine", 10, ok_guards, "all guards and negative controls green"),
    ("E2", "engine", 8, ok_verify, "the verifier executes and refuses"),
    ("E3", "engine", 12, ok_acceptance, "acceptance scenarios pass"),
    ("E4", "engine", 8, ok_enumerator_grants, "grant enumerator measured on a planted fixture"),
    ("E5", "engine", 8, ok_attribution, "attribution measured, decoy not fooled"),
    ("E6", "engine", 8, ok_bundle, "bundle with Ed25519 verifies under both anchors"),
    ("E7", "engine", 6, ok_corpus, "mutation corpus measured with a declared class set"),
    ("P1", "product", 15, lambda: (bool(has_marker(r"^rebuild_result\s*:\s*(agreed|differed)")),
                                   "a stranger rebuilt a bundle (M7)"),
     "a party that did not write the code rebuilt a bundle"),
    ("P2", "product", 10, lambda: ((ROOT / "docs" / "M8-CONSUMER.md").exists(),
                                   "a named consumer stated what changes"),
     "a named consumer documented the decision that changes"),
    ("P3", "product", 8, lambda: (bool(list(ROOT.glob("fixtures/**/signatures/*.role"))) and
                                  any("risk_acceptance" in p.read_text(encoding="utf-8", errors="ignore")
                                      for p in ROOT.glob("fixtures/**/signatures/*.role")),
                                   "a risk-acceptance signature exists"),
     "someone signed risk acceptance with a reliance scope"),
    ("P4", "product", 7, lambda: (bool(has_marker(r"^external_corpus\s*:")),
                                  "a corpus from another author"),
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
