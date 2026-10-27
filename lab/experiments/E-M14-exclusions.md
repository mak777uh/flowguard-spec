---
id: E-M14
hypothesis: H-M14
status: completed
base_commit: "uncommitted tree; the verifier digest is in the run log"
started: "2026-10-27T22:26:00+03:00"
finished: "2026-10-27T22:34:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered before the change: an exclusion must name a path that exists in the inventory, must not name a path inside the covered core, and must carry a reason. All 12 acceptance scenarios pass, including two new ones, and no earlier scenario regresses."
result: "The hole existed and was real: `excluded` was a free-text list, counted for the ceiling but never bound to anything. Two claims passed that should have failed - excluding an invented identifier, and excluding a path that is inside the covered core. After binding, 12/12 scenarios pass, including T11 (invented exclusion) and T12 (core path excluded). The ten original scenarios still pass, with two of them corrected to use real path ids instead of placeholders."
verdict: supports
---

# E-M14 — exclusions were free text, so narrowing was free

## What was wrong

`fg_verify` treated `excluded` as a list of strings. It counted them against the policy ceiling and otherwise ignored
them. Consequences, both measured here as scenarios:

- `excluded: ["wp_invented"]` — an identifier that exists nowhere — passed. An exclusion of something that does not
  exist is not a narrowing; it is noise that looks like diligence.
- `excluded: ["wp_core0"]` — a path that is *inside* the covered core — passed. A claim could cover a path and
  exclude it in the same breath.

This is the T3 vacuum the round-7 reviews named: the paying party narrows the scope, and the artifact reports a
clean result over the part that remains. We had closed the arithmetic side (coverage is recomputed) but left the
scope side open.

## The rule now enforced

An exclusion must satisfy three conditions, each with its own refusal:

| condition | refusal |
|---|---|
| names a `path_id` present in the inventory | `UNKNOWN_OR_UNBOUND_PATH` |
| does not name a path inside the covered core | `REPORT_BUNDLE_INCONSISTENT` |
| carries a reason | `MISSING_EVIDENCE` |

## Run

```
T1  PASS  T2  PASS  T3  PASS  T4  PASS  T5  PASS  T6  PASS
T7  PASS  T8  PASS  T9  PASS  T10 PASS
T11 PASS  exclusion names a path that does not exist
T12 PASS  exclusion names a path inside the covered core

scenarios passed: 12/12
```

## A note on the harness

The original T1 and T5 used placeholder reasons (`"x0"`, `"x1"`). When binding was added they failed — correctly,
because they were exercising exactly the hole. They now exclude real inventory paths with reasons, which is what a
real claim does. Their intent (a valid claim; an over-ceiling claim) is unchanged.

That correction is worth recording rather than hiding: a test that passed only because the implementation ignored a
field was not testing the field.

## What this does not fix

- **A reason can be a lie.** The verifier checks that a reason exists, not that it is true. `"not money"` on a
  money path passes. Detecting that needs the risk classification the perimeter block still lacks.
- **Excluding nothing is still allowed.** A claim that silently narrows by *never mentioning* a path is caught only
  if the inventory disagrees; that is the attribution question, not this one.

## Consequences

`docs/37-REFUSAL-CODES.md` already lists the codes used; no new code was needed. The three conditions are now part
of the verifier's contract, and the acceptance suite documents them as T11 and T12.

## Log

`lab/logs/e-m14-2026-10-27.log` — sha256 `06b7bbceb1c767bd2847c8c9a7010d1560c64e5d7c973eb5d854e773b94dce06`.
