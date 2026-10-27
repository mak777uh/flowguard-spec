# ADR-0012 — a source may only contribute paths that reach the target, and transitive attribution belongs to the merger

**Date:** 2026-10-27 · **Status:** accepted · **Source:** `E-M20`

## Context

The route manifest lists every endpoint of a service. The inventory is **per target table**. Those are different
namespaces, and joining them naively inflates the perimeter: an endpoint that writes `notes` is not a path to
`accounts`, yet counting it would lower coverage of a table it never touches.

A second problem appeared at the same time. `/transfer/batch` calls `transfer_batch`, which reaches the control
point two hops away. The route source knows the endpoint calls `transfer_batch`; the call-graph source knows
`transfer_batch` reaches the control point. **Neither alone can attribute the endpoint**, and both were right.

## Decision

**1. Filter at the source, not afterwards.** A source receives the target and contributes only paths that reach it.
The route enumerator keeps the endpoints whose declared `writes` include the target and drops the rest.

**2. Attribution resolves across sources in the merger.** A path carrying `calls` is attributed transitively when a
called function is already attributed, and the resulting record names both sources
(`merge:declared_calls`, `pgcalls`). The merger is the only place where both the call list and the reachability are
visible at once.

**3. Source interfaces carry what the resolution needs.** Path records preserve `detail` and `calls`; dropping a
field in the merger is how a resolution rule silently becomes dead code.

## Consequences

- `routes` qualifies as a coverage denominator kind by the `ADR-0011` rule: built, measured, then listed.
- A wrong `writes` list produces a wrong inventory. This is not detectable inside the manifest; it moves into
  `NC-03` (interpretation) and is declared in the source's blind spots.
- The transitive rule is deliberately narrow: one declared hop plus the call graph's own reachability. Longer
  chains through other services are out of scope and declared as such.

## What this decision does NOT do

- It does not make the manifest authoritative about the running service. Spec drift is the likeliest real failure.
- It does not attribute endpoints whose handler list is empty. An unknown handler stays outside the core, which
  lowers coverage — the honest direction.
- It does not generalise to arbitrary joins between sources. Each cross-source rule must be justified by a
  measurement, as this one was.
