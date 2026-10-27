---
id: E-M23
hypothesis: H-M23
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:14:00+03:00"
finished: "2026-10-28T00:26:00+03:00"
environment: "PostgreSQL 17.2 fixture, CPython 3.13.11"
command: "python tools/fg_verify.py --claim tools/_tmp/claim23.json --inventory tools/_tmp/m23.json"
threshold: "Pre-registered: (a) a verb observed by the runtime source but absent from the catalogue raises UNENUMERABLE_PATH and blocks any upgrade, (b) no false positive when every observed verb is catalogued, (c) the three counts are published in the verdict, (d) the acceptance suite passes with both cases and nothing regresses."
result: "21/21 scenarios. On the fixture the catalogue lists INSERT and UPDATE; the runtime witness saw INSERT, UPDATE and DELETE. The DELETE produced UNENUMERABLE_PATH, and the verdict dropped to CONSISTENT_DECLARED with the arithmetic refusal alongside it. T21 confirms no false positive when the verbs match. One defect in my own first attempt: the catalogue scan counted the runtime paths as catalogue evidence, so DELETE looked enumerated and the list came out empty - fixed by skipping kind observed_write."
verdict: supports
---

# E-M23 — observed but not enumerated

## Where this came from

All three independent reviews of round 8 named the same defect in the coverage model: one ratio cannot distinguish
three different situations.

| state | meaning | what a ratio does with it |
|---|---|---|
| **covered** | enumerated by a catalogue source and observed happening | counts as covered |
| **unobserved** | enumerated, never seen | counts as outside — which is wrong if it merely was not exercised |
| **unenumerable** | observed happening, absent from the enumeration | counts as nothing — and it is proof the denominator is wrong |

The third is the dangerous one. It does not say "we did not look"; it says **"we looked and the answer was
incomplete"** — and any arithmetic over that denominator is decoration.

## What is implemented

`tools/fg_coverage.py` computes the three states on the **verb dimension**, the only dimension where catalogue
privileges and runtime statements speak the same language. `fg_verify` publishes the counts and raises
`UNENUMERABLE_PATH` when an observed verb has no enumerated path; the refusal blocks any upgrade.

## Run on the fixture

```
catalogue verbs   INSERT, UPDATE          (two privilege paths)
observed verbs    INSERT, UPDATE, DELETE  (runtime witness)
→ unenumerable    DELETE
→ verdict         CONSISTENT_DECLARED
→ errors          UNENUMERABLE_PATH, CLAIM_EXCEEDS_EVIDENCE, POLICY_CEILING_EXCEEDED
```

The `DELETE` really happened: the workload performs it. No catalogue path mentions it, because no grant for `DELETE`
exists and no function does one. That is exactly the situation where a coverage percentage would have been
meaningless and nobody would have noticed.

## A defect in my own first attempt

The first implementation scanned every path's text for verbs, **including the runtime paths themselves**, so `DELETE`
appeared in the "catalogue" set and the unenumerable list came out empty. The check reported a clean result on the
one case it was built to catch. Fixed by skipping `kind: observed_write`; the comment in the file names this, because
the next person will make the same mistake.

## What this does not do

- **Function-level unenumerable.** A function reached by `SELECT` that never appears in the catalogue cannot be seen
  this way: nested statements are not logged without pgAudit (`E-M17`).
- **Objects, not just verbs.** `DELETE` is coarse. Two different `DELETE` paths, one catalogued, one not, look
  identical at this granularity.
- **It does not make the denominator complete.** It makes its incompleteness **visible**, which is the most a check
  can do.
