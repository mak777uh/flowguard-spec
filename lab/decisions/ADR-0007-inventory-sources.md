# ADR-0007 — the inventory is a merge of sources with declared blind spots

**Date:** 2026-10-27 · **Status:** accepted · **Related:** ADR-0005 (capped verdict), ADR-0003 (rings),
`docs/38-INVENTORY-DESIGN.md` (the design)

## Context

ADR-0005 caps the verdict at `CONSISTENT_DECLARED` without an inventory from a source the analysing agent did not
control. The obvious question — who builds that inventory — has two bad extremes:

- **a single analyser of ours**: we cannot see what we do not implement, and every new attack class means a new
  build;
- **trusting one third-party tool**: one tool's blind spot becomes our blind spot, silently.

The owner's instruction: build it so *we* can extend the inventory and maintain the list, and so new methods can be
added later without redesign.

## Decision

**The inventory is a merge of independent sources, and every source declares its blind spots.**

1. An `Enumerator` is anything producing `SourceRecord`s. Ours and a customer's are the same to the merger.
2. `blind_spots` is **mandatory and non-empty**; a source claiming universal vision is refused.
3. `covers` bounds every completeness word; the only accepted value is `exhaustive_within_covers`.
4. `path_id` is a content hash, so agreement collapses and disagreement becomes a visible `PATH_CONFLICT`, never a
   silent preference.
5. The coverage denominator is the **union** of sources.
6. Nothing is deleted by the merger: a path a source stops reporting becomes `vanished`.
7. `independent_of_agent` is computed from the source kinds the merger received, not asserted by the caller. It is
   the single boolean that lifts the round-7 ceiling.
8. Adding a method = template + adapter + landing test. **No format version change.**

## Build order

`fg-enum-grants` (Postgres privileges, `SECURITY DEFINER`, triggers) and `fg-enum-routes` (entrypoints from
configuration) come before the verifier's stronger levels, because without them every verdict is capped.

## What this decision does NOT do

- It does not make the union complete. Two sources can share a blind spot; `independent_of_agent` is a weak
  guarantee and is labelled as such in the manifest.
- It does not decide the weighting of residual risk.
- It does not turn the manifest into a proof. It records who looked, with what, and with what declared blindness.
