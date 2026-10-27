---
id: E-M37
hypothesis: H-M37
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T04:10:00+03:00"
finished: "2026-10-28T04:30:00+03:00"
environment: "PostgreSQL 17.2, GitLab db/structure.sql (public), CPython 3.13.11"
command: "python enumerators/grants-pg/fg_enum_grants.py --db fg_gitlab --schema public --table <table>"
threshold: "Pre-registered: load a production-scale public schema without editing it, run the enumerator on tables chosen by the fixed name rule, and report whatever comes out - including zero - in under a minute per table."
result: "GitLab structure.sql: 1436 tables, 558 functions, loaded in 29 s with 0 errors. projects: 10 paths in 0.4 s (3 SECURITY INVOKER functions and 7 trigger chains from the integrations table). members, gitlab_subscriptions, subscription_add_on_purchases: 0 paths in under a second each. Only 36 functions in the whole schema contain any write statement, which is the real finding: GitLab keeps its write logic in Ruby, and this tool does not look there."
verdict: supports
---

# E-M37 — a production schema from the internet: GitLab

## What was run

`db/structure.sql` from the public GitLab repository — a real production schema, unmodified.

```
tables      1436
functions    558
load         29 s, 0 errors
of those 558 functions, the ones containing any write statement: 36
```

| target | paths | seconds | what |
|---|---|---|---|
| `projects` | **10** | 0.4 | 3 functions + 7 trigger chains from `integrations` |
| `members` | 0 | 0.5 | none |
| `gitlab_subscriptions` | 0 | 0.5 | none |
| `subscription_add_on_purchases` | 0 | 0.9 | none |

The `projects` findings are real and checkable by anyone: `insert_projects_sync_event`,
`set_has_external_issue_tracker`, `set_has_external_wiki`, and seven trigger chains where a change to `integrations`
writes `projects`.

## The finding that matters

**Thirty-six functions out of five hundred and fifty-eight contain a write statement.** GitLab is a Rails
application: the database holds the tables, and the logic that writes them lives in Ruby, outside the reach of a
catalogue reader.

That is not a defect in the tool, it is a statement about where its scope ends — and it is exactly what `NC-02` and
`NC-04` say. On a system like this, the tool examines a thin slice of the write path. On a system with stored
procedures doing real work (the fixture, Pagila's `rewards_report`, the 400-function synthetic schema), it examines
most of it.

A buyer would need to know which kind of system they have before the number means anything, and the product currently
does not ask that question.

## What this does not establish

- **No owner confirmation.** Nobody at GitLab confirmed the findings, so `evidence_tier` stays 1.
- **No ground truth.** Whether 10 is all the DB-level paths into `projects`, or a subset, is unknown — there is no
  independent list.
- **Not generalisable.** One large application schema, chosen because it is public and large.

## Log

``lab/logs/e-m37-2026-10-28.log`` — the summary of these runs.
