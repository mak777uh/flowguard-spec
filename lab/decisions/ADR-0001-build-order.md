# ADR-0001 — build order: the substitution test comes first

**Date:** 2026-10-27 · **Status:** accepted · **Decided by:** round 6, five independent reviews
**Source:** [`docs/32-ROUND6-SYNTHESIS.md`](../../docs/32-ROUND6-SYNTHESIS.md)

## Context

The plan at review time was: (1) bundle format, 1 day; (2) browser verifier, 3 days; (3) substitution test,
3 days; with an Arweave archive of the claim registry as a parallel deliverable.

All five reviewers rejected the order, four of them for the same reason: the artifact that proves the mechanism
works is not the verifier, it is the **test that makes the verifier fail**. A verifier without such a test is a
program that works according to its author.

One reviewer added the argument that decided it: the verifier's substantive content is not the hash comparison —
`sha256sum` does that — it is **recomputing the denominator** (closure, coverage, excluded, unknown) and refusing
a bundle whose printed numbers do not derive from its objects. That is a few days of work and it needs no
browser.

## Decision

1. **First artifact:** `E-M9`, the substitution test, with thresholds fixed before the run. It defines what the
   verifier must reject.
2. **Second:** only the verifier checks that `E-M9` requires — schema and canonical form, digests, signatures,
   recomputation of the verdict from coverage, exclusions, invariants, detector identity and policy, and a
   machine-readable reason on refusal.
3. **Browser verifier:** deferred to an optional front end. Not a proof carrier; it adds isolated execution and
   convenience, and nothing else.
4. **Arweave archive:** deferred until a consumer exists who needs durable history. It proves durability of text,
   not that a control works.

## Two substitution classes, and why one is not enough

The original formulation was near-tautological: replace the code, the digest fails, the verifier rejects. That
tests our own hash comparison.

- **D-1 — tampering after signing.** A subject (code, build, configuration, identity) is replaced while the
  original signature remains. Rejection is expected from digest mismatch.
- **D-2 — falsely attested pair.** A bundle is correctly signed by a trusted key but describes a different target
  than the one presented. Signature and digests are valid; the claim is false. This is the mechanism we called
  **T1**, and D-1 does not touch it.

D-2 is the test that can fail in an interesting way, and therefore the one worth pre-registering.

## Offline vs bound to the running version

The reviews found a contradiction in our own framing: an offline verifier cannot establish what code is deployed
at an address. That requires `extcodehash` from a finalized checkpoint — the network, or carried evidence.

**Resolved by scope, not by cleverness:** what is verified offline is stated in the bundle and in `CLAIMS.md`,
and the *binding to the running deployment* is written into `not_claimed`. An artifact that silently claims a
property it cannot have is worse than a smaller artifact that says what it does.

## Consequences

- `STATUS-v0.md` gains the kit item M1 as present (the first experiment card), and keeps M2 and M7 absent.
- The claim "the browser verifier is where the value is" is eliminated (X-16).
- The archive decision is reversible: a consumer who needs history reopens it.

## What this decision does NOT do

- It does not make the verifier trustworthy. A verifier that passes `E-M9` has been shown to reject the
  substitutions we thought of; it has not been shown to reject the ones we did not think of.
- It does not establish that anyone wants the artifact.
- It does not settle T2 (policy drift) or T3 (a narrowed closure).
- It does not make `PROVEN` attainable for a whole application. It only makes the failure modes visible.
