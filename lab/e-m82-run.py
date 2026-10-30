"""E-M82 — decomposing a claimant's text into checkable units.

The request: take a spec, or the claimant's text of intentions, split it into precise units, and hand those to a
defended core. The deterministic part of that is classification with a named fate per sentence, and the honest
part is refusing the sentences that can never become units.

Cases:
1. an absolute ("guarantees", "always") is refused, not weakened;
2. an action sentence becomes a `measured` unit that names what it still needs;
3. a policy sentence becomes a `requirement` and an unverifiable condition an `assumption`;
4. nothing is silently dropped: every sentence appears as a unit.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "fg_decompose.py"
PY = sys.executable
tmp = pathlib.Path(tempfile.mkdtemp())

TEXTS = {
    "absolute": "The system guarantees that money cannot move past the control point.",
    "measured": "The application transfers funds between accounts through the function transfer.",
    "policy": "The operator must not write the balance directly.",
    "assumption": "Assume that the audit function is called on every path.",
    "mixed": ("The transfer function writes the balance. "
              "This design is provably safe. "
              "An operator must not update the ledger by hand."),
}


def decompose(name: str):
    src = tmp / f"{name}.txt"
    out = tmp / f"{name}.json"
    src.write_text(TEXTS[name], encoding="utf-8")
    r = subprocess.run([PY, str(TOOL), "--text", str(src), "--out", str(out)],
                       capture_output=True, text=True)
    try:
        return r.returncode, json.loads(out.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return r.returncode, None


def main() -> int:
    rows = []

    rc, doc = decompose("absolute")
    rows.append(("an absolute is refused", rc == 1 and doc["counts"].get("absolute") == 1))

    rc, doc = decompose("measured")
    unit = (doc or {}).get("units", [{}])[0]
    rows.append(("an action becomes measured, with what it needs",
                 rc == 0 and unit.get("kind") == "measured" and "target table" in unit.get("needs", "")))

    rc, doc = decompose("policy")
    rows.append(("a policy sentence becomes a requirement",
                 (doc or {}).get("units", [{}])[0].get("kind") == "requirement"))

    rc, doc = decompose("assumption")
    rows.append(("an unverified condition becomes an assumption",
                 (doc or {}).get("units", [{}])[0].get("kind") == "assumption"))

    rc, doc = decompose("mixed")
    units = (doc or {}).get("units", [])
    kinds = {u["kind"] for u in units}
    rows.append(("nothing is dropped and the absolute still refuses",
                 rc == 1 and len(units) == 3 and {"measured", "absolute", "requirement"} <= kinds))

    bad = 0
    for name, ok in rows:
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"\ncases: {len(rows)}, failures: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
