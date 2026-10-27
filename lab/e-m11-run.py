#!/usr/bin/env python3
"""E-M11 harness: build the fixture database, run the enumetator, compare with the declared truth.

Fairness note: the fixture was written with the enumerator in view. This measures whether the
catalogue can *express* these classes of bypass at all, not whether an unknown bypass would be
found by a blind search. The three expected misses are the honest ceiling of the method.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "pg-bypass" / "01-fixture.sql"
EXPECTED = ROOT / "fixtures" / "pg-bypass" / "expected.json"
ENUM = ROOT / "enumerators" / "grants-pg" / "fg_enum_grants.py"

# Map expected plant -> predicate over detected paths. Declared before the run.
MATCH = {
    "P1": lambda p: p["kind"] == "privilege" and p["detail"] == "UPDATE",
    "P2": lambda p: p["kind"] == "privilege" and p["detail"] == "INSERT",
    "P3": lambda p: p["kind"] == "function" and p["detail"] == "SECURITY DEFINER",
    "P4": lambda p: p["kind"] == "function" and p["detail"] == "SECURITY INVOKER" and "set_balance" in p["entry"],
    "P5": lambda p: p["kind"] == "disabled_control",
    "P6": lambda p: p["kind"] == "view_trigger",
    "P7": lambda p: p["kind"] == "dynamic_sql",
    "P8": lambda p: p["kind"] == "trigger_chain",
}
THRESHOLD = {"catalog": (6, 6), "text_search": (1, 2)}   # required, pre-registered


def psql(a, *args, db=None):
    cmd = [a.psql, "-h", a.host, "-p", str(a.port), "-U", a.user, "-d", db or a.db,
           "-v", "ON_ERROR_STOP=1"]
    if args and args[0] == "-f":
        cmd += ["-f", args[1]]
    else:
        cmd += ["-c", args[0]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"psql failed: {r.returncode}")
    return r.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--db", default="fgfix")
    a = ap.parse_args()

    psql(a, f"DROP DATABASE IF EXISTS {a.db}", db="postgres")
    psql(a, f"CREATE DATABASE {a.db}", db="postgres")
    psql(a, "-f", str(FIXTURE))
    print("fixture: applied")

    out = Path(tempfile.gettempdir()) / "e-m11-source.json"
    r = subprocess.run([sys.executable, str(ENUM), "--psql", a.psql, "--host", a.host,
                        "--port", str(a.port), "--user", a.user, "--db", a.db,
                        "--schema", "bank", "--table", "accounts", "--out", str(out)],
                       capture_output=True, text=True)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit("enumerator failed")
    print(r.stdout.strip())

    source = json.loads(out.read_text(encoding="utf-8"))
    paths = source["paths"]
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    print(f"\n{'plant':5} {'class':18} {'detectable_by':12} result")
    hits = {"catalog": [0, 0], "text_search": [0, 0]}
    for plant in expected["plants"]:
        found = any(MATCH[plant["id"]](p) for p in paths)
        by = plant["detectable_by"]
        hits[by][1] += 1
        if found:
            hits[by][0] += 1
        print(f"{plant['id']:5} {plant['class']:18} {by:12} {'DETECTED' if found else 'missed'}")

    ctrl = [c["entry"] for c in source.get("control_points", [])]
    print(f"\ncontrol point identified: {ctrl or 'NONE'}")

    declared = " ".join(source.get("blind_spots", [])).lower()
    print("\ndeclared blind spots cover the expected misses:")
    for m in expected["expected_misses"]:
        key = {"dynamic_sql_assembled": "dynamic sql", "outside_database": "foreign data",
               "application_level": "application-level"}[m["class"]]
        print(f"  {m['id']} {m['class']:24} {'yes' if key in declared else 'NO'}")

    # A regression guard for the class an independent oracle found missing (E-M41): a cascade into
    # the target must always be reported, or the next refactor silently loses it again.
    cascades = [p for p in paths if p["kind"] == "fk_cascade"]
    cascade_ok = any(p["entry"] == "fk:branches -> accounts" for p in cascades)
    print(f"\ncascade into the target detected: {cascade_ok} "
          f"({[p['entry'] for p in cascades]})")

    print("\nthresholds (pre-registered):")
    ok = True
    for cls, (need, total) in THRESHOLD.items():
        got = hits[cls][0]
        state = "PASS" if got >= need else "FAIL"
        ok = ok and got >= need
        print(f"  {cls:12} {got}/{total} required {need}/{total}  {state}")
    print(f"\nRESULT: {'PASS' if ok and ctrl and cascade_ok else 'FAIL'}")
    return 0 if ok and ctrl and cascade_ok else 1


if __name__ == "__main__":
    sys.exit(main())
