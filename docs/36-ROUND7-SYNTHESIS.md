# Round 7 synthesis — five reviews, one verdict: the name was wrong

**Date:** 2026-10-27. **Material:** `docs/15-ROUND7-QUESTIONS.md`. **Reviews:** five, independent.

This round did not produce objections to a design. It produced a **verdict about what the artifact is**, and all
five reviewers reached it independently. Unlike rounds 1–6, this one cannot be answered by adopting a few columns.

---

## 1. The verdict, in their words and in one line

> What we have is **verification that two documents agree** — where both documents may be produced from the same
> wrong reading of the same system. Calling that "attestation of security" is not a marketing choice; it is a
> false statement about the artifact.

Review 2 put it most sharply: *"without an independent of the agent closure, 'attestation' is the wrong name for
comparing two equally wrong documents."* Review 3: *"the party that did the work never certifies the work."*
Review 5 named the class: specification gap, oracle problem, common-mode failure.

## 2. Convergence, with counts

| # | Finding | Reviews | What it forces |
|---|---|---|---|
| 1 | **The name is wrong.** The artifact verifies internal consistency, not safety | 5/5 | rename, and add the boundary to `not_claimed` |
| 2 | **An independent anchor is mandatory**: an obligation/path inventory, a target lock, and the previous bundle | 5/5 | new mandatory inputs; without them the verdict is capped |
| 3 | **Common-mode failure cannot be removed**, only declared | 5/5 | `not_claimed` entries, and no claim of reality correspondence |
| 4 | **Signatures must be split by assertion**, not one issuer | 4/5 | four signature types |
| 5 | **Refusal codes: 5–8, machine-actionable, with a retry budget** | 4/5 | a taxonomy, and `POLICY_CEILING_EXCEEDED` must not be auto-fixable |
| 6 | **An outside-path count is not enough.** Need a denominator, weighted residual risk, a delta and a cap; and no level upgrade while the perimeter grows | 5/5 | a perimeter block that gates the verdict |

## 3. The three blockers one reviewer named explicitly, and the others assumed

**B1 — no source of truth for the boundary.** If the only source of paths is the agent, and the verifier checks only
the agent's internal consistency, the system cannot see its own blind spot. This is the same wall we hit in round
1 (`unknown_paths = ∅` proves only absence inside the analyser's model), now at the level of the product.

**B2 — the semantics of a positive verdict are undefined.** Possible meanings: documents agree; fields are filled;
required checks were performed; evidence satisfies the policy; the flow's boundary is justified; the property holds
within the model. These are different guarantees stacked under one word.

**B3 — metrics are untested against reality.** Coverage 0.85 says nothing if the list of required checks is
incomplete, and nobody has measured our false-accept rate.

## 4. What we are changing — and it is a downgrade, not a tweak

**4.1 The artifact is renamed.** Not "attestation of security". The correct name is what it does:

> **`scoped consistency attestation`** — the report of an analysis was checked against a policy, and every
> obligation the policy requires is either satisfied by evidence or explicitly listed as outside the scope.

**4.2 The verdict ladder gains an explicit ceiling.** A flow can reach `PROVEN` only when its inventory came from a
source the agent did not control. Otherwise the strongest available verdict is:

> **`CONSISTENT_DECLARED(R)`** — documents agree at the declared coverage, with an independent inventory absent.
> That absence is printed in the verdict, not in a footnote.

**4.3 Three inputs become mandatory** in the bundle: `target_lock`, `obligation_manifest`, `previous_bundle`. With
no `obligation_manifest` from outside the agent, the verifier returns `E_NO_INDEPENDENT_CLOSURE` and the verdict
cannot exceed `CONSISTENT_DECLARED`.

**4.4 Signatures split into four assertions:** `analysis_provenance` (the agent), `process_attestation` (the
harness), `consistency_verdict` (the verifier), `risk_acceptance` (a person or an operator). One signature claiming
all four is exactly the confusion the reviews named.

**4.5 The perimeter block gates the level.** `known_paths`, `core_paths`, `outside_paths`,
`outside_weighted_risk`, `delta_since_previous`, `perimeter_cap`, `perimeter_growth`,
`level_upgrade_allowed`. Growth of the perimeter without explicit acceptance forbids an upgrade, even when the core
grew.

**4.6 Refusal taxonomy:** six codes with `subject`, `expected`, `observed`, `next_action`, `retryable`, plus an
attempt budget. `POLICY_CEILING_EXCEEDED` and `E_NO_INDEPENDENT_CLOSURE` are explicitly **not** auto-fixable.

## 5. What this costs us, said plainly

- **The promise "we prove your flow cannot be bypassed" is unavailable.** It becomes available for a specific flow
  only when an independent inventory of that flow's paths exists. Without it we sell consistency and perimeter
  accounting.
- **`PROVEN` moves further away**, not closer: it now requires an inventory we do not have.
- **The first code artifact changes**: not "a verifier that proves", but "a verifier that refuses", with the
  refusal codes as its visible surface.
- **One review noted the honest upside**: an artifact whose claim is narrow can be believed. The alternative —
  a broad claim with no anchor — is what every failed verification product looked like.

## 6. Corrections to our own text

- "The agent has eyes, the tool has a conscience" (ADR-0004) was too generous. A conscience can only audit what it
  is shown; ours was described as if it could audit what it was not shown. Corrected in ADR-0005.
- `E-M9` D-2 tests a swapped pair. It does **not** test a path the agent never mentioned. The reviews are right
  that this is a different failure, and it needs its own card after an independent inventory exists.
- The perimeter rule in ADR-0003 ("publish the count of outside paths") was necessary and insufficient. Upgraded
  to the block in §4.5.

## 7. What is adopted, what is deferred

| item | status |
|---|---|
| renaming and `not_claimed` entries | **adopted now** — `ADR-0005` |
| three mandatory inputs, capped verdict | **adopted now** — `ADR-0005` |
| four signature assertions | **adopted now** — `ADR-0006` |
| perimeter block | **adopted now** — `ADR-0006` |
| six refusal codes with retry budget | **adopted now** — `docs/37-REFUSAL-CODES.md` |
| independent path inventory | **deferred, and it is the next real engineering problem** |
| testing against false accepts | **deferred to `E-M11`, after the verifier exists** |
| the T1–T10 scenario table from review 1 | **adopted as the acceptance suite**, `E-M11` |

## 8. Is another round needed

**No.** The reviews converged on a name and an anchor; the remaining work is an independent inventory and a test
suite, both of which are engineering. Round 8 would be asked to answer questions that only a path enumerator and a
false-accept measurement can answer.

One question does survive, and it is not for a review: **whether to build the independent inventory ourselves, or to
define the interface and let the customer's own tooling supply it.** That is a product decision with a technical
consequence, and it is the owner's.

---

## Addendum — M7 has an explicit marker

A kit conformance number that can be inflated by prose is worthless. `lab/check-interop.py` counted M7 as present
because `E-M10` mentioned "independent rebuild" in its consequences section — a fourth false positive of our own
instrument.

From now on M7 is satisfied only by an experiment card carrying the line:

```
rebuild_result: <agreed | differed | not attempted> by <party> on <date>: <what happened>
```

Nothing else counts. A note asking someone to rebuild is a request, not a result, and the counter now says so.
