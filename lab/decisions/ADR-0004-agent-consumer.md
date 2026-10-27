# ADR-0004 — the consumer of the tool is an agent, not a human

**Date:** 2026-10-27 · **Status:** accepted · **Related:** ADR-0003, ADR-0001

## Context

The tool was designed as if a person would run it: a report to read, minutes per review, a browser tab to check a
bundle in. The owner corrected the premise: **the user is an AI agent inside a harness**, which reads the target
code, proposes the boundary, and calls our tool. People do not run it by hand.

That correction removes the objection that blocked the variant work ("we cannot read someone else's code") —
reading code is the agent's job. It also changes what the tool must be good at, and what must be removed.

## Decision

**1. The interface is machine-only.** Stable JSON in, stable JSON out, deterministic, non-interactive, meaningful
exit codes, no prompts, no UI. A human-readable rendering may exist as an *output* of the verdict, never as an
input path.

**2. The browser verifier is not a product surface.** An agent has no browser. `X-16` stands, now for a stronger
reason.

**3. Two formats, not one.** The bundle (the claim) and the **agent report** (the analysis the claim rests on):
discovered paths, the control point, paths excluded and why, the detector and its recall, what was not found.
The verifier compares the two and refuses when the claim does not follow.

**4. The tool's job is refusal, not eloquence.** Its value is the sentence "this does not follow from what you gave
me, and here is why, machine-readably". An agent that gets a downgrade can iterate; an agent that gets prose cannot.

**5. The division of labour, stated plainly:** the agent has eyes, the tool has a conscience. The agent finds paths;
the tool decides what may be claimed, forces the denominator into the open, and blocks the exclusion of
inconvenient paths.

## The test this creates

The interesting failure is no longer "does the verifier catch a bad hash" but:

> **An agent reports coverage 0.6 and claims "proven". The tool must downgrade or refuse.**

That is the overclaim test, and it is the reason the tool exists for an agent consumer. It becomes a card
(`E-M11`) with its own threshold, and it is the demo that matters: not a hash check, but a self-confidence check.

## What this changes in existing documents

- `docs/CLAIMS.md` C-11 (reviewer minutes) is about a human workflow that is no longer the primary path — it stays,
  marked as the human branch.
- `docs/70-SERVICE-TIERS.md` and `80-PRICING-DOCTRINE.md` already frozen by ADR-0002; their assumption of human
  engagements is now doubly stale.
- `docs/50-IMPLEMENTATION-STAND.md` and `51-HARNESS-BUILD.md` assumed a human-facing CLI; the CLI stays, the
  human-facing report layer is optional.

## What this decision does NOT do

- It does not claim that agents can be trusted to report honestly. It assumes the opposite, which is why the
  verifier exists.
- It does not remove human judgement from findings (an agent's `CONFIRMED` still deserves a human sign-off in any
  liability-bearing context).
- It does not decide who signs the bundle when an agent produced it. **That is open** and goes to round 7.
