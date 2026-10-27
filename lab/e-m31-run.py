#!/usr/bin/env python3
"""E-M31: two builds of the same input produce the same address (claim C-02)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "fg_bundle.py"


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    (tmp / "c.py").write_text("x = 1\n", encoding="utf-8")
    (tmp / "claim.json").write_text(json.dumps({
        "claim_id": "det", "target_lock": {"commit": "t@1"}, "declared_control_point": "f",
        "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0, "excluded": [],
        "not_claimed": ["NC-01", "NC-02"]}), encoding="utf-8")
    (tmp / "inv.json").write_text(json.dumps({"paths": [], "sources": []}), encoding="utf-8")

    addresses = []
    for i in (1, 2):
        out = tmp / f"b{i}"
        r = subprocess.run([sys.executable, str(CLI), "create", "--out", str(out),
                            "--claim", str(tmp / "claim.json"), "--inventory", str(tmp / "inv.json"),
                            "--subject", f"code={tmp / 'c.py'}", "--key", str(tmp / "k.key"),
                            "--signer", "s", "--role", "analysis_provenance"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            return 1
        addresses.append((out / "manifest.sha256").read_text(encoding="ascii").strip())
        print(f"build {i}: {addresses[-1][:16]}…")

    same = addresses[0] == addresses[1]
    print(f"identical addresses: {same}")
    print(f"RESULT: {'PASS' if same else 'FAIL'}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
