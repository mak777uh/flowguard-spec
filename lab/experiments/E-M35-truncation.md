---
id: E-M35
hypothesis: H-M35
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T03:25:00+03:00"
finished: "2026-10-28T03:40:00+03:00"
environment: "PostgreSQL 17.2, generated 400-function schema, CPython 3.13.11"
command: "python lab/e-m35-run.py --psql <psql> --port 54329"
threshold: "Pre-registered: (a) --max-paths keeps at most N paths, highest-value kinds first, and records total/kept/omitted, (b) the summary counts describe the published list, not the list before truncation, (c) a truncated source marks itself partial and the verifier refuses to compute coverage over it, (d) earlier harnesses do not regress."
result: "100 of 480 kept with kinds prioritised (all 80 dynamic-SQL paths survive the cut, plus 20 trigger chains); truncated records total 480, kept 100, omitted 380; the summary now sums to the published list; the verifier refuses coverage with MISSING_EVIDENCE on coverage_basis and reports 'kept 100 of 480'. E-M11, E-M12 and E-M34 unchanged."
verdict: supports
---

# E-M35 — a cap for reading, a refusal for arithmetic

## Why both

E-M34 showed that 480 paths is a list nobody reads, and named --max-paths as the obvious next step. It also
showed why the obvious step is dangerous: the coverage ratio is computed over the inventory, so **a truncated
inventory silently changes the denominator**. If the tool cuts 480 paths to 100 and still reports a coverage
percentage, the number is over a fifth of the evidence.

The rule this card enforces: **truncation is allowed for reading and refused for arithmetic.**

## What was built

- --max-paths N keeps N paths, ordered by kind priority (dynamic_sql, disabled_control, iew_trigger,
  	rigger_chain, unction, privilege) so the cut removes the least actionable entries first;
- the source records 	runcated: {total, kept, omitted} and sets completeness_claim: "partial";
- the merger propagates both fields;
- g_verify refuses coverage with MISSING_EVIDENCE on subject coverage_basis and names the source and the
  numbers.

## Run

`
paths kept 100, truncated {'total': 480, 'kept': 100, 'omitted': 380}, claim partial
summary matches the published list: True
coverage refused on a truncated source: True (codes ['CLAIM_EXCEEDS_EVIDENCE', 'MISSING_EVIDENCE'])
`

## A defect found while verifying

The summary counted the paths **before** truncation: it reported 350 functions beside a published list of 100. A
summary that contradicts the list next to it is worse than no summary — it is a wrong number with a reassuring
shape. Fixed by computing the counters after the cut; the harness now asserts
sum(by_kind) == len(paths).

## What this does not do

- **It does not make truncation safe.** A reader who looks only at the summary still sees a subset; the
  eading_note and the 	runcated block are the only warnings, and a careless consumer can ignore both.
- **It does not rank by risk.** Priority is by kind, not by the weighted class — the risk policy lives in the merge
  and perimeter, not in the enumerator.
- **It does not cap the merged inventory.** A merge of several untruncated sources can still exceed any readable
  size; only per-source truncation exists.

## Log

`lab/logs/e-m35-2026-10-28.log` — sha256 `badcef9ce832456d99ae6fb6cbd1efdfeb50b8323c4a10fd6691001346e86b73`.
