# Final assessment — what this repository reached, and what it did not

Generated for the closing rounds of a continuous session. Every number below comes from a tool in this
repository; the command is named beside it.

## The four numbered objectives

### 1. A call-graph source of attribution, so coverage stopped being zero

Done, and measured on real schemas. `enumerators/pgcalls/` resolves callers through `pg_proc`/`pg_trigger`
identities to depth 8 (`attribution.sql`: `WHERE c.depth < 8`). On the fixture it attributes 2 of 2
control-point callers with 0 false attributions out of 9 decoys (`lab/e-m13-run.py`); coverage on the
fixture is 0.111 of 18 paths, where before there was no attribution at all.

### 2. The bundle format and the substitution test (E-M9)

Done, and the substitution test is the strongest artifact here. `E-M9` was a **refutation** at 3 of 6 and
is published unchanged; the repair moved the trust anchors outside the bundle; the re-run is 6 of 6.
The format has since changed twice under pressure from four independent rebuilders, each of which
reproduced the address and found defects in the *description* rather than in the artifact.

### 3. The instrument mutation corpus (E-M10)

Done: 102 generated mutants across declared classes, all named, all caught by the declared checks.

### 4. Independent rebuild (M7) with a bundle present

Done three times, by agents that never saw the source. The current artifact (`27a4c397…`) was rebuilt from
the page alone; the fourth agent went further and **wrote a conforming verifier** from the page, caught
five tamperings it made itself, and later a differential over 44 mutations found one real hole in ours
(an undeclared object in `objects/` verified green).

The honest limit, stated in `docs/STATUS-v0.md`: `M7` is satisfied by **AI agents of the same model
family**, not by a human stranger. Readiness P1 therefore still scores zero — deliberately.

## The engine, as measured

| what | value | command |
|---|---|---|
| readiness, engine half | **100%** | `python tools/fg_readiness.py` |
| readiness, product half | **0%** | same |
| method kit conformance | **7 / 7** | `python lab/check-interop.py` |
| repository and method audit | **12 / 12** | `python tools/fg_audit.py` |
| guard self-tests | **8 controls** | `bash lab/selftest-guards.sh` |
| experiment cards | **49** (46 supports, 3 refutes) | `ls lab/experiments` |
| metric rows, each with a command | **79** | `python lab/check-metric-digests.py --cards` |
| verifier acceptance scenarios | **25 / 25** | `python lab/e-m12-run.py` |
| adversarial breaks found and closed | **11 + 14 + 9 = 34** | `python lab/e-m42-run.py`, `the E-M50 cases` cases |
| differential mutations, two implementations | **44**, 1 known divergence | `python lab/e-m57-run.py` |

## What the product half is zero for

Four things, and none of them is code:

1. **No third party has rebuilt the artifact.** Three AI agents did; the readiness check refuses to count
   them, and that refusal is the honest part.
2. **No schema owner has confirmed or denied a finding.** Every `evidence_tier` in this repository is 1
   or 2 by the author's choice; `fg_confirm.py` exists and has never been used by anyone else.
3. **Nobody has signed a risk acceptance outside `fixtures/`.**
4. **No consumer has documented a decision that changes.**

`docs/QUESTIONS-FOR-OWNER.md` holds the three questions that need a human: whether an acceptance needs a
stronger cryptographic binding than `ADR-0015` gives, whether the `NC-01…NC-11` vocabulary should travel
inside the artifact, and whether the design ceiling — *a liar's document contradicts itself* — is
acceptable for a first product.

## The design ceiling, stated plainly

Three adversarial rounds, 34 breaks, all closed, and every one was the same shape: **a gate satisfied by a
field the claimant writes.** The repairs made lying harder and more visible; none made it impossible, and
`NC-01`…`NC-11` say so inside every claim.

The ceiling is therefore not "a liar cannot pass" but "a liar's document contradicts itself, and a
careful reader can see where". That is worth something. It is not the same as a guarantee, and this
repository does not call it one.

## What is genuinely unfinished

- `docs/STATUS-v0.md` is generated now, but three older documents (`docs/FLOWGUARD-MASTER-v2.md`,
  `docs/40-FLOW-GUARANTEE.md`, `docs/20-ROUND2-DECISIONS.md`) still contain the reserved words that
  `docs/CLAIMS.md` says are grep-enforced — the linter scans `docs/` and reports them, and the claims
  registry does not cover them.
- `E-M47`'s report reconciliation compares the report's coverage with the inventory's path coverage; a
  report that omits `analysed_paths` entirely still passes without the cross-check.
- The bundle's `policy_digest` field is a reference to a document no verifier can fetch; it is documented
  as uncheckable, which is honest but is still a field that looks like evidence.
- One known divergence with the third-party verifier (`F-2-1`: a truncated `.pub` is accepted by them,
  refused by us). Recorded, not resolved, because resolving it would mean copying an error.

## The sentence worth keeping

From the third adversarial round, and it is the most accurate description of this project anyone has
written:

> everything the tool "recomputes" is recomputed from the claimant's document … the honest ceiling of this
> design is not "a liar cannot pass" but "a liar's document contradicts itself".

That sentence is in `docs/CLAIMS.md`. It is the reason the product half is zero, and it is the reason the
engine half is worth something.

## Correction, 2026-10-29: what a consumer gets is checkability, not better answers

Two paired experiments (E-M73, E-M75) measured whether an agent given the inventory answers better than an
agent given the bare catalogue. Both refuted it: the bare-catalogue agent found the same bypasses, including the
one hidden behind a view grant and a SECURITY DEFINER function. The supported claim is smaller and belongs here
instead of the larger one:

> the artifact does not make a reader smarter; it makes the answer **checkable**, and it does not require the
> reader to be competent in Postgres semantics.

Anything in this document that reads as "a consumer answers better" should be read with that correction applied.
