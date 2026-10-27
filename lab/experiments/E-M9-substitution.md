---
id: E-M9
hypothesis: H-M9
status: planned
base_commit: ""
started: ""
finished: ""
environment: "unset at pre-registration; recorded at run time (OS, CPU, runtime versions, and the exact toolchain that produced the bundle)"
command: "unset at pre-registration; recorded at run time"
threshold: "D-1: 4 of 4 subject substitutions rejected with a machine-readable reason naming the mismatched field. D-2: 2 of 2 falsely attested pairs must NOT receive PROVEN or ENFORCED_TESTED. Any green verdict on any of the 6 cases fails the experiment."
result: "not run"
verdict: pending
---

# E-M9 — substitution test

## Pre-registration (before the run)

**Question.** Does a verifier built from our own documents reject a bundle that is cryptographically valid but
describes something other than what it is presented with?

**Why this is not a tautology.** Rejecting a modified payload is ordinary hash comparison. The interesting case is
a bundle whose signature and digests are intact and whose *claim* is false — the bundle was signed for target A and
is presented with target B. That is mechanism T1, and a hash check cannot see it.

**Two classes.**

| id | what is substituted | expected outcome |
|---|---|---|
| D-1a | code artifact | `INVALID`, reason names the code digest |
| D-1b | build artifact | `INVALID`, reason names the build digest |
| D-1c | configuration | `INVALID`, reason names the configuration digest |
| D-1d | identity (signing subject) | `INVALID`, reason names the identity mismatch |
| D-2a | whole pair: bundle signed for target A, presented with target B | not `PROVEN`, not `ENFORCED_TESTED` |
| D-2b | whole pair, with the manifest numbers consistent under A and inconsistent under B | not `PROVEN`, not `ENFORCED_TESTED` |

**Threshold, fixed now and not adjustable after seeing results.**

- D-1: **4 of 4** rejected, each with a reason that names the mismatched field rather than a bare boolean.
- D-2: **2 of 2** must refuse a strong verdict. `INCONCLUSIVE` or `INVALID` are both acceptable; a green verdict
  is a failure of the experiment.
- A single green verdict on any of the six cases fails `E-M9` as a whole.

**Failure is a result.** If D-2 passes a green verdict, the claim "the verifier binds a bundle to its target" is
recorded as `false as stated` in `docs/CLAIMS.md`, and the elimination is published. We pre-register this because
the alternative — quietly widening the test until it passes — is the failure mode this whole repository exists to
avoid.

**What is out of scope, and will be written into `not_claimed`.** The binding between a bundle and the *running
deployment* — what code actually sits at an address — is not verified offline. It requires `extcodehash` from a
finalized checkpoint, i.e. the network or carried evidence. `E-M9` tests the bundle's internal consistency and its
refusal behaviour, not the truth of the world.

## Run

Not run. This card exists so that the threshold is fixed before anyone writes the verifier.

## Result

Not run.

## What this card does NOT do

- It does not measure detection quality. Four substitutions we thought of are not a corpus.
- It does not validate the instrument that produces bundles.
- It does not test the ledger branch (on-chain escrow) or the legacy branch; both need their own cards.
- It does not show that a bundle which passes `E-M9` is trustworthy — only that it is not defeated by these six
  specific attacks.
