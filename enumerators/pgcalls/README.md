# pgcalls — attribute PL/pgSQL functions to a declared control point

Contributes **attribution**, not paths (ADR-0009). It answers one question per function: does its body reach the
declared control point, directly or through a chain of calls?

## Covers

- functions whose body calls the control point by name
- transitive reachability through the call graph, up to depth 8

## Blind spots (declared)

- dynamic SQL: `EXECUTE` with a function name built at runtime
- calls through variables, records or string concatenation
- C-language functions and extension code
- calls made from outside the database (application code, scheduled jobs)
- depth beyond 8
- overloads: resolution is by name, not by signature

## Why it exists

`E-M12` measured that a writer-only inventory computes coverage 0 forever: writers are listed, callers are not, and
nothing can be attributed to the control point. `E-M13` shows this source fixes that — 2/2 legitimate callers
attributed, 0/9 false attributions, including a decoy that is *named* like the flow but writes the table directly.

## Run

```bash
python fg_enum_pgcalls.py --psql <path>/psql --host 127.0.0.1 --port 5432 \
    --user postgres --db mydb --schema bank --control transfer --out attributions.json
```

## Landing test

`lab/e-m13-run.py` builds the fixture, runs both enumerators, merges, verifies, and checks the decoy is not
attributed. Recorded in `lab/experiments/E-M13-attribution.md`.
