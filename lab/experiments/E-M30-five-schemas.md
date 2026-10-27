---
id: E-M30
hypothesis: H-M30
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T01:42:00+03:00"
finished: "2026-10-28T02:05:00+03:00"
environment: "PostgreSQL 17.2, five public sample schemas, CPython 3.13.11"
command: "python lab/e-m30-run.py --psql <psql> --port 54329 --schemas <dir> --pagila <file>"
threshold: "Pre-registered BEFORE the run: five public schemas (pagila, chinook, northwind, sakila, adventureworks), target table per schema chosen by an ordered name rule, not by looking at results; one run each, no tuning between runs; zero findings is a valid result and must be reported as such; a schema that cannot be loaded is reported with its reason rather than dropped."
result: "4 of 5 loaded and measured in under 3 seconds each. pagila: 20 tables, 10 functions, payment, 2 paths (SECURITY DEFINER + dynamic SQL, the same rewards_report). sakila: identical shape and identical finding - both are the same DVD-rental model. chinook: 11 tables, 0 functions, invoice, ZERO paths. northwind: 14 tables, 0 functions, order_details, ZERO paths. adventureworks: could not load - it requires the uuid-ossp extension, which is not installed here (717 errors); reported, not dropped."
verdict: supports
---

# E-M30 — the same tool on five foreign schemas

## Why this card

Every number in this repository so far came from a fixture written by the author. Round-8 review, all three models:
that is a demonstration, not evidence. The smallest honest answer available without a third party is **foreign
input**, and this is it.

## Protocol, fixed before the run

- schemas: `pagila`, `chinook`, `northwind`, `sakila`, `adventureworks` — public sample databases, chosen because
  they are public and varied, not because of an expected result;
- target table: chosen by an ordered name rule (`payment`, `invoice`, `order` …), **not** by looking at findings;
- one run per schema, no tuning between runs;
- **zero findings is a pass.** A tool that only looks useful when something is wrong is a demo.

## Result

| schema | tables | functions | target | paths | seconds | what was found |
|---|---|---|---|---|---|---|
| pagila | 20 | 10 | `payment` | **2** | 1.3 | `SECURITY DEFINER` + SQL assembled at runtime |
| sakila | 21 | 10 | `payment` | **2** | 1.3 | the same function — both are the same DVD-rental model |
| chinook | 11 | 0 | `invoice` | **0** | 2.0 | nothing: no functions, no triggers, no writer functions |
| northwind | 14 | 0 | `order_details` | **0** | 2.7 | nothing, for the same reason |
| adventureworks | 0 | 11 | — | — | — | **could not load**: requires `uuid-ossp`, not installed (717 errors) |

`schemas run: 4/5, total paths reported: 4`.

## What this actually establishes

**The tool runs on foreign input in about two seconds and does not crash on schemas it did not expect.** Three of the
four loaded schemas have no stored procedures at all — so zero findings there is the correct answer, not a miss. The
one schema with a `SECURITY DEFINER` function that assembles SQL at runtime was flagged, in two different dumps of
the same model.

## What it does not establish — and this is the important half

- **Not recall.** Nobody confirmed these findings, and nobody produced an independent list of what should have been
  found. `evidence_tier` stays at **1** (`E-M29`).
- **Not diversity.** Four schemas, two of them the same model, three with zero functions. This is not the
  "twenty to thirty schemas across three stacks" any reviewer asked for; it is the first honest step toward it.
- **Not production.** These are sample databases, and one reviewer said plainly that Pagila is not a production
  schema. They are right.

## Two defects found in the harness itself, both reported rather than hidden

1. **The first target rule picked a partition.** Pagila's `payment` is a partitioned parent; the initial query
   filtered to `relkind = 'r'`, so it selected `payment_p2020_01` — a single partition, not the table the flow uses —
   and reported zero paths. Fixed by admitting `relkind = 'p'`.
2. **Two schemas silently produced nothing.** Chinook creates its own database and `\c` into it, so loading it into
   ours created zero tables while reporting zero errors. AdventureWorks needs an extension we do not have. Both are
   now reported with their reasons, and a schema that cannot be loaded is a row in the table, not a gap.

## Consequence

The evidence base is no longer one fixture and one database. It is still tier 1, and the card says so. The honest next
step is not more sample databases — two of the four are the same model, which is itself a finding about sample
databases — but a schema from a project that has a real control point to bypass, which needs an owner.

## Log

`lab/logs/e-m30-2026-10-28.log` — sha256 `f8041dc77b546aa7cda481efff4184c376b2a79f149ddf220b6c43b06bfc779e`.
