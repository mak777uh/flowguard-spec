# ADR-0014 — a perimeter change is classified, not counted

**Date:** 2026-10-28 · **Status:** accepted · **Amends:** ADR-0006, ADR-0009 · **Source:** `E-M26`

## Context

`ADR-0006` said: while the perimeter grows, an upgrade is blocked. `E-M19` implemented growth as "a path appeared".
Round-8 review, all three models, named the consequence: **deleting a dead path is also a change**, so a rule that
punishes every change rewards stagnation and punishes cleanup. The cleaner the repository, the worse its score.

The audit question the reviewers supplied is the one to encode: *was this a documented, tested replacement with the
same or lower risk class?*

## Decision

Every change is classified against the previous inventory by **shape** — the path kind and whether it carries a
control point:

| classification | meaning | effect on an upgrade |
|---|---|---|
| **additive** | a shape that did not exist before | blocked |
| **substitutive** | a new path paired one-for-one with a vanished path of the same shape | allowed, after re-attestation |
| **subtractive** | removed with no replacement | allowed; recorded as a reduction |

`perimeter_growth` now means **new surface** (`additive > 0`), not "something changed". A replacement is not growth.

## Why pairing, not a count

A count of new versus vanished would call a refactor net-zero and a real addition invisible when they happen in the
same window. Pairing by shape keeps both visible: one additive and one substitutive in the same delta are two facts,
not a zero.

## Consequence

A team that removes a dead path improves its position instead of freezing it. A team that adds a writer is blocked
exactly as before.

## What this decision does NOT do

- It does not judge whether a substitution is **safe**, only that it has the same shape. Two paths with the same
  kind and control-point status can differ completely in what they reach; the re-attestation requirement is where
  that difference has to be established, and it is a human act.
- It does not classify a **risk-class** change. Pairing uses kind and control-point status, not the weighted class
  from `policies/risk-classes.json`; a substitution from `other` to `money` is currently invisible.
- It does not compare inventories of different targets. Two manifests with different `target_lock` values are still
  not a delta, and the merger does not refuse that.
