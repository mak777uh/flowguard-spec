---
id: E-M29
hypothesis: H-M29
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T01:28:00+03:00"
finished: "2026-10-28T01:40:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered: (a) a declared evidence tier the inventory cannot support is refused, (b) a level above what the tier allows is refused with the tier named, (c) tier 0 caps the level at CONSISTENT_DECLARED and tier 2 unlocks PROVEN only with owner-confirmed foreign validation, (d) NC-11 is required for every level above the floor, (e) the suite passes with all of it."
result: "25/25. T24 refuses tier 3 with no foreign validation (EVIDENCE_TIER_UNSUPPORTED); T25 refuses PROVEN at tier 0 (CLAIM_EXCEEDS_EVIDENCE on evidence_tier); NC-11 is now required at SCOPED_ASSURANCE and PROVEN, so a claim cannot silently imply that a fixture result generalises. Earlier scenarios had to declare a tier, which is the intended effect: the field is no longer optional in practice."
verdict: supports
---

# E-M29 — a number needs to say what ground it stands on

## The defect

Round-8 review, all three models, in different words: **eight of eight on a fixture written by the author, and one
real finding on a stranger's schema, are not the same kind of evidence** — and in our artifact they were
indistinguishable. The coverage ratio, the level and the `not_claimed` list said nothing about the population the
numbers came from.

## What is added

**`evidence_tier` on the claim, 0–3:**

| tier | ground |
|---|---|
| 0 | only schemas the author wrote or chose |
| 1 | controlled real schemas, chosen by the author |
| 2 | foreign schemas with owner-confirmed findings |
| 3 | as tier 2, with a blind evaluation |

**Support is computed, not declared.** The verifier derives the highest supportable tier from the inventory: a
catalogue source supports 1; `foreign_validation` entries with `owner_confirmed: true` support 2; a
`blind_evaluation: true` among those supports 3. A declared tier above the supported one is refused
(`EVIDENCE_TIER_UNSUPPORTED`) — the claim does not get to assert its own evidential standing.

**The level is capped by the tier.** `PROVEN` at tier 0 or 1 is refused; `SCOPED_ASSURANCE` needs tier ≥ 1.

**`NC-11`** — "that these numbers generalise beyond the schemas actually validated" — is now required at every
level above the floor. A claim on fixtures cannot silently read as a claim on the world.

## Run

```
T24  tier 3 with no foreign validation   -> EVIDENCE_TIER_UNSUPPORTED
T25  PROVEN at tier 0                    -> CLAIM_EXCEEDS_EVIDENCE (evidence_tier)
T1   correct claim at tier 1             -> SCOPED_ASSURANCE, no errors
scenarios passed: 25/25
```

The earlier scenarios had to start declaring a tier. That is the intended effect: the field is not decorative, and
a claim that omits it lands on tier 0 and is capped.

## What this does not do

- **It does not grant a tier.** `foreign_validation` is a record the analyst writes; a dishonest tier-2 entry
  ("owner confirmed") is only as good as the owner. The check makes the assertion **visible and specific**, which is
  what a reviewer asked for, not true by construction.
- **It does not measure generalisability.** Tier 2 with one schema is still one schema; `NC-11` says the numbers do
  not generalise, and the tier records only what was validated.
- **It does not change the current state.** Everything measured here is tier 1 — Pagila is a sample database, and
  one review was right that it is not a production schema. The product half stays at zero until an owner confirms a
  finding.
