---
id: E-M16
hypothesis: H-M16
status: completed
base_commit: "uncommitted tree"
started: "2026-10-27T22:44:00+03:00"
finished: "2026-10-27T22:56:00+03:00"
environment: "Windows, CPython 3.13.11; PostgreSQL 17.2 for the fixture leg"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered: (a) a path matching no rule is weighted as unclassified and never as zero, (b) the risk policy digest appears in the verdict, (c) weighted outside risk above the ceiling refuses an upgrade above CONSISTENT_DECLARED but does not refuse the floor level, (d) the 14 earlier scenarios do not regress."
result: "17/17. T15 (risk above the ceiling) refused with POLICY_CEILING_EXCEEDED on subject perimeter; T16 (unclassified) counted 4 paths with weight 3 and risk > 0; T17 (digest) present. On the fixture manifest: 15 paths, 11 money, 4 unclassified, outside_weighted_risk 1.0. Two defects found while integrating: the ceiling was taken from the weights file only, ignoring a stricter claim policy; and the ceiling refused even CONSISTENT_DECLARED, which promises nothing about the outside."
verdict: supports
---

# E-M16 — the perimeter gets weights, and counts stop pretending to be risk

## Why

Round-7 review 4: fourteen paths outside the core may be one payment endpoint and thirteen read-only caches, or
the reverse. A count cannot tell those apart, so `outside_paths: 14` is not a risk statement of any kind.

## What was built

`policies/risk-classes.json` — ordered rules mapping a path to `money` (5), `personal_data` (4), `files` (2),
`other` (1), `unclassified` (3). The weights are a recorded convention; the verifier publishes the policy digest so
a verdict is tied to the exact numbers it used. An unclassified path is weighted **3, never 0**: an unclassified
money path is not a harmless one.

`tools/fg_perimeter.py` computes `outside_weighted_risk = weights_outside / weights_total`.

`fg_verify` refuses an upgrade above `CONSISTENT_DECLARED` when that ratio exceeds the ceiling — the stricter of the
claim policy and the weights file wins, so a lenient claim cannot loosen the classification's own limit.

## Run

```
T15  risk above the ceiling      PASS  (POLICY_CEILING_EXCEEDED, subject perimeter)
T16  unclassified not zero       PASS  (4 paths, weight 3, risk > 0)
T17  policy digest recorded      PASS
T1-T14 unchanged                 PASS
scenarios passed: 17/17
```

On the real fixture manifest: 15 paths, 11 money, 4 unclassified, weights 67/67 outside → risk 1.0. Which is the
correct answer for a fixture that is thirteen bypasses and two callers.

## Two defects found while integrating

1. **The ceiling came from the weights file only**, so a claim policy asking for a stricter limit was ignored.
   Fixed: the stricter of the two applies.
2. **The ceiling refused even `CONSISTENT_DECLARED`.** The floor level promises nothing about what lies outside, so
   refusing it for having a large outside was incoherent — it made the honest answer unavailable. Fixed: the
   ceiling gates upgrades, not the floor.

## What this does not do

- The weights are not objective. They are a convention, versioned and digested; a different convention gives a
  different number, and `NC-07` says so in every claim.
- The classification sees `entry` strings, not semantics. A table called `notes` holding card data is classified
  `other`.
- It does not measure residual risk; it measures the share of **known** weighted risk that sits outside the core.
