# CLAIMS — typed claim registry

Every claim the product makes carries an evidence type. The evidence type fixes **the strongest wording
that may be used** — in the spec, in a report, in a sales conversation. A linter (`lab/check-claims.py`)
enforces that a claim does not use stronger wording than its evidence type allows, and that every cited
artifact exists.

Borrowed from [Project Morphogenesis](https://github.com/mak777uh/-) (`manuscript/CLAIMS.md`), where a
linter enforces the schema and the existence of cited artifacts. The rule that matters most:

> A claim may not be worded more strongly than its evidence type permits. Changing the wording upwards
> without changing the evidence type is a defect, not a marketing decision.

## Evidence types and the worst they may say

| Type | Meaning | Strongest permitted wording |
|---|---|---|
| `proof` | machine-checked statement about a model extracted from code | "proved for the model of version X under assumptions A" |
| `test` | deterministic instrument run, reproduces bit-for-bit | "holds for the declared closure on the test corpus" |
| `statistics` | counts over a declared corpus with intervals | "observed k of n; interval; does not generalise beyond the corpus" |
| `observation` | single run, or a run not reproduced | "observed once" — may never carry a guarantee word |
| `judgment` | reasoned position without measurement | "our position is" — may never appear in an attestation |

Three words are reserved and may appear **only** with `proof` or `test`: `PROVEN`, `ENFORCED_TESTED`,
`guarantee`. A claim typed `statistics` or weaker may say "measured", "observed", "estimated" — never a
reserved word.

## Registry

| ID | Claim | Type | Allowed wording | Artifact | What would refute it |
|---|---|---|---|---|---|
| C-01 | The attestation bundle verifies offline, without contacting the issuer | `test` | "verifies offline for bundle format fg-bundle/1" | [bundle.json](../fixtures/sample-bundle/bundle.json) | a bundle that requires a network call to verify |
| C-02 | Two runs of the same input produce a byte-identical bundle | `test` | "reproduces byte-for-byte on the reference target" | `lab/experiments/E-M31-determinism.md` | two builds of the same input with different addresses |
| C-03 | The detector finds privileged paths with recall r on corpus C | `statistics` | "recall r on C, n targets" — with interval, never as a general property | `lab/experiments/E-M11-grant-enumeration.md` | a planted bypass that the enumerator misses |
| C-04 | Escrow invariant INV-1 holds for standard ERC-20 tokens | **withdrawn** | no claim: the product pivoted away from escrow to flow-level checks on database paths | — | not applicable |
| C-05 | INV-1 does **not** hold for fee-on-transfer or rebasing tokens | **withdrawn** | no claim: same pivot; no token-class corpus exists | — | not applicable |
| C-06 | An unknown path blocks a strong verdict | `test` | "an unenumerable action, an unresolved attribution or a contradictory exclusion blocks an upgrade" | `lab/experiments/E-M23-three-state-coverage.md` | a verdict that improves while an unknown path is present |
| C-07 | The ten on-chain attacks are blocked on the reference escrow | **withdrawn** | no claim: the escrow target no longer exists under this product | — | not applicable |
| C-08 | A signed bundle proves the target is the one attested | `judgment` | "bundle binds target digest" | `lab/experiments/E-M9b-substitution-anchored.md` | a substituted code/build/config/identity accepted with valid signatures. Promotion to `test` requires E-M9b; the reserved words are unavailable to this claim until then |
| C-09 | The database trigger is a physical guarantee | **withdrawn** | no claim: a trigger is one enforcement layer, conditioned on the privilege model | — | a mutation past the trigger via replication or a superuser session |
| C-10 | Every mutation of the ledger has a signed Permit and an Allow event | **withdrawn** | no claim: the ledger/Permit model belongs to the pre-pivot product | — | not applicable |
| C-11 | A reviewer signs one finding in 15 minutes | **not established** | may be stated only as a target; the planning value was 35–40 minutes | — | median above 45 minutes on 30 findings |
| C-12 | Three oracle classes yield at least two findings per target | **withdrawn** | no claim: the oracle-class design was cut before any measurement | — | not applicable |
| C-13 | The guarantee price follows value at risk | **withdrawn** | no claim: pricing is frozen by ADR-0002 and no loss data exists | — | not applicable |
| C-14 | An external party relies on the attestation to change a decision | **not established** | may not be implied anywhere; the form is unfilled | `docs/M8-CONSUMER.md` | one filled form naming a decision that changed |
| C-15 | A client cannot narrow the closure to manufacture a strong verdict | `test` | "exclusions are bound to real paths with typed reasons; narrowing lowers the computed coverage" | `lab/experiments/E-M14-exclusions.md` | a narrowing that raises the verdict |
| C-16 | The formal contour proves model-to-code correspondence | **false as stated** | must read: "proves statements about the extracted model; correspondence is not instrument-checked" | — | an executable instrument checking the correspondence |
| C-17 | Composing C/T/N in a dumb aggregator is safer than a combined oracle verdict | `judgment` | "our position is" | — | a correlated-error case where the combined verdict fails and the split one does not |
| C-18 | Legacy median findings per target is about 1 | **withdrawn** | no claim: the estimate was never measured and the corpus no longer applies | — | not applicable |

## Rules for adding a claim

1. A claim without a type does not exist and may not be referenced.
2. A claim citing an artifact that does not exist fails the linter.
3. Moving a claim **up** in evidence type requires a new `E-` card and an `ADR`; moving it **down** requires only an `ADR`.
4. `withdrawn` and `false as stated` are permanent records. A withdrawn claim stays in the registry with the reason — deleting it is how a team forgets why it was withdrawn.
5. The three reserved words are grep-enforced across `docs/`, `README.md` and any future report template: a file containing them must link a claim of type `proof` or `test`.

---

## Corrections from round 6 (2026-10-27)

**`PROVEN` is not unreachable in principle.** Review 3 objected, correctly, to our earlier flat statement.
Whether `PROVEN` is attainable depends on the strictness of the model, the boundary of the object and the
completeness of the checked paths. It is unreachable **for a whole application under our assumptions**; for a
narrow closure it may be attainable. Claims here must say which of the two they mean.

**A point estimate of recall is not a measurement of recall.** `0.71` on a corpus of 20 is roughly 14/20, and the
interval at that size is about 0.5–0.9. Every published recall figure must carry its interval and the corpus, or
it is decoration. A buyer with an auditor will compute the interval whether or not we print it.

**Instrument correctness is not a column.** Five reviewers converged: the eight columns cannot detect a wrong
instrument. Any claim whose strength depends on an instrument must point at that instrument's negative control —
a planted defect the instrument is required to catch. Until such a control exists, the claim's permitted wording
drops by one level.
