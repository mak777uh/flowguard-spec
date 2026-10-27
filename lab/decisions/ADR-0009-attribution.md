# ADR-0009 — attribution is a separate contribution, and an attributed caller is a path

**Date:** 2026-10-27 · **Status:** accepted · **Amends:** ADR-0007 · **Source:** `E-M13`

## Context

ADR-0007 assumed a source either finds paths or finds nothing. `E-M13` showed the assumption is too narrow: the
call-graph source does not discover writers, it says **whether a found writer goes through the control point**. And
a legitimate caller that never writes the table itself — `transfer_via_api` — appears in no writer enumerator at
all, yet it is part of the flow and it is inside the core.

Without a rule for both, coverage counts only writers and every legitimate caller is invisible. That is exactly the
defect `E-M12` measured.

## Decision

**1. A source may contribute `attributions[]` instead of, or in addition to, `paths[]`.**

```
attributions: [ { entry, attributed_to, method: direct|transitive, confidence } ]
```

**2. The merger applies an attribution to any path with the same `entry`.** Attribution is a property of a path,
never a replacement for its identity — which is why it is not written into `control_point`.

**3. An attributed entry with no matching path becomes a path** of kind `caller`, with `control_point` equal to the
declared control point. Path id is `sha256("caller|" + entry)`.

**4. Coverage counts a path as inside the core when** `attribution.to == declared_control_point`, falling back to
`control_point == declared_control_point` for single-source bundles.

## Why not overload `control_point`

`control_point` on a path means "this writer is itself a control point". Attribution means "this path passes through
that control point". Merging the two produced a conflict in the merger on the very first two-source run: the grants
source said `""`, the call-graph source said `function:bank.transfer`, for the same path. The merger was right to
refuse. Two different facts needed two fields.

## Consequences

- `independent_of_agent` now typically rests on two source kinds, so one tool's blind spot is no longer the whole
  product's blind spot.
- A decoy named like the flow but writing directly is not attributed (`E-M13`), which is the behaviour a name-based
  heuristic would get wrong.
- The manifest's `in_core_attributed` count is published next to `paths_total`, so a reader sees how much of the
  coverage comes from attribution rather than from a path's own nature.

## What this decision does NOT do

- It does not raise coverage. On the fixture it is 0.133, which is the honest number for thirteen unaddressed ways
  to write the table.
- It does not make attribution sound: dynamic calls, overloads and depth beyond 8 are declared blind spots.
