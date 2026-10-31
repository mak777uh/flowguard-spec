# Foreign validation — the protocol for a schema owner to confirm or deny a finding

This is the step that moves `evidence_tier` from 1 to 2 (`E-M29`). It needs one thing this repository cannot produce:
a person who owns a schema and says something about it.

The verifier reads `foreign_validation` from the inventory and refuses a tier the record does not support. This page
is the form that record has to satisfy — and, more importantly, what makes a confirmation *count*.

## What a confirmation is not

- Not "the tool ran on my schema". That is execution, not validation.
- Not "looks plausible". A finding is either true about the schema or it is not.
- Not our summary of what the owner said. Their words, quoted.

## The three records, in rising strength

### 1. `external_execution` — the tool ran, nothing confirmed

```json
{ "schema": "acme-billing", "version": "2026-10-28", "executed_by": "flowguard",
  "owner_confirmed": false }
```

What it supports: **nothing above tier 1.** It records that a foreign schema was processed, which is what `E-M30`
already does.

### 2. `finding_owner_confirmed` — the owner speaks to one finding

```json
{ "schema": "acme-billing", "version": "2026-10-28",
  "owner_confirmed": true,
  "owner": { "name": "<a person>", "role": "<their role at the organisation>",
             "how_contacted": "<the channel>", "date": "2026-11-02" },
  "finding": { "path_id": "wp_…", "claim": "<what we said>", "our_evidence": "<the path and why>" },
  "owner_statement": "<their sentence, quoted, in their words>",
  "verdict": "confirmed | refuted | partially_correct",
  "what_changed_for_them": "<optional: the decision this affected, if any>" }
```

What it supports: **tier 2.** Note what is required: a named person, a role, a date and a channel — and their
sentence, not ours. A confirmation without a name is a rumour with a timestamp.

### 3. `coverage_independently_evaluated` — the owner produces their own list

```json
{ "schema": "acme-billing", "version": "2026-10-28", "owner_confirmed": true,
  "blind_evaluation": true,
  "owner": { "…": "as above" },
  "ground_truth": { "produced_by": "owner", "method": "<how they built it>",
                    "paths_expected": 14, "artifact": "<where the list lives>" },
  "our_result": { "paths_found": 9, "missed": ["…"], "false_positives": ["…"] } }
```

What it supports: **tier 3** when `blind_evaluation` is true — the owner built their list **without seeing ours**.

## The rule that makes it worth anything

**A finding confirmed proves a true positive. Only an owner-produced list proves the absence of false negatives.**

An owner who reads our output and says "yes, that function does use dynamic SQL" confirms we are not hallucinating. It
says nothing about the ten things we missed. A reviewer said this plainly, and it is the reason record 3 exists: the
owner must produce the expected list **first**, or the exercise measures agreement, not coverage.

## What we will not do with the record

- We will not edit the owner's sentence. A quoted statement that we tidied is our statement.
- We will not count a confirmation of one finding as validation of the tool. Tier 2 is one schema, one finding; the
  `not_claimed` code `NC-11` still says the numbers do not generalise.
- We will not treat a refusal as a failure of the validator. A `refuted` verdict that we record and act on is the
  strongest evidence this repository can get — it means the loop works.

## The record that earns P1 — a `rebuild_result` line plus a confirmation

P1 is a third-party rebuild: a human or an organisation, not an AI agent, produced the same result and said so.
Two files carry it. Until 2026-10-31 only `tools/fg_readiness.py` knew this, which is why the gate stayed at zero
while the form looked fillable.

**1. The marker**, in any card under `lab/experiments/` — the gate reads that directory and nothing else:

```
rebuild_result: agreed by a third party
```

`agreed` or `differed`; then `third party`, `human` or `organisation`.

**2. The record**, a JSON file under `docs/`, `interop/`, `lab/experiments/` or `reports/`. Never under
`fixtures/` and never under `tools/_tmp/`: a synthetic record in a scratch directory once made P1 pass, which is
why those paths are refused in code.

```json
{
  "foreign_validation": [
    {
      "schema": "acme-billing",
      "owner_confirmed": true,
      "owner": { "name": "<a person>", "role": "<their role>", "how_contacted": "<the channel>", "date": "2026-11-04" },
      "owner_statement": "<their sentence, quoted, at least 12 characters>",
      "verdict": "confirmed"
    }
  ]
}
```

The shape is published: [`../schemas/foreign-validation-0.1.json`](../schemas/foreign-validation-0.1.json).
Check a record before committing it:

```
python tools/fg_schema_check.py --foreign-validation lab/experiments/foreign-validation-acme.json
python tools/fg_readiness.py        # P1 should read 15 / 15
```

Only `confirmed` and `partially_correct` move P1. A `refuted` record is recorded and acted on — it is the
strongest evidence the loop works — but it is not a confirmation, and the gate does not pretend otherwise.

## How to record it

```
python tools/fg_confirm.py --inventory <manifest.json> --record <record.json> --out <manifest.with-fv.json>
```

The tool validates the record against the rules above and refuses one that is missing a person, a date, or a verdict.
It does not judge whether the person exists; that is what the name is for.
