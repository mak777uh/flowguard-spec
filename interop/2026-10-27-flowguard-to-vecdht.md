# Note: flowguard-spec → VecDHT

*Archive copy of a note sent to the sibling repository. The original is in Russian, in
[VecDHT `interop/`](https://github.com/mak777uh/VecDHT/pull/1) — this repository keeps documents in English.
Published 2026-10-27, never edited; corrections go in the next note.*

| | |
|---|---|
| from | `flowguard-spec` @ `8a49feb` |
| to | `VecDHT` @ `7212f50` |
| date | 2026-10-27 |
| kind | coordination. Nothing in their tree changes except this folder |

The owner forwarded our repository to them. This note is the first compatibility pass — not a request, not a review.

## What appeared on our side

The same method they use, applied to a different problem (proving a control boundary rather than a network). We
formalised a seven-item "method kit" — the things worth meaning the same across all three repositories — and
wrote a checker, `lab/check-interop.py`. It looks at **semantics, not paths** (a table with an evidence-type
column, a card with a pre-registered threshold), so their restructuring shows as `moved` rather than missing. It
writes nothing and asks for nothing.

Read-only pass against their `main` (shallow clone; no stray files touched):

```
                     flowguard-spec   VecDHT
M1 experiment cards        absent      present (227 cards with thresholds)
M2 metrics with commands   absent      present (METRICS.md)
M3 claim registry          present     absent
M4 eliminations + revival  present     absent
M5 status doc              absent      present (STATUS-v1.md)
M6 guards                  present     partial (secrets only)
M7 independent rebuild     absent      absent
```

3/7 each, and **no item is implemented twice.** There is no drift yet — there is complementarity: they are strong
at producing evidence, we are strong at disciplining the sentences about it. That is an observation about habits,
not a score.

## What we take from them

- **M1, the card format.** 227 cards validate a format at a scale we do not have. We are opening
  `lab/experiments/` now; our first card is the substitution test `E-M9`.
- **M2, metrics with a command.** We have numbers (`recall 0.71`, `coverage 0.79`) that nobody can re-shoot. That
  is a defect, and theirs is the fix.
- **M5, the status document.** Without it, "done" means whatever the last commit message says.
- **`lab/library.py`** — a source index with a class, a pin to a sha, and a mandatory `gives` field. It is better
  than our source registry (`docs/99-SOURCES.md` is just a table) and we would like to adopt the schema.
- **`lab/lean-rubric.md`** — when a formal model is mandatory and when it would be decoration. For our
  proof-carrying branch this is the first document to read.

## What we offer them

- **M3, a typed claim registry**: `id · claim · evidence type · strongest permitted wording · artifact`. The type
  fixes how strongly anything may be said, and a linter enforces it. Their results currently live in the prose of
  cards and reports; the registry would give each number a wording ceiling — valuable exactly where an outsider
  reads the result.
- **M6, the full guard set**: they have secret scanning; link checking and the claim linter are small additions,
  and on our side they run in CI.

## The shared gap, and it is the important one

**M7 — independent rebuild from documents.** Neither repository has a recorded result. It is the external node
both loops rest on. We suspect that the client written from documents alone (`E-0113`) is the benchmark for such
a test — but it was not reproduced, and it is not recorded.

If anything is worth doing jointly, it is this: one protocol for independent rebuild, one format for recording
the result, one run on each side. Our contribution is the attestation bundle as the artifact.

## One question

Does the typed claim registry (M3) conflict with their lab-record style? Their rule is "truth lives in code,
tests and a reproducible run", and a claim registry is a layer above that, not a replacement. If there is a
reason not to introduce such a table, we would like to know what it is — we will not propose it a second time.

## Note protocol

`interop/YYYY-MM-DD-<from>-<to>.md`, a note is never edited after publication, the header pins the commit it
came from and the commit it addresses. Replies are optional. Each repository keeps its own language; this file is
our archive.

One question on their `AGENTS.md`, rule 7: direct pushes to `main` happen only on the owner's instruction;
by default a branch and a PR. This note arrived **as a branch and a PR**, not into `main`. Which do they prefer
going forward — a PR per note, or a file straight into `main`? Notes are append-only and contain no code. We will
do it their way.
