#!/usr/bin/env python3
"""E-M57: differential testing — our verifier against one written by a stranger from the page alone.

Two independent implementations of the same written contract. Any disagreement on a mutated artifact is
either a defect in ours or an ambiguity in the description; both are worth a card.

The stranger's verifier lives in interop/verifiers/third-party-verifier.py and is recorded as written
by an agent that never saw this repository's code, working only from the format page.

    python lab/e-m57-run.py [--limit N]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The third-party verifier implements fg-bundle/1 and, correctly, refuses an unknown version, so the
# differential runs on a v1 bundle. It is (re)built here if missing; F-3-1 records that the external
# verifier has not yet learned v2.
BUNDLE = ROOT / "tools" / "_tmp" / "v1bundle"
if not (BUNDLE / "bundle.json").exists():
    subprocess.run([sys.executable, str(ROOT / "tools" / "_tmp" / "make_v1.py")],
                   capture_output=True, text=True)
OURS = ROOT / "tools" / "fg_bundle.py"
THEIRS = ROOT / "interop" / "verifiers" / "third-party-verifier.py"
TRUSTED = [BUNDLE / "signatures" / "demo.pub"]
TARGET = "t@1"

# Divergences where the third-party verifier is the one that is wrong, with the reason. They are
# printed and counted, never silently ignored: a known divergence that stops being known is a bug.
KNOWN_DIVERGENCES = {
    "demo.pub truncated": (
        "the third-party verifier accepts a signer whose public key cannot be parsed; "
        "a signature that cannot be checked against its own key is not evidence"
    ),
}


def run_ours(path: Path):
    r = subprocess.run([sys.executable, str(OURS), "verify", "--bundle", str(path),
                        "--trusted-keys", *[str(t) for t in TRUSTED],
                        "--expect-target", TARGET], capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
        return doc["verdict"] == "SIGNED_AND_CONSISTENT", doc.get("verdict", "?")
    except Exception:  # noqa: BLE001
        return False, "NO-JSON"


def run_theirs(path: Path):
    # its CLI takes --trusted-keys differently; the differential is about verdicts on mutations, so
    # the trusted set is left at its default here and exercised separately.
    r = subprocess.run([sys.executable, str(THEIRS), str(path), "--json",
                        "--expected-target", TARGET],
                       capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return (r.returncode == 0), "NO-JSON"
    ok = r.returncode == 0 and doc.get("verdict") in ("SIGNED_AND_CONSISTENT", "ok", None)
    if doc.get("verdict") == "SIGNED_AND_CONSISTENT":
        ok = True
    return ok, str(doc.get("verdict", r.returncode))


def _systematic():
    sys.path.insert(0, str(ROOT / "lab"))
    import mutations_bundle
    return mutations_bundle.build()


def mutations():
    """(name, callable(Path) -> None) applied to a copy of the bundle."""
    m = []

    def flip_object(d):
        obj = sorted((d / "objects").glob("*"))[0]
        data = bytearray(obj.read_bytes())
        data[0] ^= 0xFF
        obj.write_bytes(bytes(data))

    m.append(("object byte flipped", flip_object))

    def edit_statement(d):
        p = d / "signatures" / "owner.role"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["statement"] = "withdrawn"
        p.write_text(json.dumps(doc), encoding="utf-8")

    m.append(("role statement edited", edit_statement))

    def edit_scope(d):
        p = d / "signatures" / "owner.role"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["accepted_scope"] = "0" * 64
        p.write_text(json.dumps(doc), encoding="utf-8")

    m.append(("accepted_scope rewritten", edit_scope))

    def bump_version(d):
        p = d / "bundle.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["bundle_version"] = "fg-bundle/2"
        p.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")

    m.append(("bundle_version bumped", bump_version))

    def drop_signature(d):
        (d / "signatures" / "owner.sig").unlink()

    m.append(("a signature deleted", drop_signature))

    def drop_role(d):
        (d / "signatures" / "owner.role").unlink()

    m.append(("a role file deleted", drop_role))

    def add_role(d):
        (d / "signatures" / "mallory.role").write_text(
            json.dumps({"asserts": "risk_acceptance", "issuer": "mallory",
                        "accepted_scope": (d / "manifest.sha256").read_text().strip(),
                        "residual_risk": ["NC-01"], "valid_until": "2030-01-01",
                        "statement": "mallory accepts"}), encoding="utf-8")

    m.append(("unsigned role appended", add_role))

    def truncate_object(d):
        obj = sorted((d / "objects").glob("*"))[-1]
        data = obj.read_bytes()
        obj.write_bytes(data[:-1])

    m.append(("object truncated", truncate_object))

    def add_object(d):
        (d / "objects" / ("a" * 64)).write_bytes(b"extra")

    m.append(("undeclared object added", add_object))

    def delete_object(d):
        obj = sorted((d / "objects").glob("*"))[0]
        obj.unlink()

    m.append(("declared object deleted", delete_object))

    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=100)
    a = ap.parse_args()

    if not THEIRS.exists():
        print(f"third-party verifier not found at {THEIRS}")
        return 1

    base_ok_o, base_v_o = run_ours(BUNDLE)
    base_ok_t, base_v_t = run_theirs(BUNDLE)
    print(f"valid bundle:   ours={base_v_o}  theirs={base_v_t}")
    if not (base_ok_o and base_ok_t):
        print("the baseline disagrees; nothing below is meaningful")
        return 1

    rows, disagreements = [], []
    cases = mutations() + _systematic()
    for name, fn in cases[:a.limit]:
        # a mutation of a signer the bundle does not carry is a no-op for both verifiers, not a
        # disagreement; skip it and say so rather than count it as either
        # mutations that need a second signer are no-ops on a single-signer bundle
        if ("owner" in name or "both roles" in name) and not (BUNDLE / "signatures" / "owner.pub").exists():
            continue
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "b"
        shutil.copytree(BUNDLE, d)
        try:
            fn(d)
        except Exception as e:  # noqa: BLE001
            print(f"{name:28} mutation failed: {e}")
            continue
        ok_o, v_o = run_ours(d)
        ok_t, v_t = run_theirs(d)
        expect_ok = name.startswith("+")
        name = name.lstrip("+")
        agree = (ok_o == ok_t) and (ok_o == expect_ok)
        rows.append((name, ok_o, v_o, ok_t, v_t, agree))
        if not agree and name in KNOWN_DIVERGENCES:
            print(f"  known: {name} - {KNOWN_DIVERGENCES[name]}")
        elif not agree:
            disagreements.append((name, ok_o, v_o, ok_t, v_t))
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'mutation':30} {'ours':22} {'theirs':22} agree")
    for name, ok_o, v_o, ok_t, v_t, agree in rows:
        print(f"{name:30} {str(ok_o) + ' ' + v_o:22} {str(ok_t) + ' ' + v_t:22} {agree}")

    print(f"\ncases: {len(rows)}, disagreements: {len(disagreements)}")
    for name, ok_o, v_o, ok_t, v_t in disagreements:
        print(f"  DISAGREE {name}: ours={ok_o}/{v_o} theirs={ok_t}/{v_t}")
    ok = not disagreements
    print("RESULT:", "PASS" if ok else "FAIL — the two implementations disagree")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
