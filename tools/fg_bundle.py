#!/usr/bin/env python3
"""fg_bundle — build, sign and verify an fg-bundle/1 attestation bundle.

Layout (ADR-0005, ADR-0006):

    <bundle>/bundle.json          manifest: version, subject digests, claim, inventory digest, perimeter
    <bundle>/objects/<sha256>     content-addressed payloads
    <bundle>/manifest.sha256      sha256 of the canonical bundle.json — the bundle's address
    <bundle>/signatures/<id>.sig  detached Ed25519 signature over manifest.sha256
    <bundle>/signatures/<id>.pub  the public key, so a verifier needs no network

    python tools/fg_bundle.py create --out b1 --claim claim.json --inventory m.json \
        --subject code=target.py --key k1.key --signer alice --role consistency_verdict
    python tools/fg_bundle.py verify --bundle b1
    python tools/fg_bundle.py substitute --bundle b1 --class code --out b1-code
"""
import argparse
import base64
import hashlib
import json
import shutil
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, PublicFormat, NoEncryption,
                                                           load_pem_private_key, load_pem_public_key)

VERSION = "fg-bundle/1"
SUBJECTS = ("code", "build", "config", "identity")


def canon(doc) -> bytes:
    """Canonical JSON: sorted keys, no whitespace. RFC 8785-shaped for this subset."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_key(p: Path) -> Ed25519PrivateKey:
    if not p.exists():
        k = Ed25519PrivateKey.generate()
        p.write_bytes(k.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        p.chmod(0o600)
        print(f"generated key {p}")
    return load_pem_private_key(p.read_bytes(), password=None)


ROLES_POLICY = ROOT_POLICY = None


def load_roles():
    global ROLES_POLICY
    if ROLES_POLICY is None:
        p = Path(__file__).resolve().parent.parent / "policies" / "signature-roles.json"
        ROLES_POLICY = json.loads(p.read_text(encoding="utf-8"))
    return ROLES_POLICY


def check_roles(bundle_dir: Path, address: str):
    """Validate every signature's role against policies/signature-roles.json (E-M28).

    Round-8 review: an attestation, an acceptance of risk and a contract are different acts. A role
    file that says whatever it likes turns the three into one field, which is worse than having none.
    """
    policy = load_roles()
    roles = policy["roles"]
    problems = []
    holders = {}
    for rolefile in sorted(bundle_dir.glob("signatures/*.role")):
        signer = rolefile.stem
        try:
            doc = json.loads(rolefile.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            problems.append(("SIGNATURE_ROLE_UNKNOWN", signer, "a JSON role document", str(e)))
            continue
        role = doc.get("asserts")
        if role in policy.get("not_a_role", {}):
            problems.append(("LIABILITY_NOT_A_ROLE", signer, "no liability role in a bundle",
                             "a contract cannot be created by a JSON field"))
            continue
        spec = roles.get(role)
        if spec is None:
            problems.append(("SIGNATURE_ROLE_UNKNOWN", signer,
                             "one of: " + ", ".join(sorted(roles)), str(role)))
            continue
        # Holder identity is the KEY, not the file name: the same key under two names is still one
        # party, and comparing names let that through (found by E-M28).
        pubp = bundle_dir / "signatures" / f"{signer}.pub"
        holders[role] = pubp.read_bytes() if pubp.exists() else signer.encode()
        for req in spec.get("requires", []):
            val = doc.get(req)
            if req == "accepted_scope":
                if val != address:
                    problems.append(("RISK_ACCEPTANCE_INCOMPLETE", signer,
                                     f"accepted_scope = the bundle address {address[:12]}…", str(val)))
                continue
            if not val:
                problems.append(("RISK_ACCEPTANCE_INCOMPLETE" if role == "risk_acceptance" else "MISSING_EVIDENCE",
                                 signer, f"{role} requires {req}", "absent"))
    verdict_signer = holders.get("consistency_verdict")
    acceptance_signer = holders.get("risk_acceptance")
    if verdict_signer and verdict_signer == acceptance_signer:
        problems.append(("SEPARATION_OF_DUTIES_VIOLATED", str(verdict_signer)[:12],
                         "different keys for consistency_verdict and risk_acceptance",
                         "the same key signed both"))
    return problems

def cmd_create(a) -> int:
    out = Path(a.out)
    (out / "objects").mkdir(parents=True, exist_ok=True)
    (out / "signatures").mkdir(exist_ok=True)

    claim = json.loads(Path(a.claim).read_text(encoding="utf-8"))
    inventory = json.loads(Path(a.inventory).read_text(encoding="utf-8"))

    subjects, objects = {}, {}
    for spec in a.subject:
        name, _, src = spec.partition("=")
        if name not in SUBJECTS:
            raise SystemExit(f"unknown subject '{name}', expected one of {SUBJECTS}")
        src_path = Path(src)
        data = src_path.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        (out / "objects" / h).write_bytes(data)
        objects[h] = {"bytes": len(data), "name": src_path.name}
        subjects[name] = {"sha256": h, "source": src_path.name}

    bundle = {
        "bundle_version": VERSION,
        "subjects": subjects,
        "objects": objects,
        "claim": claim,
        "inventory_digest": "sha256:" + sha256_file(Path(a.inventory)),
        "plaintext_notified": True,
    }
    (out / "bundle.json").write_bytes(canon(bundle) if a.canonical else
                                      json.dumps(bundle, indent=1, ensure_ascii=False).encode())
    addr = hashlib.sha256(canon(bundle)).hexdigest()
    (out / "manifest.sha256").write_text(addr + "\n", encoding="ascii")

    key = load_key(Path(a.key))
    sig = key.sign(addr.encode("ascii"))
    (out / "signatures" / f"{a.signer}.sig").write_text(base64.b64encode(sig).decode("ascii") + "\n", encoding="ascii")
    (out / "signatures" / f"{a.signer}.pub").write_bytes(
        key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
    role_doc = {"asserts": a.role, "issuer": a.signer}
    if a.role == "consistency_verdict":
        rp = Path(__file__).resolve().parent.parent / "policies" / "risk-classes.json"
        role_doc["policy_digest"] = "sha256:" + hashlib.sha256(rp.read_bytes()).hexdigest()
    if a.role == "risk_acceptance":
        role_doc.update({
            "accepted_scope": addr,
            "residual_risk": a.residual_risk or ["NC-01", "NC-02"],
            "valid_until": a.valid_until or "2027-01-01",
            "statement": a.statement or "accepted by the named party for the stated period",
        })
    (out / "signatures" / f"{a.signer}.role").write_text(json.dumps(role_doc), encoding="utf-8")

    print(f"bundle: {out}  address {addr[:16]}…  subjects {', '.join(subjects)}")
    return 0


def verify_bundle(a) -> tuple:
    """Pure verification: returns (result document, exit code). No printing, so the corpus
    harness can call it in-process (E-M10 needs ~130 verifications)."""
    b = Path(a.bundle)
    problems = []

    # A self-signed bundle proves nothing: it carries its own key. Two anchors must come from
    # outside the bundle (E-M9 run 1 failed 3/6 precisely because both were missing).
    trusted = []
    for kp in (a.trusted_keys or []):
        trusted.append(Path(kp).read_bytes())
    expect_target = a.expect_target

    bj = b / "bundle.json"
    if not bj.exists():
        return {"verdict": "INVALID", "errors": [{"code": "MISSING_EVIDENCE", "subject": "bundle.json",
                                                    "next_action": "bundle is not a bundle"}]}, 2

    try:
        bundle = json.loads(bj.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"verdict": "INVALID", "errors": [{"code": "REPORT_BUNDLE_INCONSISTENT",
                                                    "subject": "bundle.json", "observed": str(e)}]}, 2

    if bundle.get("bundle_version") != VERSION:
        problems.append(("REPORT_BUNDLE_INCONSISTENT", "bundle_version",
                         f"expected {VERSION}", str(bundle.get("bundle_version"))))

    # 1. objects exist and hash to their names
    for h, meta in (bundle.get("objects") or {}).items():
        f = b / "objects" / h
        if not f.exists():
            problems.append(("MISSING_EVIDENCE", f"object {h[:12]}", "object present", "absent"))
            continue
        actual = sha256_file(f)
        if actual != h:
            problems.append(("MISSING_EVIDENCE", f"object {h[:12]}", f"sha256 {h[:12]}", f"sha256 {actual[:12]}"))

    # 2. subjects point at objects that exist
    for name, sub in (bundle.get("subjects") or {}).items():
        if sub.get("sha256") not in (bundle.get("objects") or {}):
            problems.append(("MISSING_EVIDENCE", f"subject {name}",
                             "digest listed in objects", "digest not listed"))

    # 3. address matches the manifest
    addr_file = b / "manifest.sha256"
    if not addr_file.exists():
        problems.append(("MISSING_EVIDENCE", "manifest.sha256", "the bundle address", "absent"))
        addr = None
    else:
        addr = addr_file.read_text(encoding="ascii").strip()
        recomputed = hashlib.sha256(canon(bundle)).hexdigest()
        if addr != recomputed:
            problems.append(("REPORT_BUNDLE_INCONSISTENT", "manifest.sha256",
                             f"address {recomputed[:12]}", f"recorded {addr[:12]}"))

    # 4. at least one signature verifies over the address, from a key supplied out-of-band
    verified = []
    for sigf in sorted((b / "signatures").glob("*.sig")):
        name = sigf.stem
        pub = b / "signatures" / f"{name}.pub"
        if not pub.exists() or addr is None:
            problems.append(("MISSING_EVIDENCE", f"signature {name}", "public key beside the signature", "absent"))
            continue
        pub_bytes = pub.read_bytes()
        if trusted and pub_bytes not in trusted:
            # The bundle carries its own key, so without this check any key that signs its own
            # address passes. That is what E-M9 run 1 measured (3/6).
            problems.append(("POLICY_UNTRUSTED", f"signature {name}",
                             "a key from the trusted set supplied out-of-band", "key is not in the trusted set"))
            continue
        try:
            key = load_pem_public_key(pub_bytes)
            key.verify(base64.b64decode(sigf.read_text(encoding="ascii").strip()),
                       addr.encode("ascii"))
            verified.append(name)
        except Exception:  # noqa: BLE001
            problems.append(("MISSING_EVIDENCE", f"signature {name}", "a valid signature over the address",
                             "verification failed"))

    if not verified:
        problems.append(("MISSING_EVIDENCE", "signatures", "at least one valid signature", "none"))

    # 4b. signature roles, and who is allowed to hold which (E-M28)
    if addr:
        for code, signer, expected, observed in check_roles(b, addr):
            problems.append((code, "role:" + signer, expected, observed))

    # 5. the target the caller is actually looking at, not the one the bundle chose for itself.
    # Without this anchor a correctly re-signed bundle passes whatever it claims (E-M9 D-2).
    if expect_target:
        got = ((bundle.get("claim") or {}).get("target_lock") or {}).get("commit")
        if got != expect_target:
            problems.append(("TARGET_MISMATCH", "claim.target_lock",
                             f"commit {expect_target}", f"commit {got}"))

    out = {
        "verdict": "INVALID" if problems else "SIGNED_AND_CONSISTENT",
        "address": (addr or "")[:16] + "…" if addr else None,
        "signed_by": verified,
        "errors": [{"code": c, "subject": s, "expected": e, "observed": o} for c, s, e, o in problems[:3]],
    }
    return out, (2 if problems else 0)


def cmd_verify(a) -> int:
    out, code = verify_bundle(a)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return code


def cmd_substitute(a) -> int:
    """Produce a mutated copy. Used by E-M9; kept in the tool so the mutations are reproducible."""
    src, dst = Path(a.bundle), Path(a.out)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    bundle = json.loads((dst / "bundle.json").read_text(encoding="utf-8"))
    cls = a.kind

    if cls in ("code", "build", "config"):
        name = {"code": "code", "build": "build", "config": "config"}[cls]
        subj = bundle["subjects"].get(name)
        if not subj:
            raise SystemExit(f"subject '{name}' not present in this bundle")
        old = subj["sha256"]
        payload = (dst / "objects" / old).read_bytes()
        mutant = payload + b"\n# mutated by E-M9\n"
        nh = hashlib.sha256(mutant).hexdigest()
        (dst / "objects" / nh).write_bytes(mutant)
        bundle["subjects"][name]["sha256"] = nh
        bundle["objects"][nh] = bundle["objects"].pop(old, {"bytes": len(mutant), "name": name})
        # the address and signature are deliberately NOT updated: this is tampering after signing
        (dst / "bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")

    elif cls == "identity":
        # swap the signer for another trusted key, leaving the address intact
        other = Path(a.out).parent / "other.key"
        k = load_key(other)
        addr = (dst / "manifest.sha256").read_text(encoding="ascii").strip()
        (dst / "signatures" / "mallory.sig").write_text(
            base64.b64encode(k.sign(addr.encode("ascii"))).decode("ascii") + "\n", encoding="ascii")
        (dst / "signatures" / "mallory.pub").write_bytes(
            k.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
        for f in list((dst / "signatures").glob("*.sig")):
            if f.stem != "mallory":
                f.unlink()

    elif cls == "pair":
        # D-2: a correctly signed bundle, re-pointed at a different target.
        # The bundle stays internally consistent and its signature stays valid; only the claim's
        # target differs from the target the bundle was signed for.
        bundle["claim"]["target_lock"] = {"commit": a.target or "some-other-commit"}
        (dst / "bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
        addr = hashlib.sha256(canon(bundle)).hexdigest()
        (dst / "manifest.sha256").write_text(addr + "\n", encoding="ascii")
        # re-sign the new address with the ORIGINAL key: this is the dangerous case, not tampering
        key = load_key(Path(a.key))
        for f in list((dst / "signatures").glob("*.sig")):
            f.unlink()
        sig = key.sign(addr.encode("ascii"))
        (dst / "signatures" / f"{a.signer}.sig").write_text(
            base64.b64encode(sig).decode("ascii") + "\n", encoding="ascii")
        (dst / "signatures" / f"{a.signer}.pub").write_bytes(
            key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

    else:
        raise SystemExit(f"unknown substitution class '{cls}'")

    print(f"mutated: {cls} -> {dst}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create")
    c.add_argument("--out", required=True)
    c.add_argument("--claim", required=True)
    c.add_argument("--inventory", required=True)
    c.add_argument("--subject", action="append", default=[])
    c.add_argument("--key", required=True)
    c.add_argument("--signer", required=True)
    c.add_argument("--role", default="consistency_verdict")
    c.add_argument("--canonical", action="store_true")
    c.add_argument("--residual-risk", nargs="*")
    c.add_argument("--valid-until")
    c.add_argument("--statement")
    c.set_defaults(fn=cmd_create)

    v = sub.add_parser("verify")
    v.add_argument("--bundle", required=True)
    v.add_argument("--trusted-keys", nargs="*",
                   help="PEM public keys supplied out-of-band; without them any self-signed key passes")
    v.add_argument("--expect-target",
                   help="the target the caller is actually looking at; without it a re-signed claim passes")
    v.set_defaults(fn=cmd_verify)

    s = sub.add_parser("substitute")
    s.add_argument("--bundle", required=True)
    s.add_argument("--class", dest="kind", required=True,
                   choices=["code", "build", "config", "identity", "pair"])
    s.add_argument("--out", required=True)
    s.add_argument("--key")
    s.add_argument("--signer", default="alice")
    s.add_argument("--target")
    s.set_defaults(fn=cmd_substitute)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
