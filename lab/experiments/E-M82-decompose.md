---
id: E-M82
hypothesis: H-M82
status: completed
base_commit: "baacccb"
started: "2026-10-30T19:10:00+03:00"
finished: "2026-10-30T19:50:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m82-run.py"
threshold: "Pre-registered: a claimant's text must be split into units with a named fate - measured, assumption, requirement, absolute, unmapped - refuse the sentences no artifact can support, and never drop a sentence silently. Five cases, one per fate plus a mixed text."
result: "tools/fg_decompose.py classifies every sentence deterministically and refuses absolutes instead of weakening them. Five of five cases pass. Three defects were found by the tests themselves: Russian verb stems were matched by set intersection instead of substring, so 'записать' read as 'no action'; absolutes were stored with hyphens, so 'provably-safe' never matched 'provably safe'; and a mixed text produced three units while the absolute inside it was not recognised. All three closed. The output is a draft claim whose control point is deliberately left as a placeholder - the tool will not invent it."
verdict: supports
---

# E-M82 — from a text of intentions to checkable units

## What the request was, and what is honestly possible

> take a spec, or the claimant's text of intentions, split it into precise units, and hand those to a defended core.

The first half cannot be "understand the prose" in a way that allows a strong claim. What it can be is:
**every sentence gets a fate**, and the fates that cannot become units are named as refusals.

| kind | meaning | what happens next |
|---|---|---|
| `measured` | names an action a program can perform, with an object | becomes a path candidate; the unit says it still needs a target table and a control point |
| `requirement` | "must", "may not" — policy, not observation | a human decision; it is not a path |
| `assumption` | "assume", "provided that" — a condition nobody is named as verifying | flagged: this is where an extra assumption would enter (Q8) |
| `absolute` | "guarantees", "provably safe", "always", "never" | **refused**, not weakened |
| `unmapped` | none of the above | kept and marked, never dropped |

## The three defects the tests found

1. **Russian stems matched as whole words.** `ACTION_VERBS` held stems like `запис`, and the matcher did a set
   intersection, so `записать` counted as "no action" — a false negative in the worst direction for this tool.
2. **Absolutes stored with hyphens.** `provably-safe` never matched `provably safe`, and the sentence passed as
   `unmapped` instead of being refused. The classifier now normalises hyphens before comparing.
3. **A mixed text hid its absolute.** With the hyphen bug, three sentences produced one `measured` and two
   `unmapped` — the refusal was silently absent from a text that contained a claim no artifact can support.

Each of the three was found by a case, not by reading the code, which is the pattern this repository keeps
repeating: a classifier is only as good as the sentence that breaks it.

## What it produces

```json
{"claim": {"claim_id": "<set by a human>",
           "target_lock": {"commit": "<the source this text describes>"},
           "declared_control_point": "<from the measured units; the tool will not invent it>",
           "declared_level": "CONSISTENT_DECLARED", "claimed_coverage": 0.0,
           "evidence_tier": 0, "not_claimed": ["NC-01", "NC-02"]}}
```

The claim is deliberately weak and incomplete: a draft that asserts nothing, with the two fields the tool may not
invent left blank. Filling them is the claimant's act, and the `measured` units say which fields they correspond to.

## What it does not do

- It does not decide whether a `measured` unit is true. It becomes a path, and a path is only as good as the
  enumerator that finds it — the same ceiling as everywhere else.
- It does not resolve pronouns or cross-sentence references. A sentence that says "this" is `unmapped` and stays
  that way.
- It does not connect to the enumerators yet. The bridge from a `measured` unit to `fg_init`/`fg_enum_*` is the
  next step, and it is a design decision (which enumerator a verb implies), not a parser improvement.
