---
id: E-M81
hypothesis: H-M81
status: completed
base_commit: "11f688e"
started: "2026-10-30T19:00:00+03:00"
finished: "2026-10-30T19:40:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m81-run.py"
threshold: "Pre-registered: the verifier must count the denominator itself rather than accept the claimant's. Given an inventory that omits a path the tool can enumerate, it must refuse with UNDERCOUNTED_DENOMINATOR; given one that already carries every path, it must not refuse on that ground; and given a source it cannot read it must refuse RECOUNT_UNAVAILABLE rather than fall back silently to the claimant's number."
result: "fg_verify --recount DIR runs the migrations enumerator over the same source and unions what it finds into the claim's inventory, attributing each new path to nothing and marking it recounted, so every added path LOWERS coverage. Three cases pass: an undercounted inventory gives UNDERCOUNTED_DENOMINATOR with the first missing path named; a complete inventory passes; an unreadable source gives RECOUNT_UNAVAILABLE instead of silently trusting the claim. The recount is one-directional by construction - it can only enlarge the denominator, so it can only refute the claimant's number, never manufacture a favourable one."
verdict: supports
---

# E-M81 — the tool counts for itself

## Why this exists

LongTails' Comparator can audit a budget because the budget is part of the proof. Ours could not audit a
denominator, because the denominator arrived inside the document being judged. The user's objection was exact:
*the tool should be able to count too.*

## What was added

```
python tools/fg_verify.py --claim c.json --inventory i.json --recount fixtures/hidden-bypass
```

- runs `enumerators/migrations/fg_enum_migrations.py` over the same source;
- unions the paths it finds with the claim's, by identity `(kind, entry, target)`;
- every added path is `recounted: true` and attributed to **nothing**, so it cannot count toward coverage;
- if anything was added, the verdict carries `UNDERCOUNTED_DENOMINATOR` naming the first missing path;
- if the source cannot be read, `RECOUNT_UNAVAILABLE` — never a silent fallback.

One-directional by construction: the recount can only *enlarge* the denominator, so it can only refute the
claimant's number, never manufacture a favourable one. That is the property that makes it safe to run against a
claimant who controls the other input.

## The three cases

| case | result |
|---|---|
| inventory omits what the recount finds | `UNDERCOUNTED_DENOMINATOR`, first missing path named |
| inventory already carries every path | no refusal on that ground |
| source absent | `RECOUNT_UNAVAILABLE`, not a silent pass |

## What this does not do, and the honest size of the step

- **Only the migrations enumerator is wired.** `--recount` reads a directory of SQL. A live database source
  (`--psql`, the grants and pgcalls enumerators) is not connected, so a claim about a real system still relies on
  whoever ran the enumerators there.
- **The Rust core has no `recount`.** The two implementations now differ in capability, which the differential will
  not catch — it compares verdicts on the same input, and only one side can produce this input.
- **It does not make the denominator complete.** It catches omission relative to *one* enumerator. `NC-01` stands:
  a path that no enumerator sees is still unseen, and the recount cannot find what the tool cannot enumerate.

That last point is the ceiling, and it is unchanged by this experiment: the tool now counts, but it counts only
what it knows how to count.
