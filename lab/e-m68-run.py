"""E-M68: the Rust claim CLI against the Python verifier, on the six attack cases and a few controls."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUST_DIR = ROOT / "core-rs" / "target" / "debug"
# Platform-dependent name: fg-core.exe on Windows, fg-core on Linux CI.
RUST = RUST_DIR / ("fg-core.exe" if (RUST_DIR / "fg-core.exe").exists() else "fg-core")
PYCORE = ROOT / "tools" / "fg_verify.py"
tmp = Path(tempfile.mkdtemp())

NC_PROVEN = ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10", "NC-11"]


def claim(level="PROVEN", not_claimed=None, tier=2):
    return {"claim_id": "x", "target_lock": {"commit": "t@1"},
            "declared_control_point": "function:bank.transfer", "declared_level": level,
            "claimed_coverage": 1.0, "evidence_tier": tier,
            "not_claimed": NC_PROVEN if not_claimed is None else not_claimed}


def paths(n=8):
    return [{"path_id": f"wp_{i:03}", "entry": f"table:app.t{i}", "kind": "privilege",
             "attribution": {"to": "function:bank.transfer", "method": "direct", "sources": ["s"]}}
            for i in range(1, n + 1)]


BASE = {"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers",
        "db_logic_density": 0.9}


def inv(**over):
    doc = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
           "sources": [dict(BASE)], "paths": paths()}
    doc.update(over)
    return doc


FV = {"schema": "s", "owner_confirmed": True, "verdict": "confirmed",
      "owner": {"name": "A", "role": "b", "how_contacted": "c", "date": "d"},
      "owner_statement": "confirmed the findings",
      "finding": {"path_id": "wp_001", "claim": "x"}}


def run_py(c, i, r=None):
    cp, ip = tmp / "c.json", tmp / "i.json"
    cp.write_text(json.dumps(c), encoding="utf-8")
    ip.write_text(json.dumps(i), encoding="utf-8")
    cmd = [sys.executable, str(PYCORE), "--claim", str(cp), "--inventory", str(ip)]
    if r is not None:
        rp = tmp / "r.json"
        rp.write_text(json.dumps(r), encoding="utf-8")
        cmd += ["--report", str(rp)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)["verdict"]
    except Exception:  # noqa: BLE001
        return "NO-JSON"


def run_rs(c, i, r=None):
    cp, ip = tmp / "c.json", tmp / "i.json"
    cp.write_text(json.dumps(c), encoding="utf-8")
    ip.write_text(json.dumps(i), encoding="utf-8")
    cmd = [str(RUST), "verify-claim", "--claim", str(cp), "--inventory", str(ip)]
    if r is not None:
        rp = tmp / "r.json"
        rp.write_text(json.dumps(r), encoding="utf-8")
        cmd += ["--report", str(rp)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)["verdict"]
    except Exception:  # noqa: BLE001
        return "NO-JSON"


CASES = [
    ("clean, full NC set", claim(), inv()),
    ("missing NC codes for the level", claim(), inv()),
    ("nearly correct level string", claim(level="PROVEN "), inv()),
    ("nan density", claim(), inv(sources=[{"source_id": "s", "kind": "grants", "db_logic_density": float("nan")}])),
    ("sampled completeness", claim(), inv(sources=[dict(BASE, completeness_claim="sampled")])),
    ("growth false + unpublished delta", claim(),
     inv(perimeter_growth=False, delta_since_previous={"new_paths": 3, "published": False})),
    ("first inventory (baseline false)", claim(),
     inv(delta_since_previous={"new_paths": 8, "published": False, "baseline": False})),
    ("duplicate path ids", claim(), inv(paths=[dict(p, path_id="wp_001") for p in paths()])),
    ("honest report", claim(), inv(), {"coverage": 1.0, "analysed_paths": []}),
    ("lying report", claim(), inv(), {"coverage": 0.5, "analysed_paths": []}),
]


def main() -> int:
    if not RUST.exists():
        print("build the Rust core first")
        return 1
    bad = 0
    print(f"{'case':34} {'python':22} {'rust':22} agree")
    for case in CASES:
        name, c, i = case[0], case[1], case[2]
        r = case[3] if len(case) > 3 else None
        py = run_py(c, i, r)
        rs = run_rs(c, i, r)
        agree = py == rs
        bad += 0 if agree else 1
        print(f"{name:34} {py:22} {rs:22} {agree}")
    print(f"\ncases: {len(CASES)}, disagreements: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
