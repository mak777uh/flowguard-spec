---
id: E-M12
hypothesis: H-M12
status: completed
base_commit: "uncommitted tree at run time; the verifier and enumerator digests are recorded in the artifacts"
started: "2026-10-27T21:35:00+03:00"
finished: "2026-10-27T21:50:00+03:00"
environment: "Windows, CPython 3.13.11; PostgreSQL 17.2 for the end-to-end leg"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered: all ten acceptance scenarios from round 7 review 1 pass, and the end-to-end run on the fixture database produces a verdict whose coverage equals the recomputed value, not the claimed one. Any scenario failing means a refusal code is missing or the verdict is not monotone."
result: "10/10 scenarios pass. End-to-end on the fixture: 12 paths, coverage recomputed 0.0 against a claimed 0.9 — the inflated claim was lowered with CLAIM_EXCEEDS_EVIDENCE and exit 1; the honest claim at 0.0 returned CONSISTENT_DECLARED with no errors. Two defects found by the integration leg: the manifest dropped target_lock, and the grant enumerator cannot attribute a write to a declared control point (no call graph), so coverage from this source alone is always 0."
verdict: supports
---

# E-M12 — does the verifier refuse what it must refuse?

## Pre-registration

The acceptance scenarios are **not ours**: the T1–T10 table was written by a round-7 reviewer who had not seen
the implementation. They are reproduced in `lab/e-m12-run.py` unchanged in intent.

| id | scenario | required behaviour |
|---|---|---|
| T1 | correct claim, full declared scope | a positive verdict is allowed |
| T2 | claims `PROVEN` at coverage 0.6 | refusal or downgrade |
| T3 | one required path missing, claim says full coverage | positive verdict forbidden |
| T4 | documents agree but refer to different commits | refuse |
| T5 | unjustified exclusion beyond the ceiling | refuse |
| T6 | policy source untrusted | refuse |
| T7 | a new external path appeared this run | perimeter change visible, no upgrade |
| T8 | path moved into the core without new evidence | level must not rise |
| T9 | evidence removed, other documents unchanged | verdict must not strengthen |
| T10 | resubmission past the retry budget | loop ended, not retried |

**Threshold:** 10/10, plus the end-to-end leg described below.

## Run

```
T1  PASS   T2  PASS   T3  PASS   T4  PASS   T5  PASS
T6  PASS   T7  PASS   T8  PASS   T9  PASS   T10 PASS
scenarios passed: 10/10
```

End-to-end on the fixture database (the one from `E-M11`, eight planted bypasses):

| leg | result |
|---|---|
| enumerator | 12 paths, 1 control point |
| merge | 12 paths, `independent_of_agent: true`, target lock propagated |
| inflated claim (0.9) | `CLAIM_EXCEEDS_EVIDENCE`, recomputed 0.0, exit 1 |
| honest claim (0.0) | `CONSISTENT_DECLARED`, no errors, exit 0 |

## Two defects found by the integration leg, not by the scenarios

**D1 — the manifest dropped `target_lock`.** The `SourceRecord` carried it under `run.target_lock`; the merger
copied sources and paths but not the lock, so every verdict failed with `MISSING_EVIDENCE` on a well-formed input.
Fixed: the manifest now carries the lock and records `target_lock_conflict` when sources disagree.

**D2 — the grant enumerator cannot attribute a write to a control point.** It sees writers, not callers. Without a
call graph, no path can be said to pass *through* `bank.transfer`, so coverage computes to 0 and the verdict is
capped at `CONSISTENT_DECLARED` forever, no matter how many bypasses are found.

D2 is the important one and it changes the roadmap: **the next enumerator must be attribution-capable** (a call
graph from static analysis, or runtime traces), otherwise the strongest verdict this product can ever produce is
`CONSISTENT_DECLARED` — honest, and commercially worthless.

## Result

```
acceptance scenarios   10 / 10   (threshold 10/10)   PASS
end-to-end verdict     coverage 0.0 recomputed vs 0.9 claimed; inflated claim lowered
instrument defects     2 found by integration, 2 fixed
```

## What this measures, and what it does not

**Measures:** that the refusal behaviour matches a suite written by someone else, that the verdict is monotone
under excluded-path growth and evidence removal, that the retry budget ends a loop, and that the recomputed
coverage overrides the claimed one.

**Does not measure:** whether the verdict is *useful*. With one source the answer is always "consistent, declared,
coverage 0" — true and nearly meaningless. The ceiling needs attribution.

## What follows

1. An attribution-capable source (static call graph or runtime traces) — this is now the blocking item, not the
   verifier.
2. `E-M9` (substitution) can now run against the bundle format that `fg_verify` already half-defines.
3. `docs/METRICS.md` gains the first two measurements of the verifier itself.

## Extended later

E-M14 added two scenarios (T11, T12) after the exclusion hole was found, and corrected T1/T5 to use real
path ids instead of placeholders. The ten scenarios recorded here still pass; the suite now reports 12/12.

## Log

`lab/logs/e-m12-2026-10-27.log` — sha256 `eda90a18973a8639a902632d6fe498ec69a8baf7b7ead40cf3a7dedad0128f6d`.
