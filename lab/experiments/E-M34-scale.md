---
id: E-M34
hypothesis: H-M34
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T03:05:00+03:00"
finished: "2026-10-28T03:20:00+03:00"
environment: "PostgreSQL 17.2, generated schema, CPython 3.13.11"
command: "python lab/e-m34-run.py --psql <psql> --port 54329"
threshold: "Pre-registered shape: 50 tables, 400 functions, 30 triggers, 10 roles. Thresholds: run under 60 seconds, every planted writer reported, and the output readable - at most 120 paths, or a triage summary that makes a longer list usable."
result: "0.4 seconds, 480 paths, 320 of 320 planted writers found, and the list is NOT readable at 480 entries - the reviewer was right. A summary block was added (totals, by kind, by control-point status, and a reading note above 120 paths) and the criterion now passes. Two defects on my side: the first threshold asked for all 400 functions when 80 of them deliberately do not write the table, and the first run had no summary at all."
verdict: supports
---

# E-M34 — four hundred functions, and the list nobody would read

## What was measured

A generated schema: 50 tables, 400 functions writing the target table in five different shapes (direct
UPDATE/INSERT/DELETE, dynamic EXECUTE, and a helper call that writes nothing), 30 trigger chains, 10 roles
with grants — 0 load errors.

`
runtime          0.4 s
paths reported   480   (350 function, 80 dynamic_sql, 30 trigger_chain, 20 privilege)
distinct entries 390
`

**Speed is not the problem.** Four tenths of a second for four hundred functions.

**Readability is.** 480 paths is a list no human opens twice. The reviewer who predicted this was right, and the
first run of this harness failed on exactly that criterion.

## What was changed

The enumerator now publishes a summary before the list:

`json
"summary": {
  "paths_total": 480, "distinct_entries": 390,
  "by_kind": {"function": 350, "dynamic_sql": 80, "trigger_chain": 30, "privilege": 20},
  "by_control_point_status": {"inside": 0, "outside": 480},
  "reading_note": "more than 120 paths: read the summary first"
}
`

The full list stays for the machine, which is the actual consumer. The summary is for the human who has to decide
where to look — and the decision it enables is real: 80 dynamic-SQL paths and 30 trigger chains are a different kind
of problem from 350 ordinary writers.

## Two defects on my side

1. **The threshold asked for all 400 functions.** Eighty of them call a helper and never write the table, so the
   correct expectation was 320 writers. The first "failure" was my arithmetic, not the tool's recall. Fixed: the
   harness computes how many of its own plants are writers.
2. **The first run had no summary at all.** The structure existed only in the paths list, so the only way to triage
   was to parse it.

## What this does not do

- **It does not cap the list.** 480 paths is still 480 paths for the machine, and a schema ten times larger would
  produce thousands. A --max-paths with an explicit omitted count is the obvious next step and is not built.
- **It does not rank.** The summary counts by kind; it does not say which 20 of the 480 to read first. The perimeter
  block does that later, by risk class, but only after a merge — not inside the enumerator.
- **It does not make the human's job small.** The reviewer's real point stands: on a large schema the output is a
  starting point for triage, not a report.

## Log

`lab/logs/e-m34-2026-10-28.log` — sha256 `1cc08484d4b13ef3ade45df5a6833b15ecb6aaa05bdff4db12378577089f82a7`.
