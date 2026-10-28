# Advisor input, 2026-10-28 — five models, not owner decisions

Five external models were asked the same eight questions. Their answers were sent as one message. **None of it
is an owner decision**, and this file records it as advice: what they agree on, where they split, and what
therefore still needs the owner.

Treating their answers as decisions would be the exact failure this repository is built to refuse — a
document about a decision substituted for the decision.

## Where all five agree

| item | advice | status in the repository |
|---|---|---|
| Q1 real schema | synthetic evidence is spent; public schemas are useful but not proof of production fit | already the position: five public schemas measured, `E-M37` records that GitLab's write logic is mostly outside the database |
| Q2 consumer | the product thesis cannot be confirmed internally; a named human is needed | unchanged: product half 0%, `P2` zero |
| Q5 Nosana | ignore | closed, no action |
| ceiling "a liar's document contradicts itself" | acceptable for a first product **only** if every surface says self-consistency / provenance, never truth | already enforced by `NC-01`…`NC-11`; wording check is in `docs/CLAIMS.md` |
| external attestation | a gate for reliance / T3, not a prerequisite for the evidence tool | matches `docs/READINESS.md` T3 definition |

## Where they split — and why I did not pick for you

### Q3 — risk acceptance

Two of the five said "Option 1 now, no signature, no reliance". Three said "Option 2, signature with a reliance
scope". One of those three added that Option 3 needs a legal entity, insurance and a cap.

This is a money-and-liability decision and it is yours. **Nothing in the repository changed**: no artifact
outside `fixtures/` carries an acceptance, `P3` stays zero, and no public surface offers reliance.

### The NC dictionary

Two said "embed the full text so a verifier works offline forever". Two said "embed only a version and a
content hash, because full text bloats the artifact". One said "embed both, hash for drift".

The difference is real: with text, a stranger can read what was accepted without a second document; with a
hash, the stranger must obtain the file and can only prove it matches. **Not implemented either way** — see
below.

### The signature envelope

Three proposals, two of which I implemented and then **reverted**, because a format change invalidates issued
artifacts and the owner's standing instruction is to ask first:

1. keep `ADR-0015` (scope outside the signature, checked separately) — cheapest, weakest;
2. add a second signature over `address + role digest` — rejected by another model as an anti-pattern that
   complicates verification;
3. one signature over `sha256(role_digest ‖ address ‖ scope)` — strictly better than (1), no exception to
   "the signature covers everything".

I implemented (3) as `ADR-0016` and then put it back behind a flag: `create --envelope v2`. The default remains
`v1`, the sample bundle is `fg-bundle/1` at address `27a4c397…`, and `ADR-0016` is marked **proposed**. The code
and its tests exist so that adopting it is a decision, not a project.

## What is still the owner's to decide

1. **Q3** — whether an acceptance may be offered at all, and who is entitled to sign it.
2. **NC dictionary** — full text inside the bundle, or a hash plus a published immutable document.
3. **Signature envelope** — adopt `ADR-0016` (one signature, scope included) and accept that the sample
   address changes, or keep `ADR-0015`.
4. **Q4** — publish Part 2 of the article or leave it drafted.

## What I do while these wait

- Engineer work continues on everything that cannot create a commercial or liability claim.
- `db_logic_density` → incident-probability mapping is prepared as a **draft**, because an underwriter
  conversation was described but no conversation has happened and no name was given.
- No artifact is issued, no acceptance is offered, no product claim appears on any surface.
