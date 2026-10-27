---
id: E-M41
hypothesis: H-M41
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T05:45:00+03:00"
finished: "2026-10-28T06:10:00+03:00"
environment: "PostgreSQL 17.2, GitLab structure.sql and the fixture, CPython 3.13.11"
command: "python lab/e-m41-run.py --psql <psql> --port 54329 --db fg_gitlab --schema public --table projects"
threshold: "Pre-registered: an independent oracle asking the same question by different SQL must agree with the enumerator on every writer function, every trigger chain and every cascading key that writes the target. Any object found by one and not the other is a defect in one of them."
result: "First run: the enumerator missed TWO REAL PATHS. GitLab has foreign keys from namespaces and organizations into projects with ON DELETE CASCADE: deleting a namespace or an organization deletes project rows, and the enumerator reported neither. Added fk_cascade to the enumerator; after that the oracle and the enumerator agree on both systems - GitLab 12 paths (3 writers, 7 trigger chains, 2 cascades) and the fixture 13 paths, with zero disagreements. Three harness defects of my own were found and fixed on the way: a broken psql flag that made the oracle return zero rows, a direction mismatch, and the declared control point counted as a missed writer."
verdict: supports
---

# E-M41 — a second implementation found two real paths I was missing

## Why

Reviewer В6: *"to test false negatives you need a ground-truth list built independently; a confirmation of true
positives does not test what you missed."* Nobody will produce a ground-truth list for a public schema, so the next
best thing is a **second implementation** that answers the same question by different SQL and is allowed to disagree.

## What the oracle asks, differently

- any function whose body mentions the table at all (no 200-character window, no semicolon cut-off);
- every trigger, mapped through 	grelid/	gfoid identities rather than text;
- every foreign key with a cascading action, in both directions.

## What it found on GitLab

`
before:  enumerator 10 paths, oracle: 2 cascading keys INTO projects
         namespaces -> projects        ON DELETE CASCADE
         organizations -> projects     ON DELETE CASCADE
`

**Deleting a namespace or an organization deletes project rows.** That is a write path into the target that no grant,
no function body and no trigger mentions, and the enumerator had no concept of it. A defender reading the report
would have believed those two doors did not exist.

## What was added

k_cascade paths: a foreign key whose **child** is the target, with ON DELETE CASCADE | SET NULL | SET DEFAULT or a
cascading ON UPDATE. Direction matters: a key where the target is the *parent* cascades **out** of it and is not a
write path into it. GitLab has 397 of those; they are reported in the harness output and deliberately not listed as
paths.

## After the fix

| system | enumerator | oracle agreement |
|---|---|---|
| GitLab projects | 12 paths (3 writers, 7 trigger chains, 2 cascades) | writers 3/3, chains 7/7, cascades 2/2 |
| fixture ccounts | 13 paths | no disagreement |

## Three defects of my own, found before the result was usable

1. **The oracle returned zero rows** because of a broken psql flag (-tAF swallowed the next argument). The first
   "result" — zero writers — was my tooling, not the schema.
2. **Direction mismatch**: the enumerator writes parent -> child, the oracle child -> parent, so both cascades
   looked missing.
3. **The declared control point counted as a missed writer** on the fixture: it is reported as control_point, not as
   a path, which is correct.

Each of these would have produced a wrong conclusion in a different direction: a false alarm, a false negative, and a
false positive.

## What this establishes, and what it does not

**Establishes:** on one production schema, a second implementation agrees with the enumerator object-for-object after
one real class of paths was added. The enumerator's recall on that table is now consistent with an independent reader.

**Does not establish:** that both are complete. Two implementations can share a blind spot — this is NC-05 — and my
oracle was written by the same person in the same hour. What changed is that the class was found at all, and that the
disagreement mechanism now exists for the next table.

## Log

`lab/logs/e-m41-2026-10-28.log` — sha256 `a5fef60438339aa68b39a642c49ce83c42dea3d383a8600624ff100474f0b6a5`.
