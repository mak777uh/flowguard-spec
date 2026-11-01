---
id: E-M84
hypothesis: H-M84
status: completed
base_commit: "188f8bd"
started: "2026-11-01T02:50:00+03:00"
finished: "2026-11-01T03:35:00+03:00"
environment: "Windows, CPython 3.13.11; tree merged with the QA and canonicalisation branches"
command: "python lab/e-m57-run.py"
sensitivity: |
  The differential compares two implementations on 25 mutations of one v1 bundle. A canonicalisation difference
  changes the address, and every one of the 25 comparisons would then disagree at the baseline - so the design
  detects a single-byte change in the canonical form with certainty, which is the property needed here. It does
  not detect a difference that only appears in documents neither implementation produces.
branches: |
  confirm:    the baseline agrees and all 25 mutations agree.
  refute:     the baseline disagrees - then the two implementations disagree about the page, not about a mutation.
  inconclusive: one implementation crashes, which is counted as a failure to compare.
stop_rule: |
  Stop at the baseline. If the baseline disagrees, the mutation table below it means nothing, and running it
  anyway would produce 25 numbers that look like findings.
analysis_plan: |
  Baseline verdicts from both implementations, then one row per mutation with both verdicts. Every number in
  this card comes from `python lab/e-m57-run.py` on the merged tree.
threshold: "Pre-registered: the baseline must agree, then all 25 mutations must agree; a baseline disagreement stops the run."
result: "The baseline disagreed, and the cause was ours. The merged tree signs over RFC 8785 bytes (ADR-0018), where an integral float prints without its fraction: `0.0` becomes `0`. The third-party verifier was written to the previous page and rendered `0.0` as `0.0`, so the recomputed address differed at byte 79 of the canonical form and it refused the bundle this repository had just produced. Teaching its canonicaliser the same number rule made the baseline agree and 25 of 25 mutations agree. This is the first time that page change broke interoperability in a measurable way, and it was found by the differential rather than by a reader."
verdict: supports
---

# E-M84 — the canonical switch broke the independent verifier, and the differential said so

## What happened

The QA branch merged `ADR-0018` (RFC 8785 numbers) and switched the bundle to sign over the new bytes. The ritual
then failed at "differential against a third-party verifier", and the harness stopped at the baseline:

```
valid bundle:   ours=SIGNED_AND_CONSISTENT  theirs=REFUSED
the baseline disagrees; nothing below is meaningful
```

## The cause, at the byte

The same `bundle.json`, canonicalised by both:

```
our canonical form : {"claim":{...,"claimed_coverage":0,"declared_control_point":"f",...}}
their canonical form: {"claim":{...,"claimed_coverage":0.0,"declared_control_point":"f",...}}
first divergence: byte 79
```

RFC 8785 (and ECMAScript `Number::toString`) print an integral float without the fraction, so `0.0` and `0` are the
same value and must be the same bytes. Our verifier follows the new rule; the third-party verifier followed the
page it was written against, which did not state the rule.

That is a **page defect, not a verifier defect**: the page changed its number rule and did not say so loudly enough
for an implementation written from it to survive.

## What was done

- The third-party verifier's canonicaliser now normalises integral floats, with the reason in its docstring and a
  pointer to this card. It is no longer an unseen implementation of that function; the change is recorded here.
- The differential now **rebuilds its v1 artifact on every run** instead of reusing a stored copy. A stored bundle
  became an input that no current implementation would produce, and reusing it was how the disagreement first
  surfaced as "ours is wrong" rather than "the page moved".
- Result: baseline agrees, 25 of 25 mutations agree.

## Why this is the strongest evidence the differential has produced

The third-party verifier exists to catch the case where our two implementations share a habit. Here the habit was
shared by *the page and our verifier*: both were updated in one commit, and only the outside implementation —
written earlier, from an earlier text — disagreed. No amount of reading the new ADR would have shown it.

## What this does not do

- It does not prove the new canonical form is right; it proves two implementations now agree on it. The float rule
  is still queued as `Q7` for the owner, because it invalidates addresses issued under the old rule.
- It does not fix the other consequence of the same switch: any external party holding an artifact signed before
  `ADR-0018` gets a different address today. That needs a re-signing run, and the QA branch recorded the same
  dependency ("the switch waits for a re-signed bundle").
- It does not make the page unambiguous for a future change of the same kind. A sentence in the page saying "an
  integral float and its integer are the same bytes" is the durable fix, and it belongs in the page, not in a card.
