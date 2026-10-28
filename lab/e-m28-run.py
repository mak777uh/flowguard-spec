#!/usr/bin/env python3
"""E-M28 harness: three acts, three signatures, and who may hold which.

Round-8 review, all three: a signature under a verification result, an acceptance of residual risk,
and a contractual liability are different acts with different subjects. Ours carried one role field
that said whatever it liked.

Cases:
  R1 unknown role                        -> SIGNATURE_ROLE_UNKNOWN
  R2 risk acceptance without an expiry   -> RISK_ACCEPTANCE_INCOMPLETE
  R3 the same key signs verdict + risk   -> SEPARATION_OF_DUTIES_VIOLATED
  R4 liability declared as a role        -> LIABILITY_NOT_A_ROLE
  R5 a correct split                     -> SIGNED_AND_CONSISTENT

    python lab/e-m28-run.py
"""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "fg_bundle.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("fgb28", CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    fgb = load_mod()
    tmp = Path(tempfile.mkdtemp())

    (tmp / "code.py").write_text("def transfer(a, b, x):\n    return a - x, b + x\n", encoding="utf-8")
    (tmp / "claim.json").write_text(json.dumps({
        "claim_id": "E-M28", "target_lock": {"commit": "t@1"},
        "declared_control_point": "function:f", "declared_level": "CONSISTENT_DECLARED",
        "claimed_coverage": 0.0, "excluded": [], "not_claimed": ["NC-01", "NC-02"]}), encoding="utf-8")
    (tmp / "inv.json").write_text(json.dumps({"paths": [], "sources": []}), encoding="utf-8")

    base = tmp / "base"
    r = subprocess.run([sys.executable, str(CLI), "create", "--out", str(base),
                        "--claim", str(tmp / "claim.json"), "--inventory", str(tmp / "inv.json"),
                        "--subject", f"code={tmp / 'code.py'}", "--key", str(tmp / "verifier.key"),
                        "--signer", "verifier", "--role", "consistency_verdict"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("could not build the base bundle")

    trusted = [str(base / "signatures" / "verifier.pub")]
    address = (base / "manifest.sha256").read_text(encoding="ascii").strip()

    def verify(path, trusted_keys=None):
        ns = argparse.Namespace(bundle=str(path), trusted_keys=trusted_keys or trusted, expect_target="t@1")
        return fgb.verify_bundle(ns)

    def clone(tag):
        d = tmp / tag
        shutil.copytree(base, d)
        return d

    def add_role(d, name, doc, sign_with=None):
        key = Path(sign_with) if sign_with else (tmp / f"{name}.key")
        if not key.exists():
            subprocess.run([sys.executable, str(CLI), "create", "--out", str(tmp / f"noop-{name}"),
                            "--claim", str(tmp / "claim.json"), "--inventory", str(tmp / "inv.json"),
                            "--subject", f"code={tmp / 'code.py'}", "--key", str(key),
                            "--signer", name, "--role", "analysis_provenance"],
                           capture_output=True, text=True)
        fgb_key = fgb.load_key(key) if hasattr(fgb, "load_key") else None
        import base64
        # ADR-0015: sign the role-bound message, not the address alone. Signing the address
        # made every acceptance's terms editable after signing (E-M52).
        sig = (fgb_key.sign(fgb.role_message(address, doc)) if fgb_key else b"")
        (d / "signatures" / f"{name}.sig").write_text(base64.b64encode(sig).decode("ascii") + "\n", encoding="ascii")
        (d / "signatures" / f"{name}.pub").write_bytes(
            fgb_key.public_key().public_bytes(fgb.Encoding.PEM, fgb.PublicFormat.SubjectPublicKeyInfo))
        (d / "signatures" / f"{name}.role").write_text(json.dumps(doc), encoding="utf-8")

    results = []

    d1 = clone("r1")
    (d1 / "signatures" / "verifier.role").write_text(json.dumps({"asserts": "chief_vibes_officer",
                                                                 "issuer": "verifier"}), encoding="utf-8")
    out, _ = verify(d1)
    results.append(("R1 unknown role", any(e["code"] == "SIGNATURE_ROLE_UNKNOWN" for e in out["errors"])))

    d2 = clone("r2")
    add_role(d2, "owner", {"asserts": "risk_acceptance", "issuer": "owner",
                           "accepted_scope": address, "residual_risk": ["NC-01"],
                           "statement": "accepted"})
    out, _ = verify(d2, trusted + [str(d2 / "signatures" / "owner.pub")])
    results.append(("R2 acceptance without expiry",
                    any(e["code"] == "RISK_ACCEPTANCE_INCOMPLETE" for e in out["errors"])))

    d3 = clone("r3")
    # the same KEY under a different name: the file name must not decide who the party is
    add_role(d3, "owner", {"asserts": "risk_acceptance", "issuer": "owner",
                           "accepted_scope": address, "residual_risk": ["NC-01"],
                           "valid_until": "2027-01-01", "statement": "accepted"},
             sign_with=str(tmp / "verifier.key"))
    out, _ = verify(d3)
    results.append(("R3 same key signs both",
                    any(e["code"] == "SEPARATION_OF_DUTIES_VIOLATED" for e in out["errors"])))

    d4 = clone("r4")
    (d4 / "signatures" / "verifier.role").write_text(json.dumps({"asserts": "liability_agreement",
                                                                 "issuer": "verifier"}), encoding="utf-8")
    out, _ = verify(d4)
    results.append(("R4 liability as a role", any(e["code"] == "LIABILITY_NOT_A_ROLE" for e in out["errors"])))

    out, code = verify(base)
    results.append(("R5 correct split accepted", out["verdict"] == "SIGNED_AND_CONSISTENT" and code == 0))

    for name, ok in results:
        print(f"{name:34} {'PASS' if ok else 'FAIL'}")
    passed = sum(ok for _, ok in results)
    print(f"\ncases passed: {passed}/{len(results)}")
    print(f"RESULT: {'PASS' if passed == len(results) else 'FAIL'}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
