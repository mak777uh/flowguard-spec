#!/usr/bin/env python3
"""rebuild-sample-bundle — the fixture is reproducible from its own contents, or it is a relic.

`fixtures/sample-bundle` carries signatures over its canonical bytes. Those bytes changed when the number rule
did (ADR-0018), and the private keys are deliberately absent, so the fixture could only be restored by the key
holder. That is a fixture nobody can maintain.

This script rebuilds it the honest way: read the claim, the inventory and the subject bytes out of the bundle
itself, rebuild the bundle under the current canonical form, sign with two freshly generated keys
(`consistency_verdict` and `risk_acceptance`, so the separation-of-duties case survives), verify against both
keys, and throw the private halves away.

    python lab/rebuild-sample-bundle.py            # rebuild in a temp dir and verify; changes nothing
    python lab/rebuild-sample-bundle.py --apply    # write the result into fixtures/sample-bundle

A rebuild that verifies is the proof that the format is reproducible; a rebuild that does not, is a defect in
the canonical form or in the signing path, and either way it should be seen before a signature is published.
"""
import argparse
import base64
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "fixtures" / "sample-bundle"
TOOLS = ROOT / "tools"

sys.path.insert(0, str(TOOLS))
from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

import fg_bundle  # noqa: E402


def pem(private) -> bytes:
    return private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                 serialization.NoEncryption())


def rebuild(work: pathlib.Path) -> tuple[pathlib.Path, str]:
    bundle = json.loads((BUNDLE / "bundle.json").read_text(encoding="utf-8"))
    claim = bundle["claim"]

    inv = work / "inventory.json"
    inv.write_bytes((BUNDLE / "objects" / bundle["inventory_digest"]).read_bytes())
    claim_path = work / "claim.json"
    claim_path.write_text(json.dumps(claim, ensure_ascii=False, indent=1), encoding="utf-8")

    subjects = []
    for name, rec in bundle["subjects"].items():
        src = work / rec["source"]
        src.write_bytes((BUNDLE / "objects" / rec["sha256"]).read_bytes())
        subjects.append(f"{name}={src}")

    demo_key, owner_key = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    (work / "demo.pem").write_bytes(pem(demo_key))
    (work / "owner.pem").write_bytes(pem(owner_key))

    out = work / "bundle"
    cmd = [sys.executable, str(TOOLS / "fg_bundle.py"), "create", "--out", str(out),
           "--claim", str(claim_path), "--inventory", str(inv),
           "--key", str(work / "demo.pem"), "--signer", "demo", "--role", "consistency_verdict"]
    for s in subjects:
        cmd += ["--subject", s]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-600:], r.stderr[-600:])
        raise SystemExit(1)

    addr = (out / "manifest.sha256").read_text(encoding="ascii").strip()
    role = fg_bundle.role_document("risk_acceptance", "owner", accepted_scope=addr,
                                   residual_risk=["NC-01", "NC-02"], valid_until="2027-01-01",
                                   statement="accepted by the named party for the stated period")
    (out / "signatures" / "owner.sig").write_bytes(
        base64.b64encode(owner_key.sign(fg_bundle.signature_payload(addr, role))) + b"\n")
    (out / "signatures" / "owner.pub").write_bytes(
        owner_key.public_key().public_bytes(serialization.Encoding.PEM,
                                            serialization.PublicFormat.SubjectPublicKeyInfo))
    (out / "signatures" / "owner.role").write_text(json.dumps(role), encoding="utf-8")
    (work / "owner.pub").write_bytes((out / "signatures" / "owner.pub").read_bytes())
    (work / "demo.pub").write_bytes((out / "signatures" / "demo.pub").read_bytes())
    return out, addr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the result into fixtures/sample-bundle")
    a = ap.parse_args()

    work = pathlib.Path(tempfile.mkdtemp(prefix="rebuild-sample-"))
    try:
        out, addr = rebuild(work)
        claim = json.loads((out / "bundle.json").read_text(encoding="utf-8"))["claim"]
        v = subprocess.run([sys.executable, str(TOOLS / "fg_bundle.py"), "verify",
                            "--bundle", str(out),
                            "--trusted-keys", str(work / "demo.pub"), str(work / "owner.pub"),
                            "--expect-target", str((claim.get("target_lock") or {}).get("commit", ""))],
                           capture_output=True, text=True)
        verdict = ""
        for line in (v.stdout or "").splitlines():
            if '"verdict"' in line:
                verdict = line.strip().strip(",")
        print(f"rebuilt address: {addr[:12]}…  verify exit: {v.returncode}  {verdict}")
        if v.returncode != 0:
            print((v.stdout or v.stderr)[-600:])
            return 1
        if a.apply:
            for item in out.iterdir():
                if item.name == "README.md":
                    continue
                target = BUNDLE / item.name
                if item.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)
            print("applied to fixtures/sample-bundle")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
