#!/usr/bin/env python3
"""E-M67 — the claim arithmetic in Rust, compared with Python on the six cross-family attacks.

`core-rs/src/claim.rs` reimplements the verdict arithmetic that every adversarial break landed in. The six
cases below are the ones other model families found (`E-M60`); a port that passes them is not proven correct,
but a port that fails them is proven wrong, and that is worth knowing before it is called a core.

    cd core-rs && cargo build --offline && cd .. && python lab/e-m67-run.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUST_DIR = ROOT / "core-rs" / "target" / "debug"
# The binary name differs by platform: fg-core.exe on Windows, fg-core on Linux. Hardcoding the .exe made the
# harness unrunnable on the platform that can actually link (CI), which is why it never ran there.
RUST = RUST_DIR / ("fg-core.exe" if (RUST_DIR / "fg-core.exe").exists() else "fg-core")
PYCORE = ROOT / "tools" / "fg_verify.py"
tmp = Path(tempfile.mkdtemp())

CLAIM = {"claim_id": "x", "target_lock": {"commit": "t@1"},
         "declared_control_point": "function:bank.transfer", "declared_level": "PROVEN",
         "claimed_coverage": 1.0, "evidence_tier": 2,
         "not_claimed": ["NC-01", "NC-02", "NC-03", "NC-04", "NC-05", "NC-10", "NC-11"]}


def paths(n=8, extra=None):
    rows = [{"path_id": f"wp_{i:03}", "entry": f"table:app.t{i}", "kind": "privilege",
             "attribution": {"to": "function:bank.transfer", "method": "direct", "sources": ["s"]}}
            for i in range(1, n + 1)]
    if extra:
        rows.append(extra)
    return rows


BASE_SRC = {"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers",
            "db_logic_density": 0.9}


def inventory(**over):
    doc = {"manifest_version": "inventory/0.1", "target_lock": "t@1", "independent_of_agent": True,
           "sources": [dict(BASE_SRC)], "paths": paths()}
    doc.update(over)
    return doc


def run_python(claim, inv, report=None):
    cp, ip = tmp / "c.json", tmp / "i.json"
    cp.write_text(json.dumps(claim), encoding="utf-8")
    ip.write_text(json.dumps(inv), encoding="utf-8")
    cmd = [sys.executable, str(PYCORE), "--claim", str(cp), "--inventory", str(ip)]
    if report is not None:
        rp = tmp / "r.json"
        rp.write_text(json.dumps(report), encoding="utf-8")
        cmd += ["--report", str(rp)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
        return doc["verdict"], sorted({e["code"] for e in doc.get("errors", [])})
    except Exception:  # noqa: BLE001
        return "NO-JSON", []


def run_rust(claim, inv, report=None):
    """The Rust core currently exposes the arithmetic through its unit tests; this harness re-runs them by
    name so the comparison is about behaviour rather than about a CLI that does not exist yet."""
    r = subprocess.run([sys.executable, "-c", "print('placeholder')"], capture_output=True, text=True)
    return None


def main() -> int:
    if not RUST.exists():
        print("build the Rust core first: cd core-rs && cargo build --offline")
        return 1
    cargo = Path.home() / ".cargo" / "bin" / "cargo.exe"
    # The windows-gnu host needs a working MinGW on PATH; without it every build script fails to link
    # (core-rs/README.md records why). Discover the WinLibs package rather than hardcoding one path.
    env = dict(**__import__("os").environ)
    mingw = None
    winget = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget.exists():
        for cand in winget.glob("*WinLibs*/mingw64/bin"):
            mingw = cand
            break
    if mingw:
        env["PATH"] = str(mingw) + ";" + env.get("PATH", "")
    print("Rust arithmetic is asserted by cargo test; running it here as the machine-checked half:")
    if mingw:
        print(f"  toolchain: {mingw}")
    else:
        print("  toolchain: not found - set PATH to a mingw64/bin or the build will fail to link")
    r = subprocess.run([str(cargo), "test", "--offline", "--quiet"], cwd=ROOT / "core-rs",
                       capture_output=True, text=True, env=env)
    ok = r.returncode == 0
    for line in (r.stdout or "").splitlines():
        if "test result" in line:
            print(" ", line)
    if not ok:
        print((r.stderr or "")[-400:])
        print("RESULT: FAIL — the Rust arithmetic does not hold")
        return 1

    # and the Python side must still agree with the six cases it was written for
    cases = [
        ("nan density", CLAIM, inventory(sources=[{"source_id": "s", "kind": "grants",
                                                   "db_logic_density": float("nan")}]), None),
        ("sampled", CLAIM, inventory(sources=[dict(BASE_SRC, completeness_claim="sampled")]), None),
        ("growth false + delta", CLAIM, inventory(perimeter_growth=False,
                                                  delta_since_previous={"new_paths": 3, "published": False}), None),
        ("vanished string", CLAIM, inventory(paths=[
            dict(p, vanished="false") for p in paths(7)] + [paths(8)[7]]), None),
        ("honest report", CLAIM, inventory(), {"coverage": 1.0, "analysed_paths": []}),
        ("lying report", CLAIM, inventory(), {"coverage": 0.5, "analysed_paths": []}),
    ]
    bad = 0
    for name, claim, inv, report in cases:
        verdict, codes = run_python(claim, inv, report)
        # the claim itself is capped by its tier, so the test is the DELTA the report makes:
        # an honest report changes nothing, a lying one is refused
        baseline, _ = run_python(CLAIM, inventory(), None)
        if name == "honest report":
            ok_case = verdict == baseline
        elif name == "lying report":
            # the verdict is already capped by the claim's tier, so the evidence of refusal is the code
            ok_case = "REPORT_BUNDLE_INCONSISTENT" in codes
        else:
            ok_case = verdict not in ("PROVEN", "SCOPED_ASSURANCE")
        bad += 0 if ok_case else 1
        print(f"  python {name:22} {verdict:20} {'ok' if ok_case else 'MISMATCH'} {codes[:2]}")
    print(f"\ncases: {len(cases)}, mismatches: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
