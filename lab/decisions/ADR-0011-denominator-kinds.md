# ADR-0011 — a denominator kind exists only after its enumerator is measured

**Date:** 2026-10-27 · **Status:** accepted · **Source:** `E-M19`

## Context

`fg_verify` listed `routes` among the kinds that may form a coverage denominator. No `routes` enumerator exists.
The list was written when the distinction between denominators and witnesses was introduced (`E-M18`), and it
included the kind that the design *expected* to build.

That is the sixth instance of one failure in this repository's own instruments: **a declaration standing in for an
artifact.** Five were in checkers, one in a readiness score, and this one in the definition of what a coverage
number may rest on.

## Decision

A kind may appear in `DENOMINATOR_KINDS` only when both hold:

1. an enumerator of that kind exists in `enumerators/`, and
2. it has a completed experiment card with a measurement.

`routes` is removed. It returns when `fg-enum-routes` exists and is measured, and not before.

## Why this is not pedantry

The coverage denominator is the one number the product sells. If the list of admissible sources includes a source
that does not exist, then a manifest could name a source kind that never contributed a path, and the ratio would
still compute — a number resting on a category rather than on evidence.

## Consequences

- `docs/38-INVENTORY-DESIGN.md` describes `routes` as a planned source; that stays true, but it is not a basis.
- The readiness check E5-style "measured" wording already requires a card for each enumerator; the same standard now
  applies to the kinds list.
- Any future kind (`http`, `openapi`, `schema-diff`) enters the same way: built, measured, then listed.

## What this decision does NOT do

- It does not rank the existing kinds. `grants`, `static` and `manual` are admissible because they are measured, not
  because they are better.
- It does not prevent a witness from contributing evidence. Witnesses still constrain and corroborate; they simply
  cannot set the denominator.
