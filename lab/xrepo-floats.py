"""Non-integer numbers in the canonical form: do our address and a JavaScript one agree?

LexSpec refuses floats outright. FlowGuard accepts them, and ships artifacts that contain `0.9` and `0.0`.
That means the address depends on how a given language renders a float - and JSON has no single answer:
Python writes `1.0`, JavaScript writes `1`, and both are the same value.

This script measures the class instead of asserting it: Python's canonical bytes against Node's
`JSON.stringify` for a set of numbers, and a scan of the repository's own artifacts for non-integer numbers.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import importlib.util

spec = importlib.util.spec_from_file_location("fgb", ROOT / "tools" / "fg_bundle.py")
fgb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fgb)

NUMBERS = [1.0, 0.5, 0.9, 0.1, 1e21, 1e-7, 1234567890123456789.0, 2.0 ** 53, -0.0, 100.0]


def js_canonical(values):
    script = (
        "const v=" + json.dumps(values) + ";"
        "console.log(JSON.stringify(v.map(x=>JSON.stringify({n:x}))));"
    )
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def main() -> int:
    js = js_canonical(NUMBERS)
    print(f"{'value':24} {'python bytes':22} {'javascript bytes':22} same")
    bad = 0
    for i, v in enumerate(NUMBERS):
        py = fgb.canon({"n": v}).decode()
        jsb = js[i] if js else "node unavailable"
        same = py == jsb
        bad += 0 if same else 1
        print(f"{repr(v):24} {py:22} {jsb:22} {same}")

    # and the artifacts we actually ship
    print("\nnon-integer numbers in shipped artifacts:")
    hits = 0
    for path in list(ROOT.glob("fixtures/**/*.json")) + list(ROOT.glob("inbox/*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        for token in ("0.9", "0.0", "0.5", "0.75", "0.15", "0.40"):
            if token in text:
                hits += 1
                print(f"  {path.relative_to(ROOT)} contains {token}")
                break
    if not hits:
        print("  none")

    print(f"\nrendering disagreements: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL - the address is language-dependent for these values")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
