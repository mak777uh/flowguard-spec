---
id: E-M46
hypothesis: H-M46
status: completed
base_commit: "0804c3e"
started: "2026-10-28T09:25:00+03:00"
finished: "2026-10-28T09:40:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/check-metric-digests.py --cards"
threshold: "Pre-registered: E-M45 said it covered only docs/METRICS.md and not the cards. Every sha256 written in an experiment card must resolve to a file in lab/logs/, and the check must fail when a digest is planted that resolves to nothing."
result: "The card scan found three stale digests that METRICS had already been repaired for: E-M30, E-M19 and E-M11 still carried the pre-rewrite hashes. Re-pointed. A planted all-zero digest is caught, so the check has a negative control. Now 63 metric rows and 38 cards, 34 logs, 0 unresolved."
verdict: supports
---

# E-M46 — the cards drifted too

`E-M45` closed its own gap by naming it: the digest check covered `docs/METRICS.md` and not the cards. Extending
it found three more stale digests — in `E-M30`, `E-M19` and `E-M11` — each pointing at the pre-rewrite log, exactly
the class `E-M45` had just fixed one layer up.

That is the pattern worth recording: a repair applied to the surface the reviewer named leaves the same defect one
layer below. The check was extended rather than the rows patched, and a planted all-zero digest proves it fails.

## What it does not do

It still cannot prove the number in the card came from that log; it proves the log exists and is unchanged since the
digest was taken.
