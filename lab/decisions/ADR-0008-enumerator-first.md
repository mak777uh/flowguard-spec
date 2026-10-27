# ADR-0008 — the enumerator comes before the verifier

**Date:** 2026-10-27 · **Status:** accepted · **Amends:** ADR-0001 (which put the substitution test first)

## Context

ADR-0001 ordered the work: substitution test → verifier → browser (later dropped). That order assumed the thing
the verifier checks exists. After ADR-0005 it does not: without an inventory from a source the agent did not
control, **every verdict is capped at `CONSISTENT_DECLARED`**. Building a verifier first would produce a machine
that formats a capped answer.

## Decision

Order becomes: **enumerator → inventory merge → verifier → substitution test (`E-M9`) → corpus (`E-M10`)**.

Reason: the enumerator is what lifts the round-7 ceiling, it is useful on its own without any verifier, and its
quality can be measured immediately against a planted ground truth — as `E-M11` just did (8/8 planted bypasses,
one false positive, two instrument defects found in the process).

## Consequences

- `lab/experiments/E-M11` is completed before `E-M9` runs, which reverses the plan's card order but not its logic:
  the first measurement is now about discovery, not about formatting.
- The next artifact is `fg-enum-routes` or the verifier, whichever is chosen; the enumerator already satisfies
  `independent_of_agent` for analyses that include it.
- ADR-0001's rationale for test-first is not refuted, only postponed: `E-M9` still gates any claim about rejection
  behaviour.

## What this decision does NOT do

- It does not make the inventory complete. E-M11 measures expressibility on a fixture written with the enumerator
  in view, and says so.
- It does not remove the need for `E-M9`. A verifier built before its substitution test is still a program that
  works according to its author.
