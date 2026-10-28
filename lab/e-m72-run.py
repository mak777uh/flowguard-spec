"""E-M72 — the fourth check, and the three negative controls the page promised.

docs/28-CORRESPONDENCE.md lists three tests that would make the mapping falsifiable. This harness runs them, plus
one positive case, so "the checker refuses what the page says it refuses" is a measurement rather than a claim.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "fg_map.py"
PY = sys.executable


def canon(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def address_of(doc):
    import hashlib
    return hashlib.sha256(canon(doc)).hexdigest()


INV = {
    "manifest_version": "inventory/0.1",
    "target_lock": "shop@1",
    "independent_of_agent": True,
    "sources": [{"source_id": "s", "kind": "static", "completeness_claim": "exhaustive_within_covers",
                 "db_logic_density": 0.9}],
    "paths": [
        {"path_id": "wp_017", "entry": "function:shop.ship", "target": "table:shop.shipments",
         "kind": "function", "verbs": ["stmt:INSERT"],
         "attribution": {"to": "function:shop.audit_write", "method": "caller", "sources": ["s"]}},
        {"path_id": "wp_018", "entry": "role:app_rw", "target": "table:shop.shipments",
         "kind": "privilege", "verbs": ["stmt:UPDATE"], "attribution": {"to": None}},
    ],
}

ATOM = {"corpus_id": "gk-rf", "revision": "2026-10-01", "atom_id": "a1", "span_sha256": "a" * 64,
        "mechanical": True}


def mapping(**over):
    doc = {
        "mapping_version": "1",
        "target_lock": "shop@1",
        "atom": dict(ATOM),
        "path": {"inventory_address": address_of(INV), "path_id": "wp_017"},
        "claim": "ENFORCES",
        "basis": {"kind": "control_point_on_all_paths",
                  "evidence": {"control_point": "function:shop.audit_write",
                               "checked_path_ids": ["wp_017"], "coverage": 1.0}},
        "not_claimed": ["that the mapping from the legal action to the write is the right mapping",
                        "legal validity"],
    }
    doc.update(over)
    return doc


CASES = [
    # name, mapping, expect_code (None = accepted)
    ("positive: a covered path with a named mechanism", mapping(), None),
    ("negative 1: ENFORCES with no mechanism", mapping(basis={"kind": "no_mechanism", "evidence": {}}),
     "MAP_CLAIM_UNSUPPORTED"),
    ("negative 2: path that disappeared from the inventory",
     mapping(path={"inventory_address": address_of(INV), "path_id": "wp_999"}), "MAP_PATH_UNKNOWN"),
    ("negative 2b: stale inventory address",
     mapping(path={"inventory_address": "0" * 64, "path_id": "wp_017"}), "MAP_PATH_UNKNOWN"),
    ("negative 3: non-mechanical atom (добросовестность)",
     mapping(atom=dict(ATOM, mechanical=False)), "MAP_ATOM_NOT_MECHANICAL"),
    ("unanchored atom", mapping(atom=dict(ATOM, span_sha256="")), "MAP_ATOM_UNANCHORED"),
    ("ENFORCES that skips a covered path",
     mapping(basis={"kind": "control_point_on_all_paths",
                    "evidence": {"control_point": "function:shop.audit_write",
                                 "checked_path_ids": []}}), "MAP_CLAIM_UNSUPPORTED"),
    ("mechanism names a point nothing reaches",
     mapping(basis={"kind": "control_point_on_all_paths",
                    "evidence": {"control_point": "function:shop.nonexistent",
                                 "checked_path_ids": ["wp_017"]}}), "MAP_CLAIM_UNSUPPORTED"),
    ("scope mismatch", mapping(target_lock="other@9"), "MAP_SCOPE_MISMATCH"),
    ("no not_claimed list", mapping(not_claimed=[]), "MAP_NOT_CLAIMED"),
]


def run(m, inv):
    tmp = pathlib.Path(tempfile.mkdtemp())
    mp, ip = tmp / "m.json", tmp / "i.json"
    mp.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    ip.write_text(json.dumps(inv), encoding="utf-8")
    r = subprocess.run([PY, str(CHECKER), "--mapping", str(mp), "--inventory", str(ip)],
                       capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return f"NO-JSON({r.returncode})", [], None
    codes = sorted({e["code"] for e in doc.get("errors", [])})
    shutil.rmtree(tmp, ignore_errors=True)
    return doc["verdict"], codes, doc.get("ceiling")


def main() -> int:
    if not CHECKER.exists():
        print("tools/fg_map.py is missing")
        return 1
    bad = 0
    print(f"{'case':52} {'verdict':10} {'ceiling':18} codes")
    for name, m, expect in CASES:
        verdict, codes, ceil = run(m, INV)
        ok = (expect is None and verdict == "ACCEPTED") or (expect is not None and expect in codes)
        bad += 0 if ok else 1
        print(f"{name:52} {verdict:10} {str(ceil):18} {','.join(codes[:2])}")

    # the ceiling rule: ENFORCES may never reach PROVEN
    _, _, ceil = run(mapping(), INV)
    if ceil == "PROVEN":
        bad += 1
        print("  CEILING VIOLATED: ENFORCES reached PROVEN")
    print(f"\ncases: {len(CASES)}, failures: {bad}")
    print("RESULT:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
