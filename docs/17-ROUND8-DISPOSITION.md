# Round 8 answers — disposition

Three independent models answered the uncertainty brief. This file records what was done with each
recommendation, so nothing is silently dropped and nothing is silently accepted. Every line is one of:
**done** (with the card), **accepted** (with the card that will do it), **rejected** (with the reason).

Sources: three reviews of `DOSSIER.md`, received 2026-10-28. All three converged on items 1, 3, 4, 5, 6, 7, 8.

---

## Where all three agreed, and what changed

### Coverage needs three states, not a ratio — **done** (`E-M23`)

All three: a single ratio cannot distinguish "enumerated and observed", "enumerated and never seen", and
"observed but not enumerated". The third is the dangerous one: it proves the denominator is already incomplete.

Implemented: `tools/fg_coverage.py` computes `covered / unobserved / unenumerable` on the verb dimension, where the
catalogue and the log speak the same language. An observed verb with no catalogue path raises
**`UNENUMERABLE_PATH`** and blocks any upgrade. Measured on the fixture: `DELETE` was observed, the catalogue knew
`INSERT` and `UPDATE` → the ratio was computed over a denominator already known to be wrong, and the verifier now
refuses to.

*Not yet done:* function-level `unenumerable`. It needs nested-statement logging (pgAudit
`log_nested_statements`), which is exactly the gap `E-M17` measured. Accepted, not claimed.

### Numbers are demonstration, not evidence — **accepted** (`E-M24`, needs foreign schemas)

All three: fixtures written by the author prove the detector, not the world. Suggested shapes: 12–20 schemas
(one reviewer), ≥30 stratified across three stacks (another), 3–5 with owner-confirmed ground truth (the third).

What is already true and stays true: one public schema exists (Pagila), and it produced one real finding.
What is added: `evidence_tier` (0 fixtures / 1 controlled real / 2 foreign with ground truth / 3 blind independent)
as a field, plus an `NC` code so a claim on tier 1 cannot be read as tier 2.

What cannot be done from inside: the schemas themselves. This is the owner question, unchanged.

### Risk weights are policy, not measurement — **done** (`E-M24`)

Accepted as stated: rename to a policy-weighted score, publish `weight_provenance`
(`internal_convention | customer_contract | regulatory_table | actuarial`), and say in `not_claimed` that the
weights are not a measurement. One reviewer's `NC-07` already said the second half; the first half was the missing
water.

### Name-based joining is not an identity — **accepted** (`E-M25`)

Convergent: joins must carry `(schema, object, signature|oid)` and a `resolution_level`
(`exact | probable | ambiguous | unresolvable`), and ambiguous edges must block an upgrade rather than be silently
resolved. Ours currently joins on a bare function name and records `transitive`.

Not done in this round because it touches the merge contract; carded with the four states named above.

### Perimeter growth should be classified, not blanket-blocked — **accepted** (`E-M26`)

Convergent: split `additive` / `subtractive` / `substitutive`. Blanket blocking rewards stagnation and punishes
cleanup — the ratchet problem. One reviewer's phrasing of the audit question is the one to keep: *"was this a
documented, tested replacement with the same or lower risk class?"*

### Exclusion reasons need typed preconditions — **done** (`E-M27`)

Convergent: a `reason_code` enum with machine-checkable preconditions (`NOT_REACHABLE` needs no inbound edges,
`COMPENSATING_CONTROL_PRESENT` needs a reference that resolves), plus a contradiction check between reason class and
path risk class. Ours checks existence, non-core membership, and that the reason is at least eight characters — which
is what one reviewer called "syntactic validity". They are right.

### Signatures must be split — **accepted** (`E-M28`, format change)

Convergent: `attestation_signature` (provenance and integrity), `risk_acceptance` (an authorised party accepts
residual risk, with scope and expiry), `liability_agreement` (a contract, not a field). Ours reserves one field for
all three, which is worse than reserving none.

### The consumer question — **no change**, and none was needed

All three said the same thing the repository already says: no named consumer, no evidence, and ten conversations
that produce nothing is a legitimate negative result. One added a narrower and more useful hypothesis: an internal
AppSec engineer or DBA who would *choose which twenty functions to review by hand* differently. That is a better
first question than "who signs", and it is now the first line of `M8-CONSUMER.md`.

---

## Where the reviewers disagreed, and what I decided

**How many schemas.** 12–20, ≥30, or 5. Decided: **5 public schemas first**, because I can do that alone, and the
number that matters is not the count but whether the sample was chosen before the result. A blind protocol with 5
beats an unblinded 30.

**Whether pgaudit closes the nested-statement gap.** Two said yes, one said it only adds a witness. Decided: they
are both right about different things — it closes **observability**, not **enumeration**. It goes into the witness
column with a separate code, never into the denominator.

**Whether an agent can be prevented from narrowing scope.** Two said no, only made visible; one proposed a
`scope_commitment` signed before analysis. Decided: implement the commitment (it is cheap and it makes narrowing a
recorded diff), and keep the honest sentence — an agent that controls the policy can still pick a narrow world.

---

## What I am NOT doing, and why

- **Attestation-as-a-service, pricing, indemnity.** Both the reviews and the owner's own doubts agree. Frozen since
  `ADR-0002`; nothing here changes that.
- **A universal risk-weight table.** "No evidence" from all three. The weight stays a recorded convention.
- **Claiming tier 2 on public schemas.** Pagila is a sample database, and one reviewer is right that it is not a
  production schema. Tier 1 until an owner confirms a finding.

## The sentence I am adopting

> The product is not a legal shield. It is an X-ray for a DBA that also shows where the machine could not see
> through — and it does not issue a pathologist's report.

That is a better description of the artifact than anything in our own docs, and it goes into `README.md` as the
positioning line, credited to the review rather than to us.
