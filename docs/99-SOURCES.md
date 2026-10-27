# SOURCES — where solutions come from

Before designing anything in this repository, check the sources below. A solution that already exists
somewhere is adapted, cited, and improved — not reinvented. A solution that was already rejected is logged in
[eliminations.md](eliminations.md) and needs new evidence to come back.

Rule: **adapt or cite, never silently copy.** If a pattern is taken from one of these sources, the file that
uses it says where it came from. If a source's approach is deliberately not used, that is a decision worth one
line in an ADR.

---

## S1 — VecDHT · [github.com/mak777uh/VecDHT](https://github.com/mak777uh/VecDHT)

The primary reference for **method**. A Rust research prototype built under the same constraints: one
developer, agents writing code, claims that must be checkable by a stranger.

What to take:

| Artifact there | What it solves here |
|---|---|
| `lab/hypotheses` + `lab/experiments` | the `E-` card format: hypothesis, pre-registered threshold, result, one ADR per finding |
| pre-registered thresholds | thresholds are fixed **before** the run, so a result cannot be re-fitted after seeing it |
| `docs/METRICS.md` | every number carries the command that produced it; counters are generated, not typed by hand |
| `docs/STATUS-v1.md` | honest status: what works, what is partial, what is a stub — written so a reviewer can falsify it |
| `AGENTS.md` | the rules an implementing agent must obey, including what it may not touch |
| bit-for-bit seed anchors | a change that shifts the reference run is caught in minutes, not in a review |
| independent client from documents alone (`E-0113`) | the external node for this project's loop: rebuild from documents, not from code |
| the "model ↔ code not instrumented" caveat | the same honesty we need for formal proofs: statements are about a model |

What **not** to take: its scaffolding and module layout are tuned to a P2P network; copying the tree wholesale
would import structure we do not need.

## S2 — Project Morphogenesis · [github.com/mak777uh/-](https://github.com/mak777uh/-)

The primary reference for **epistemics**: how a claim is worded relative to the evidence behind it.

| Artifact there | What it solves here |
|---|---|
| `manuscript/CLAIMS.md` + linter | the typed-claim registry: evidence kind fixes the strongest permitted wording |
| `docs/eliminations.md` | negative results as a first-class document, each with what would revive it |
| sensitivity arithmetic before launch | a test that cannot distinguish the effect it looks for is reported as "did not reach the effect", never as "no effect" |
| `sha256` on every figure | any number in a report can be traced to the file that produced it |
| "modified worlds are named" | never compare results across different configuration without saying so |
| "skipped in CI is never reported as proven" | the same rule, enforced by our own gates |

What **not** to take: the domain (cellular automata) and the manuscript culture; we publish specifications and
instrument output, not papers.

## S3 — our own review rounds

Six cycles of external review, four to five independent reviews each, answers kept in `docs/`. They are a
source of **objections**, not of solutions: when a design question comes up, check whether a reviewer already
answered it, and whether the answer was adopted or rejected.

## S4 — external prior art

Named because a claim about novelty is worthless without it: Anderson's reference monitor (1972), Goguen–Meseguer
noninterference, seL4, SLSA provenance, Sigstore/Rekor, in-toto, RFC 8785 canonicalization, the DARPA AI Cyber
Challenge results, Amazon automated reasoning, Certora/Halmos/Echidna for smart-contract invariants, the Rust
standard-library verification contest, Arweave and Nosana as infrastructure.

---

## How a task travels

1. **Check S1–S4** for an existing answer. Found → adapt, cite, improve.
2. **Not found** → write the hypothesis as an `E-` card with a threshold fixed before the run.
3. **Result** → one ADR if the spec or method changes; one `X-` entry if a position died.
4. **Nothing produced** → the turn is logged `no-delta` in the loop ledger, and that is recorded honestly.

Tasks may also be **parked in VecDHT as worked examples** when the task is about method rather than about this
product — that repository is the shared example corpus, and this one is the product. A method answer developed
here that generalises should be contributed back there, so the corpus stays the place where the pattern is
readable in isolation.

## Standing caution

Both S1 and S2 are stronger than this repository in one respect each: VecDHT has working code, Morphogenesis has
measured results. This project currently has neither. Citing them is therefore a **loan against future work**,
and the interest is paid by actually closing `E-M9` first. Until then no claim here may borrow their credibility.
