# grants-pg — enumerate the writers of a Postgres table

The first `Enumerator` in the sense of [ADR-0007](../../lab/decisions/ADR-0007-inventory-sources.md).

**What it does:** reads the system catalogue and lists every way a given table can be written, with the declared
control point identified separately. Read-only: nothing is written to the target database.

## Covers

- table privileges granted to roles (`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`)
- functions whose body writes the table (write verb required near the name)
- trigger state on the table, including **disabled** triggers — a control that exists and is switched off
- `INSTEAD OF` triggers on views that write the table
- triggers on other tables whose body writes the table (indirect chains)

## Blind spots (declared, mandatory)

- dynamic SQL where the table name is assembled at runtime and never appears literally
- writes from another database, a foreign data wrapper, `dblink`, or a different service
- application-level checks the database never sees
- privileges inherited through role membership chains and column-level grants
- writes performed by extensions or by superuser sessions outside these catalogues
- **attribution of a path to a declared control point** — this needs a call graph (static or runtime). Without
  one, every path looks like it bypasses the control point, coverage computes to 0, and the verdict stays capped.
  This was found by the end-to-end run, not by reasoning: the enumerator sees writers, not callers.

A one-line summary of the method's honesty: **it can see every door the database knows about, and no door that
lives outside the database.**

## Run

```bash
python fg_enum_grants.py --psql /path/to/psql --host 127.0.0.1 --port 5432 \
    --user postgres --db mydb --schema bank --table accounts --out source.json
```

Output is a `SourceRecord`: `paths[]` with content-hashed `path_id`, `control_points[]`, `covers`,
`blind_spots`, and the tool digest.

## Landing test (required by ADR-0007)

```bash
python lab/e-m11-run.py --psql <path>/psql.exe --port 54329
```

The harness builds `fixtures/pg-bypass` (eight planted bypasses), runs this enumerator, and compares against
`fixtures/pg-bypass/expected.json`. It must find all six catalogue-class plants, at least one of the two
text-search plants, and identify `function:bank.transfer` as the control point. Recorded in
[`lab/experiments/E-M11-grant-enumeration.md`](../../lab/experiments/E-M11-grant-enumeration.md).

## Known false positive

A function whose body contains the table name inside a **string literal** (for example `VALUES ('accounts
changed')`) can be reported as a writer. The write-verb requirement reduces this but does not remove it. Recorded
in E-M11 rather than hidden.

## Add a new enumerator

Copy this directory's shape: `README.md` (covers and blind spots), an `enumerate.sql` or any implementation
emitting rows, and an adapter that produces a `SourceRecord`. Add a landing test. **No format change is
required** — that is the test of the design.
