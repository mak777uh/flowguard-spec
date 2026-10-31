# 000 — the one command ran from a clean cluster to a verdict on a schema with two planted bypasses

**Verdict:** confirmed

## Claim

On a freshly initialised PostgreSQL 17.2 cluster, `pg_dump --schema-only` of a small payments schema followed by
`tools/fg_init.py` produced a `CONSISTENT_DECLARED` verdict in one run, and the inventory contained both planted
bypasses: a direct `INSERT/UPDATE` grant to `app_role`, and an `adjust()` function that writes `payments` without
reaching the declared control point `public.audit`.

## Evidence

- `transcript.txt` in this folder — the run from `initdb` to the verdict, exit code 0, including the per-step
  `[1/7] … [7/7]` lines.
- The inventory reported 5 paths: `role:app_role table:public.payments` (`INSERT`, `UPDATE`), `adjust()` with no
  attribution, and `pay()` / `refund()` attributed to `function:public.audit` with method `direct`.
- The claim the tool wrote was honest by construction: `claimed_coverage: 0.0`, `evidence_tier: 0`,
  `not_claimed: NC-01, NC-02, NC-04, NC-05, NC-11`.

## Reproduce

```
initdb -D <dir> -U postgres -A trust -E UTF8 --locale=C
pg_ctl -D <dir> -o "-p 5434" -l <log> start
psql -h 127.0.0.1 -p 5434 -U postgres -c "CREATE DATABASE shopdb"
psql -h 127.0.0.1 -p 5434 -U postgres -d shopdb -f shopdb.sql     # the schema described in Claim
pg_dump -h 127.0.0.1 -p 5434 -U postgres --schema-only -d shopdb -f schema.sql
python tools/fg_init.py --psql <psql> --port 5434 --db fg_try --dump schema.sql \
       --schema public --table payments --control function:public.audit
```

The schema file is not committed; it is twelve statements and the transcript names every object it creates.

## Verdict

`confirmed`: the tool found both planted bypasses and attributed the two legitimate writers, in one run, without
manual steps.

## Limits

- **Author-side run; it does not count toward P1.** The definition of P1 is a party that did not write the code.
- The schema is the author's own, so this measures the mechanism, not the utility: two bypasses planted by the
  person who knows what the enumerator looks for.
- One run, one schema, no timing claim. A second run against the same database name fails at the dump step
  because the objects already exist; that behaviour is documented in the README and is not measured here.
- The transcript is the run's stdout. It is not a substitute for an independent rebuild.
