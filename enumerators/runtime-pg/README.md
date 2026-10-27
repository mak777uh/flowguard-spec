# runtime-pg — what actually happened, according to the server log

A source from a different mechanism than the catalogue: it reads the PostgreSQL log, not the metadata.

## Covers

- writes to the target table that were executed during the observed window, by verb
- the statement text of each write, truncated to 200 characters

## Blind spots (declared)

- **writes performed inside a function reached by `SELECT`** — only the outer `SELECT` is logged, so a legitimate
  write through a control point is invisible. **This source under-counts.** (Found by E-M17.)
- paths not exercised during the window — absence of evidence, not evidence of absence
- writes from other sessions, databases or services that do not share this log
- parameterised statements whose table name is bound at execution
- `COPY`, and statements rotated or truncated out of the log
- attribution: the log shows the statement, not which control point the caller went through

## Consequence for the product

A runtime source may never be the coverage denominator on its own. It is a **witness**: it turns "this path exists"
into "this path happened". The denominator comes from the catalogue sources.

## Run

```bash
python fg_enum_runtime.py --psql <path>/psql --host 127.0.0.1 --port 5432 --user postgres \
    --db mydb --schema bank --table accounts --log <server.log> \
    --workload fixtures/pg-bypass/02-workload.sql --out runtime.json
```

The workload runs with `log_statement = 'all'`; only the bytes appended to the log during that window are read.
