---
id: E-M26
hypothesis: H-M26
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:48:00+03:00"
finished: "2026-10-28T00:58:00+03:00"
environment: "PostgreSQL 17.2, three states of the same database, CPython 3.13.11"
command: "python lab/e-m26-run.py --psql <psql> --port 54329"
threshold: "Pre-registered: (a) adding a writer classifies the change as additive and blocks an upgrade, (b) removing it classifies as subtractive and does not count as growth, (c) a path disappearing is not counted as a replacement unless a new path of the same shape actually takes its place, (d) no earlier harness regresses."
result: "additive=1 growth=true upgrade blocked; after removal subtractive=1 growth=false. One defect in the first implementation: every vanished path was marked replaced, so subtractive came out zero and cleanup looked identical to stagnation - the very failure this card exists to fix. Fixed by tracking the pairs actually made. E-M11, E-M12, E-M13, E-M25 unchanged."
verdict: supports
---

# E-M26 — cleanup must not be punished

## The defect in the old rule

`ADR-0006` blocked upgrades while the perimeter grew, and growth was "a path appeared". Deleting a dead path is also
a change, so a team that cleaned up was scored the same as a team that added surface. All three round-8 reviews said
this rewards stagnation; they were describing our own rule.

## What is measured now — three real states

```
base    : catalogue as usual
+ add   : CREATE FUNCTION bank.settle_batch(...)      -> additive 1, growth true,  upgrade blocked
- remove: DROP FUNCTION bank.settle_batch(...)        -> subtractive 1, growth false
```

## The bug inside the fix

The first implementation computed "replaced" as *every* vanished path, so after a removal the subtractive list came
out empty: cleanup was indistinguishable from nothing happening. That is the same class of error this card was
written to remove, appearing one level down. Fixed by pairing explicitly and recording only the pairs actually made.

## Second defect fixed in passing

The grant enumerator set each function's `control_point` to the function itself, so every writer claimed to be its
own control point (`ADR-0013` recorded it as known). Now empty: a writer is a writer, and the control point is
reported as its own row. `E-M11`, `E-M12`, `E-M13` and `E-M25` are unchanged by the correction.

## What this does not do

- **Shape is coarse.** Kind plus control-point status does not capture a substitution from `other` to `money`.
  `ADR-0014` says so; a risk-class-aware pairing is a separate card.
- **Substitution is not verified.** The rule allows an upgrade after re-attestation; whether the new path is
  equivalent is a human judgement, and nothing here checks it.
- **Different targets are still comparable.** A delta between two `target_lock` values is not refused, which is a
  gap, not a decision.
