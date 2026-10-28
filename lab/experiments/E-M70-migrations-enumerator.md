---
id: E-M70
hypothesis: H-M70
status: completed
base_commit: "7ce506e"
started: "2026-10-28T20:50:00+03:00"
finished: "2026-10-28T21:30:00+03:00"
environment: "Windows, CPython 3.13.11; corpus: 5 SQL migration files from nearai/ironclaw"
command: "python enumerators/migrations/fg_enum_migrations.py --dir inbox/ironclaw-migrations --schema public --control function:public.audit_write --out inbox/ironclaw-migrations.json --target-lock ironclaw@2026-10-28 && python tools/fg_verify.py --claim inbox/ironclaw-claim.json --inventory inbox/ironclaw-migrations.json"
threshold: "Pre-registered: the third enumerator must read a migration directory as text, with no database, and emit a valid inventory fragment: functions whose bodies write, triggers that fire on a table, grants that give a write, and writes performed by the migration itself. It must reach the verifier without shape errors in BOTH cores, and it must not claim completeness it does not have."
result: "Built and run on a real corpus (IronClaw's 5 migrations): 6 paths - 1 writing function, 4 triggers reaching tables without the control point, 1 backfill - and the inventory passes both cores with CONSISTENT_DECLARED at coverage 0. Three of my own defects surfaced in the first runs: the function regex found 1 of 4 functions because parameters contain brackets, so the body is now located by the dollar quote that follows the head; a table detector returned 'public.1', 'public.ON' and 'public.length' because it matched anything after FROM/UPDATE, now filtered by keyword and by a following bracket; and the observed_write entry named the migration instead of the statement, which the page requires and the verifier refused. A fourth was a divergence: Rust accepted an inventory Python called INVALID, and the cause was my enumerator emitting 'CALL:dynamic' as a verb token - not a verb the format allows. Fixed to stmt:CALL plus a dynamic_sql flag."
verdict: supports
---

# E-M70 — the third enumerator, on somebody else's migrations

## Why this was the next step

Two enumerators existed and both need a **live database**. Most of an application's write logic is defined in a
migration directory, and a repository is a thing you can read without connecting to anything. The accepted
recommendation named "migrations/ORM" as the next target; IronClaw — a Rust assistant with 34 SQLx migrations —
is a real corpus that arrived by accident and fits.

## What it reads

| found | how it becomes a path |
|---|---|
| `CREATE FUNCTION` whose body writes | `function` path, verbs taken from the body's statements |
| `CREATE TRIGGER ... ON table EXECUTE fn` | `trigger_chain` path: a write to the table reaches the body without passing the control point |
| `GRANT INSERT/UPDATE/DELETE ON table TO role` | `privilege` path with no function in between |
| `INSERT INTO`/`UPDATE` inside the migration | `observed_write`, marked `partial`, because a migration runs once and is not a path afterwards |

Result on 5 files: **6 paths** — 1 writing function (`update_updated_at_column`), 4 triggers
(`memory_documents`, `secrets`, `wasm_tools`, `tool_capabilities`), 1 backfill. Both cores answer
`CONSISTENT_DECLARED`, coverage 0.

## Four defects, three of them mine and one of them a divergence

1. **Recall 1 of 4.** The function regex required `AS $$` right after a bracket-packed parameter list, so every
   function with a `DEFAULT` or an array type was missed. Now the body is located from the dollar quote that
   follows the head.
2. **A table detector that returned `public.1`, `public.ON`, `public.length`.** `UPDATE new.updated_at = now()`
   has the shape of a table name followed by `SET`; the filter now rejects keywords, `NEW`/`OLD`, and any
   identifier followed by a bracket (that is a function call).
3. **`observed_write` named the migration, not the statement.** The format page requires a statement, and the
   verifier refused it — the page was right and I was wrong.
4. **The divergence.** Rust accepted an inventory that Python called `INVALID`, and the cause was my enumerator
   emitting `CALL:dynamic` as a verb token. It is not a verb the format allows. Fixed to `stmt:CALL` plus a
   `dynamic_sql` flag, which is what the information actually is.

The fourth is the useful one: two implementations of the same page turned a sloppy token into a visible
disagreement instead of a silent acceptance.

## What it does not do

- It does not claim completeness. A body built by string concatenation is reported with
  `completeness_claim: partial` and a reason, and the inventory as a whole is `partial` when any path is.
- It does not read a database. What a later `ALTER TABLE ... DROP` removes is still in the text, and the source
  note says so.
- It does not look at the Rust side: `sqlx::query("INSERT ...")` in application code is the next surface, and it
  is a different parser.
