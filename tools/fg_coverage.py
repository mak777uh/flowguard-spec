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
    """Verbs the catalogue says are possible, from structured fields only.

    Paths of kind `observed_write` are skipped: they are the observation, not the enumeration, and
    counting them here made every observed verb look catalogued - which silently emptied the
    `unenumerable` list this file exists to produce (found while testing E-M23).

    `detail` is free text and is NOT read. Typing "DELETE" into it used to satisfy the check that
    exists in order not to be satisfied (E-M47): the whole point is that an event the enumeration
    cannot explain must block a strong verdict, and an unconstrained string let the claimant decide.
    A verb counts only when a path names it in a structured way: `stmt:VERB ...` or `VERB ...`.
    """
    found = set()
    for p in inventory.get("paths", []):
        if p.get("kind") == "observed_write":
            continue
        entry = str(p.get("entry") or "")
        m = re.match(r"^stmt:([A-Z]+)\b", entry)
        if m:  # any verb: CALL, EXECUTE, GRANT …
            found.add(m.group(1))
            continue
        head = entry.split(" ", 1)[0].rstrip(":").upper()
        if head in VERBS:
            found.add(head)
    return found


def _verbs_observed(inventory):
    found = {}
    for p in inventory.get("paths", []):
        if p.get("kind") != "observed_write":
            continue
        m = re.search(r"stmt:([A-Z]+)", p.get("entry", ""))
        if m:  # any verb: CALL, EXECUTE, GRANT …
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
