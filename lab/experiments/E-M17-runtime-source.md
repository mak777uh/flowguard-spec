---
id: E-M17
hypothesis: H-M17
status: completed
base_commit: "uncommitted tree"
started: "2026-10-27T23:04:00+03:00"
finished: "2026-10-27T23:12:00+03:00"
environment: "Windows, PostgreSQL 17.2 local cluster, CPython 3.13.11"
command: "python enumerators/runtime-pg/fg_enum_runtime.py ... --workload fixtures/pg-bypass/02-workload.sql"
threshold: "Pre-registered: (a) the runtime source observes all three direct writes in the workload (INSERT, UPDATE, DELETE on the target), (b) it observes none of the two writes performed inside the control point, and that absence is declared as a blind spot rather than reported as a gap in the system, (c) merging three sources keeps independent_of_agent true and does not silently reduce the path count."
result: "3 of 3 direct writes observed as three distinct verbs; 0 of 2 function-mediated writes observed, and the reason is declared: only the outer SELECT is logged, so a legitimate write through a control point is invisible and this source under-counts. Three-source manifest: 18 paths, independent_of_agent true (grants, static, runtime), perimeter weights 82/82 outside."
verdict: supports
---

# E-M17 — a third source, from the log instead of the catalogue

## Why a runtime source at all

The two catalogue sources can share a blind spot: both read metadata, so anything the catalogue does not
represent is invisible to both. A source that reads the **server log** shares no code path with them, which is the
whole point of having three.

## What it does

Runs a workload with `log_statement = 'all'`, reads only what was appended to the server log during that window,
and extracts every `INSERT`/`UPDATE`/`DELETE` against the target table. Each observed verb becomes a path of kind
`observed_write` with the occurrence count.

## Pre-registered expectations, and what happened

| expectation | result |
|---|---|
| all three direct writes observed | **3 / 3** — `INSERT INTO`, `UPDATE`, `DELETE FROM`, each a distinct verb |
| the two writes inside the control point **not** observed | **0 / 2** — confirmed, and the reason is declared |
| merging three sources keeps `independent_of_agent` true | **yes** — grants, static, runtime |
| the path count is not silently reduced | **18 paths** after the merge (15 before, +3 observed verbs) |

## The finding that matters

A write performed **inside** `bank.transfer()` is invisible to the log, because the top-level statement is
`SELECT bank.transfer(1, 2, 10)` and PL/pgSQL internals are not logged as separate statements. So a runtime source
**under-counts**: it sees the bypasses and misses the legitimate path.

That is not a defect to fix by turning on more logging; it is a defect of the *kind of evidence*, and it is now the
first entry in this source's declared blind spots:

> writes performed inside a function reached by SELECT — only the outer SELECT is logged, so a legitimate write
> through a control point is invisible; this source under-counts.

Consequence for the product, stated plainly: **a runtime source may never be the coverage denominator on its own.**
It is a witness — it proves that a write happened — not an inventory. The denominator comes from the catalogue
sources; the log is what makes a path's *occurrence* a fact rather than a possibility.

## Merged state after three sources

```
paths_total          18
sources              grants-pg (catalogue), pgcalls (static), runtime-pg (log)
independent_of_agent true
outside_weighted_risk 1.0 (82/82) - correct for a fixture of thirteen bypasses and two callers
```

## What this does not do

- It does not see paths that were not exercised. Absence of evidence is now, as always, not evidence of absence.
- It does not attribute: the log shows a statement, not the caller's route through a control point.
- It does not replace the catalogue sources; it constrains them. A path the catalogue lists but the log never shows
  is a path that exists and was not exercised — which is a different fact, and both are worth publishing.
