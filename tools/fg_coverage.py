#!/usr/bin/env python3
"""fg_coverage — three states instead of a ratio.

All three independent reviews of round 8 converged on the same defect in the coverage model: a
single ratio cannot distinguish

  covered       enumerated by a catalogue source AND observed happening
  unobserved    enumerated, never seen - a path that exists and was not exercised
  unenumerable  observed happening but ABSENT from the enumeration - proof the denominator is
                incomplete, which is the dangerous one

The third state is the reason this file exists. If a DELETE happened and no catalogue path mentions
DELETE, the ratio was computed against a denominator that is already known to be wrong.

Scope, stated honestly: the comparison works on the **verb dimension**, where catalogue privileges
and runtime statements speak the same language (`INSERT`/`UPDATE`/`DELETE` ...). Function-level
"observed but not enumerated" is not measurable with `log_statement`, because nested statements are
not logged without pgAudit - which is exactly what E-M17 measured.
"""
import re

VERBS = ("INSERT", "SELECT", "UPDATE", "DELETE", "TRUNCATE", "MERGE")


def _verbs_from_catalogue(inventory):
    """Verbs the catalogue says are possible, from privilege paths whose detail names the privilege.

    Paths of kind `observed_write` are skipped: they are the observation, not the enumeration, and
    counting them here made every observed verb look catalogued - which silently emptied the
    `unenumerable` list this file exists to produce (found while testing E-M23).
    """
    found = set()
    for p in inventory.get("paths", []):
        if p.get("kind") == "observed_write":
            continue
        detail = (p.get("detail") or "").upper()
        for v in VERBS:
            if v in detail:
                found.add(v)
        entry = (p.get("entry") or "").upper()
        for v in VERBS:
            if f":{v} " in entry or entry.startswith(f"{v} ") or f" {v} " in entry:
                found.add(v)
    return found


def _verbs_observed(inventory):
    found = {}
    for p in inventory.get("paths", []):
        if p.get("kind") != "observed_write":
            continue
        m = re.search(r"stmt:([A-Z]+)", p.get("entry", ""))
        if m and m.group(1) in VERBS:
            found[m.group(1)] = p.get("path_id")
    return found


def states(inventory):
    """Return the three-state summary plus the lists behind each count."""
    catalogue = _verbs_from_catalogue(inventory)
    observed = _verbs_observed(inventory)

    covered = sorted(set(observed) & catalogue)
    unobserved = sorted(catalogue - set(observed))
    unenumerable = sorted(set(observed) - catalogue)

    return {
        "basis": "verb",
        "covered": covered,
        "unobserved": unobserved,
        "unenumerable": unenumerable,
        "counts": {"covered": len(covered), "unobserved": len(unobserved),
                   "unenumerable": len(unenumerable)},
        "note": "unobserved is a path that exists and was not exercised; "
                "unenumerable is an event the enumeration cannot explain",
    }
