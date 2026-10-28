# Correspondence — the fourth check, between law and code

Two projects in this family check two different things. `lexspec` checks that a legal statement's atoms are
anchored in a pinned revision and internally coherent. `flowguard` checks that a declared control point actually
covers the paths by which a table can be written. **Both can be green while saying nothing about each other.**

This document specifies the artifact that would make the third question answerable: *does this control point
enforce this legal atom, and how would we know?* It is a format, not an implementation. Nothing here is checked
yet, and that sentence belongs in any quotation of it.

## Why the joint cannot be inferred

The temptation is to compose two verdicts: "the atom is anchored" + "the path is in the core" ⇒ "the duty is
enforced". That inference is invalid for a reason that does not go away with better tooling:

- the legal atom talks about an **action between parties** ("передать товары"), the code path about a **write to a
  table** ("INSERT INTO shipments"). The mapping from one to the other is a human judgement, not a computation;
- an anchored atom can be anchored to a sentence that no software enforces, and a covered path can cover a write
  that has no legal meaning;
- both artifacts have their own `not_claimed` list, and their union does not include "the mapping is correct".

So the joint needs its own artifact, its own refusals, and its own ceiling.

## The artifact

```json
{
  "mapping_version": "1",
  "atom":   {"corpus_id": "gk-rf", "revision": "2026-10-01", "atom_id": "a1",
             "span_sha256": "<sha256 of the anchored span>"},
  "path":   {"inventory_address": "<64 hex>", "path_id": "wp_017"},
  "claim":  "ENFORCES",
  "basis":  {"kind": "control_point_on_all_paths",
             "evidence": {"control_point": "function:bank.audit_write",
                          "checked_path_ids": ["wp_017"], "coverage": 1.0,
                          "verdict_address": "<the bundle that says so>"}},
  "not_claimed": ["that the mapping from the legal action to the write is the right mapping",
                  "that the anchored sentence is the whole of the duty",
                  "legal validity"]
}
```

Three fields carry all the weight:

- `atom.span_sha256` and `atom.revision` — the legal side is pinned to bytes, so an amendment cannot silently
  re-point the mapping (LexSpec's rule, inherited rather than re-implemented);
- `path.inventory_address` — the code side is pinned to an **address**, not a file name, so a re-run that changes
  the inventory invalidates the mapping by construction;
- `basis` — the *mechanism*, named. A mapping without a mechanism is an opinion.

## Refusals

Closed vocabulary, in the family's shape — a code, what it means, what a reader should do.

| code | means | remedy |
|---|---|---|
| `MAP_ATOM_UNANCHORED` | the atom has no verifiable span in the named revision, or the digest does not match | anchor it, or do not map it |
| `MAP_PATH_UNKNOWN` | `path_id` does not occur in an inventory at the stated address | re-enumerate; a mapping may not refer to a recollection |
| `MAP_CLAIM_UNSUPPORTED` | `claim` is `ENFORCES` but `basis` names no mechanism over the same paths | name the mechanism, or lower the claim to `UNDECIDED` |
| `MAP_ATOM_NOT_MECHANICAL` | the atom describes something no code can enforce ("добросовестность", "разумный срок") | this is not an error in the mapping, it is a fact about the atom: record `UNDECIDED` and stop |
| `MAP_BASIS_STALE` | the bundle at `basis.evidence.verdict_address` no longer covers the path | re-run the gate; a mapping may not outlive its evidence |
| `MAP_SCOPE_MISMATCH` | the inventory's `target_lock` differs from the corpus revision's declared system | the two sides describe different things |

`MAP_ATOM_NOT_MECHANICAL` is the interesting one. It is a **result**, not a failure: it says which part of the law
cannot be bound to code at all. A mapping set that reports 40% of atoms as non-mechanical is more informative than
one that maps all of them, because the second is certainly guessing.

## The three claims, and what each costs

| claim | basis must show | ceiling |
|---|---|---|
| `ENFORCES` | every path in the inventory that writes the target passes the control point, and the atom's action is that write | `SCOPED` — never stronger, because the mapping from action to write is a human judgement |
| `DOES_NOT_ENFORCE` | at least one path that writes the target bypasses the control point | this is the useful one: it is falsifiable by a single path |
| `UNDECIDED` | nothing | no ceiling; it asserts nothing |

Note that `ENFORCES` has a hard ceiling of `SCOPED` and no code path to `PROVEN`. That is deliberate and it is the
whole point: the mapping is a judgement about meaning, and a checker may not promote a judgement to a proof.

## What would make this falsifiable

Three tests, each of which can fail:

1. **Negative control:** take an atom whose action is clearly not any write in the inventory, map it as
   `ENFORCES`, and the gate must refuse `MAP_CLAIM_UNSUPPORTED` (no mechanism names the write).
2. **Staleness:** map an atom to a path, then re-run the enumerator with a changed schema so the path disappears;
   the mapping must refuse `MAP_BASIS_STALE` rather than keep its claim.
3. **Non-mechanical:** map "добросовестность" and the gate must answer `MAP_ATOM_NOT_MECHANICAL`, not
   `UNDECIDED` — the distinction between "we have not decided" and "this cannot be decided by code" is the
   product.

## What this document does not do

- It does not implement the checker. There is no `fg_map.py`, and the table above is a promise about refusals
  that nobody has exercised yet.
- It does not make `ENFORCES` mean the duty is performed. It means: *the writes this duty names pass the point
  this code declares*. Parties, intent and remedies are outside.
- It does not move either project's ceiling. `NC-01` (the inventory may be incomplete) and LexSpec's "no legal
  validity" both survive the mapping, multiplied rather than cancelled.
