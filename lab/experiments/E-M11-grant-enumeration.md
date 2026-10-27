---
id: E-M11
hypothesis: H-M11
status: completed
base_commit: "uncommitted tree at run time; the enumerator digest is inside the SourceRecord"
started: "2026-10-27T21:14:00+03:00"
finished: "2026-10-27T21:24:00+03:00"
environment: "Windows, PostgreSQL 17.2 (conda-forge, x86_64-windows), local cluster on 127.0.0.1:54329, CPython 3.13.11, psql 17.2"
command: "python lab/e-m11-run.py --psql <conda>/Library/bin/psql.exe --port 54329"
threshold: "Pre-registered: catalogue classes (P1-P6) 6/6 detected, any miss is a defect in the query rather than a limit of the method. Text-search classes (P7, P8) at least 1 of 2. Control point identified. All three declared misses named in blind_spots. Anything else fails."
result: "Recall 8/8 planted bypasses. Control point function:bank.transfer identified. Blind spots name all three expected misses. Findings from the run: 13 rows in run 1, of which 8 true writers, 3 further legitimate writers (trigger functions) and 1 false positive (a function whose body contains the table name inside a string literal); the merger collapsed the INSERT and UPDATE grants into one path because detail was not part of path identity. After fixing identity and tightening the write-verb pattern: 12 rows, recall 8/8, precision 11/12."
verdict: supports
---

# E-M11 — can a catalogue enumerator see the bypasses to a declared control point?

## Pre-registration (written before the run)

**Question.** On a database whose documentation states "all writes to `bank.accounts` go through
`bank.transfer()`", can a read-only catalogue enumerator list the paths that violate that statement?

**Corpus.** `fixtures/pg-bypass/01-fixture.sql`: eight planted bypasses in two classes.

| id | class | plant | expected |
|---|---|---|---|
| P1 | direct privilege | `GRANT UPDATE` to the app role | detect |
| P2 | direct privilege | `GRANT INSERT` to the app role | detect |
| P3 | security definer | `SECURITY DEFINER` function writes the table | detect |
| P4 | plain writer | invoker function writes with no check | detect |
| P5 | disabled control | audit trigger exists and is disabled | detect |
| P6 | view trigger | view with `INSTEAD OF` trigger writes the table | detect |
| P7 | dynamic SQL | function uses `EXECUTE` with the table name | detect, weak |
| P8 | indirect chain | trigger on another table writes the table | detect, weak |

**Thresholds, fixed before the run.** Catalogue classes 6/6 — a miss there is a bug in my query, not a limit of
the method. Text-search classes ≥ 1/2. Control point identified. All three expected misses
(dynamic SQL assembled at runtime, writes from outside the database, application-level checks) named in
`blind_spots`.

## Run

Two runs, because the first one found defects in the instrument.

**Run 1** — 13 rows. Recall 8/8. But: the `INSERT` and `UPDATE` grants shared a `path_id` (the privilege type was
not part of identity), so the merger **silently dropped one path** — exactly the failure ADR-0007 forbids; one
function was reported as a writer because its body contains the table name inside a string literal; the same view
trigger was reported twice under two kinds.

**Fixes:** `detail` became part of `path_id`; the text search requires a write verb within 200 characters of the
table name; trigger-chain detection excludes views.

**Run 2** — 12 rows, recall 8/8, control point identified, three expected misses declared.

## Result

```
catalogue classes      6/6   (threshold 6/6)   PASS
text-search classes    2/2   (threshold 1/2)   PASS
control point          function:bank.transfer  PASS
declared misses        3/3 named in blind_spots PASS

row precision          11/12  — one false positive: a function whose string literal
                               contains the table name ("accounts changed")
```

Log: `lab/logs/e-m11-2026-10-27-run2.log`, sha256
`21a30af4b4aed7cb052e7593b731935da61dd59860237f52aed8e7e840972375`.

## What this measures, and what it does not

**Measures:** that a read-only catalogue enumerator can express these eight classes of bypass at all, that it
identifies the declared control point, and that its blind spots, declared in advance, cover the classes it cannot
see.

**Does not measure:** whether an unknown bypass would be found. The fixture was written with the enumerator in
view, so this is a test of *expressibility*, not of blind discovery. A reviewer of round 7 would call this the
difference between "the vocabulary can say it" and "the method finds it".

**Does not measure false-accept risk.** Precision here is about rows, not about a verdict: nothing in this run
produced an attestation, so there is nothing to falsely accept yet.

## Defects found in the instrument, recorded rather than smoothed

1. Privilege type missing from path identity → one path lost silently in merge (fixed).
2. Text search matching string literals → one false writer (tightened to require a write verb; still a residual
   risk for literals containing a verb).
3. The same object reported under two kinds (`function` and `dynamic_sql`) — kept deliberately: the two rows carry
   different evidence, and the merger accumulates provenance rather than choosing.

## What follows

`fg-enum-grants` is the first source, and it lifts `independent_of_agent` to true for any analysis that includes it
— which is what ADR-0005 requires before a verdict may exceed `CONSISTENT_DECLARED`. Building the verifier is now
unblocked in the sense that matters: there is something for it to check.
