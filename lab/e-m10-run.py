#!/usr/bin/env python3
"""E-M10 harness: does the bundle verifier's refusal generalise beyond six hand-made cases?

E-M9 tested six substitutions someone thought of. This measures the same verifier against a
generated corpus with declared classes, per the pre-registration in
lab/experiments/E-M10-instrument-evidence.md.

Independence rule (written before the run): the **generator** below does not import the verifier.
It re-implements canonical JSON and signing from the format description alone. The verifier is
imported only to be the subject of the measurement.

    python lab/e-m10-run.py [--per-class 17] [--valid 30]
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE_CLI = ROOT / "tools" / "fg_bundle.py"

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, PublicFormat,
                                                          NoEncryption, load_pem_private_key)


def load_verifier():
    spec = importlib.util.spec_from_file_location("fgb", BUNDLE_CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canon(doc) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def mutate(bundle_dir: Path, kind: str, i: int, base_key: Path, mallory: Ed25519PrivateKey) -> None:
    """Produce one mutant in place. Deliberately independent of the verifier's code."""
    bj = bundle_dir / "bundle.json"
    bundle = json.loads(bj.read_text(encoding="utf-8"))
    tag = f"mutant-{kind}-{i}".encode()

    if kind in ("code", "build", "config"):
        name = kind
        old = bundle["subjects"][name]["sha256"]
        payload = (bundle_dir / "objects" / old).read_bytes() + b"\n# " + tag + b"\n"
        new = sha(payload)
        (bundle_dir / "objects" / new).write_bytes(payload)
        bundle["subjects"][name]["sha256"] = new
        bundle["objects"][new] = {"bytes": len(payload), "name": name}
        # the address and the signature are NOT recomputed: tampering after signing
        bj.write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
        return

    if kind == "identity":
        addr = (bundle_dir / "manifest.sha256").read_text(encoding="ascii").strip()
        for f in list((bundle_dir / "signatures").glob("*.sig")):
            f.unlink()
        for f in list((bundle_dir / "signatures").glob("*.pub")):
            f.unlink()
        sig = mallory.sign(addr.encode("ascii"))
        import base64
        (bundle_dir / "signatures" / f"mallory{i}.sig").write_text(
            base64.b64encode(sig).decode("ascii") + "\n", encoding="ascii")
        (bundle_dir / "signatures" / f"mallory{i}.pub").write_bytes(
            mallory.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
        return

    if kind in ("pair", "pair_consistent"):
        bundle["claim"]["target_lock"] = {"commit": f"target@other-{i}"}
        if kind == "pair_consistent":
            bundle["claim"]["target_lock"]["note"] = "looks intentional"
        bj.write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
        addr = sha(canon(bundle))
        (bundle_dir / "manifest.sha256").write_text(addr + "\n", encoding="ascii")
        for f in list((bundle_dir / "signatures").glob("*.sig")):
            f.unlink()
        key = load_pem_private_key(base_key.read_bytes(), password=None)
        import base64
        (bundle_dir / "signatures" / "alice.sig").write_text(
            base64.b64encode(key.sign(addr.encode("ascii"))).decode("ascii") + "\n", encoding="ascii")
        return

    raise SystemExit(f"unknown class {kind}")


CLASSES = ["code", "build", "config", "identity", "pair", "pair_consistent"]
THRESHOLDS = {"D1": 0.95, "D2": 0.90, "false_rejection": 0.05}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=17)
    ap.add_argument("--valid", type=int, default=30)
    a = ap.parse_args()

    fgb = load_verifier()
    tmp = Path(tempfile.mkdtemp())
    alice_key = tmp / "alice.key"

    def make(target: str, code_text: str, out: Path):
        (tmp / "c.py").write_text(code_text, encoding="utf-8")
        (tmp / "b.json").write_text('{"compiler":"cpython"}', encoding="utf-8")
        (tmp / "cfg.yml").write_text("limit: 1000\n", encoding="utf-8")
        (tmp / "id.txt").write_text("service: bank-api\n", encoding="utf-8")
        claim = tmp / "claim.json"
        claim.write_text(json.dumps({
            "claim_id": "E-M10", "target_lock": {"commit": target},
            "declared_control_point": "function:bank.transfer",
            "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0, "excluded": [],
        }), encoding="utf-8")
        inv = tmp / "inv.json"
        inv.write_text(json.dumps({"paths": [], "sources": []}), encoding="utf-8")
        r = subprocess.run([sys.executable, str(BUNDLE_CLI), "create", "--out", str(out),
                            "--claim", str(claim), "--inventory", str(inv),
                            "--subject", f"code={tmp / 'c.py'}", "--subject", f"build={tmp / 'b.json'}",
                            "--subject", f"config={tmp / 'cfg.yml'}", "--subject", f"identity={tmp / 'id.txt'}",
                            "--key", str(alice_key), "--signer", "alice"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr)
            raise SystemExit("bundle creation failed")
        return out

    base = make("target@e-m10", "def transfer(a,b,x):\n    return a-x, b+x\n", tmp / "base")
    trusted = [str(base / "signatures" / "alice.pub")]
    mallory = Ed25519PrivateKey.generate()

    def verify(path: Path, expected_target="target@e-m10"):
        ns = argparse.Namespace(bundle=str(path), trusted_keys=trusted, expect_target=expected_target)
        return fgb.verify_bundle(ns)

    # --- valid set: 30 correct bundles, none may be rejected
    false_rej = 0
    for i in range(a.valid):
        b = make(f"target@valid-{i}", f"def transfer(a,b,x):\n    return a-x, b+x  # {i}\n",
                 tmp / f"valid-{i}")
        ns = argparse.Namespace(bundle=str(b), trusted_keys=trusted, expect_target=f"target@valid-{i}")
        out, code = fgb.verify_bundle(ns)
        if out["verdict"] != "SIGNED_AND_CONSISTENT":
            false_rej += 1
    fr = false_rej / a.valid
    print(f"valid bundles: {a.valid}, false rejections: {false_rej} ({fr:.3f})")

    # --- mutated corpus
    results = {}
    for cls in CLASSES:
        caught = 0
        for i in range(a.per_class):
            d = tmp / f"m-{cls}-{i}"
            shutil.copytree(base, d)
            mutate(d, cls, i, alice_key, mallory)
            out, code = verify(d)
            if cls in ("code", "build", "config", "identity"):
                caught += out["verdict"] == "INVALID"
            else:
                caught += out["verdict"] != "SIGNED_AND_CONSISTENT"
        results[cls] = caught / a.per_class
        print(f"{cls:16} detected {caught}/{a.per_class} = {results[cls]:.3f}")

    d1 = sum(results[c] for c in ("code", "build", "config", "identity")) / 4
    d2 = sum(results[c] for c in ("pair", "pair_consistent")) / 2
    print(f"\nD-1 combined detection: {d1:.3f}  (threshold >= {THRESHOLDS['D1']})")
    print(f"D-2 combined detection: {d2:.3f}  (threshold >= {THRESHOLDS['D2']})")
    print(f"false rejection:        {fr:.3f}  (threshold <= {THRESHOLDS['false_rejection']})")
    print(f"corpus: {a.per_class * len(CLASSES)} mutants, {a.valid} valid")

    ok = d1 >= THRESHOLDS["D1"] and d2 >= THRESHOLDS["D2"] and fr <= THRESHOLDS["false_rejection"]
    print(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
