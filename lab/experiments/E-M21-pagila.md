---
id: E-M21
hypothesis: H-M21
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:00:00+03:00"
finished: "2026-10-28T00:12:00+03:00"
environment: "PostgreSQL 17.2, Pagila v2.1.0 (devrimgunduz/pagila), CPython 3.13.11"
command: "python enumerators/grants-pg/fg_enum_grants.py --psql <psql> --port 54329 --user postgres --db fgpagila --schema public --table payment --out pagila.json"
threshold: "Pre-registered BEFORE the run, on a schema nobody here wrote and where nothing is planted: (a) exit 0 under 60 seconds, (b) at most 40 paths for one table, (c) every path legible without the tool's source, (d) the honest expected outcome is ZERO bypasses, and reporting zero is a pass."
result: "Exit 0 in 0.4 seconds. Two paths for public.payment, both attributed to public.rewards_report: one SECURITY DEFINER function, one dynamic SQL path assembled at runtime. Every entry legible; the list is two items, not forty. Reading the function body confirms the finding: it builds a string containing 'FROM payment AS p' and executes it with EXECUTE. Neither path is a false positive on inspection. Zero would have passed; two true ones is the better outcome."
verdict: supports
---

# E-M21 — the first measurement on a schema nobody here wrote

## Why this card exists

Every number in this repository so far comes from a fixture written by the person who wrote the tool. Review round 8
asks the obvious question (В6): *what sample would make these numbers evidence rather than a demonstration?*

This is the smallest honest step toward an answer: **run the tool on a real, public, unmodified schema where nothing
is planted**, and publish whatever comes out — including "nothing".

## Pre-registration (written before the run)

Corpus: Pagila, the standard PostgreSQL sample database — a DVD rental model with customers, rentals, payments,
staff and stores. Downloaded from `devrimgunduz/pagila`. The master branch requires PostgreSQL 18 (`uuidv7()`,
`VIRTUAL` generated columns) and produced 263 errors on 17.2, so the tagged release **v2.1.0** was used; it restores
clean, 0 errors, 20 tables, 10 functions.

Target: `public.payment` — chosen because it holds money, the class the tool treats as risk 5.

| # | expectation | pass condition |
|---|---|---|
| a | the enumerator runs on a foreign schema | exit 0, under 60 seconds |
| b | the output is reviewable | at most 40 paths for one table |
| c | every path is legible without the tool's source | non-empty `entry` for every path |
| d | the honest expected result is zero bypasses | reporting 0 is a **pass** |

**d is the important one.** A tool that only looks good when planted paths exist is a demo. The test of a real
instrument is what it says about a schema where the answer might be "your writer privileges are fine and nothing
bypasses anything".

## Run

```
load:   Pagila v2.1.0 restored clean, 0 errors, 20 tables, 10 functions
target: public.payment
exit:   0, 0.4 s
paths:  2
  dynamic_sql | function:public.rewards_report | EXECUTE with the table name assembled at runtime
  function    | function:public.rewards_report | SECURITY DEFINER
```

## Result — supported, and better than the expected zero

| # | expectation | outcome |
|---|---|---|
| a | exit 0, under 60 s | **0.4 s** |
| b | at most 40 paths | **2** |
| c | every entry legible | **2 of 2** |
| d | zero bypasses is a pass | **2 found, both true** |

The flagged function is real. Its body contains:

```
tmpSQL := 'INSERT INTO tmpCustomer (customer_id)
    SELECT p.customer_id FROM payment AS p WHERE ...';
EXECUTE tmpSQL;
```

with `prosecdef = true`. A human reviewing `payment` would flag the same function for the same reason —
`SECURITY DEFINER` plus a statement assembled in a string. The tool did not match a planted pattern, because there
was none; it found what a reviewer would find, in four tenths of a second, with a reason attached.

## What this does not establish

- **Not recall.** Nobody knows how many paths Pagila "has": the notion depends on a declared control point, and
  Pagila declares none. This measures behaviour on foreign input, not recall.
- **Not a bypass.** Whether `rewards_report` bypasses anything is undefined here — there is nothing to bypass.
- **Not one sample.** One schema, one table. It answers В6 with "the tool behaves sanely on foreign input", not with
  "the numbers hold in the wild".
- **The list is short because the schema is small.** Twenty tables and ten functions is a toy by industry standards;
  a schema with four hundred functions may produce a list nobody reads, which is a different failure and not
  measured here.

## What it changes

The evidence base is no longer purely synthetic. It is still thin, and the honest next step is a schema from a
project that has a real control point worth bypassing — which is a question for the owner, not for the tool.
