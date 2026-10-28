"""E-M69: the four divergences the cross-family attack found, as cases both cores must now refuse."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUST = ROOT / "core-rs" / "target" / "debug" / "fg-core.exe"
PYCORE = ROOT / "tools" / "fg_verify.py"
tmp = Path(tempfile.mkdtemp())

NC = ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10", "NC-11"]
FV = {"schema": "s", "owner_confirmed": True, "verdict": "confirmed",
      "owner": {"name": "A", "role": "b", "how_contacted": "c", "date": "d"},
      "owner_statement": "confirmed the findings",
      "finding": {"path_id": "wp_001", "claim": "x"}}


def claim(**over):
    doc = {"claim_id": "x", "target_lock": {"commit": "t@1"},
           "declared_control_point": "function:bank.transfer", "declared_level": "PROVEN",
           "claimed_coverage": 1.0, "evidence_tier": 2, "not_claimed": list(NC)}
    doc.update(over)
    return doc


def inv(**over):
    doc = {"manifest_version": "inventory/0.1", "target_lock": "t@1",
           "independent_of_agent": True,
           "sources": [{"source_id": "s", "kind": "static",
                        "completeness_claim": "exhaustive_within_covers",
                        "db_logic_density": 0.9}],
           "foreign_validation": [dict(FV)],
           "paths": [{"path_id": f"wp_{i:03}", "entry": f"table:app.t{i}", "kind": "privilege",
                      "attribution": {"to": "function:bank.transfer", "method": "direct",
                                      "sources": ["s"]}} for i in range(1, 9)]}
    doc.update(over)
    return doc


CASES = [
    ("invented NC-77 code", claim(not_claimed=NC + ["NC-77"]), inv(), False),
    ("excludes a covered path", claim(excluded=[{"path_id": "wp_001", "reason": "no caller",
                                                 "reason_code": "NOT_REACHABLE",
                                                 "evidence": {"source_id": "s"}}]), inv(), False),
    ("inventory is the agent's own word", claim(),
     inv(independent_of_agent=False,
         sources=[{"source_id": "s", "kind": "agent", "db_logic_density": 0.9}]), False),
    ("coverage below the floor", claim(),
     inv(paths=[{"path_id": f"wp_{i:03}", "entry": f"table:app.t{i}", "kind": "privilege",
                 "attribution": {"to": "function:other" if i > 2 else "function:bank.transfer",
                                 "sources": ["s"]}} for i in range(1, 9)]), False),
    ("clean control", claim(), inv(), True),
]


def run(which, c, i):
    cp, ip = tmp / "c.json", tmp / "i.json"
    cp.write_text(json.dumps(c), encoding="utf-8")
    ip.write_text(json.dumps(i), encoding="utf-8")
    if which == "python":
        cmd = [sys.executable, str(PYCORE), "--claim", str(cp), "--inventory", str(ip)]
    else:
        cmd = [str(RUST), "verify-claim", "--claim", str(cp), "--inventory", str(ip)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)["verdict"]
    except Exception:  # noqa: BLE001
        return "NO-JSON"


def main() -> int:
    if not RUST.exists():
        print("build the Rust core first")
        return 1
    bad = 0
    print(f"{'case':38} {'python':22} {'rust':22} ok")
    for name, c, i, expect_strong in CASES:
        py = run("python", c, i)
        rs = run("rust", c, i)
        strong_py = py in ("PROVEN", "SCOPED_ASSURANCE")
        strong_rs = rs in ("PROVEN", "SCOPED_ASSURANCE")
        ok = py == rs and strong_py == expect_strong and strong_rs == expect_strong
        bad += 0 if ok else 1
        print(f"{name:38} {py:22} {rs:22} {ok}")
    print(f"\ncases: {len(CASES)}, failures: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
