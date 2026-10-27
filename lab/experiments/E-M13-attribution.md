---
id: E-M13
hypothesis: H-M13
status: completed
base_commit: "uncommitted tree at run time; both enumerator digests are inside their SourceRecords"
started: "2026-10-27T21:40:00+03:00"
finished: "2026-10-27T21:55:00+03:00"
environment: "Windows, PostgreSQL 17.2 local cluster, CPython 3.13.11"
command: "python enumerators/pgcalls/fg_enum_pgcalls.py ... && python tools/merge_inventory.py s-grants.json s-calls.json && python tools/fg_verify.py ..."
threshold: "Pre-registered: both planted legitimate callers attributed (2/2), zero false attribution among the eight bypasses and the decoy (0/9), transitive attribution found, coverage no longer zero, and an inflated claim lowered with CLAIM_EXCEEDS_EVIDENCE."
result: "2/2 attributed (one direct, one transitive), 0/9 false attributions - the decoy transfer_fast, which writes the table directly, was not attributed. Coverage moved from 0.000 to 0.133 (2 of 15 paths inside the core). Inflated claim at 0.85 refused with CLAIM_EXCEEDS_EVIDENCE and exit 1; honest claim at 0.133 accepted with exit 0."
verdict: supports
---

# E-M13 — can a call graph attribute a path to the control point?

## Why this card exists

`E-M12` found the blocking defect: the grant enumerator sees writers, not callers, so no path could be attributed
to `bank.transfer` and coverage computed to 0 forever. This card tests the fix — a PL/pgSQL call-graph source that
contributes **attribution** rather than paths, and a merge rule that promotes an attributed caller to a path.

## Pre-registration

Corpus: the E-M11 fixture, extended with three functions:

| plant | intent | required outcome |
|---|---|---|
| `transfer_via_api` | calls `bank.transfer` directly | attributed, `direct` |
| `transfer_batch` | calls `transfer_via_api` in a loop | attributed, `transitive` |
| `transfer_fast` | **decoy**: named like a transfer, writes the table directly | **not** attributed |

**Thresholds, fixed before the run.** Attribution 2/2 on the legitimate callers. False attribution 0/9 across the
eight bypasses and the decoy. Transitive attribution must be found. Coverage must exceed 0. An inflated claim must
be lowered.

## Run

```
call-graph source   2 functions reach bank.transfer
merge               15 paths, 2 attributed, independent_of_agent: true (grants-pg, pgcalls)
coverage            0.133  (2 of 15)
claim 0.85          CLAIM_EXCEEDS_EVIDENCE, expected <= 0.133, exit 1
claim 0.133         CONSISTENT_DECLARED, no errors, exit 0
acceptance suite    10/10 still passing
```

## Result

| measurement | value | threshold |
|---|---|---|
| attribution on legitimate callers | **2 / 2** | 2/2 |
| false attribution (plants + decoy) | **0 / 9** | 0 |
| transitive attribution found | yes (`transfer_batch`) | required |
| coverage | **0.133** (was 0.000) | > 0 |
| inflated claim lowered | yes, exit 1 | required |

## What the decoy proves

`transfer_fast` is named as if it were the flow, and writes the table directly. It was **not** attributed. That
matters more than the 2/2: a name-based heuristic would have passed it, and a name-based heuristic is what a quick
implementation would have used.

## What this does not measure

- **Depth beyond 8** is not tested; the source declares that limit.
- **Dynamic call resolution** (`EXECUTE`, calls through variables) is invisible and declared as a blind spot.
- **Coverage is still low by construction**: the fixture is eight bypasses and two callers, so 0.133 is the correct
  answer, not a failure. The threshold is about the mechanism, not the number.

## Consequences

`independent_of_agent` now rests on two source kinds, so a single tool's blind spot is no longer the product's
blind spot. The verdict is still capped at `CONSISTENT_DECLARED` because coverage is 0.133 — which is honest, and
would be the right answer for any real system with thirteen unaddressed ways to write the table.

## Log

`lab/logs/e-m13-2026-10-27.log` — sha256 `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe`.
