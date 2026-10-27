# ADR-0003 — the core grows ring by ring, and the perimeter is always published

**Date:** 2026-10-27 · **Status:** accepted · **Related:** ADR-0001 (build order), ADR-0004 (the consumer is an agent)

## Context

Everything in this repository until now assumed one boundary per engagement and one verdict per system. That
assumption is what broke the product twice: an whole-application guarantee is unreachable, and a verdict that
covers "the system" is either false or says nothing.

The owner's framing is the one that survives: start from a **real, large service**, find one flow inside it that
can be made strict *today* (storage, money movement), pin it as a core behind a single door, and let the rest of
the system stay messy **while saying so**. When the mathematics catches up, the next flow is absorbed into the
core. The core grows; the messy part shrinks; nobody ever claims the whole house is safe.

This is how verification has actually shipped — seL4 did not verify Linux, it built a verified kernel and left the
rest above it — and it is the only shape that survives the finding that whole-application completeness is not
provable.

## Decision

**1. The unit of attestation is a flow, not a system.** A bundle carries a list of flows, each with its own level,
its own date, and its own evidence.

**2. The perimeter is a first-class field.** Every bundle states, explicitly and machine-readably, which paths are
**outside the core**. A bundle that lists only what is inside is invalid.

**3. A flow enters the core only through evidence.** Promotion is not a decision but a change of the claim's
evidence type: `judgment` → `test` → `proof`, each requiring its artifact. There is no "we decided it is safe now".

**4. Growth is published as a versioned map**, not as a badge:

```
flow "balance transfer"   level=proof          since=2027-01  evidence=E-C2, INV-1..3
flow "file retrieval"     level=chokepoint+witness since=2027-03  evidence=E-G9
flow "personal data"      level=chokepoint     since=2027-05  evidence=E-G8
outside the core          14 paths, listed in `outside[]`
```

## The failure this creates, and the rule against it

Progressive growth invites the vacuum (T3) at a higher level: adding rings looks like progress while the
perimeter quietly stays unstated. The rule:

- `outside[]` is mandatory and its **count is published next to the coverage scalar**;
- an attestation that adds a ring must show the perimeter before and after;
- a reader who sees only rising levels and no perimeter is looking at a brochure, and the format does not let them
  see that by accident — the field is required.

## Consequences

- `SPEC-v0.1.md` and `SPEC-v0.2-LEGACY.md` describe one boundary each; they remain valid as **the first ring**, not
  as the product's shape.
- `docs/32-ROUND6-SYNTHESIS.md`'s single-verdict framing is superseded for the format, not for the arithmetic.
- The claim registry gains a per-flow dimension; `CLAIMS.md` rows that assume one boundary per engagement are
  marked as such rather than rewritten.

## What this decision does NOT do

- It does not make any flow strict. It defines where strictness is recorded.
- It does not promise that a later ring will be reachable. Each ring is its own experiment.
- It does not change the verdict ladder; it changes the scope the ladder applies to.
