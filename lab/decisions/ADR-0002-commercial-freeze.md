# ADR-0002 — commercial work is deferred until the first measurement

**Date:** 2026-10-27 · **Status:** accepted · **Supersedes:** nothing · **Related:** ADR-0001, `docs/34-OPEN-QUESTIONS.md`

## Context

The repository carries a pricing doctrine, service tiers, margin caps and a conditional promise. All of it was
written before anything executable existed, and none of it has been tested against a real budget. Round 6 concluded
that the binding constraint is not commercial design but the absence of a working artifact, and that the one
commercial question that matters — who acts on a verdict and what the publisher loses if it is wrong — cannot be
answered by review at all.

Meanwhile the commercial documents cost attention on every change: they invite refinement, and refinement of
untested commercial text is the same failure as another review round with different vocabulary.

## Decision

**Commercial work is frozen until the first executable measurement exists** — that is, until `E-M9` is recorded
with its pre-registered thresholds and the result is published.

Frozen means: `docs/70-SERVICE-TIERS.md`, `docs/80-PRICING-DOCTRINE.md`, and every price, margin, SKU and promise
in them. No edits except a correction of a factual error, each of which cites this ADR.

**Two exceptions, because they are cheap now and expensive later.**

### Exception 1 — three reserved fields in the bundle

The bundle format gains three optional fields. They are defined now and may stay unused:

```
issuer            # who signs: identity of the party asserting the claim
valid_until       # the period during which the assertion is claimed to hold
reliance_scope    # for what a third party may rely on it, and for what not
```

Cost of adding them now: minutes. Cost of adding them after bundles exist: every bundle is re-signed, the format
version is bumped, and every verifier written against the old format is wrong. The liability surface a buyer needs
(round 6, review 1 and 3) lives in exactly these three fields, so the envelope is cut before we know what goes in it.

Their semantics are `not_claimed` until a counterparty defines them: the fields reserve the shape, not the meaning.

### Exception 2 — one conversation, triggered by the artifact

The buyer conversation (`docs/34-OPEN-QUESTIONS.md` P1, P2) is **not** deferred indefinitely. It is triggered by
`E-M9`, not by a date, and it happens within two weeks of that measurement. Asking before an artifact exists
produces opinions about a plan; asking with a bundle in hand produces a decision about a thing.

## What this changes

- `STATUS-v0.md` records the freeze and the trigger.
- `70` and `80` carry a one-line freeze notice pointing here, so a reader does not mistake doctrine for a live offer.
- `SPEC-v0.1.md` and the bundle definition note the three reserved fields.
- No new commercial document, no pricing calibration, no grant applications until the trigger fires.

## Consequences

- If the product turns out to be unsellable, we learn it after three days of code rather than after another month of
  documents. That is the intended failure mode.
- The frozen doctrine may drift from reality. That is accepted: a wrong live price is worse than a stale frozen one.
- `ADR-0001` is unaffected: the build order stands.

## What this decision does NOT do

- It does not decide whether a liability surface will be offered. It only reserves the fields where it would live.
- It does not make the product sellable. It postpones the question of whether it is.
- It does not commit the owner to signing anything. `reliance_scope` can legitimately end up saying "informational,
  not a basis for payment", and that is a product decision for later.
