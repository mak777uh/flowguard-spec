---
id: E-M45
hypothesis: H-M45
status: completed
base_commit: "c815afd"
started: "2026-10-28T09:00:00+03:00"
finished: "2026-10-28T09:20:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/check-metric-digests.py"
threshold: "Pre-registered: every digest in docs/METRICS.md must be the sha256 of a file that exists in lab/logs/. A digest that resolves to nothing is worse than an empty cell, because it looks like a trail. Rows whose run was never captured must say so in the cell, not carry a plausible number."
result: "Found 14 unresolved digests across 8 rows. Two causes, both mine. First, the E-M44 cleanup rewrote four logs to strip a home path, which changed their sha256 while the rows kept the old value - the digest was honest when written and became false when the file changed. Second, three rows carried digests that were never computed from a captured run at all. Fixed: 12 re-pointed to the log that exists, 2 marked '(run not captured)'. Now 62 rows, 34 logs, 0 unresolved. The check is a guard: it runs in the ritual and in CI."
verdict: supports
---

# E-M45 — a digest is a trail only if it resolves

## What was wrong

`docs/METRICS.md` carries the sha256 of the log each number came from. Eight rows carried digests that
resolved to no file. Two causes:

1. **The cleanup broke its own trail.** In `E-M44` I rewrote four logs to strip a home path. The rows kept
   the digests of the pre-rewrite files. A digest that was honest when written became false when the file
   changed underneath it — and nothing noticed, because no check compared the two.
2. **Three rows never had a captured run.** The numbers reproduce by hand; the digest was written as if a
   log existed.

The second is the worse one: `E-M43`'s reviewer called it out exactly — *"a reader who follows the digest
reaches a file that does not contain the number."*

## What was added

`lab/check-metric-digests.py`: every 64-hex digest in a metric row must be the sha256 of a file in
`lab/logs/`. Wired into `lab/round-check.sh` and CI, so it cannot silently rot again.

## Result

```
metric rows: 62, log files: 34, unresolved digests: 0
re-pointed: 12, marked "(run not captured)": 2
```

The two marked rows keep their numbers and state that the run was not captured. An honest gap beats a
plausible trail.

## The lesson worth keeping

**A digest is a promise about a file's current bytes, and editing the file changes the promise.** Any
process that rewrites a log — redaction, normalisation, reformatting — must recompute every digest that
points at it. That is now a check rather than a habit.

## What this does not do

- It does not prove the number in the row came from that log; it proves the log exists and is unchanged
  since the digest was taken. The extraction step is still a human act.
- It does not cover the cards' own trailing digests, only `METRICS.md`. The cards could drift the same way.




