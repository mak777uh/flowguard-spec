---
id: E-M36
hypothesis: H-M36
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T03:45:00+03:00"
finished: "2026-10-28T04:05:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m36-run.py"
threshold: "Pre-registered: eight attempts to obtain a strong verdict without the evidence for it must all fail — coverage from 1-2 paths, self-declared in-core status, an attribution with no source, a missing not_claimed, PROVEN at tier 0, a witness-only inventory, and excluding everything."
result: "First run: 4 of 8 blocked. The four that passed produced verdict PROVEN: an artifact with an empty not_claimed, a PROVEN claim at tier 0, a witness-only inventory (all reported as errors, then ignored by the verdict), and an attribution carrying no source. Two structural defences were added - in-core status must be contributed by a named source, and any reported error caps the verdict at CONSISTENT_DECLARED - plus a floor on the denominator size. Now 8 of 8 blocked; E-M12, E-M13, E-M25, E-M26, E-M35 unchanged."
verdict: supports
---

# E-M36 — attacking my own gate: four of eight passed

## What this is

Not a feature. An attempt to obtain PROVEN without the evidence for it, using only what the format allows. The value
is in what succeeded, not in what failed.

## The four that worked

| attack | what it exploited |
|---|---|
| **A1/A2** one or two paths, coverage 1.0 | a ratio over a one-path inventory is 1.0 by arithmetic |
| **A3/A4** every path declares itself in-core | control_point was accepted as a *self-declaration* |
| **A5** empty 
ot_claimed | the error was reported — and the verdict was still PROVEN |
| **A6** PROVEN at tier 0 | same: reported, then ignored by the verdict |
| **A7** witness-only inventory | same |

The last three are one defect, and the worst one in this repository so far: **the verdict did not account for its own
errors.** An artifact could carry three blocking findings and still be labelled PROVEN, because the level was
computed from coverage alone. Every rule added over the last ten rounds was being reported into a list nobody read at
the moment that mattered.

## What was changed

1. **In-core status must be contributed, not declared.** A path is inside the core only when an attribution names the
   control point *and* names the source that contributed it. A path that points at the control point without that is
   reported as UNSUPPORTED_CONTROL_POINT_CLAIM and stays outside.
2. **Any reported error caps the verdict at CONSISTENT_DECLARED.** The strong labels are now a function of the
   evidence *and* of the findings.
3. **A floor on the denominator.** SCOPED_ASSURANCE needs at least 3 paths, PROVEN at least 8; below that the
   ratio is noise (COVERAGE_BASIS_TOO_SMALL).

## Run

`
A1 one path, coverage 1.0              CONSISTENT_DECLARED
A2 two paths, coverage 1.0             CONSISTENT_DECLARED
A3 every path declares itself in-core  CONSISTENT_DECLARED
A4 attribution with no source          CONSISTENT_DECLARED
A5 empty not_claimed                   CONSISTENT_DECLARED
A6 PROVEN at tier 0                    CONSISTENT_DECLARED
A7 witness-only inventory              CONSISTENT_DECLARED
A8 excluded everything                 INVALID
attacks blocked: 8/8
`

Regression: E-M12 25/25, E-M13, E-M25, E-M26, E-M35 unchanged.

## What this does not do

- **It does not prove the absence of other attacks.** Eight that I thought of. The honest statement is that the gate
  survived eight attempts, not that it is sound.
- **It cannot stop an inventory that is legitimately small.** A schema with two write paths is a real thing; the
  floor refuses it a strong level, which is a trade: a small honest claim cannot be strong either.
- **The floor is a policy number, not a measurement.** Three and eight are my choice, recorded in the policy, and a
  reader can disagree with them — policy_id travels with every verdict.

## Log

`lab/logs/e-m36-2026-10-28.log` — sha256 `342c72f86615288308a5c782c31261b9a56834dabbdc4cd710211638dd81a1ac`.
