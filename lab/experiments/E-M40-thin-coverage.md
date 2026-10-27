---
id: E-M40
hypothesis: H-M40
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T05:25:00+03:00"
finished: "2026-10-28T05:40:00+03:00"
environment: "PostgreSQL 17.2, three systems of different shapes, CPython 3.13.11"
command: "python enumerators/grants-pg/fg_enum_grants.py ... && python tools/merge_inventory.py ... && python tools/fg_verify.py ..."
threshold: "Pre-registered: (a) the enumerator publishes how much of the schema's write logic lives in the database, (b) a system where that share is below 0.15 cannot carry a level above CONSISTENT_DECLARED, (c) a database-heavy system is not refused for the same reason, (d) earlier harnesses do not regress."
result: "Density published and enforced. GitLab: 36 of 558 functions write (0.065), and for the projects table 3 of 558 (0.005) -> THIN_DB_LOGIC_COVERAGE, verdict capped. Pagila: 0.100. Synthetic 400-function schema: 0.812 -> no refusal. E-M12 25/25 and E-M36 8/8 unchanged."
verdict: supports
---

# E-M40 — the report now says whether the system is the kind it can see

## Where this came from

E-M37 ran on GitLab's public schema: 1436 tables, 558 functions, and **36 functions containing any write
statement**. The report said "10 paths on projects" and nothing about the fact that it had examined a fraction of the
write path. A reader would take it as a statement about the system.

## What is measured

db_logic_density = functions containing a write statement ÷ functions in the schema, published per source.

| system | functions | writing | density |
|---|---|---|---|
| synthetic, 400 functions | 400 | 325 | **0.812** |
| Pagila | 10 | 1 | **0.100** |
| GitLab projects | 558 | 3 | **0.005** |
| GitLab members | 558 | 0 | **0.000** |

## What is enforced

Below 0.15, a claim above CONSISTENT_DECLARED is refused with THIN_DB_LOGIC_COVERAGE, and the verdict is capped:

`
GitLab, density 0.005, SCOPED_ASSURANCE  -> CONSISTENT_DECLARED + THIN_DB_LOGIC_COVERAGE
synthetic, density 0.812                 -> no refusal
`

The refusal is retryable and its message says what to do: state the scope, or lower the level. It is not a
judgement that the system is bad; it is a statement that **this report cannot speak for it**.

## Why the threshold is 0.15 and why that is weak

It is my choice, placed in the policy next to the other floors, and a reader can disagree. It exists because a
denominator of 558 with a numerator of 3 is not a sample of the same population as a denominator of 400 with 325.
Nobody has calibrated it: there is no measurement linking density to how much a report misses. That is the honest
status — a guard against an obvious misreading, not a validated model.

## What this does not do

- **It does not measure the application layer.** A density of 0.005 means the write logic is elsewhere; it does not
  say where, how much, or whether it is safe.
- **It does not stop a consumer from ignoring the code.** The verdict says THIN_DB_LOGIC_COVERAGE; a reader who
  quotes only the verdict string "CONSISTENT_DECLARED" still misleads, and no artifact prevents that.
- **It uses one crude proxy.** A function that writes one row and a function that rewrites the ledger both count as
  one. The number says "how much of the code is here", not "how much of the risk".

## Log

`lab/logs/e-m40-2026-10-28.log` — sha256 `e30dc94502c77f474c5f702555606f666a2167f3e8550516ca379f1f3dfa5fb7`.
