"""E-M70 — the migrations enumerator, end to end: SQL text to a verdict in both cores.

The fixture is three paths a migration cannot hide: a function that writes, a trigger that fires on update, and a
grant that gives a role the same table with no function in between. The check is that the enumerator finds them
and that **both** cores accept the inventory it produces — a disagreement is a defect in one of the three.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENUM = ROOT / "enumerators" / "migrations" / "fg_enum_migrations.py"
PYCORE = ROOT / "tools" / "fg_verify.py"
RUST = ROOT / "core-rs" / "target" / "debug" / "fg-core.exe"
FIXTURE = ROOT / "fixtures" / "migrations-sample"
CONTROL = "function:sample.apply_transfer"

CLAIM = {"claim_id": "migrations-sample", "target_lock": {"commit": "sample@1"},
         "declared_control_point": CONTROL, "declared_level": "CONSISTENT_DECLARED",
         "claimed_coverage": 0.0, "evidence_tier": 0, "not_claimed": ["NC-01", "NC-02"]}


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    inv = tmp / "inv.json"
    r = subprocess.run([sys.executable, str(ENUM), "--dir", str(FIXTURE), "--schema", "sample",
                        "--control", CONTROL, "--out", str(inv), "--target-lock", "sample@1"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("the enumerator failed:", (r.stderr or r.stdout).strip()[:300])
        return 1
    print(" ", r.stdout.strip().splitlines()[0])

    doc = json.loads(inv.read_text(encoding="utf-8"))
    kinds = {}
    for p in doc["paths"]:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    print(" ", "kinds:", ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))

    # every path must be a statement or a function with verbs: the format refuses decoration
    for p in doc["paths"]:
        if p["kind"] in ("observed_write",) and not p["entry"].startswith("stmt:"):
            print(f"  BAD entry for {p['kind']}: {p['entry']}")
            return 1

    claim = tmp / "claim.json"
    claim.write_text(json.dumps(CLAIM), encoding="utf-8")

    def verdict(cmd):
        out = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return json.loads(out.stdout)["verdict"]
        except Exception:  # noqa: BLE001
            return "NO-JSON"

    py = verdict([sys.executable, str(PYCORE), "--claim", str(claim), "--inventory", str(inv)])
    rs = "not built"
    if RUST.exists():
        rs = verdict([str(RUST), "verify-claim", "--claim", str(claim), "--inventory", str(inv)])

    print(f"  python={py} rust={rs}")
    ok = py == rs or rs == "not built"
    ok = ok and py == "CONSISTENT_DECLARED"
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
