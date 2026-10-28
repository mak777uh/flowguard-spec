#!/usr/bin/env python3
"""E-M66 — differential: the Rust core against the Python core on the same mutations.

Two implementations of one written contract, in two languages, by the same author. That is weaker than the
third-party verifier (which had never seen the code) and stronger than either alone on the classes where a
language hides a mistake: canonicalisation, number formatting, key ordering, enum strictness.

    python lab/e-m66-run.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "fixtures" / "sample-bundle"
RUST = ROOT / "core-rs" / "target" / "debug" / "fg-core.exe"
PYCORE = ROOT / "tools" / "fg_bundle.py"
TRUSTED = [BUNDLE / "signatures" / "demo.pub", BUNDLE / "signatures" / "owner.pub"]
TARGET = "flowguard-sample@2026-10-27"


def run_python(path: Path):
    r = subprocess.run([sys.executable, str(PYCORE), "verify", "--bundle", str(path),
                        "--trusted-keys", *[str(t) for t in TRUSTED],
                        "--expect-target", TARGET], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["verdict"] == "SIGNED_AND_CONSISTENT"
    except Exception:  # noqa: BLE001
        return None


def run_rust(path: Path):
    if not RUST.exists():
        return None
    r = subprocess.run([str(RUST), "verify", "--bundle", str(path),
                        "--trusted-keys", *[str(t) for t in TRUSTED]],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["verdict"] == "SIGNED_AND_CONSISTENT"
    except Exception:  # noqa: BLE001
        return None


def mutations():
    m = []

    def flip(d):
        obj = sorted((d / "objects").glob("*"))[0]
        data = bytearray(obj.read_bytes())
        data[0] ^= 0xFF
        obj.write_bytes(bytes(data))
    m.append(("object byte flipped", flip))

    def edit_role(d):
        p = d / "signatures" / "owner.role"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["statement"] = "withdrawn"
        p.write_text(json.dumps(doc), encoding="utf-8")
    m.append(("role statement edited", edit_role))

    def edit_scope(d):
        p = d / "signatures" / "owner.role"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["accepted_scope"] = "0" * 64
        p.write_text(json.dumps(doc), encoding="utf-8")
    m.append(("accepted_scope rewritten", edit_scope))

    def reformat(d):
        p = d / "bundle.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        p.write_text(json.dumps(doc, indent=4, sort_keys=True), encoding="utf-8")
    m.append(("bundle.json reformatted (must stay valid)", reformat))

    def no_lf(d):
        p = d / "manifest.sha256"
        p.write_text(p.read_text().strip())
    m.append(("manifest without LF", no_lf))

    def crlf(d):
        p = d / "manifest.sha256"
        p.write_bytes(p.read_text().strip().encode() + b"\r\n")
    m.append(("manifest with CRLF", crlf))

    def extra_object(d):
        (d / "objects" / ("a" * 64)).write_bytes(b"extra")
    m.append(("undeclared object added", extra_object))

    def drop_sig(d):
        (d / "signatures" / "demo.sig").unlink()
    m.append(("a signature deleted", drop_sig))

    def bump(d):
        p = d / "bundle.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["bundle_version"] = "fg-bundle/9"
        p.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    m.append(("bundle_version bumped", bump))

    def unicode(d):
        p = d / "bundle.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["claim"]["note_unicode"] = "поток"
        p.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    m.append(("non-ASCII string added (address changes)", unicode))

    return m


def main() -> int:
    rust_ok = run_rust(BUNDLE)
    py_ok = run_python(BUNDLE)
    print(f"valid bundle: python={py_ok} rust={rust_ok}")
    if rust_ok is None:
        print("the Rust core is not built: run cargo build in core-rs/")
        return 1
    if not (rust_ok and py_ok):
        print("the baseline disagrees; nothing below is meaningful")
        return 1

    rows, bad = [], 0
    for name, fn in mutations():
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "b"
        shutil.copytree(BUNDLE, d)
        fn(d)
        py = run_python(d)
        rs = run_rust(d)
        agree = py == rs
        bad += 0 if agree else 1
        rows.append((name, py, rs, agree))
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'mutation':44} {'python':8} {'rust':8} agree")
    for name, py, rs, agree in rows:
        print(f"{name:44} {str(py):8} {str(rs):8} {agree}")
    print(f"\ncases: {len(rows)}, disagreements: {bad}")
    for name, py, rs, agree in rows:
        if not agree:
            print(f"  DISAGREE {name}: python={py} rust={rs}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
