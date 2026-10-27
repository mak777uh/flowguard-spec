#!/usr/bin/env python3
"""fg_confirm — attach a schema owner's confirmation to an inventory, or refuse it.

The verifier reads `foreign_validation` and refuses an evidence tier the record does not support
(E-M29). That check is only as good as the record, so this tool enforces the shape described in
docs/FOREIGN-VALIDATION.md:

  * a named person, a role, a date and a channel - a confirmation without a name is a rumour;
  * a verdict: confirmed / refuted / partially_correct;
  * the owner's own sentence, quoted - not our summary of it;
  * for tier 3, an owner-produced ground-truth list with `blind_evaluation: true`.

    python tools/fg_confirm.py --inventory m.json --record record.json --out m.with-fv.json
    python tools/fg_confirm.py --record record.json --check      # validate only
"""
import argparse
import json
import sys
from pathlib import Path

VERDICTS = {"confirmed", "refuted", "partially_correct"}


def find_missing(rec):
    problems = []
    if not rec.get("schema"):
        problems.append("schema: which schema this is about")
    if json.loads(json.dumps(rec.get("owner_confirmed", False))) is not True:
        problems.append("owner_confirmed: must be true for a record that claims confirmation")
    owner = rec.get("owner") or {}
    for field in ("name", "role", "how_contacted", "date"):
        if not owner.get(field):
            problems.append("owner." + field)
    if rec.get("verdict") not in VERDICTS:
        problems.append("verdict: one of " + ", ".join(sorted(VERDICTS)))
    if len((rec.get("owner_statement") or "").strip()) < 12:
        problems.append("owner_statement: their sentence, quoted, at least a dozen characters")
    finding = rec.get("finding") or {}
    if rec.get("verdict") in ("confirmed", "partially_correct", "refuted"):
        for field in ("path_id", "claim"):
            if not finding.get(field):
                problems.append("finding." + field)
    if rec.get("blind_evaluation"):
        gt = rec.get("ground_truth") or {}
        for field in ("produced_by", "method"):
            if not gt.get(field):
                problems.append("ground_truth." + field)
        if rec.get("our_result") is None:
            problems.append("our_result: needed when the owner produced a ground-truth list")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory")
    ap.add_argument("--record", required=True)
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    rec = json.loads(Path(a.record).read_text(encoding="utf-8"))
    problems = find_missing(rec)
    if problems:
        print("record refused:")
        for p in problems:
            print("  missing or invalid:", p)
        print("RESULT: fail")
        return 1

    print("record accepted:", rec["schema"], "—", rec["verdict"], "by", rec["owner"]["name"],
          "on", rec["owner"]["date"])
    if a.check or not a.inventory:
        print("RESULT: ok")
        return 0

    inv = json.loads(Path(a.inventory).read_text(encoding="utf-8"))
    inv.setdefault("foreign_validation", [])
    if rec not in inv["foreign_validation"]:
        inv["foreign_validation"].append(rec)
    out = Path(a.out or a.inventory)
    out.write_text(json.dumps(inv, indent=1, ensure_ascii=False), encoding="utf-8")
    print("attached to", out, "- the inventory now supports evidence tier",
          3 if any(r.get("blind_evaluation") for r in inv["foreign_validation"]) else 2)
    print("RESULT: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
