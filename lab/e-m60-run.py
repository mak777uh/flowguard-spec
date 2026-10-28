"""Verify the cross-family findings mechanically (E-M60)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = ROOT / "tools" / "fg_verify.py"
tmp = Path(tempfile.mkdtemp())

CLAIM = {"claim_id": "x", "target_lock": {"commit": "t@1"},
         "declared_control_point": "function:bank.transfer", "declared_level": "PROVEN",
         "claimed_coverage": 1.0, "evidence_tier": 2,
         "not_claimed": ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10", "NC-11"]}
FV = {"schema": "s", "owner_confirmed": True, "verdict": "confirmed",
      "owner": {"name": "A", "role": "b", "how_contacted": "c", "date": "d"},
      "owner_statement": "confirmed the findings",
      "finding": {"path_id": "wp_001", "claim": "x"}}


def paths(n=8, control="function:bank.transfer", kind="privilege", extra=None):
    rows = []
    for i in range(1, n + 1):
        rows.append({"path_id": f"wp_{i:03d}", "entry": f"table:app.t{i}", "kind": kind,
                     "attribution": {"to": control, "method": "direct", "sources": ["s"]}})
    if extra:
        rows.append(extra)
    return rows


def run(name, claim, inv, report=None, raw=False):
    cp, ip = tmp / f"{name}.claim.json", tmp / f"{name}.inv.json"
    cp.write_text(json.dumps(claim), encoding="utf-8")
    ip.write_text(inv if raw else json.dumps(inv), encoding="utf-8")
    cmd = [sys.executable, str(V), "--claim", str(cp), "--inventory", str(ip)]
    if report is not None:
        rp = tmp / f"{name}.report.json"
        rp.write_text(json.dumps(report), encoding="utf-8")
        cmd += ["--report", str(rp)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
        return out["verdict"], [e["code"] for e in out.get("errors", [])]
    except Exception:
        return "NO-JSON", (r.stderr or "")[:80]


base_src = {"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers",
            "db_logic_density": 0.9}

cases = []

# 1. glm: NaN density, written as raw JSON (json.dumps would emit NaN too)
inv_nan = ('{"manifest_version":"inventory/0.1","target_lock":"t@1","independent_of_agent":true,'
           '"sources":[{"source_id":"s","kind":"grants","db_logic_density":NaN}],'
           '"foreign_validation":' + json.dumps([FV]) + ',"paths":' + json.dumps(paths()) + '}')
cases.append(("NaN density", CLAIM, inv_nan, None, True))

# 2. glm: report denominator double counts -> honest report refused, lying accepted
claim8 = dict(CLAIM)
claim8["declared_level"] = "SCOPED_ASSURANCE"
claim8["claimed_coverage"] = 0.875
p8 = paths(8)
p8[7]["attribution"] = {"to": "function:other", "method": "direct", "sources": ["s"]}
inv8 = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
        "sources": [base_src], "foreign_validation": [FV], "paths": p8}
cases.append(("report honest 0.875", claim8, inv8, {"coverage": 0.875, "analysed_paths": []}, False))
cases.append(("report lying 0.78", claim8, inv8, {"coverage": 0.78, "analysed_paths": []}, False))

# 3. qwen: completeness_claim "sampled"
inv_s = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
         "sources": [dict(base_src, completeness_claim="sampled")],
         "foreign_validation": [FV], "paths": paths()}
cases.append(("completeness_claim sampled", CLAIM, inv_s, None, False))

# 4. mimo: perimeter_growth false but delta shows unpublished growth
inv_g = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
         "perimeter_growth": False,
         "delta_since_previous": {"new_paths": 3, "vanished_paths": 0, "net_change": 3, "published": False},
         "sources": [base_src], "foreign_validation": [FV], "paths": paths()}
cases.append(("growth false + delta +3", CLAIM, inv_g, None, False))

# 5. haiku: vanished as the string "false"
p_v = paths()
for row in p_v[:7]:
    row["vanished"] = "false"
inv_v = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
         "sources": [base_src], "foreign_validation": [FV], "paths": p_v}
cases.append(("vanished as string", CLAIM, inv_v, None, False))

# 6. qwen: observed non-verb CALL
extra = {"path_id": "wp_999", "entry": "stmt:CALL sp_x", "kind": "observed_write",
         "attribution": {"to": "function:bank.transfer", "method": "direct", "sources": ["s"]}}
inv_c = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
         "sources": [base_src], "foreign_validation": [FV], "paths": paths(extra=extra)}
cases.append(("observed stmt:CALL", CLAIM, inv_c, None, False))

# the honest report case MUST stay accepted: it is the control that the check is not inverted
MUST_PASS = {"report honest 0.875"}
bad = 0
for name, claim, inv, report, raw in cases:
    verdict, codes = run(name.replace(" ", "_").replace("/", "_"), claim, inv, report, raw)
    strong = verdict in ("PROVEN", "SCOPED_ASSURANCE")
    if name in MUST_PASS:
        ok = strong
        label = "MUST PASS" if ok else "REFUSED HONEST"
    else:
        ok = not strong
        label = "blocked" if ok else "BREAK"
    bad += 0 if ok else 1
    print(f"{name:32} {verdict:20} {label:14} {codes[:3]}")
print("RESULT:", "PASS" if not bad else "FAIL")
sys.exit(0 if not bad else 1)
