#!/usr/bin/env python3
"""fg_map — the fourth check: does a declared control point enforce a declared legal atom?

`docs/28-CORRESPONDENCE.md` specifies the artifact and six refusals. This is the checker for that page, and it
implements the page's ceiling: `ENFORCES` never reaches `PROVEN`, because the mapping from a legal action to a
write is a human judgement and a checker may not promote a judgement to a proof.

    python tools/fg_map.py --mapping m.json --inventory inv.json [--bundle b/] [--statement s.lex.json]

Exit 0 when the mapping survives, 1 when it is refused, 2 on a usage or parse error.
"""
import argparse
import hashlib
import json
import pathlib
import sys

MAPPING_VERSION = "1"
CLAIMS = ("ENFORCES", "DOES_NOT_ENFORCE", "UNDECIDED")
MECHANISMS = ("control_point_on_all_paths", "control_point_absent", "no_mechanism")
MECHANICAL_LIMIT = 0.0   # a claim of ENFORCES may not reach PROVEN


def canon(doc) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def address_of(doc) -> str:
    return hashlib.sha256(canon(doc)).hexdigest()


def read_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


class Report:
    def __init__(self):
        self.errors = []
        self.checked = []

    def err(self, code, subject, expected, observed, next_action):
        self.errors.append({"code": code, "subject": subject, "expected": expected,
                            "observed": observed, "next_action": next_action})

    @property
    def verdict(self):
        return "REFUSED" if self.errors else ("ENFORCES" if self._claim else "MAP_ACCEPTED")

    def ok(self, level, note=""):
        self.checked.append({"level": level, "note": note})


def check(mapping, inventory, bundle=None, statement=None) -> Report:
    r = Report()
    r._claim = None

    # --- shape ---------------------------------------------------------------------------------
    if mapping.get("mapping_version") != MAPPING_VERSION:
        r.err("MAP_VERSION", "mapping_version", MAPPING_VERSION,
              str(mapping.get("mapping_version")),
              "write a mapping this checker understands")
        return r

    atom = mapping.get("atom") or {}
    path = mapping.get("path") or {}
    claim = mapping.get("claim")
    basis = mapping.get("basis") or {}

    if claim not in CLAIMS:
        r.err("MAP_CLAIM_UNSUPPORTED", "claim", " | ".join(CLAIMS), str(claim),
              "use one of the three claims")
        return r
    r._claim = claim

    if not mapping.get("not_claimed"):
        r.err("MAP_NOT_CLAIMED", "not_claimed", "the list of what this mapping does not assert",
              "absent", "carry the boundary with the claim, as every verdict in this family does")

    # --- the legal side is pinned to bytes ----------------------------------------------------
    span = atom.get("span_sha256") or ""
    if not isinstance(span, str) or len(span) != 64 or any(c not in "0123456789abcdef" for c in span):
        r.err("MAP_ATOM_UNANCHORED", "atom.span_sha256",
              "64 lowercase hex of the anchored span", str(span)[:20],
              "anchor the atom, or do not map it")
    if not atom.get("revision") or not atom.get("corpus_id"):
        r.err("MAP_ATOM_UNANCHORED", "atom.corpus_id/revision",
              "a pinned corpus and revision", "absent",
              "an atom without a revision can re-point after an amendment")
    r.ok("atom anchored", f"{atom.get('corpus_id')}@{atom.get('revision')}")

    # --- a non-mechanical atom is a result, not a failure --------------------------------------
    if atom.get("mechanical") is False:
        r.err("MAP_ATOM_NOT_MECHANICAL", "atom.action",
              "an action a program can perform", "the atom describes something code cannot enforce",
              "record UNDECIDED and stop: this part of the law cannot be bound to code")
        return r

    # --- the code side is pinned to an address -------------------------------------------------
    actual = address_of(inventory)
    stated = path.get("inventory_address")
    if stated != actual:
        r.err("MAP_PATH_UNKNOWN", "path.inventory_address",
              f"the address of this inventory ({actual[:12]}…)", str(stated)[:20],
              "re-enumerate; a mapping may not refer to a recollection")
    else:
        r.ok("inventory address", actual[:12] + "…")

    pid = path.get("path_id")
    ids = {p.get("path_id") for p in inventory.get("paths", [])}
    if pid not in ids:
        r.err("MAP_PATH_UNKNOWN", "path.path_id", "a path_id present in the inventory", str(pid),
              "name a path that exists, or re-run the enumerator")

    # --- scope: the two sides must describe the same system ------------------------------------
    if mapping.get("target_lock") and inventory.get("target_lock") != mapping["target_lock"]:
        r.err("MAP_SCOPE_MISMATCH", "target_lock",
              str(mapping.get("target_lock")), str(inventory.get("target_lock")),
              "the mapping and the inventory describe different systems")

    # --- the mechanism ------------------------------------------------------------------------
    kind = basis.get("kind")
    evidence = basis.get("evidence") or {}
    if claim == "ENFORCES":
        if kind != "control_point_on_all_paths":
            r.err("MAP_CLAIM_UNSUPPORTED", "basis.kind",
                  "control_point_on_all_paths for ENFORCES", str(kind),
                  "name the mechanism, or lower the claim to UNDECIDED")
        else:
            control = evidence.get("control_point")
            covered = evidence.get("checked_path_ids") or []
            attrib = {
                p.get("path_id"): (p.get("attribution") or {}).get("to")
                for p in inventory.get("paths", [])
            }
            writes = [k for k, v in attrib.items() if v == control]
            if not control:
                r.err("MAP_CLAIM_UNSUPPORTED", "basis.evidence.control_point",
                      "the control point that is supposed to do the enforcing", "absent",
                      "name it")
            elif not writes:
                r.err("MAP_CLAIM_UNSUPPORTED", "basis.evidence.control_point",
                      "a control point with at least one path attributed to it", control,
                      "no path in this inventory reaches that point")
            else:
                missing = sorted(set(writes) - set(covered))
                if missing:
                    r.err("MAP_CLAIM_UNSUPPORTED", "basis.evidence.checked_path_ids",
                          f"every path attributed to {control} ({len(writes)})",
                          f"{len(missing)} not listed, e.g. {missing[0]}",
                          "list every covered path, or lower the claim")
                else:
                    r.ok("mechanism", f"{control} covers {len(writes)} path(s)")

    if claim == "DOES_NOT_ENFORCE":
        bypass = [p for p in inventory.get("paths", [])
                  if p.get("path_id") == pid and (p.get("attribution") or {}).get("to") is None]
        if kind != "control_point_absent":
            r.err("MAP_CLAIM_UNSUPPORTED", "basis.kind",
                  "control_point_absent for DOES_NOT_ENFORCE", str(kind),
                  "a falsifiable claim names the path that bypasses, not a general absence")
        elif not bypass:
            r.err("MAP_CLAIM_UNSUPPORTED", "path.path_id",
                  "a path with no attribution to any control point", str(pid),
                  "the named path is attributed, so it does not bypass")

    # --- the bundle behind the basis, if one is given ------------------------------------------
    if bundle:
        b = pathlib.Path(bundle)
        manifest = b / "manifest.sha256"
        if not manifest.exists():
            r.err("MAP_BASIS_STALE", "basis.evidence.verdict_address",
                  "a bundle whose address can be recomputed", "no manifest.sha256",
                  "re-run the gate; a mapping may not outlive its evidence")
        else:
            recorded = manifest.read_text(encoding="ascii").strip()
            stated_addr = evidence.get("verdict_address")
            if stated_addr and stated_addr != recorded:
                r.err("MAP_BASIS_STALE", "basis.evidence.verdict_address",
                      recorded[:12] + "…", str(stated_addr)[:12] + "…",
                      "the evidence moved; re-run the gate")

    # --- the statement, if one is given ---------------------------------------------------------
    if statement:
        try:
            doc = read_json(statement)
        except Exception as e:  # noqa: BLE001
            r.err("MAP_ATOM_UNANCHORED", "statement", "a LexSpec statement", str(e)[:60],
                  "pass the statement the atom came from")
        else:
            atoms = {a.get("id") for a in doc.get("atoms", [])}
            if atom.get("atom_id") and atom["atom_id"] not in atoms:
                r.err("MAP_ATOM_UNANCHORED", "atom.atom_id",
                      "an atom present in the statement", str(atom["atom_id"]),
                      "the statement does not contain this atom")
            revs = {c.get("revision") for c in doc.get("corpus", [])}
            if atom.get("revision") and atom["revision"] not in revs:
                r.err("MAP_ATOM_UNANCHORED", "atom.revision",
                      "a revision the statement pins", str(atom["revision"]),
                      "an atom may not cite a revision its statement does not carry")

    return r


def ceiling(claim):
    """The page's ceiling: ENFORCES is SCOPED at best, and there is no path to PROVEN."""
    return {"ENFORCES": "SCOPED_ASSURANCE", "DOES_NOT_ENFORCE": "SCOPED_ASSURANCE",
            "UNDECIDED": "CONSISTENT_DECLARED"}.get(claim, "CONSISTENT_DECLARED")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--bundle")
    ap.add_argument("--statement")
    a = ap.parse_args()

    try:
        mapping = read_json(a.mapping)
        inventory = read_json(a.inventory)
    except Exception as e:  # noqa: BLE001
        print(f"cannot read the input: {e}")
        return 2

    r = check(mapping, inventory, a.bundle, a.statement)
    claim = mapping.get("claim")
    doc = {
        "mapping_version": mapping.get("mapping_version"),
        "verdict": "REFUSED" if r.errors else "ACCEPTED",
        "claim": claim,
        "ceiling": ceiling(claim) if isinstance(claim, str) else None,
        "not_claimed": mapping.get("not_claimed", []),
        "checked": r.checked,
        "errors": r.errors,
    }
    print(json.dumps(doc, indent=1, ensure_ascii=False))
    return 0 if not r.errors else 1


if __name__ == "__main__":
    sys.exit(main())
