#!/usr/bin/env python3
"""E-M53: a role's terms are covered by its signature — demonstrated by tampering.

Pre-registered threshold: create a bundle with a risk acceptance, verify it, then edit one term of
that acceptance and verify again. The first must be SIGNED_AND_CONSISTENT with binding "role"; the
second must fail. If the second passes, the binding is decorative and the whole ADR-0015 is false.

    python lab/e-m53-run.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "fg_bundle.py"


def keypair(path: Path):
    k = Ed25519PrivateKey.generate()
    path.write_bytes(k.private_bytes(serialization.Encoding.PEM,
                                     serialization.PrivateFormat.PKCS8,
                                     serialization.NoEncryption()))
    return path


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    (tmp / "claim.json").write_text(json.dumps({
        "claim_id": "E-M53", "target_lock": {"commit": "t@1"},
        "declared_control_point": "function:f", "declared_level": "CONSISTENT_DECLARED",
        "claimed_coverage": 0.0, "excluded": [], "not_claimed": ["NC-01", "NC-02"]}), encoding="utf-8")
    (tmp / "inv.json").write_text(json.dumps({"paths": [], "sources": []}), encoding="utf-8")

    vk = keypair(tmp / "verifier.key")
    base = tmp / "base"
    r = subprocess.run([sys.executable, str(CLI), "create", "--out", str(base),
                        "--claim", str(tmp / "claim.json"), "--inventory", str(tmp / "inv.json"),
                        "--key", str(vk), "--signer", "verifier", "--role", "consistency_verdict"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        return 1
    address = (base / "manifest.sha256").read_text(encoding="ascii").strip()

    # a second party accepts the risk, signed over the role-bound message
    ok = keypair(tmp / "owner.key")
    owner = tmp / "owner"
    r = subprocess.run([sys.executable, str(CLI), "create", "--out", str(owner),
                        "--claim", str(tmp / "claim.json"), "--inventory", str(tmp / "inv.json"),
                        "--key", str(ok), "--signer", "owner", "--role", "risk_acceptance",
                        "--valid-until", "2027-01-01", "--statement", "Acme accepts the residual risk",
                        "--residual-risk", "NC-01"], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        return 1
    # move the owner's signature and role into the verifier's bundle
    for f in ("owner.sig", "owner.pub", "owner.role"):
        shutil.copy(owner / "signatures" / f, base / "signatures" / f)
    # the acceptance must name the verifier's address, and be signed for it
    role_path = base / "signatures" / "owner.role"
    doc = json.loads(role_path.read_text(encoding="utf-8"))
    doc["accepted_scope"] = address
    role_path.write_text(json.dumps(doc), encoding="utf-8")

    sys.path.insert(0, str(ROOT / "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("fgb53", CLI)
    fgb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fgb)
    k = fgb.load_key(ok)
    import base64
    (base / "signatures" / "owner.sig").write_text(
        base64.b64encode(k.sign(fgb.role_message(address, doc))).decode("ascii") + "\n", encoding="ascii")

    trusted = [str(base / "signatures" / "verifier.pub"), str(base / "signatures" / "owner.pub")]

    def verify():
        return subprocess.run([sys.executable, str(CLI), "verify", "--bundle", str(base),
                               "--trusted-keys", *trusted, "--expect-target", "t@1"],
                              capture_output=True, text=True)

    good = json.loads(verify().stdout)
    ok_good = good["verdict"] == "SIGNED_AND_CONSISTENT" and good.get("signature_binding", {}).get("owner") == "role"

    # tamper: the accepting party "withdraws" — the same words an attacker used in E-M50 B2
    doc2 = json.loads(role_path.read_text(encoding="utf-8"))
    doc2["statement"] = "this acceptance is withdrawn"
    role_path.write_text(json.dumps(doc2), encoding="utf-8")
    bad = json.loads(verify().stdout)
    ok_bad = bad["verdict"] != "SIGNED_AND_CONSISTENT"

    print(f"genuine acceptance verifies:      {ok_good}  (binding {good.get('signature_binding')})")
    print(f"tampered acceptance is refused:   {ok_bad}   ({bad['verdict']})")
    ok = ok_good and ok_bad
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
