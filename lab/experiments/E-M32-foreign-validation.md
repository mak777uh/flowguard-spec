---
id: E-M32
hypothesis: H-M32
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T02:30:00+03:00"
finished: "2026-10-28T02:40:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python tools/fg_confirm.py --record <record.json> --check"
threshold: "Pre-registered: (a) a confirmation record without a named person, a role, a contact channel, a date, a verdict and the owner's own quoted sentence is refused, naming every missing field, (b) a complete record is accepted and raises the evidence tier the inventory supports to 2, (c) the verifier then accepts a tier-2 declaration that it refused before."
result: "5 of 5 refusals named on the incomplete record; the complete record accepted and the inventory moved to tier 2; a PROVEN claim at tier 2 no longer trips EVIDENCE_TIER_UNSUPPORTED (its verdict is still CONSISTENT_DECLARED, because coverage and other errors stand — the tier is not a shortcut past them)."
verdict: supports
---

# E-M32 — the landing ground for a foreign confirmation

## Why this exists

E-M29 made the evidence tier a field the inventory must support, and the product half has been at zero because
nobody outside has confirmed anything. The step that changes that is a conversation — but the conversation needs a
place to land, and the landing place must be shaped so that a form cannot substitute for a fact.

## What was built

docs/FOREIGN-VALIDATION.md — three record shapes in rising strength:

| record | needs | supports |
|---|---|---|
| xternal_execution | that it ran | nothing above tier 1 |
| inding_owner_confirmed | a person, a role, a channel, a date, a verdict, their quoted sentence | tier 2 |
| coverage_independently_evaluated | the owner's own ground-truth list, produced blind | tier 3 |

The rule the page insists on: **a confirmed finding proves a true positive; only an owner-produced list proves the
absence of false negatives.** An owner who reads our output and agrees confirms we are not hallucinating and says
nothing about what we missed.

	ools/fg_confirm.py enforces the shape. It refuses a record that is missing any of: person, role, channel, date,
verdict, a quoted statement of at least a dozen characters, and the finding it refers to.

## Run

`
incomplete record -> 5 refusals, each naming the field:
  owner.how_contacted · owner.date · owner_statement · finding.path_id · finding.claim
complete record   -> accepted: acme-billing — confirmed by Ivan Petrov on 2026-11-02
                     inventory now supports evidence tier 2
`

The example record is synthetic and is **not** attached to any real inventory: a fabricated confirmation would be the
worst artifact this repository could produce, and the tool cannot tell a real person from a plausible name. It can
only insist that the name is there.

## What this does not do

- **It cannot verify the person exists.** Names are claims. This is exactly NC-08 and it stays in every verdict.
- **It does not make the schema confidential-safe.** A confirmation may attach our finding about their schema to a
  public inventory; whether that is acceptable to the owner is a question the owner answers, and the record has a
  field for it.
- **It does not raise the tier of existing work.** Everything measured so far is tier 1; this is the door, not the
  room.

## Log

`lab/logs/e-m32-2026-10-28.log` — sha256 `e03e4c2eaf0b22ae921650e4c9874828c07905e8ff0ed6ad342f63df71618752`.
