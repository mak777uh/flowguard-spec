---
id: E-M19
hypothesis: H-M19
status: completed
base_commit: "uncommitted tree"
started: "2026-10-27T23:34:00+03:00"
finished: "2026-10-27T23:42:00+03:00"
environment: "Windows, PostgreSQL 17.2 local cluster, CPython 3.13.11"
command: "python lab/e-m19-run.py  (or the manual sequence in the Run section)"
threshold: "Pre-registered: (a) the merger computes the delta itself rather than accepting it from the caller, (b) adding one writer to a live database produces new_paths = 1 and perimeter_growth = true, (c) the verifier then reports level_upgrade_allowed = false, (d) a path that disappears does not cancel a path that appeared."
result: "16 paths after, 15 before; delta +1 new, -0 vanished, net +1; perimeter_growth true; level_upgrade_allowed false. The claim at coverage 0.9 was refused twice over: the recomputed coverage is 0.125, and the weighted risk outside the core exceeds the ceiling."
verdict: supports
---

# E-M19 — the perimeter delta is computed, and it blocks an upgrade

## Two gaps this closes

**1. `delta_since_previous` was a field nobody computed.** ADR-0006 requires an upgrade to be blocked while the
perimeter grows, and `fg_verify` read `perimeter_growth` from the manifest — but the merger only counted vanished
paths and never produced a delta. A field the caller fills in is a claim about a number that does not exist.

**2. `routes` was listed as a denominator kind with no such source.** The coverage basis accepted a kind that had
never been built or measured — the same "declared, not built" pattern this repository has caught five times in its
own instruments. `routes` is removed from the list until an enumerator exists and is measured (`ADR-0011`).

## What was built

`merge_inventory --previous` now publishes:

```json
"delta_since_previous": { "new_paths": 1, "vanished_paths": 0, "net_change": 1, "published": true },
"perimeter_growth": true
```

Growth is `new_paths > 0`, and it is **not** cancelled by vanished paths: a replacement is still a change of shape,
and a reader has to see it.

## Run — two real states of the same database

```
before:  15 paths, 2 sources, no previous           -> delta unpublished
add:     CREATE FUNCTION bank.pay_rewards(...)      -> one more writer of accounts
after:   16 paths                                   -> delta +1 new, -0 vanished, net +1
                                                     -> perimeter_growth = true
verdict: CONSISTENT_DECLARED
         CLAIM_EXCEEDS_EVIDENCE   expected <= 0.125, claimed 0.900
         POLICY_CEILING_EXCEEDED  perimeter
         level_upgrade_allowed = false
```

The last line is the point: a new bypass appeared, and the artifact refuses to improve its level even before anyone
looks at the coverage arithmetic.

## Why the delta lives in the merger

The alternative — let the caller pass `delta` in — was already in the format and is exactly wrong: the party being
measured would report how much it grew. The merger sees both inventories and cannot avoid the comparison.

## What this does not do

- It does not decide whether growth is good. Discovering six paths that always existed is a better inventory, not a
  worse system; `perimeter_growth` is a fact, and the interpretation belongs in the report, not in the verdict.
- It does not compare inventories of different targets. Two manifests with different `target_lock` values are not a
  delta, and the merger does not yet refuse that — recorded as a gap, not a solved problem.
- It does not measure risk; the weighted perimeter is a separate computation (`E-M16`).

## Log

re-run on 2026-10-28 with the output captured, because the original run was a command sequence
whose transcript was the only record: `lab/logs/e-m19-2026-10-28.log` — sha256 `4462d7977460f1d74b1720a1f6754badba41572371ad03858b2d579d6c5fed02`.
