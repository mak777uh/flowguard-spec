---
id: E-M48
hypothesis: H-M48
status: completed
base_commit: "bf1aed8"
started: "2026-10-28T10:40:00+03:00"
finished: "2026-10-28T11:05:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m48-run.py && python tools/fg_schema_check.py --claim fixtures/attack/k-proven.json"
threshold: "Pre-registered: the three items E-M47 left open must each be closed measurably - the report must be able to block a verdict, malformed policy input must not produce a traceback, and the published schemas must accept the artifacts the tool actually writes."
result: "All three closed. (1) A report is now an input, not decoration: if its own coverage differs from the inventory's arithmetic by more than 0.05, or it marks every analysed path outside the core while the inventory puts paths inside, the verdict is capped with REPORT_BUNDLE_INCONSISTENT. Round-one break 7 survived two adversarial rounds and is now refused. (2) The three policy tracebacks are refusals (exit 2, INVALID, no stack trace); validate_shapes now covers target_lock, sources and every path rather than the first 2000. (3) schemas/inventory-0.1.json was not valid JSON at all - two stray apostrophes - and is now; claim-0.1.json gained evidence_tier; the merge's own fields were added to the schema; and fg_schema_check is in the ritual and CI, where it immediately caught three real mismatches."
verdict: supports
---

# E-M48 — the three things the second attacker left open

## 1. A report that contradicts the inventory now blocks

The round-one break that survived two rounds: a report asserting "none of the analysed paths passes through the
control point; coverage is 0.0" changed nothing. The report was read for `control_point` only.

Now the report's own arithmetic is compared with the inventory's: a difference above 0.05, or every analysed path
marked outside the core while the inventory puts paths inside, produces `REPORT_BUNDLE_INCONSISTENT` and caps the
verdict. The attacker's exact case now returns `CONSISTENT_DECLARED` with that code.

## 2. Malformed policy is a refusal, not a stack trace

Three of the seven tracebacks were in the policy: a list, a text floor, a text density. All three now return
**exit 2 / INVALID / no traceback**, because a floor that is not a number is not a floor. `validate_shapes` also
covers `target_lock`, `sources` and every path — the old window of 2000 meant path 2001 was never checked and reached
the arithmetic.

## 3. The published schema was not valid JSON

`schemas/inventory-0.1.json` had two stray apostrophes and did not parse. `claim-0.1.json` forbade `evidence_tier`,
so **every strong claim violated its own schema**, including the repository's PROVEN fixture. Both are fixed, the
merge's own fields are now in the schema, and `fg_schema_check` runs in the ritual and CI — where it immediately
found three more mismatches (`target_lock` type, `vanished_since_previous`, `non_agent_sources`) that had been
invisible because nothing ran it.

## The pattern, third time

Each of the three was an artifact that existed, was documented, and was **never executed**. The schema was published
and never validated; the report was accepted and never read; the policy was merged and never shape-checked. A check
that does not run is a comment.
