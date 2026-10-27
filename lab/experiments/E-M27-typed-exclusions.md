---
id: E-M27
hypothesis: H-M27
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:58:00+03:00"
finished: "2026-10-28T01:10:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered: (a) a reason code is required and a free-text reason is refused, (b) each code's required evidence is checked, (c) a code may not be applied to a risk class it is forbidden for, (d) an unknown class may not be excluded with DATA_NOT_SENSITIVE, (e) all 23 acceptance scenarios pass and none regresses."
result: "23/23. T13 refuses prose, T22 catches DATA_NOT_SENSITIVE on a money path (EXCLUSION_REASON_CONTRADICTION), T23 catches COMPENSATING_CONTROL_PRESENT with no control_ref (MISSING_EVIDENCE). The earlier exclusion scenarios had to be rewritten: they passed a free-text reason, which is exactly what this card makes invalid."
verdict: supports
---

# E-M27 — a reason is a claim with preconditions

## What was wrong

Round-8 review, all three models, said the same thing about our exclusions: checking that the path exists and that
the reason is at least eight characters long is **syntactic validity**. A reason can be formally complete and
factually false, and the one most likely to be false is `DATA_NOT_SENSITIVE` applied to a path that moves money.

## What is enforced now

A reason is a **code**, from `policies/exclusion-reasons.json`, and a code carries preconditions:

| code | requires | forbidden for |
|---|---|---|
| `NOT_REACHABLE` | `evidence.source_id` | — |
| `COMPENSATING_CONTROL_PRESENT` | `evidence.control_ref` | — |
| `DATA_NOT_SENSITIVE` | — | `money`, `personal_data`, and any unclassified path |
| `TEST_ONLY` | `evidence.source_id` | `money` |
| `OWNER_ACCEPTS` | `accepted_by`, `valid_until` | — |

Refusals: `EXCLUSION_REASON_UNKNOWN` for a code that does not exist,
`EXCLUSION_REASON_CONTRADICTION` for a code applied where it cannot hold, `MISSING_EVIDENCE` for an unmet
precondition. The risk class comes from the same policy the perimeter uses, so an exclusion cannot contradict the
class the product assigns to the same path.

## Run

```
T13  prose instead of a code                PASS (refused)
T22  DATA_NOT_SENSITIVE on a money path     PASS (EXCLUSION_REASON_CONTRADICTION)
T23  COMPENSATING_CONTROL_PRESENT, no ref   PASS (MISSING_EVIDENCE: control_ref)
T1, T5 rewritten to use codes               PASS
scenarios passed: 23/23
```

## A correction this card forced on its own tests

`T1` and `T5` passed free-text reasons and started failing. That was not a regression — those scenarios were
exercising the hole. They now carry `OWNER_ACCEPTS` with a person and an expiry, which is what a real exclusion
looks like.

## What this does not do

- **It cannot check that the reason is true.** `OWNER_ACCEPTS` with a real name and a real date is still only a
  claim; whether that person had the authority and whether the risk was understood is outside any machine. This is
  stated in the verdict rather than implied.
- **`NOT_REACHABLE` is checked for evidence, not for proof.** Requiring `evidence.source_id` means "you must point
  at the source that makes this claim", not "the claim is correct".
- **Risk classes are coarse.** `money` is matched by strings in `entry`; a payments table called `notes` is
  classified `other`, and `DATA_NOT_SENSITIVE` would pass on it. `ADR-0012` and the risk policy both say the
  classification is a convention.

## Log

`lab/logs/e-m27-2026-10-28.log` — sha256 `b323be8b120b99e41edc13716805e2ca8287ee90a577c228e597d9f30db343ba`.
