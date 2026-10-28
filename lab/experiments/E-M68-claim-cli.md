---
id: E-M68
hypothesis: H-M68
status: completed
base_commit: "bbf307d"
started: "2026-10-28T18:05:00+03:00"
finished: "2026-10-28T18:55:00+03:00"
environment: "Windows, rustc 1.99.1 + WinLibs UCRT, CPython 3.13.11"
command: "python lab/e-m68-run.py && python lab/e-m67-run.py && cd core-rs && cargo test --offline"
threshold: "Pre-registered: the Rust arithmetic must answer through a binary, not only through unit tests, and must agree with the Python verifier on ten cases - the six cross-family attacks plus NC-code requirements, the level-string near-miss, duplicate identifiers and a first inventory. A disagreement is a defect in one of them and is fixed before the card."
result: "Ten of ten now agree, after the comparison found four gaps in the port. The CLI `fg-core verify-claim` exists and answers with a verdict, coverage, band and codes. What the comparison exposed: the port had no evidence-tier ceiling (a tier-2 claim was accepted without a confirmation that fg_confirm would accept); it returned a level where Python returns INVALID for shape errors (unknown level string, duplicate path_id); it crashed with no JSON on a malformed document instead of refusing; and it did not enforce the NC codes each level requires, which is read from docs/NOT-CLAIMED.md so the two cores cannot drift. All four closed. cago test 15/15, e-m67 6/6, e-m68 10/10, E-M12 25/25 unchanged."
verdict: supports
---

# E-M68 — the arithmetic answers as a binary, and the comparison found four gaps

## What exists now

```
fg-core verify-claim --claim c.json --inventory i.json [--report r.json]
```

It prints the verdict, the claimed level, the coverage, the distinct-path count, the density band and every
refusal with its code. Exit 0 when the verdict is what the claim asked for or stronger, 1 when it was lowered or
the input was unanswerable, 2 when an argument is missing.

## The four gaps the comparison found

| gap | what it looked like | fix |
|---|---|---|
| no tier ceiling | a tier-2 claim was accepted with no confirmation at all; Python capped it | ported `_valid_confirmation` and the 3→2→1 ladder |
| shape errors returned a level | `"PROVEN "` and duplicate `path_id`s produced `CONSISTENT_DECLARED`; Python says `INVALID` | a shape error now makes the verdict `INVALID` — an unanswerable claim is not a lowered one |
| a malformed document crashed | exit 2 with stderr and no JSON | a refusal with `REPORT_BUNDLE_INCONSISTENT`, because a caller reading only the exit code must tell a refusal from a broken tool |
| no NC requirement | `PROVEN` passed without `NC-03`, `NC-04`, `NC-05`, `NC-10`, `NC-11` | read from `docs/NOT-CLAIMED.md`, the same document Python reads, so the two cores cannot drift |

The last one is the interesting design decision: the requirement lives in a **document**, and both cores parse it.
A table copied into two codebases is a table that will disagree within a month.

## What the tests had to learn

Three of the port's own unit tests failed after the tier port, and all three were the fixture's fault rather than
the rule's: the test claim declared tier 2 without a confirmation, so the ceiling capped it and the test was
measuring the ceiling rather than the rule it named. The lesson is the same one `E-M67` recorded in the other
direction — **a test asserts a rule, and a fixture that violates a different rule tests nothing.**

## What this does not do

- It does not make the Rust core the one that decides in production; both answer, and the differential runs in the
  ritual.
- It does not prove anything. The port is a second implementation, not a verification.
- It does not move the ceiling: the arithmetic is about a document the claimant wrote.
