#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone verifier for an `fg-bundle/1` signed artifact.

Written ONLY from sample-bundle/README.md.  No code, spec directory, or
second artifact was consulted.  Standard library only (Ed25519 is
implemented below per RFC 8032), so this runs anywhere Python 3.8+ runs.

Usage:
    python verify_bundle.py <bundle-dir> [--json]
                            [--expected-target SPEC]
                            [--trusted-keys PEMFILE]

Exit status: 0 = SIGNED_AND_CONSISTENT, 2 = refused.

Output: one JSON object on stdout.  A human summary goes to stderr.

Every judgement the README left open is marked `DECISION n` below and is
also listed in DECISIONS.md next to this file.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys

BUNDLE_VERSION = "fg-bundle/1"

# ---------------------------------------------------------------- Ed25519

_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _P - 2, _P)) % _P
_SQRT_M1 = pow(2, (_P - 1) // 4, _P)


def _recover_x(y, sign):
    """Decompress the x-coordinate that goes with y (RFC 8032 5.1.3)."""
    if y >= _P:
        raise ValueError("y out of range")
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        if sign:
            raise ValueError("negative-zero x")
        return 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P != 0:
        x = x * _SQRT_M1 % _P
    if (x * x - x2) % _P != 0:
        raise ValueError("point not on curve")
    if (x & 1) != sign:
        x = _P - x
    return x


def _pt_add(p1, p2):
    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = t1 * 2 * _D * t2 % _P
    d = z1 * 2 * z2 % _P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % _P, g * h % _P, f * g % _P, e * h % _P)


def _pt_mul(scalar, pt):
    acc = (0, 1, 1, 0)  # neutral element
    while scalar > 0:
        if scalar & 1:
            acc = _pt_add(acc, pt)
        pt = _pt_add(pt, pt)
        scalar >>= 1
    return acc


_BASE = (_recover_x(4 * pow(5, _P - 2, _P) % _P, 0), 4 * pow(5, _P - 2, _P) % _P, 1,
         _recover_x(4 * pow(5, _P - 2, _P) % _P, 0) * (4 * pow(5, _P - 2, _P) % _P) % _P)


def _pt_decompress(raw):
    if len(raw) != 32:
        raise ValueError("point is not 32 bytes")
    y = int.from_bytes(raw, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    # on-curve check: -x^2 + y^2 = 1 + d x^2 y^2
    if (-x * x + y * y - 1 - _D * x * x * y * y) % _P != 0:
        raise ValueError("point not on curve")
    return (x, y, 1, x * y % _P)


def _pt_equal(p1, p2):
    x1, y1, z1, _ = p1
    x2, y2, z2, _ = p2
    return (x1 * z2 - x2 * z1) % _P == 0 and (y1 * z2 - y2 * z1) % _P == 0


def ed25519_verify(public_key, signature, message):
    """RFC 8032 5.1.7.  True/False; never raises on bad input."""
    if len(public_key) != 32 or len(signature) != 64:
        return False
    try:
        a = _pt_decompress(public_key)
        r = _pt_decompress(signature[:32])
    except ValueError:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _L:  # non-canonical S is rejected outright
        return False
    k = int.from_bytes(
        hashlib.sha512(signature[:32] + public_key + message).digest(), "little"
    ) % _L
    return _pt_equal(_pt_mul(s, _BASE), _pt_add(r, _pt_mul(k, a)))


# ------------------------------------------------------------- primitives

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_bytes(doc):
    """README §2 / §4: recursive code-point key sort, (",", ":"), no spaces,
    ensure_ascii=False, UTF-8, no trailing newline."""
    text = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def read_pem_pubkey(path):
    """Ed25519 SubjectPublicKeyInfo PEM -> raw 32 bytes (README §6b: identity
    is the raw 32-byte key, not the file name or formatting)."""
    with open(path, "rb") as fh:
        blob = fh.read().decode("ascii", "replace")
    body = []
    inside = False
    for line in blob.splitlines():
        s = line.strip()
        if s.startswith("-----BEGIN"):
            inside = True
            continue
        if s.startswith("-----END"):
            inside = False
            continue
        if inside:
            body.append(s)
    if not body:
        raise ValueError("no PEM body")
    der = base64.b64decode("".join(body))
    # SPKI for Ed25519 is 12 fixed bytes then the 32-byte key:
    # 30 2a 30 05 06 03 2b 65 70 03 21 00 <32 bytes>
    if len(der) == 44 and der[:12] == bytes.fromhex("302a300506032b6570032100"):
        return der[12:]
    if len(der) >= 32:
        return der[-32:]
    raise ValueError("not an Ed25519 SubjectPublicKeyInfo")


def read_sig_file(path):
    """README §1: base64 of 64 raw bytes (+ one LF).  Decode tolerantly by
    stripping surrounding whitespace; interior whitespace is refused."""
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise ValueError("signature file is not ASCII")
    stripped = text.strip()
    if not stripped:
        raise ValueError("signature file is empty")
    if any(ch.isspace() for ch in stripped):
        raise ValueError("interior whitespace in signature file")
    try:
        sig = base64.b64decode(stripped, validate=True)
    except Exception:
        raise ValueError("not valid base64")
    if len(sig) != 64:
        raise ValueError("decoded signature is %d bytes, expected 64" % len(sig))
    return sig


# ---------------------------------------------------------------- refusal

NEXT_ACTION = {
    "REPORT_BUNDLE_INCONSISTENT":
        "rebuild the bundle: bundle.json, objects/ and subjects must describe one "
        "artifact, and bundle_version must be fg-bundle/1 (README 6b)",
    "MISSING_EVIDENCE":
        "supply the missing declared evidence, or re-sign with the message form the "
        "README prescribes; do not treat this bundle as verified",
    "SIGNATURE_ROLE_UNKNOWN":
        "ship .sig, .pub and .role for the same signer id, and use only the roles in "
        "README 8; otherwise report the signer as unbound",
    "LIABILITY_NOT_A_ROLE":
        "remove liability_agreement: a contract cannot be created by a JSON field "
        "(README 8)",
    "RISK_ACCEPTANCE_INCOMPLETE":
        "the acceptance must carry accepted_scope equal to the recorded address, "
        "residual_risk, valid_until and statement (README 6b, 8)",
    "SEPARATION_OF_DUTIES_VIOLATED":
        "risk_acceptance and consistency_verdict must be held by different public "
        "keys (README 7)",
    "TARGET_MISMATCH":
        "re-issue the claim against the target the verifier expects (README 6b)",
    "POLICY_UNTRUSTED":
        "re-sign with a key that the out-of-band trusted set contains (README 6b)",
}


class Refusal(object):
    def __init__(self, code, subject, expected, observed):
        self.code = code
        self.subject = subject
        self.expected = expected
        self.observed = observed

    def as_dict(self):
        return {
            "code": self.code,
            "subject": self.subject,
            "expected": self.expected,
            "observed": self.observed,
            "next_action": NEXT_ACTION.get(self.code, "(no next action recorded)"),
        }


class Report(object):
    def __init__(self):
        self.refusals = []
        self.notes = []
        self.bindings = {}
        self.address_recorded = None
        self.address_recomputed = None
        self.address_used = None
        self.checks = []

    def refuse(self, code, subject, expected, observed):
        self.refusals.append(Refusal(code, subject, expected, observed))

    def note(self, text):
        self.notes.append(text)

    def ok(self, text):
        self.checks.append(text)

    def refused(self):
        return bool(self.refusals)


# ----------------------------------------------------------------- roles
#
# README §8 table.  `allowed` = keys the role document may carry, derived
# from the "inside the role digest" column plus accepted_scope for
# risk_acceptance (README §4: accepted_scope is the only field outside the
# digest, because it must equal the address).
ROLES = {
    "analysis_provenance": {
        "requires": ["issuer"],
        "digest_fields": ["asserts", "issuer"],
    },
    "process_attestation": {
        "requires": ["issuer"],
        "digest_fields": ["asserts", "issuer"],
    },
    "consistency_verdict": {
        "requires": ["issuer", "policy_digest"],
        "digest_fields": ["asserts", "issuer", "policy_digest"],
    },
    "risk_acceptance": {
        "requires": ["issuer", "accepted_scope", "residual_risk",
                     "valid_until", "statement"],
        "digest_fields": ["asserts", "issuer", "residual_risk",
                          "valid_until", "statement"],
    },
}

# DECISION 6: README §6b says LIABILITY_NOT_A_ROLE fires for
# `liability_agreement` "or another key in `not_a_role`", but the contents
# of `not_a_role` are not listed anywhere on the page.  Only the one name
# the page states is recognised.
NOT_A_ROLE = {"liability_agreement"}

SCOPE_FIELD = "accepted_scope"


def allowed_keys(role):
    keys = set(ROLES[role]["digest_fields"]) | {"asserts"}
    if role == "risk_acceptance":
        keys.add(SCOPE_FIELD)
    return keys


def role_bound_message(address_hex, role_doc):
    """README §4:
    message = address_hex || "\\n" || "role:" || sha256(canonical(role doc
              without accepted_scope))
    DECISION 7: "without accepted_scope" = delete the top-level key only.
    """
    stripped = {k: v for k, v in role_doc.items() if k != SCOPE_FIELD}
    digest = sha256_hex(canonical_bytes(stripped))
    return (address_hex + "\n" + "role:" + digest).encode("ascii"), digest


def address_only_message(address_hex):
    """README §3: the address alone, 64 hex chars, ASCII, no prefix/newline/NUL."""
    return address_hex.encode("ascii")


# ------------------------------------------------------------------ checks

def load_json(path):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def target_lock_value(value):
    """DECISION 8 (see DECISIONS.md): the claim carries target_lock as an
    object {"commit": ...} while the inventory carries it as a bare string.
    Normalise both to the commit string before comparing."""
    if isinstance(value, dict):
        if set(value.keys()) == {"commit"}:
            return value["commit"]
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def verify(bundle_dir, expected_target=None, trusted_keys_path=None):
    rep = Report()
    j = lambda *parts: os.path.join(bundle_dir, *parts)

    # ---- 1. bundle_version -------------------------------------------
    bundle_path = j("bundle.json")
    if not os.path.isfile(bundle_path):
        rep.refuse("MISSING_EVIDENCE", "artifact", "bundle.json at the bundle root",
                   "bundle.json absent")
        return rep
    try:
        bundle = load_json(bundle_path)
    except Exception as exc:
        rep.refuse("REPORT_BUNDLE_INCONSISTENT", "artifact",
                   "bundle.json parses as JSON", "parse error: %s" % exc)
        return rep
    if not isinstance(bundle, dict):
        rep.refuse("REPORT_BUNDLE_INCONSISTENT", "artifact",
                   "bundle.json is a JSON object", "top level is %s"
                   % type(bundle).__name__)
        return rep

    version = bundle.get("bundle_version")
    if version != BUNDLE_VERSION:
        rep.refuse("REPORT_BUNDLE_INCONSISTENT", "artifact",
                   "bundle_version == %r" % BUNDLE_VERSION,
                   "bundle_version == %r" % (version,))
    else:
        rep.ok("bundle_version == %s" % BUNDLE_VERSION)

    # ---- 2. required manifest fields ---------------------------------
    # DECISION 1: the page never enumerates the manifest's required fields.
    # Required = every field the page itself relies on somewhere.
    required_top = ["bundle_version", "subjects", "objects", "claim",
                    "inventory_digest"]
    for key in required_top:
        if key not in bundle:
            rep.refuse("MISSING_EVIDENCE", "artifact",
                       "bundle.json carries %r" % key, "field absent")
    claim = bundle.get("claim") if isinstance(bundle.get("claim"), dict) else {}
    if not isinstance(bundle.get("claim"), dict):
        rep.refuse("MISSING_EVIDENCE", "artifact", "claim is an object",
                   "claim is %s" % type(bundle.get("claim")).__name__)
    for key in ["target_lock", "not_claimed"]:
        if key not in claim:
            rep.refuse("MISSING_EVIDENCE", "artifact",
                       "claim carries %r (README 8b)" % key, "field absent")
    if not isinstance(bundle.get("subjects"), dict):
        rep.refuse("MISSING_EVIDENCE", "artifact", "subjects is an object",
                   "subjects is %s" % type(bundle.get("subjects")).__name__)
    if not isinstance(bundle.get("objects"), dict):
        rep.refuse("MISSING_EVIDENCE", "artifact", "objects is an object",
                   "objects is %s" % type(bundle.get("objects")).__name__)

    objects_map = bundle.get("objects") if isinstance(bundle.get("objects"), dict) else {}
    subjects = bundle.get("subjects") if isinstance(bundle.get("subjects"), dict) else {}

    # ---- 3. the address ----------------------------------------------
    recomputed = sha256_hex(canonical_bytes(bundle))
    rep.address_recomputed = recomputed

    manifest_path = j("manifest.sha256")
    recorded = None
    if not os.path.isfile(manifest_path):
        rep.refuse("MISSING_EVIDENCE", "artifact", "manifest.sha256 present",
                   "file absent")
    else:
        with open(manifest_path, "rb") as fh:
            raw = fh.read()
        # README §1: 64 lowercase hex then one LF, 65 bytes.
        if len(raw) == 65 and raw[64:] == b"\n" and _HEX64.match(
                raw[:64].decode("ascii", "replace")):
            recorded = raw[:64].decode("ascii")
            rep.address_recorded = recorded
        else:
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", "artifact",
                       "manifest.sha256 is 64 lowercase hex chars + one LF (65 bytes)",
                       "%d bytes, %r" % (len(raw), raw[:80]))
        if recorded is not None and recorded != recomputed:
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", "artifact",
                       "address recomputed from canonical bundle.json == manifest.sha256",
                       "recomputed %s, recorded %s" % (recomputed, recorded))
        elif recorded is not None:
            rep.ok("address == %s (canonical bundle.json)" % recomputed)

    # The address the rest of the checks must use: the recorded one when the
    # bundle was consistent, else the recomputed one.
    # DECISION 9: the README says "the recorded address"/"address_hex" without
    # saying which of the two when they differ; the recorded value is the
    # artifact's claim about itself and is what a signer would have seen.
    address = recorded if recorded is not None else recomputed
    rep.address_used = address

    # ---- 4. objects: digest, declared byte length, presence ----------
    obj_dir = j("objects")
    for digest, meta in sorted(objects_map.items()):
        if not _HEX64.match(digest):
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", digest,
                       "objects key is 64 lowercase hex characters",
                       repr(digest))
            continue
        if not isinstance(meta, dict):
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", digest,
                       "objects[digest] is an object with bytes/name",
                       "value is %s" % type(meta).__name__)
            continue
        path = os.path.join(obj_dir, digest)
        if not os.path.isfile(path):
            rep.refuse("MISSING_EVIDENCE", digest,
                       "declared object present under objects/", "file absent")
            continue
        with open(path, "rb") as fh:
            data = fh.read()
        actual = sha256_hex(data)
        declared_len = meta.get("bytes")
        if not isinstance(declared_len, int) or isinstance(declared_len, bool):
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", digest,
                       "objects[digest].bytes is an integer",
                       "bytes == %r" % (declared_len,))
        elif declared_len != len(data):
            # DECISION 2: byte-length mismatch is a map/file disagreement ->
            # REPORT_BUNDLE_INCONSISTENT (README 6b row 1 covers "the objects
            # map, the directory and a subject disagree").
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", digest,
                       "objects[digest].bytes == len(objects/<digest>) == %d"
                       % len(data),
                       "declared %d bytes, file is %d bytes"
                       % (declared_len, len(data)))
        if actual != digest:
            # DECISION 3: an object whose bytes no longer hash to its own name.
            # REPORT_BUNDLE_INCONSISTENT (dir disagrees with the map); the other
            # candidate, MISSING_EVIDENCE, is reserved for "absent".
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", digest,
                       "objects/<digest> hashes to its own file name",
                       "file hashes to %s" % actual)
        else:
            rep.ok("object %s: %d bytes, digest ok" % (digest[:12], len(data)))

    # present but undeclared
    if os.path.isdir(obj_dir):
        for name in sorted(os.listdir(obj_dir)):
            full = os.path.join(obj_dir, name)
            if not os.path.isfile(full):
                continue
            if name not in objects_map:
                rep.refuse("REPORT_BUNDLE_INCONSISTENT", name,
                           "every file under objects/ is declared in objects",
                           "present but undeclared")
    elif objects_map:
        rep.refuse("MISSING_EVIDENCE", "artifact", "objects/ directory present",
                   "objects/ absent")

    # ---- 5. subjects and inventory_digest resolve --------------------
    for name, subj in sorted(subjects.items()):
        if not isinstance(subj, dict):
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", str(name),
                       "subjects[%r] is an object" % name,
                       "value is %s" % type(subj).__name__)
            continue
        want = subj.get("sha256")
        if not isinstance(want, str):
            rep.refuse("MISSING_EVIDENCE", str(name),
                       "subjects[%r].sha256 is a digest" % name, "absent")
        elif want not in objects_map:
            rep.refuse("REPORT_BUNDLE_INCONSISTENT", want,
                       "subjects[%r].sha256 is a key in objects" % name,
                       "not declared in objects")

    inv_digest = bundle.get("inventory_digest")
    if not isinstance(inv_digest, str):
        rep.refuse("MISSING_EVIDENCE", "artifact",
                   "inventory_digest is a digest", "absent")
    elif inv_digest not in objects_map:
        rep.refuse("REPORT_BUNDLE_INCONSISTENT", inv_digest,
                   "inventory_digest is a key in objects",
                   "not declared in objects")

    # ---- 6. cross-file equality: target_lock -------------------------
    inventory = None
    if isinstance(inv_digest, str) and _HEX64.match(inv_digest):
        inv_path = os.path.join(obj_dir, inv_digest)
        if os.path.isfile(inv_path):
            try:
                inventory = load_json(inv_path)
            except Exception as exc:
                # DECISION 10: §8b needs the inventory parsed; unparseable
                # inventory means its target_lock cannot be checked.
                rep.refuse("MISSING_EVIDENCE", inv_digest,
                           "inventory object parses as JSON",
                           "parse error: %s" % exc)

    if isinstance(inventory, dict) and "target_lock" in claim:
        lhs = target_lock_value(claim.get("target_lock"))
        rhs = target_lock_value(inventory.get("target_lock"))
        if lhs != rhs:
            # DECISION 11: README 8b says a mismatch is "a refusal" but assigns
            # no code; TARGET_MISMATCH is the code about target locks.
            rep.refuse("TARGET_MISMATCH", "artifact",
                       "claim.target_lock == inventory.target_lock (%r)" % rhs,
                       "%r" % (lhs,))
        else:
            rep.ok("claim.target_lock == inventory.target_lock (%r)" % rhs)

    # target the verifier was told to expect
    if expected_target is not None and "target_lock" in claim:
        lhs = target_lock_value(claim.get("target_lock"))
        if lhs != expected_target:
            rep.refuse("TARGET_MISMATCH", "artifact",
                       "claim.target_lock == expected target %r" % expected_target,
                       "%r" % (lhs,))

    # ---- 7. signatures ------------------------------------------------
    sig_dir = j("signatures")
    signers = {}
    pubkeys = {}

    if not os.path.isdir(sig_dir):
        rep.refuse("MISSING_EVIDENCE", "artifact", "signatures/ directory present",
                   "absent")
    else:
        names = sorted(os.listdir(sig_dir))
        ids = sorted({os.path.splitext(n)[0] for n in names
                      if os.path.isfile(os.path.join(sig_dir, n))})
        for signer in ids:
            have_role = os.path.isfile(os.path.join(sig_dir, signer + ".role"))
            have_sig = os.path.isfile(os.path.join(sig_dir, signer + ".sig"))
            have_pub = os.path.isfile(os.path.join(sig_dir, signer + ".pub"))
            signers[signer] = {"role": have_role, "sig": have_sig, "pub": have_pub}

            if have_role and not (have_sig and have_pub):
                # README 6b: SIGNATURE_ROLE_UNKNOWN when a .role exists without
                # a .sig or a .pub from the same party.
                missing = [x for x, ok in ((".sig", have_sig), (".pub", have_pub))
                           if not ok]
                rep.refuse("SIGNATURE_ROLE_UNKNOWN", signer,
                           "a .role file is accompanied by .sig and .pub",
                           "missing %s" % ", ".join(missing))
                continue
            if not have_role and not have_sig:
                continue  # a stray .pub alone binds nothing
            if have_sig and not have_pub:
                rep.refuse("MISSING_EVIDENCE", signer,
                           ".pub for the signer to verify .sig with", "absent")
                continue

            # public key
            try:
                pub = read_pem_pubkey(os.path.join(sig_dir, signer + ".pub"))
            except Exception as exc:
                rep.refuse("MISSING_EVIDENCE", signer,
                           "Ed25519 SubjectPublicKeyInfo PEM decodes to 32 bytes",
                           "error: %s" % exc)
                continue
            pubkeys[signer] = pub

            # signature bytes
            try:
                sig = read_sig_file(os.path.join(sig_dir, signer + ".sig"))
            except Exception as exc:
                rep.refuse("MISSING_EVIDENCE", signer,
                           "base64 of 64 raw Ed25519 bytes plus optional trailing "
                           "whitespace", "error: %s" % exc)
                continue

            role_doc = None
            if have_role:
                try:
                    role_doc = load_json(os.path.join(sig_dir, signer + ".role"))
                except Exception as exc:
                    rep.refuse("SIGNATURE_ROLE_UNKNOWN", signer,
                               "role document parses as a JSON object",
                               "parse error: %s" % exc)
                    continue
                if not isinstance(role_doc, dict):
                    rep.refuse("SIGNATURE_ROLE_UNKNOWN", signer,
                               "role document is a JSON object",
                               "top level is %s" % type(role_doc).__name__)
                    continue

            if role_doc is not None:
                refusal, binding = check_role_document(
                    rep, signer, role_doc, pub, sig, address, bundle)
                if binding:
                    rep.bindings[signer] = binding
                if refusal:
                    continue
            else:
                # README §3: no .role -> address-only form.
                if ed25519_verify(pub, sig, address_only_message(address)):
                    rep.bindings[signer] = "address"
                    rep.ok("%s: address-only binding verifies (weaker, README 3)"
                           % signer)
                else:
                    rep.refuse("MISSING_EVIDENCE", signer,
                               "signature verifies over the applicable message form "
                               "(address alone, ASCII, no newline)",
                               "Ed25519 verify failed over %r" % address)

    # ---- 8. separation of duties -------------------------------------
    # README §7: compared by raw public-key bytes, not by file name.
    holders = {}
    for signer, binding in rep.bindings.items():
        role = signers.get(signer, {})
        if not role.get("role"):
            continue
        try:
            doc = load_json(os.path.join(sig_dir, signer + ".role"))
        except Exception:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("asserts"), str):
            holders.setdefault(doc["asserts"], []).append(signer)
    risk = holders.get("risk_acceptance", [])
    verdict = holders.get("consistency_verdict", [])
    for r in risk:
        for v in verdict:
            if r not in pubkeys or v not in pubkeys:
                continue
            if pubkeys[r] == pubkeys[v]:
                rep.refuse("SEPARATION_OF_DUTIES_VIOLATED",
                           "%s / %s" % (r, v),
                           "risk_acceptance and consistency_verdict hold different "
                           "public keys",
                           "both are %s" % pubkeys[r].hex())
    if risk and verdict and not any(x.code == "SEPARATION_OF_DUTIES_VIOLATED"
                                    for x in rep.refusals):
        rep.ok("separation of duties: %s and %s differ by key" % (risk[0], verdict[0]))

    # ---- 8b. no signing evidence at all ------------------------------
    # DECISION 14: the page never says how many signers a bundle must carry,
    # but §6 forbids printing a success it cannot support, and a bundle with
    # no verifying signature supports nothing.
    if not rep.bindings and not rep.refused():
        rep.refuse("MISSING_EVIDENCE", "artifact",
                   "at least one signature that verifies over a message form in "
                   "README 3", "no signer produced any binding")
    # DECISION 15: nothing on the page makes risk_acceptance or
    # consistency_verdict mandatory, so their absence is reported, not refused.
    for role in ("risk_acceptance", "consistency_verdict"):
        if role not in holders:
            rep.note("no signer asserts %s; the page does not say it is required, "
                     "so this is reported and not refused" % role)

    # ---- 9. out-of-band trust (optional) ------------------------------
    if trusted_keys_path:
        try:
            trusted = set()
            with open(trusted_keys_path, "rb") as fh:
                text = fh.read().decode("ascii", "replace")
            for chunk in text.split("-----BEGIN PUBLIC KEY-----")[1:]:
                body = chunk.split("-----END PUBLIC KEY-----")[0]
                der = base64.b64decode("".join(body.split()))
                trusted.add(der[-32:])
        except Exception as exc:
            rep.refuse("POLICY_UNTRUSTED", "artifact",
                       "trusted-key file parses as PEM public keys",
                       "error: %s" % exc)
            trusted = set()
        for signer, pub in sorted(pubkeys.items()):
            if pub not in trusted:
                rep.refuse("POLICY_UNTRUSTED", signer,
                           "signing key in the out-of-band trusted set",
                           "key %s not trusted" % pub.hex())

    # ---- 10. inventory arithmetic: report, do not refuse -------------
    if isinstance(inventory, dict):
        total = inventory.get("paths_total")
        listed = inventory.get("paths")
        if isinstance(total, int) and isinstance(listed, list) and total != len(listed):
            # README 8b: may be reported, must not be treated as a contradiction.
            rep.note("inventory paths_total=%d but %d path entries listed; "
                     "per README 8b this is reported, not a refusal"
                     % (total, len(listed)))

    return rep


def check_role_document(rep, signer, role_doc, pub, sig, address, bundle):
    """All role-level checks.  Returns (refused?, binding or None)."""
    asserts = role_doc.get("asserts")

    # DECISION 4: `asserts` absent is not covered by any row of 6b.  A role
    # document with no role is not a role -> SIGNATURE_ROLE_UNKNOWN (its row
    # already covers "asserts is not one of README 8's roles").
    if not isinstance(asserts, str):
        rep.refuse("SIGNATURE_ROLE_UNKNOWN", signer,
                   "role document carries asserts naming one of README 8's roles",
                   "asserts == %r" % (asserts,))
        return True, None

    if asserts in NOT_A_ROLE:
        rep.refuse("LIABILITY_NOT_A_ROLE", signer,
                   "asserts is a role, not a contract (README 8: liability_agreement "
                   "is not a role)",
                   "asserts == %r" % asserts)
        return True, None

    if asserts not in ROLES:
        rep.refuse("SIGNATURE_ROLE_UNKNOWN", signer,
                   "asserts one of %s" % sorted(ROLES),
                   "asserts == %r" % asserts)
        return True, None

    # keys the role may carry
    allowed = allowed_keys(asserts)
    extra = sorted(set(role_doc) - allowed)
    if extra:
        # README §4 + 6b row 1: a key §8 does not list is refused.
        rep.refuse("REPORT_BUNDLE_INCONSISTENT", signer,
                   "%s role may carry only %s" % (asserts, sorted(allowed)),
                   "unexpected key(s) %s" % extra)
        return True, None

    # required fields
    for key in ROLES[asserts]["requires"]:
        if key not in role_doc:
            if asserts == "risk_acceptance":
                rep.refuse("RISK_ACCEPTANCE_INCOMPLETE", signer,
                           "risk_acceptance carries %r" % key, "field absent")
                return True, None
            # DECISION 5: missing required field for a non-risk role has no
            # dedicated code; MISSING_EVIDENCE is the closest row.
            rep.refuse("MISSING_EVIDENCE", signer,
                       "%s carries %r (README 8)" % (asserts, key), "field absent")
            return True, None

    if asserts == "risk_acceptance":
        if not isinstance(role_doc.get(SCOPE_FIELD), str):
            rep.refuse("RISK_ACCEPTANCE_INCOMPLETE", signer,
                       "accepted_scope is a string equal to the address",
                       "accepted_scope == %r" % (role_doc.get(SCOPE_FIELD),))
            return True, None

    # issuer must equal the file stem (README §8)
    if role_doc.get("issuer") != signer:
        # DECISION 12: no code is assigned to an issuer/stem disagreement.
        rep.refuse("MISSING_EVIDENCE", signer,
                   "issuer == signer id %r (the file stem, README 8)" % signer,
                   "issuer == %r" % (role_doc.get("issuer"),))
        return True, None

    # policy_digest is a reference to an external document and cannot be
    # checked here (README §8).  Noted so silence is not mistaken for a pass.
    if asserts == "consistency_verdict":
        rep.note("%s: policy_digest %r is an external reference; not checkable "
                 "from the bundle (README 8)" % (signer, role_doc.get("policy_digest")))

    # signature over the §4 message
    message, digest = role_bound_message(address, role_doc)
    if not ed25519_verify(pub, sig, message):
        rep.refuse("MISSING_EVIDENCE", signer,
                   "Ed25519 signature over address_hex || '\\n' || 'role:' || "
                   "sha256(canonical(role minus accepted_scope)) [expected digest %s]"
                   % digest,
                   "signature does not verify over that message")
        return True, None
    rep.ok("%s: role-bound signature verifies (%s, digest %s…)"
           % (signer, asserts, digest[:16]))

    # accepted_scope versus the recorded address (README 6b line 128)
    if asserts == "risk_acceptance":
        scope = role_doc.get(SCOPE_FIELD)
        if scope != address:
            rep.refuse("RISK_ACCEPTANCE_INCOMPLETE", signer,
                       "accepted_scope == recorded address %s" % address,
                       "accepted_scope == %s" % scope)
            return True, "role"
        # residual_risk must equal the claim's not_claimed set (README 8b).
        not_claimed = bundle.get("claim", {}).get("not_claimed")
        if isinstance(not_claimed, list):
            lhs = role_doc.get("residual_risk")
            if not isinstance(lhs, list) or set(map(str, lhs)) != set(map(str, not_claimed)):
                # DECISION 13: 8b mandates the check but assigns no code;
                # RISK_ACCEPTANCE_INCOMPLETE is the row about the acceptance.
                rep.refuse("RISK_ACCEPTANCE_INCOMPLETE", signer,
                           "residual_risk == claim.not_claimed %s as sets"
                           % sorted(map(str, not_claimed)),
                           "residual_risk == %r" % (lhs,))
                return True, "role"
            rep.ok("%s: residual_risk == claim.not_claimed %s"
                   % (signer, sorted(set(map(str, lhs)))))
    return False, "role"


# -------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify an fg-bundle/1 signed artifact.")
    ap.add_argument("bundle", help="path to the bundle directory")
    ap.add_argument("--expected-target", default=None,
                    help="the target lock the verifier expects out of band")
    ap.add_argument("--trusted-keys", default=None,
                    help="PEM file of public keys trusted out of band")
    ap.add_argument("--json", action="store_true", help="JSON only on stdout")
    args = ap.parse_args(argv)

    rep = verify(args.bundle, args.expected_target, args.trusted_keys)

    out = {
        "verdict": ("SIGNED_AND_CONSISTENT" if not rep.refused()
                    else "REFUSED"),
        "bundle_version_expected": BUNDLE_VERSION,
        "address": {
            "recorded": rep.address_recorded,
            "recomputed": rep.address_recomputed,
            "match": (rep.address_recorded is not None
                      and rep.address_recorded == rep.address_recomputed),
        },
        "signature_binding": dict(sorted(rep.bindings.items())),
        "refusals": [r.as_dict() for r in rep.refusals],
        "checks_passed": rep.checks,
        "notes": rep.notes,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

    if not args.json:
        print("", file=sys.stderr)
        print("address recorded   : %s" % rep.address_recorded, file=sys.stderr)
        print("address recomputed : %s" % rep.address_recomputed, file=sys.stderr)
        print("signature_binding  : %s"
              % json.dumps(dict(sorted(rep.bindings.items()))), file=sys.stderr)
        if rep.refused():
            print("REFUSED:", file=sys.stderr)
            for r in rep.refusals:
                print("  %-32s %s" % (r.code, r.subject), file=sys.stderr)
        else:
            print("SIGNED_AND_CONSISTENT", file=sys.stderr)
    return 0 if not rep.refused() else 2


if __name__ == "__main__":
    sys.exit(main())
