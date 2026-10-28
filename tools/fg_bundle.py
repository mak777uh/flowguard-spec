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



def role_message(address: str, role_doc: dict) -> bytes:
    """The bytes a role signature covers: the address, then the role's own terms.

    ADR-0015. Both creation and verification call this with the parsed document, so there is exactly
    one implementation of the message and no way for the two sides to canonicalise differently.
    `accepted_scope` is excluded: it must equal the address and is checked separately.
    """
    bounded = {k: v for k, v in role_doc.items() if k != "accepted_scope"}
    digest = hashlib.sha256(
        json.dumps(bounded, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return address.encode("ascii") + b"\nrole:" + digest.encode("ascii")


def role_document(asserts: str, issuer: str, **fields) -> dict:
    """The one place a role document is built, so creation and signing cannot drift."""
    doc = {"asserts": asserts, "issuer": issuer}
    for key, value in fields.items():
        if value:
            doc[key] = value
    return doc



V2 = "fg-bundle/2"


def role_digest(role_doc: dict) -> str:
    """sha256 of the canonical role document, accepted_scope included."""
    return hashlib.sha256(
        json.dumps(role_doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def signature_payload(addr: str, role_doc: dict) -> bytes:
    """ADR-0016: the bytes an Ed25519 signature covers.

    address | role digest (all terms, scope included) | scope, hashed once so the message is fixed-size.
    Nothing is excluded, so nothing has to be checked "separately".
    """
    scope = str(role_doc.get("accepted_scope") or "")
    body = "fg-bundle/2|%s|%s|%s" % (addr, role_digest(role_doc), scope)
    return hashlib.sha256(body.encode()).hexdigest().encode("ascii")


def nc_commitment(vocab_text: str, version: str) -> dict:
    """The bundle must commit to the NC vocabulary it was written against, not merely reference it."""
    return {"version": version,
            "sha256": hashlib.sha256(vocab_text.encode()).hexdigest(),
            "text_included": False}

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
        # A role file without that party's signature is a claim about a party written by whoever
        # holds the directory: an acceptance can be appended and its terms edited without touching
        # the address (E-M50 B2). Binding the role bytes into the address needs a format change and
        # is recorded as open; requiring the signature is available today.
        if not (bundle_dir / "signatures" / f"{signer}.sig").exists():
            problems.append(("SIGNATURE_ROLE_UNKNOWN", signer,
                             "a .sig by the party asserting this role",
                             "unsigned role: nobody signed this assertion"))
            continue
        if not (bundle_dir / "signatures" / f"{signer}.pub").exists():
            problems.append(("SIGNATURE_ROLE_UNKNOWN", signer, "a .pub identifying the party",
                             "no key: the party cannot be identified"))
            continue
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

    inv_bytes = Path(a.inventory).read_bytes()
    inv_hash = hashlib.sha256(inv_bytes).hexdigest()
    (out / "objects" / inv_hash).write_bytes(inv_bytes)
    objects[inv_hash] = {"bytes": len(inv_bytes), "name": "inventory.json"}

    _nc_path = Path(__file__).resolve().parent.parent / "docs" / "NOT-CLAIMED.md"
    _nc = nc_commitment(_nc_path.read_text(encoding="utf-8"), "nc-1") if _nc_path.exists() else None
    bundle = {
        "bundle_version": getattr(a, "envelope", "v1") == "v2" and V2 or VERSION,
        "subjects": subjects,
        "objects": objects,
        "claim": claim,
        # The inventory is part of the evidence, so it travels inside the bundle as an object and
        # its digest is bare hex: the rebuilder found that a "sha256:" prefix here matched nothing
        # in the bundle at all (E-M38).
        "inventory_digest": inv_hash,
        "plaintext_notified": True,
    }
    if _nc:
        bundle["nc_vocabulary"] = _nc
    (out / "bundle.json").write_bytes(canon(bundle) if a.canonical else
                                      json.dumps(bundle, indent=1, ensure_ascii=False).encode())
    addr = hashlib.sha256(canon(bundle)).hexdigest()
    (out / "manifest.sha256").write_bytes((addr + "\n").encode("ascii"))  # LF, always

    key = load_key(Path(a.key))
    # ADR-0015: sign over the document that will be written, built by the one function that builds
    # role documents. Signing whatever exists at this moment is what made the first attempt degrade
    # to an address-only signature (E-M52).
    _fields = {}
    if a.role == "consistency_verdict":
        _rp = Path(__file__).resolve().parent.parent / "policies" / "risk-classes.json"
        _fields["policy_digest"] = hashlib.sha256(_rp.read_bytes()).hexdigest()
    if a.role == "risk_acceptance":
        _fields.update({
            "accepted_scope": addr,
            "residual_risk": a.residual_risk or ["NC-01", "NC-02"],
            "valid_until": a.valid_until or "2027-01-01",
            "statement": a.statement or "accepted by the named party for the stated period",
        })
    _role_doc = role_document(a.role, a.signer, **_fields)
    sig = (key.sign(signature_payload(addr, _role_doc))
           if getattr(a, "envelope", "v1") == "v2" else key.sign(role_message(addr, _role_doc)))
    (out / "signatures" / f"{a.signer}.sig").write_bytes(base64.b64encode(sig).decode("ascii").encode("ascii") + b"\n")
    (out / "signatures" / f"{a.signer}.pub").write_bytes(
        key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
    # The document is written exactly as it was signed. Building it twice is what let creation and
    # verification disagree on two bytes (E-M52), so `_role_doc` from above is used here, not rebuilt.
    (out / "signatures" / f"{a.signer}.role").write_text(json.dumps(_role_doc), encoding="utf-8")

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
        # The page fixes the file exactly: 64 lowercase hex characters and one LF, 65 bytes.
        _raw = addr_file.read_bytes()
        if len(_raw) != 65 or _raw.count(b"\n") != 1 or not _raw.endswith(b"\n"):
            problems.append(("REPORT_BUNDLE_INCONSISTENT", "manifest.sha256",
                             "64 lowercase hex characters and one LF (65 bytes)",
                             f"{len(_raw)} bytes"))
        addr = _raw.decode("ascii", "replace").strip()
        recomputed = hashlib.sha256(canon(bundle)).hexdigest()
        if addr != recomputed:
            problems.append(("REPORT_BUNDLE_INCONSISTENT", "manifest.sha256",
                             f"address {recomputed[:12]}", f"recorded {addr[:12]}"))

    # 4. at least one signature verifies over the address, from a key supplied out-of-band
    verified = []
    bindings = {}
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
            sig_bytes = base64.b64decode(sigf.read_text(encoding="ascii").strip())
            # ADR-0015: a role signature covers the address AND the role's terms. The address-only
            # form is the older, weaker binding; it is accepted for roles that predate the rule but
            # reported as such, never taken silently (E-M52: silence let a tampered acceptance pass).
            role_path = b / "signatures" / f"{name}.role"
            binding = "v1-address"
            role_doc_here = None
            if role_path.exists():
                try:
                    role_doc_here = json.loads(role_path.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    role_doc_here = None
            if role_doc_here is not None:
                try:
                    key.verify(sig_bytes, signature_payload(addr, role_doc_here))
                    binding = "v2"
                except Exception:  # noqa: BLE001
                    binding = "v1-role"
                    try:
                        key.verify(sig_bytes, role_message(addr, role_doc_here))
                    except Exception:  # noqa: BLE001
                        binding = "v1-address"
            if binding == "v1-address":
                key.verify(sig_bytes, addr.encode("ascii"))
            # ADR-0015: an acceptance whose terms the signature does not cover is the defect B2 of
            # E-M50, so it is refused rather than accepted with a weaker binding.
            if binding == "v1-address" and role_path.exists():
                try:
                    _doc_r = json.loads(role_path.read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    _doc_r = {}
                if _doc_r.get("asserts") == "risk_acceptance":
                    raise ValueError("terms are not covered by this party's signature")
            verified.append(name)
            bindings[name] = binding
        except Exception:  # noqa: BLE001
            problems.append(("MISSING_EVIDENCE", f"signature {name}", "a valid signature over the address",
                             "verification failed"))

    # A file in objects/ that the manifest does not declare is evidence nobody accounted for: the
    # page forbids it, the third-party verifier refused it, and we did not (found by the differential
    # harness E-M57 - our own attacks had never added an undeclared object).
    try:
        declared = set(json.loads((b / "bundle.json").read_text(encoding="utf-8")).get("objects") or {})
    except Exception:  # noqa: BLE001
        declared = set()
    present = {f.name for f in (b / "objects").glob("*") if f.is_file()}
    for extra in sorted(present - declared):
        problems.append(("REPORT_BUNDLE_INCONSISTENT", f"object {extra[:12]}…",
                         "every file under objects/ declared in the manifest",
                         "present but undeclared"))
    for missing in sorted(declared - present):
        problems.append(("MISSING_EVIDENCE", f"object {missing[:12]}…",
                         "a declared object present on disk", "declared but absent"))

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
        "signature_binding": bindings,
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
    c.add_argument("--envelope", choices=["v1", "v2"], default="v1",
                   help="v2 = ADR-0016 single signature binding address+role+scope; NOT yet adopted")
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
