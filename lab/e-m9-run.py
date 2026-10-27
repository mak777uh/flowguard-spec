#!/usr/bin/env python3
"""E-M9 harness: the substitution test.

Six cases, thresholds pre-registered in lab/experiments/E-M9-substitution.md:

  D-1a code       subject bytes replaced, old signature kept   -> must be INVALID
  D-1b build      build digest replaced, old signature kept    -> must be INVALID
  D-1c config     configuration replaced, old signature kept   -> must be INVALID
  D-1d identity   signer swapped for another key               -> must be INVALID
  D-2a pair       validly signed bundle re-pointed at target B -> must NOT be SIGNED_AND_CONSISTENT
  D-2b pair       same, with the manifest internally consistent  -> must NOT be SIGNED_AND_CONSISTENT

Run 1 (without anchors) failed 3/6: a self-signed bundle accepts any key that signs its own address,
and a re-signed claim is internally consistent whatever it claims. `--no-anchors` reproduces that.
Run 2 supplies the two anchors from outside the bundle: a trusted key list and the target the caller
is actually looking at.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "tools" / "fg_bundle.py"

CASES = [
    ("D-1a", "code", True),
    ("D-1b", "build", True),
    ("D-1c", "config", True),
    ("D-1d", "identity", True),
    ("D-2a", "pair", False),
    ("D-2b", "pair", False),
]

TARGET_CODE = "def transfer(a, b, x):\n    return a - x, b + x\n"


def sh(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--no-anchors", action="store_true",
                    help="reproduce run 1: no trusted key list and no externally supplied target")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())

    (tmp / "target.py").write_text(TARGET_CODE, encoding="utf-8")
    (tmp / "build.json").write_text(json.dumps({"compiler": "cpython", "flags": "-O"}), encoding="utf-8")
    (tmp / "config.yml").write_text("limit: 1000\n", encoding="utf-8")
    (tmp / "identity.txt").write_text("service: bank-api\n", encoding="utf-8")

    claim = tmp / "claim.json"
    claim.write_text(json.dumps({
        "claim_id": "E-M9-DEMO", "flow": "balance_transfer",
        "target_lock": {"commit": "target@e-m9"},
        "declared_control_point": "function:bank.transfer",
        "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0, "excluded": [],
    }), encoding="utf-8")
    inventory = tmp / "inv.json"
    inventory.write_text(json.dumps({"paths": [], "sources": []}), encoding="utf-8")

    base = tmp / "b0"
    r = sh([sys.executable, BUNDLE, "create", "--out", base, "--claim", claim, "--inventory", inventory,
            "--subject", f"code={tmp / 'target.py'}", "--subject", f"build={tmp / 'build.json'}",
            "--subject", f"config={tmp / 'config.yml'}", "--subject", f"identity={tmp / 'identity.txt'}",
            "--key", tmp / "alice.key", "--signer", "alice"])
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("could not create the base bundle")

    anchors = [] if a.no_anchors else ["--trusted-keys", str(base / "signatures" / "alice.pub")]
    covers = [] if a.no_anchors else ["--expect-target", "target@e-m9"]

    v = sh([sys.executable, BUNDLE, "verify", "--bundle", base] + anchors + covers)
    out = json.loads(v.stdout)
    print(f"mode: {'run 1 — no anchors' if a.no_anchors else 'run 2 — anchors supplied'}")
    print(f"base bundle: {out['verdict']} signed_by={out['signed_by']}")
    if out["verdict"] != "SIGNED_AND_CONSISTENT":
        print("base bundle must be valid before any substitution is meaningful")
        return 1

    passed = 0
    print(f"\n{'case':5} {'class':9} {'expect':24} result")
    for cid, cls, must_invalid in CASES:
        dst = tmp / f"mut-{cid}"
        args = ["substitute", "--bundle", base, "--class", cls, "--out", dst,
                "--key", tmp / "alice.key", "--signer", "alice"]
        if cls == "pair":
            args += ["--target", "target@someone-else"]
        r = sh([sys.executable, BUNDLE] + args)
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            raise SystemExit(f"substitute {cid} failed")
        v = sh([sys.executable, BUNDLE, "verify", "--bundle", dst] + anchors + covers)
        out = json.loads(v.stdout)
        if must_invalid:
            ok = out["verdict"] == "INVALID"
            expect = "INVALID"
        else:
            ok = out["verdict"] != "SIGNED_AND_CONSISTENT"
            expect = "not SIGNED_AND_CONSISTENT"
        passed += ok
        print(f"{cid:5} {cls:9} {expect:24} {'CAUGHT' if ok else 'ACCEPTED — FAIL'}")
        if a.verbose or not ok:
            print("     ", json.dumps(out, ensure_ascii=False)[:300])

    total = len(CASES)
    print(f"\ncases caught: {passed}/{total}")
    print("threshold (pre-registered): 6/6")
    print(f"RESULT: {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
