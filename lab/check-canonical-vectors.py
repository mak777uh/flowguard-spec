#!/usr/bin/env python3
"""check-canonical-vectors — what our canonical form does with the RFC 8785 numbers.

A canonical form is a contract between implementations. Ours was written before anyone checked it against a
published rule, and `E-M71` measured the consequence: 6 of 10 floats serialise differently in Python and in
JavaScript, so two honest implementations disagree about the same document.

This harness feeds the published number cases into our own canonicaliser and reports, per case, what we emit
and what the rule requires. It is a *report* by default because the current answer is wrong on most cases;
`--strict` exists so the day the implementation lands, the same command becomes the gate and no other code has
to change.

    python lab/check-canonical-vectors.py            # report, exit 0
    python lab/check-canonical-vectors.py --strict   # exit 1 if any case disagrees
"""
import argparse
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VECTORS = ROOT / "lab" / "vectors" / "rfc8785-numbers.json"


def load_canonical():
    spec = importlib.util.spec_from_file_location("fgb", ROOT / "tools" / "fg_bundle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.canon


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    canonical = load_canonical()
    cases = json.loads(VECTORS.read_text(encoding="utf-8"))["vectors"]

    passed, failed = 0, []
    for case in cases:
        raw = case["input"]
        value = json.loads(raw)
        got = canonical({"n": value}).decode()
        got = got[len('{"n":'):-1]
        if got == case["expected"]:
            passed += 1
        else:
            failed.append((raw, got, case["expected"], case["why"]))

    print(f"vectors: {len(cases)}, reproduced: {passed}, divergent: {len(failed)}")
    for raw, got, want, why in failed:
        print(f"  {raw:>18} -> {got:<24} rule wants {want:<24} ({why})")
    if failed:
        print("note: the canonicaliser predates the rule; the divergence is the measured defect, not the test")
    print("RESULT:", "ok" if not failed else ("fail" if a.strict else "reported"))
    return 0 if (not failed or not a.strict) else 1


if __name__ == "__main__":
    sys.exit(main())
