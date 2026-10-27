# ADR-0013 — attribution resolves by identity, and an ambiguous name may not place a path in the core

**Date:** 2026-10-28 · **Status:** accepted · **Source:** `E-M25` · **From:** round-8 review, all three reviewers

## Context

The merger joined sources by bare function name. PostgreSQL allows overloads, so `transfer` can be two
functions: the control point, and another one that writes the table directly. In that situation the join is a
guess, and it errs in the direction that hides risk — the route is placed inside the core, and the overload that
bypasses it is never mentioned.

The same defect existed inside our own grant enumerator, which excluded the control point with
`p.proname NOT IN ('transfer')`: with an overload present, **both** functions disappeared from the inventory. A
name-based exclusion hid a real direct writer. This is the third instance of the same disease in this repository
(after the decoy route and the transitive lookup index).

## Decision

**1. The enumerator excludes by identity, not by name.** If the control-point name is ambiguous in the schema, every
candidate is kept and the ambiguity is left for the merger to report.

**2. The merger checks every path that declares `calls`** — including a path its own source already attributed.
An attribution made by name is precisely the guess this rule exists to stop, so it is withdrawn, not trusted.

**3. Withdrawal is recorded, not silent.** The path carries
`attribution_conflict: {called, candidates, resolution: "ambiguous"}`, and its `control_point` is cleared.

**4. An ambiguous attribution blocks an upgrade** (`AMBIGUOUS_ATTRIBUTION`). "We are not sure this route goes
through the control point" may not be counted as "it does".

## Consequence for the verdict

`level_upgrade_allowed` used to depend on perimeter growth alone. It now requires that no blocking error was raised,
because a claim was able to raise its level while an unresolved ambiguity sat in the same document.

## What this decision does NOT do

- It does not resolve overloads by signature. The route manifest carries a bare name, so resolution is impossible
  without more data; the honest output is `ambiguous`, and a signature would have to come from the manifest's author.
- It does not detect ambiguity inside a single source's own attribution when no `calls` list is present. A source
  that attributes without declaring the call is not checkable, and that is declared in each source's blind spots.
- It does not fix the second defect found here: the grant enumerator sets `control_point` to the function itself,
  making every writer look like its own control point. That is carded separately and is not corrected by this ADR.
