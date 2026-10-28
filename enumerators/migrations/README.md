# migrations — what this enumerator cannot see

Reads a migration **directory** as text. No database, no application code, no history.

## What it reports

| found in the SQL | path kind |
|---|---|
| a function whose body writes | `function`, verbs from the body's statements |
| `CREATE TRIGGER ... ON table EXECUTE fn` | `trigger_chain` — a write to the table reaches the body without the control point |
| `GRANT INSERT/UPDATE/DELETE ON table TO role` | `privilege`, no function in between |
| `INSERT INTO`/`UPDATE` run by the migration itself | `observed_write`, marked `partial` |

## Blind spots, stated rather than implied

- **Later migrations.** A function defined in `V1` and dropped in `V9` is reported as if it exists. The
  inventory is the text of the series, not the state of the schema. The source note says so;
  `completeness_claim` is `partial` whenever any path is partial.
- **Dynamic SQL.** A body that builds a statement in a string is reported with `dynamic_sql: true` and
  `completeness_claim: partial`. What the string contains is not read.
- **Application code.** `sqlx::query("INSERT ...")`, an ORM's `save()`, a raw statement in a Rust handler — none
  of it is here. That is the next parser, and it is a different one.
- **Column-level and row-level policy.** `GRANT` on a table is reported; a row-level security policy that makes
  the grant harmless, and a column-level grant, are not distinguished.
- **What the database actually allows.** Privileges inherited through roles, defaults in `pg_default_acl`, and
  anything granted outside a migration file are invisible to a text reader. The grants enumerator reads the live
  catalogue for exactly this reason; the two are meant to be merged, not compared.

## Why it exists anyway

Two enumerators required a live database. Most repositories publish their migrations and nothing else, so a
consumer who has a repository and no DBA can still get a coverage number — with a denominator known to be
incomplete, which the source note states.
