# Cross-repo registry — the styks between the owner's projects

Each project in this family has its own gate. This directory checks the **joints**: the places where two projects
claim to agree, where a defect is invisible to both gates and only appears between them.

The rule, from `E-M71`: **agreement between two implementations by the same author proves less than agreement
between two authors, and both prove less than agreement with a third language.**

## Entries

| # | styk | how it is checked | today |
|---|---|---|---|
| X-1 | canonical form: FlowGuard `tools/fg_bundle.py` (function `canon`) vs LexSpec LexSpec's `lexcheck.py` (function `canonical_text`) | `python lab/xrepo-canonical.py` | **14/14 documents identical bytes** |
| X-2 | address independence from the serialising language | `python lab/xrepo-floats.py` (Python vs Node) | **6 of 10 float values differ** → `E-M71`, Q7 |
| X-3 | refusal-vocabulary overlap: `docs/37-REFUSAL-CODES.md` vs LexSpec's own refusal-codes page | manual, promised in note 2 | not done |
| X-4 | a number quoted in one repository, recomputed by the other's script | not started | not done |

## What a styk finding looks like

Not "their approach differs from ours". A finding has: two artifacts, one input, a command that runs both, and a
difference that a reader can reproduce. `E-M71` is the shape: two canonicalisers, fourteen documents, one class of
disagreement, a digest pair for each.

## Running them

```
python lab/xrepo-canonical.py     # needs a LexSpec checkout: LEXSPEC_DIR, default ../lexspec-review
python lab/xrepo-floats.py        # needs Node on PATH
```

Both exit non-zero on a byte disagreement, so they can be wired into CI for splits that keep the sibling clone
next to this repository. They are **not** in `lab/round-check.sh`: a ritual must not depend on a checkout that may
not exist on a given machine. That is a deliberate difference from the other harnesses, and the reason is written
here rather than discovered by the next person.
