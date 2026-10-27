---
id: E-M33
hypothesis: H-M33
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T02:45:00+03:00"
finished: "2026-10-28T03:00:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m33-run.py"
threshold: "Pre-registered: all 17 malformed or hostile inputs produce parseable JSON with a verdict, exit code 1 or 2, and no traceback on stderr."
result: "First run: 12 of 17. Five defects, one of them serious: four inputs produced a stack trace (empty claim, invalid JSON, empty inventory, paths given as an object), and one malformed path - an object with no entry - was ACCEPTED with a clean CONSISTENT_DECLARED verdict. After adding a shape validation layer: 17 of 17, and E-M12, E-M13, E-M25 unchanged."
verdict: supports
---

# E-M33 — a machine consumer gets refusals, not stack traces

## Why

The consumer of this tool is an agent. It sends JSON and parses JSON. A traceback on stderr is not a verdict: it tells
the caller to retry, guess, or abandon — and none of those is a decision. The input contract had never been tested
against inputs that are wrong in *shape* rather than in value.

## What the first run found

| case | result |
|---|---|
| empty claim file | **traceback** |
| claim is not JSON | **traceback** |
| inventory empty | **traceback** |
| inventory paths is an object | **traceback** |
| a path object with no ntry | **accepted, verdict CONSISTENT_DECLARED** |

The last one is the serious one. Four crashes are loud and would be reported by any caller; a malformed path passing
silently means the tool computed a verdict over an inventory it did not understand. That is the failure mode this
repository is built to refuse.

## What was added

load() now refuses on missing file, non-UTF-8 bytes, empty file and invalid JSON with
REPORT_BUNDLE_INCONSISTENT and exit 2 — never a traceback. alidate_shapes() checks the claim and every inventory
path for required keys and types **before** any arithmetic, and reports up to eight problems with the field named.

## Run

`
cases: 17, handled as a verdict: 17
RESULT: PASS
`

Regression: E-M12 25/25, E-M13, E-M25 unchanged.

## What this does not do

- It does not validate against the JSON Schemas in schemas/. Those are a documentation and integration artifact;
  the verifier's own checks are hand-written and stricter in some places, looser in others. Unifying them is a real
  task, and pretending they are one system would be the usual lie.
- It does not bound memory or time for absurd inputs. A 200 KB claim passes; a 2 GB one would not be handled
  gracefully, and no limit is enforced.
- It does not test semantic hostility — a claim that is well-formed and false. That is what E-M9, E-M10 and the
  acceptance scenarios are for.

## Log

`lab/logs/e-m33-2026-10-28.log` — sha256 `1befaf7f8e3289b8e89889a06ca19c41168d651e1a78aafde183ce809a611c50`.
