---
id: E-M72
hypothesis: H-M72
status: completed
base_commit: "fa1efad"
started: "2026-10-28T23:20:00+03:00"
finished: "2026-10-28T23:35:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m72-run.py"
threshold: "Pre-registered, from docs/28: the mapping checker must run the three negative controls the page names - ENFORCES with no mechanism, a path that is no longer in the inventory, and a non-mechanical atom - and must refuse each with its own code. A positive case must be accepted, and ENFORCES must never reach PROVEN."
result: "tools/fg_map.py implements the artifact and six refusals of docs/28; ten of ten cases behave as specified. Negative control 1 (ENFORCES with basis.kind no_mechanism) gives MAP_CLAIM_UNSUPPORTED. Negative control 2, in both forms - a path_id that is not in the inventory and an inventory whose address does not match the mapping - gives MAP_PATH_UNKNOWN. Negative control 3 (atom with mechanical false) gives MAP_ATOM_NOT_MECHANICAL, the code that is a RESULT rather than a failure: it says this part of the law cannot be bound to code at all. Also caught: an ENFORCES that lists none of the paths attributed to its control point, a mechanism naming a control point nothing reaches, a target_lock mismatch, and a mapping with no not_claimed list. Ceiling: ENFORCES reports SCOPED_ASSURANCE and has no code path to PROVEN."
verdict: supports
---

# E-M72 — the fourth check exists, and it refuses the three things the page said it would

## What was built

`tools/fg_map.py`, the checker for [docs/28](../docs/28-CORRESPONDENCE.md). It takes a mapping, the inventory it
refers to, optionally a bundle and a LexSpec statement, and answers:

```
ACCEPTED | claim=ENFORCES  ceiling=SCOPED_ASSURANCE
REFUSED  | one code per reason, each with subject, expected, observed and next_action
```

The two pins are the point of the artifact: the atom is pinned by `span_sha256` + `revision`, the code side by
`inventory_address` — the canonical address of the inventory, recomputed by the checker rather than trusted. A
mapping therefore cannot outlive the inventory it describes, which is the failure mode a file name would hide.

## The three negative controls

| control from the page | result |
|---|---|
| ENFORCES with no mechanism | `MAP_CLAIM_UNSUPPORTED` |
| the mapped path is no longer in the inventory (or the address is stale) | `MAP_PATH_UNKNOWN` |
| a non-mechanical atom ("добросовестность") | `MAP_ATOM_NOT_MECHANICAL` |

The third is the one I would defend hardest. It is a **result**, not a failure: it says that this atom's action is
not something a program can perform, so no amount of better tooling will bind it to code. A mapping set that
reports 40% of atoms this way is more informative than one that maps all of them, because the second is certainly
guessing.

## Two defects the cases found in the checker itself

1. **A mechanism must be checked against the inventory, not just named.** My first version accepted
   `control_point: function:shop.audit_write` on the strength of the string. The case "mechanism names a point
   nothing reaches" now refuses, because the checker looks for paths attributed to that control point and finds
   none.
2. **`ENFORCES` must list every covered path.** The case "ENFORCES that skips a covered path" refuses when
   `checked_path_ids` is empty, even though the mechanism is real. A claim that names a mechanism but shows no
   paths is the same defect the main gate calls `CLAIM_EXCEEDS_EVIDENCE`, in a new place.

## The ceiling

`ENFORCES` reports `SCOPED_ASSURANCE` and the checker has no branch that reaches `PROVEN`. The harness asserts
this separately, so a future edit that promotes the ceiling fails a test rather than a review.

## What this does not do

- It does not implement LexSpec's side. `--statement` only cross-checks that the atom id and revision exist there;
  the span itself is not re-verified, because that is their checker's job and duplicating it would create two
  authorities.
- It does not decide whether the mapping is *right*. It decides whether it is *supported*: the mechanism exists,
  the paths are covered, the evidence is current, the atom is anchored. The judgement from a legal action to a
  write remains human, which is why the ceiling is where it is.
