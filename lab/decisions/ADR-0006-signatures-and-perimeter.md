# ADR-0006 — four signatures, one perimeter block

**Date:** 2026-10-27 · **Status:** accepted · **Related:** ADR-0005, ADR-0003, ADR-0002

## Context

Two convergences from round 7 remain to be encoded: signatures that claim different things must be different
signatures, and a growing core must be gated by a perimeter that cannot be quietly improved.

## Decision 1 — four assertions, four signers

| assertion | signed by | claims | does NOT claim |
|---|---|---|---|
| `analysis_provenance` | the agent or its harness | this report was produced by this producer from these inputs | that the report is right |
| `process_attestation` | the harness / orchestrator | the run used this policy in this environment; these are the artifact digests | that the process was adequate |
| `consistency_verdict` | the verifier | the report was checked against the policy and the result is this | that the policy or the inventory is complete |
| `risk_acceptance` | a named person or operator | I have seen the perimeter and accept reliance within `reliance_scope` | that the system is safe |

Bundle shape:

```
signatures: [
  { issuer, role, asserts, valid_until, reliance_scope, target_lock, policy_id, evidence_digest }
]
```

A bundle with a single signature asserting everything is **invalid**. Round 7, review 2: *"без
`responsible_operator` это не аттестация, а machine-readable verdict — его можно выпускать, но нельзя называть
аттестацией."*

`valid_until` is a calendar date **and** a revocation set: a change to the target commit, to a significant
configuration, to a dependency of the conclusion, to the policy, or evidence that contradicts the conclusion all
void it earlier than the date.

## Decision 2 — the perimeter block gates the level

```
perimeter: {
  known_paths, core_paths, outside_paths,
  outside_weighted_risk,          # weighted by an agreed classification, never by an LLM's guess
  delta_since_previous: { new_paths, closed_paths, net_change },
  perimeter_cap, cap_breached,
  perimeter_growth,
  level_upgrade_allowed          # false whenever perimeter_growth is true and no acceptance is signed
}
```

Rules:

1. Coverage is computed against `known_paths`, never against `core_paths` alone.
2. `level_upgrade_allowed = false` when the perimeter grew, including when it grew because previously unknown paths
   were discovered — discovery is good, but it is not an upgrade, and the two must not be confused in a report.
3. A new discovery may still be *published* as an improvement in inventory, marked `discovery`, with `valid_until`
   shortened and an explicit acceptance signed.
4. Unclassifiable paths stay `unclassified`; they do not receive a weight of zero.

## What this decision does NOT do

- It does not produce the weights in `outside_weighted_risk`. That requires an agreed classification (external
  reachability, authority, data touched, impact) and is a separate artifact.
- It does not make any signature legally meaningful in any jurisdiction. It makes each signature's claim narrow
  enough to be true.
