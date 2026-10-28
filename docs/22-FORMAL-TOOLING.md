# Formal-verification tooling worth adopting — assessment, 2026-10-28

The job-postings stream of the Lean Zulip is mostly positions, but it is a good index of **who is building
what**: a posting names the tool, the team and the verification target, which is more than a paper abstract
does. Reading it alongside the current tooling landscape gives three candidates that would change how this
repository argues, and several that would not.

## What the stream actually points at

| appeared in the stream | what it is | relevance here |
|---|---|---|
| Cryspen (three separate postings: compiler, proof engineer, verification) | **hax** — Rust → F\*/Coq/Lean/ProVerif, now at [`pereq-dev/hax`](https://github.com/pereq-dev/hax); plus libcrux, formally verified crypto | high **if** the gate is ever written in Rust |
| "Consultants to work on **Aeneas**" | Rust → Lean/Coq/F\* translation from Inria | same, and it targets Lean directly |
| Lean FRO postings (tooling, release notes) | the ecosystem's own infrastructure | signals maturity, not a tool to adopt |
| "Lean for Program Verification with **MLIR**" | Lean as a verification layer over a compiler IR | interesting but heavy |
| Google Summer of Code: **JSON Schema + Lean** | schema-to-type generation and proof obligations | directly usable, see below |
| Axiom Math, Cajal, Harmonic, Axiomatic AI, Succinct, Reilabs | companies hiring proof engineers | where an external reviewer could come from |
| Cardano/IOG **Blaster** + Lean 4 formalisations | end-to-end automated verification for smart contracts | the closest product analogue to what this repository claims |
| `AXLE` — cloud Lean 4 service ([arXiv 2606.26442](https://arxiv.org/pdf/2606.26442v1)) | remote proof checking and extraction at scale | removes the "no local toolchain" objection |
| [FVjobs](https://github.com/typetheoryforall/FVjobs) | job board for formal verification, maintained with Type Theory Forall | where to look for the human reviewer `M7` needs |

## Three adoptions, ranked by value per week

### 1. Formalise the verdict algebra in Lean 4 — the one worth doing first

Everything the gate decides is arithmetic over a handful of definitions: distinct paths, a floor per level,
coverage as a ratio, a clamp to the claim, and a set of exclusion rules. Thirty-four adversarial breaks landed
in exactly this arithmetic — a floor keyed to the wrong string, a denominator counting labels, a `min` where a
`max` belonged, `NaN` clearing a comparison.

Those are theorems, not tests. In Lean the statements are short:

```lean
-- verdict never exceeds the claim
theorem clamp_le_claim (computed claimed : Level) :
    min computed claimed ≤ claimed

-- a floor is monotone: more distinct paths never lowers the level
theorem floor_monotone {a b : Nat} (h : a ≤ b) :
    levelOf a ≤ levelOf b

-- the arithmetic is total: for any finite inputs the comparison is decidable
theorem nan_free (x : Rat) : ¬ (x < 0.15 ∧ x ≠ x)
```

The value is not the proofs — those are easy. The value is that **the definition becomes a single artifact**
that a reviewer, or another implementation, can be checked against, instead of a Python function whose meaning
lives in forty regression cases. The differential with the third-party verifier is the same idea with a
program; this is the same idea with a proof.

Cost: a day for the arithmetic, two for the coverage semantics. Risk: low, because the model is small and the
code stays the reference implementation.

### 2. Generate the schema obligations instead of testing them

We have had seven tracebacks on shapes the published schema said were legal, and a schema that did not parse
at all. The GoSC project above does the obvious thing: turn the JSON Schema into types, and prove (or at least
type-check) that the verifier is total on schema-valid input. Even without Lean, `pydantic`-free structural
validation generated from the schema would have caught every one of those seven.

Recommendation: derive the validator from `schemas/*.json` mechanically, and keep the hand-written shape checks
only for what the schema cannot express (cross-field rules).

### 3. Keep hax/Aeneas in reserve, with a trigger

If the gate is ever ported to Rust for speed or for embedding, then hax or Aeneas gives a path from the Rust
code to Lean/F\* proofs without rewriting. Not now: there is no Rust core, and adopting a translation toolchain
before there is code to translate is how a project spends a month on infrastructure it never uses.

**Trigger to revisit:** the first time `fg_verify` needs to run inside another program's process (an SDK, a
service), because that is when the Python implementation stops being obviously safe to depend on.

## What none of this fixes

A proof about our definitions says the arithmetic cannot be gamed **given the inputs**. It says nothing about
whether the inventory is complete (`NC-01`) or true (`ADR-0010`). The ceiling does not move: a liar's document
still only has to contradict itself. Formal verification makes the *consistency* half airtight; the *soundness*
half still needs the external anchor nobody has agreed to provide.

That distinction is worth keeping in the same sentence whenever a proof is mentioned, because "formally
verified" is exactly the phrase a buyer will over-read.

## Next step if this is accepted

A Lean 4 file under `formal/` with the coverage algebra, the verdict ladder and the clamp theorem, checked by
`lake build` in CI when a Lean toolchain is present and skipped honestly when it is not. The card would state,
before the run, that success means three named theorems and that failure to install the toolchain is recorded
as `not run`, never as `passed`.
