"""E-M81 — the verifier counts the denominator itself.

The user's point: a denominator supplied by the party being judged is not a denominator. `fg_verify --recount DIR`
runs the migrations enumerator over the same source and unions what it finds into the claim's inventory, so an
omitted path lowers coverage instead of raising it.

Cases:
1. an inventory missing the paths the recount finds -> UNDERCOUNTED_DENOMINATOR, verdict INVALID;
2. an inventory that already contains them -> no refusal from the recount;
3. a source that does not exist -> RECOUNT_UNAVAILABLE, never a silent fallback to the claim's number.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools" / "fg_verify.py"
PY = sys.executable
SRC = ROOT / "fixtures" / "hidden-bypass"
tmp = pathlib.Path(tempfile.mkdtemp())

CLAIM = {"claim_id": "recount", "target_lock": {"commit": "hidden@1"},
         "declared_control_point": "function:sample2.review_transfer",
         "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0,
         "evidence_tier": 0, "not_claimed": ["NC-01", "NC-02"]}


def inventory(paths):
    return {"manifest_version": "inventory/0.1", "target_lock": "hidden@1", "schema": "sample2",
            "independent_of_agent": True,
            "sources": [{"source_id": "s", "kind": "static", "db_logic_density": 0.9,
                         "completeness_claim": "exhaustive_within_covers"}],
            "paths": paths}


ONE = {"path_id": "wp_1", "entry": "function:sample2.set_balance", "target": "table:sample2.accounts",
       "kind": "function", "verbs": ["stmt:UPDATE"],
       "attribution": {"to": "function:sample2.review_transfer", "method": "caller", "sources": ["s"]}}


def run(inv, recount):
    cp, ip = tmp / "c.json", tmp / "i.json"
    cp.write_text(json.dumps(CLAIM), encoding="utf-8")
    ip.write_text(json.dumps(inv), encoding="utf-8")
    cmd = [PY, str(VERIFY), "--claim", str(cp), "--inventory", str(ip)]
    if recount:
        cmd += ["--recount", str(recount)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
        return doc["verdict"], sorted({e["code"] for e in doc.get("errors", [])})
    except Exception:  # noqa: BLE001
        return f"NO-JSON({r.returncode})", []


def main() -> int:
    if not SRC.is_dir():
        print("the hidden-bypass fixture is missing")
        return 1
    rows = []

    v, codes = run(inventory([ONE]), SRC)
    rows.append(("claim omits what the recount finds", v, codes,
                 "UNDERCOUNTED_DENOMINATOR" in codes))

    # a claim that already carries everything the enumerator finds
    enumerated = tmp / "enumerated.json"
    subprocess.run([PY, str(ROOT / "enumerators" / "migrations" / "fg_enum_migrations.py"),
                    "--dir", str(SRC), "--schema", "sample2",
                    "--control", CLAIM["declared_control_point"],
                    "--out", str(enumerated), "--target-lock", "hidden@1"],
                   capture_output=True, text=True)
    full = json.loads(enumerated.read_text(encoding="utf-8"))
    v, codes = run(inventory(full["paths"]), SRC)
    rows.append(("claim already carries every path", v, codes,
                 "UNDERCOUNTED_DENOMINATOR" not in codes))

    v, codes = run(inventory([ONE]), tmp / "does-not-exist")
    rows.append(("recount source absent", v, codes, "RECOUNT_UNAVAILABLE" in codes))

    bad = 0
    for name, v, codes, ok in rows:
        bad += 0 if ok else 1
        print(f"{name:38} {v:18} {'ok' if ok else 'FAIL'}  {','.join(codes[:2])}")
    print(f"\ncases: {len(rows)}, failures: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
