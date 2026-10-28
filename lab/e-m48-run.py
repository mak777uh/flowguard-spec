"""Re-run the seven traceback cases and the schema check (E-M48)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tmp = Path(tempfile.mkdtemp())
claim = {"claim_id": "a", "target_lock": {"commit": "t"}, "declared_control_point": "c",
         "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0, "excluded": [],
         "not_claimed": ["NC-01", "NC-02"]}
inv = {"manifest_version": "inventory/0.1", "target_lock": "t", "independent_of_agent": True,
       "sources": [{"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers"}],
       "paths": []}
cp, ip = tmp / "c.json", tmp / "i.json"
cp.write_text(json.dumps(claim), encoding="utf-8")
ip.write_text(json.dumps(inv), encoding="utf-8")

cases = [
    ("policy is a list", [1, 2]),
    ("policy floor is text", {"trusted": True, "min_paths_for_level": {"PROVEN": "x"}}),
    ("policy density is text", {"trusted": True, "min_db_logic_density": "x"}),
]
bad = 0
for name, pol in cases:
    pp = tmp / "p.json"
    pp.write_text(json.dumps(pol), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "fg_verify.py"),
                        "--claim", str(cp), "--inventory", str(ip), "--policy", str(pp)],
                       capture_output=True, text=True)
    crashed = "Traceback" in (r.stderr or "")
    invalid = '"INVALID"' in r.stdout
    print(f"{name:26} crash={crashed} invalid={invalid} exit={r.returncode}")
    bad += 1 if crashed or not invalid else 0

print("crashes remaining:", bad)
sys.exit(1 if bad else 0)
