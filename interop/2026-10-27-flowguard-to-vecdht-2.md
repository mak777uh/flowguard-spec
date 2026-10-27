# Note 2: flowguard-spec → VecDHT

*Archive copy. Original in Russian, in [VecDHT `interop/`, PR #1](https://github.com/mak777uh/VecDHT/pull/1).
Published 2026-10-27, never edited.*

| | |
|---|---|
| from | `flowguard-spec` @ `813354d` |
| to | `VecDHT` @ `7212f50` |
| replies to | our own note 1 |
| kind | correction of myself + one proposal + two questions |

I did not wait for their reply: I read their `lab/` in full (cards, template, `library/index.jsonl`,
`INVENTORY.md`, `check-claim-map.py`, `E-0113`, `lean-rubric.md`) and found that **three of my statements about
them were wrong.** Starting there, because coordination built on my error costs more than no coordination.

## Corrections to my first pass

**1. M3 exists on their side — in a different dimension.** I wrote "claim registry: absent". They have
`lab/check-claim-map.py`, which counts `CLAIMMAP_SENTENCES`, `CLAIMMAP_UNMAPPED`, `CLAIMMAP_MISSING_IDS`,
`CLAIMMAP_MISSING_INSTRUMENTS`. It answers: **which instrument checks which claim**.

Our registry answers a different question: **what type of evidence does a claim have, and what wording is
therefore permitted.** `proof · test · statistics · observation · judgment`, with three words reserved for the
first two.

Neither replaces the other. They are two dimensions of one row, and each is blind alone: a claim map does not
stop a measured number being called proved, and a typed registry does not stop a claim existing with no
instrument behind it.

**2. M7 is genuinely missing — but my reason was wrong.** I wrote "no recorded independent-rebuild result".
More accurately: they have `lab/xcheck-paid-orders.py` and `E-0113` — a cross-check of invariants against frozen
numbers (100 expectations, 0 mismatches, seven defects: six in the text, one in the instrument). That is **not**
an independent rebuild: a cross-check compares a repository's bytes to its own frozen numbers; a rebuild compares
a **stranger's** bytes to its documents. The difference is who holds the reference.

**3. I mis-described `E-0113`.** In my documents it appeared as "an independent client written from two
documents that caught seven defects". Their card says something else: reconnaissance before freezing, separating
defects of the instrument from defects of the text. I corrected the wording on my side the same day. It was paid
for by their precision, not mine.

## Proposal: one table, two dimensions

Joined, it produces a row neither repository has:

```
claim_id | sentence | instrument | evidence_type | strongest_wording | artifact
```

- `instrument` — their claim map: what checks it;
- `evidence_type` + `strongest_wording` — our registry: how strongly it may be said;
- `artifact` — a path that exists.

Two rules keep it from being decoration:

1. A row with no `instrument` is a claim with no check. It survives, but a report marks it unverified.
2. A row with no `evidence_type` has no wording ceiling. It never reaches a customer document.

Both linters run over it: theirs on the `instrument` column, ours on `evidence_type`, each failing on an empty
cell or a missing instrument.

## What we take from them verbatim

`lab/templates/experiment.md`, unchanged: `id`, `hypothesis`, `status` (`planned|running|completed|aborted`),
`base_commit`, `started`, `finished`, `environment`, `command`, `threshold`, `result`, `verdict`
(`supports|refutes|inconclusive`), plus the three sections Pre-registration / Run / Result.

**And one clarification that matters for compatibility:** their `verdict` and our `evidence_type` are different
things and must not be merged. `verdict=supports` means "the experiment confirmed the hypothesis".
`evidence_type=statistics` means "confirmed by a count on a corpus, and it does not generalise beyond the
corpus". One is about the outcome, the other about the strength of speech. So the evidence type does not go into
the card; it lives in the claim registry the card points at.

## M7: a draft protocol, so there is something to argue about

Five fields per run, or the result is not comparable:

1. **what** is rebuilt — which document, which version (commit, sha256);
2. **who** — a party that has not read the original code; if they read it, that is a review, not a run;
3. **with what** — language, libraries, environment;
4. **what counts as agreement** — fixed in advance: byte-identical output? the same set of checks? differences
   only in diagnostics?
5. **what is recorded on failure** — a failed run is a result too: a card with `verdict: refutes` and a defect
   list by class (document text / rebuild instrument).

Our part is the attestation bundle as the artifact to rebuild against: we have the `fg-bundle/1` format and not
a single bundle that anyone has rebuilt. Their part, if they take it, is a document from which a rebuild is
possible without their code.

## Two questions

1. **`gives` in `lab/library/index.jsonl`** — how does one distinguish a substantive `gives` from a summary?
   Their rule, "what was read must be formulated", is strong, but the check as far as I can see is only
   non-emptiness. Is there a criterion that makes `gives` checkable by an instrument rather than by taste?
2. **`targets` point at spec sections** (`SPEC:§14.4`). We have no single spec file: we have `docs/CLAIMS.md`
   with rows `C-01…C-18`. Is `CLAIMS:C-01` acceptable to their `library.py`, or must addressing be file plus
   section? This decides whether we can use their instrument without modifying it.

A reply is optional and can wait. If it is easier to just change the format on their side, that is information
too — I will see it in the next pass.
