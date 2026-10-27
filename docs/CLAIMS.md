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
| C-01 | The attestation bundle verifies offline, without contacting the issuer | `test` | "verifies offline for bundle format fg/1" | `lab/e2e/verify-offline` | a bundle accepted after the issuer is unreachable *and* the artifact is swapped |
| C-02 | Two runs of the same input produce a byte-identical bundle | `test` | "reproduces byte-for-byte on the reference target" | `lab/e2e/replay` | one differing byte between two runs of an unchanged tree |
| C-03 | The detector finds privileged paths with recall r on corpus C | `statistics` | "recall r on C, n targets" — with interval, never as a general rate | `lab/experiments/E-M1` | a manually found path absent from `discovered_paths` in a blind arm |
| C-04 | Escrow invariant INV-1 holds for standard ERC-20 tokens | `proof` | "proved for the model under the standard-transfer assumption" | `lab/experiments/E-C2` | any accepted input where the accounting identity breaks |
| C-05 | INV-1 does **not** hold for fee-on-transfer or rebasing tokens | `test` | "fails on the token-class corpus; such targets return INCONCLUSIVE" | `lab/experiments/E-C2b` | a fee-on-transfer target receiving a strong verdict |
| C-06 | An unknown path blocks a strong verdict | `test` | "returns INCONCLUSIVE when `unknown_paths` is non-empty" | `lab/e2e/unknown-path` | a bundle with a non-empty unknown set receiving `PROVEN` |
| C-07 | The ten on-chain attacks are blocked on the reference escrow | `test` | "10 of 10 blocked on the reference target; each attack fails on the mutated target" | `lab/e2e/attacks` | one attack passing, or an attack passing on the mutated target too (tautology) |
| C-08 | A signed bundle proves the target is the one attested | `judgment` | "bundle binds target digest" | `lab/experiments/E-M9b-substitution-anchored.md` | a substituted code/build/config/identity accepted with valid signatures. Promotion to `test` requires E-M9b; the reserved words are unavailable to this claim until then |
| C-09 | The database trigger is a physical guarantee | **withdrawn** | may be stated only as "one enforcement layer, conditioned on the privilege model" | `lab/experiments/E-G8` | a mutation past the trigger via replication, superuser or DDL |
| C-10 | Every mutation of the ledger has a signed Permit and an Allow event | `test` | "holds on the instrumented target for the declared privilege model" | `lab/experiments/E-G9` | a mutation without a cryptographically bound Allow event |
| C-11 | A reviewer signs one finding in 15 minutes | **not established** | may be stated only as a target; planning value is 35–40 minutes `[statistics pending]` | `lab/experiments/E-M2` | median above 45 minutes on 30 findings with three reviewers |
| C-12 | Three oracle classes yield at least two findings per target | **not established** | may not be stated until E-M5 runs | `lab/experiments/E-M5` | median below 1 on 12 targets |
| C-13 | The guarantee price follows value at risk | `judgment` | "our pricing model is" — never "the price is justified by loss data" | `lab/experiments/E-M6` | fewer than 3 of 10 buyers accepting the formula at any level |
| C-14 | An external party relies on the attestation to change a decision | **not established** | may not be implied anywhere | `lab/experiments/E-M8` | zero of ten consumers willing to commit in writing |
| C-15 | A client cannot narrow the closure to manufacture a strong verdict | `test` | "excluded-path ceiling and coverage scalar are enforced; a narrowing attempt drops the level" | `lab/e2e/narrowing` | a bundle with `excluded > 0` on a money path receiving `PROVEN` |
| C-16 | The formal contour proves model-to-code correspondence | **false as stated** | must read: "proves statements about the extracted model; correspondence is not instrument-checked" | — | an executable instrument checking the correspondence |
| C-17 | Composing C/T/N in a dumb aggregator is safer than a combined oracle verdict | `judgment` | "our position is" | — | a correlated-error case where the combined verdict fails and the split one does not |
| C-18 | Legacy median findings per target is about 1 | `statistics` | "five independent estimates clustered at 1; not measured" | `lab/experiments/E-M5` | a measured median ≥ 2 on the M5 corpus |

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
