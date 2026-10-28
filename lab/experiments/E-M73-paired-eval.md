---
id: E-M73
hypothesis: H-M73
status: completed
base_commit: "96a52a5"
started: "2026-10-29T00:40:00+03:00"
finished: "2026-10-29T01:10:00+03:00"
environment: "Windows, qwen3.8-flash via the harness agent(), five questions, two arms"
command: "python lab/paired-eval.py --dry-run; then both arms through the session; python lab/paired-eval.py --score"
threshold: "Pre-registered: arm B (our inventory + verdict) must find strictly more true bypasses than arm A (bare catalogue) and must not introduce more false ones. Anything else is reported as it comes out, including 'no difference' and 'arm B is worse'."
result: "THE THRESHOLD WAS NOT MET, and the reason is not what I expected. Arm A answered three of five questions and named the same three bypass mechanisms arm B named - the apply_transfer path, the app_rw grant, and the trigger - so arm B did not find strictly more. Two of five arm-A calls returned empty output twice in a row. What arm B did produce is different in kind rather than in quality: every bypass it named carries a path_id from the inventory, plus the coverage number 0.0 and the absence of any path attributed to the control point, so its answer can be checked against the artifact. Arm A's answers are correct prose with nothing to check them against - no path ids, no denominator, no statement of what it did not examine. The weaker claim the data supports: the artifact does not make a model smarter, it makes its answer auditable."
verdict: refutes
---

# E-M73 — the paired evaluation: our report did not make the model smarter

## What was run

Five questions about one small schema, two arms, the same model (`qwen3.8-flash`), one difference:

- **arm A** — the catalogue: tables, functions, triggers, grants, and the declared control point.
- **arm B** — the same catalogue plus our inventory (five paths, each with its verbs and attribution), the verdict
  `CONSISTENT_DECLARED`, `coverage 0.0`, and the `NC-01`/`NC-02` non-claims.

Ground truth was written from the catalogue by hand, before any call: `apply_transfer` as a function bypass,
`app_rw` as a grant bypass, the trigger as a code path the control point never sees, three independent ways, and
"none" as the answer to what a grader would accept.

## The result, against the threshold

The threshold was: arm B finds **strictly more** true bypasses, no more false ones.

**It did not.** Arm A, in the three questions that produced an answer, named the same three mechanisms. So the
honest verdict is `refutes`: there is no evidence here that the artifact improves recall.

Two execution facts belong in the record:

- **Two of five arm-A calls returned empty output**, on two separate runs. The same prompt shape produced an
  answer for q3–q5 and nothing for q1–q2. That is a harness fact, not a model-quality claim, and it means the
  comparison has 3/5 usable arm-A answers — which is itself a reason the threshold could not be met cleanly.
- **Arm A's answers drifted off their labels**: the answer returned for `q3` contained `q1`'s content. Question
  identity is unreliable in this protocol unless the harness enforces it; mine did not.

## The difference that is real

Arm B's answers **carry their evidence**:

```
wp_mig_da45f55b3383  function  sample.apply_transfer → sample.accounts, attributed to: none
wp_mig_9f8ea01ded6f  privilege role:app_rw → sample.accounts, INSERT/UPDATE
coverage 0.0, no path attributed to sample.review_transfer
NC-01: the inventory may be incomplete
```

A reader can check each sentence against the artifact and re-run the enumerator. Arm A's answers are correct
prose — and when they are wrong, or when they leave something out, there is nothing to compare them against. That
is exactly the product thesis, stated honestly and smaller than a claim of better recall:

> the artifact does not make a model smarter; it makes its answer **auditable**.

## What this changes in the product story

The earlier phrasing in `docs/21-FINAL-ASSESSMENT.md` implied that a consumer who reads the bundle answers
*better*. This run does not support "better". It supports "checkable", which is the thing this repository can
actually deliver and the thing the ceiling section has been saying all along: consistency, not truth.

Anyone quoting this experiment should quote the smaller claim.

## What would test the larger claim

A schema where the bypass is **not visible in the catalogue** — a path that only exists because two facts must be
combined (a grant on a view over a table that a trigger writes). If the inventory surfaces it and a bare catalogue
does not, arm B finds strictly more. That is the next experiment, and it needs a fixture designed to hide the
path rather than one that lists it.

## What this does not do

- It does not measure a human reader. `P2` stays zero: five model calls are not a consumer.
- It does not generalise from one model and one schema. The sample is five calls per arm on a schema built to be
  checkable in a few hundred tokens.
- It does not retract the ledger's earlier claim that cross-family attacks pay: that measured finding real
  defects, and it found four.
