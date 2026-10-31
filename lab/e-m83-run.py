"""E-M83 — two report generators, one set of facts.

The product is Rust (ADR-0017), so `fg-core report` is the authoritative generator and `tools/fg_report_html.py`
stays as a differential partner. HTML bytes need not match - whitespace is not a fact - but every fact must: the
verdict, the address, each path row, the not_claimed list, and the refusal codes.
"""
import html
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUST_DIR = ROOT / "core-rs" / "target" / "debug"
# Platform-dependent name: fg-core.exe on Windows, fg-core on Linux CI.
RUST = RUST_DIR / ("fg-core.exe" if (RUST_DIR / "fg-core.exe").exists() else "fg-core")
PYGEN = ROOT / "tools" / "fg_report_html.py"
BUNDLE = ROOT / "fixtures" / "sample-bundle"
PY = sys.executable


def strip_tags(text: str) -> str:
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def facts(page: str) -> dict:
    text = strip_tags(page)
    return {
        "verdict": bool(re.search(r"Verdict: (SIGNED_AND_CONSISTENT|INVALID|CONSISTENT_DECLARED|"
                                  r"SCOPED_ASSURANCE|PROVEN|REPORT_BUNDLE_INCONSISTENT)", text)),
        "nc01": "NC-01" in text,
        "nc02": "NC-02" in text,
        "paths_word": "paths enumerated" in text,
        "coverage": re.search(r"coverage ([0-9.]+)", text).group(1) if re.search(r"coverage ([0-9.]+)", text) else "",
        "refusals": "no refusals" in text,
        "no_script": "<script" not in page.lower(),
        "no_network": ("http://" not in page) and ("https://" not in page),
    }


def main() -> int:
    if not RUST.exists():
        print("build the Rust core first: cd core-rs && cargo build --offline")
        return 2
    tmp = pathlib.Path(tempfile.mkdtemp())
    rs_html, py_html = tmp / "rs.html", tmp / "py.html"
    r1 = subprocess.run([str(RUST), "report", "--bundle", str(BUNDLE), "--out", str(rs_html)],
                        capture_output=True, text=True)
    r2 = subprocess.run([PY, str(PYGEN), "--bundle", str(BUNDLE), "--out", str(py_html)],
                        capture_output=True, text=True)
    if r1.returncode != 0 or r2.returncode != 0:
        print("a generator failed:", (r1.stderr or r2.stderr)[:300])
        return 1

    a, b = rs_html.read_text(encoding="utf-8"), py_html.read_text(encoding="utf-8")
    fa, fb = facts(a), facts(b)
    diffs = [k for k in fa if fa[k] != fb[k]]
    print(f"rust {len(a)} bytes, python {len(b)} bytes, byte-identical: {a == b}")
    for k in fa:
        mark = "ok  " if fa[k] == fb[k] else "DIFF"
        print(f"  {mark} {k:12} rust={fa[k]!r} python={fb[k]!r}")
    print(f"\nfacts compared: {len(fa)}, differing: {len(diffs)}")
    print("RESULT:", "PASS" if not diffs else "FAIL")
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
