---
id: E-M25
hypothesis: H-M25
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:30:00+03:00"
finished: "2026-10-28T00:46:00+03:00"
environment: "PostgreSQL 17.2 fixture with an added 4-argument overload, CPython 3.13.11"
command: "python lab/e-m25-run.py --psql <psql> --port 54329"
threshold: "Pre-registered: (a) with two functions named transfer, a route declaring a call to transfer is NOT attributed to the control point, (b) the path carries an attribution_conflict listing both candidates, (c) the verdict raises AMBIGUOUS_ATTRIBUTION and level_upgrade_allowed is false, (d) E-M11, E-M12 and E-M13 do not regress."
result: "All four hold. Route attribution becomes None, conflict names both candidates, verdict carries AMBIGUOUS_ATTRIBUTION with upgrade blocked, and the three earlier harnesses still pass. Two defects were found on the way, both ours: the grant enumerator excluded the control point by name (so the overload vanished and the direct writer was invisible), and level_upgrade_allowed ignored blocking errors entirely."
verdict: supports
---

# E-M25 — an overload makes the join a guess

## The shape built

The fixture gains a second `bank.transfer`, four arguments instead of three, `SECURITY DEFINER`, writing
`accounts` directly. Nothing else changes: one route `/transfer` declares `calls: ["transfer"]`.

Under a name-based join the route is placed inside the core, and the overload that bypasses the control point is
never mentioned. That is the failure mode all three round-8 reviews named.

## Run

```
before the fix:  attribution {'to': 'function:bank.transfer', 'method': 'transitive'}  conflict None
after:           attribution None
                 conflict {'called': 'transfer',
                           'candidates': ['function:bank.transfer', 'function:bank.transfer'],
                           'resolution': 'ambiguous'}
verdict:         CONSISTENT_DECLARED
                 codes: AMBIGUOUS_ATTRIBUTION, CLAIM_EXCEEDS_EVIDENCE, POLICY_CEILING_EXCEEDED
level_upgrade_allowed: False
```

## Two defects on our side, found by building the case

**1. The grant enumerator excluded the control point by name.** `p.proname NOT IN ('transfer')` removed **both**
functions when an overload appeared, so the direct writer never entered the inventory at all. Fixed: exclusion by
identity, and when the name is ambiguous every candidate is kept so the ambiguity can be reported.

**2. `level_upgrade_allowed` was computed from perimeter growth alone.** A claim could raise its level while an
ambiguous attribution sat in the same document. Fixed: any non-retryable error blocks an upgrade.

Both are the same sentence as before, now for the third time: **a name is not an identity**, and a flag that
answers a question nobody asks is not a check.

## What this does not do

- **It cannot resolve the overload itself.** The route manifest carries a bare name; without a signature there is
  nothing to resolve against, so the honest answer is "ambiguous" and a human or a better manifest supplies more.
- **It does not catch attribution without a declared call.** A source that attributes silently is unfalsifiable
  here; that limitation is declared in every source's blind spots.
- **It does not fix the self-referential `control_point`.** The grant enumerator sets each function's
  `control_point` to the function itself, so every writer claims to be its own control point. Carded, not fixed, and
  named in `ADR-0013` so it cannot be forgotten.
