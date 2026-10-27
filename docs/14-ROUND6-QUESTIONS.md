# Round 6 — questions, and an analysis of how we have been working

**Date:** 2026-10-27. **State:** 39 files, six review cycles, ~150 claims and eliminations, **zero executable
artifacts**.

This pack is different from the previous five. Those asked "what is wrong with the design". This one asks
"what is wrong with the way we are building it, and what should we build first" — because after six cycles the
binding constraint is no longer the design.

---

## Part 1. Where we actually are

| Dimension | Count | Honest reading |
|---|---|---|
| Documents of specification and method | 22 | thorough |
| Claims with an evidence type | 18 | typed, none measured |
| Eliminated positions with revival conditions | 19 | the most useful artifact in the repository |
| External review cycles | 6, four to five independent reviews each | produced objections, not code |
| Instruments that run in CI | 4 (secrets, links, claims, interop) | these work and have caught real defects |
| Measurements produced by this repository | **0** | every number is a citation |
| Lines of executable product code | **0** | no verifier, no bundle, no invariant, no attack harness |

Kit conformance against our own seven-item kit: **4/7**. M1 (experiment cards), M2 (metrics with commands) and
M7 (independent rebuild) are absent. The status document says this plainly.

**The single largest fact about this project is the last row of that table.** Everything else is preparation.

## Part 2. What the development method got right

1. **Typed claims with a wording ceiling.** Enforced by a linter; the linter has already blocked two bad pushes.
   This is the one mechanism that transferred to a sibling repository within a day.
2. **Eliminations with revival conditions.** Made review rounds cost something: re-asserting a killed position
   now requires addressing the evidence that killed it.
3. **Separating the instrument from its own audit.** Our interop checker was wrong three times (M1 double-count,
   M6 blind, M7 counting a mention as a run) and each time the error was found by running it, not by reading it.
4. **A sibling repository as an external node.** Its review produced three factual corrections to our numbers and
   two format columns we did not have (`not_claimed`, `snapshot`). That is more than any prose review achieved.

## Part 3. What the method got wrong — five findings

**F1. The method optimises the axis that is not binding.** The lab loop (hypothesis → preregistered experiment →
result → one ADR) is a discipline for producing *evidence*. This project has no evidence to produce yet: it has
nothing executable. Six cycles of method refinement ran on an empty product. A method that cannot notice "we have
written 22 documents and no code" is missing a counter — and the counter existed in the sibling repository all
along (`INVENTORY.md`, generated, with a rule that the instrument exits non-zero if a printed number cannot be
computed from the tree).

**F2. Review cycles became the product.** Each cycle was real work and each produced a genuine improvement, but
the loop can run forever at constant apparent progress because prose has no completion criterion. The code path
has one: it compiles or it does not.

**F3. The agent-development plan is entirely untested.** The plan says agents write the code, tests are written
by a different agent that never sees the implementation, `tests/` is read-only for the implementer, and any
weakened assertion in a diff is an automatic reject. All four are reasonable, none has been executed once. The
risk is not syntax; it is an agent producing a plausible implementation of a misread paragraph, with tests that
pass because they test the misreading.

**F4. The specification has grown faster than the ability to check it.** 22 documents, cross-referenced, with
claims referencing artifacts that do not exist. The registry says "referencing a missing artifact is the to-do
list, not a lie" — true, but a to-do list of 16 items in a 22-document tree is also a signal about scope.

**F5. The external consumer (M8) is still unmeasured, and it is the proposition's premise.** The product asserts
that a verifiable attestation is worth paying for because someone downstream must act on it. That someone has
never been named, asked, or quoted. If nobody acts, the entire ladder — `PROVEN`, coverage, wording ceilings —
is instrumentation with excellent manners.

## Part 4. Questions for this round

Each question states what would change in our plan depending on the answer. **An answer with no number, no named
practice and no artifact is not useful this time** — we have enough opinions; we are short of things that can be
checked.

### Q1. The build order — what would you cut?

We intend to build, in this order: (1) an offline verifier for a bundle format in a browser tab, (2) a
substitution test that swaps code, build, config and identity while keeping signatures valid, (3) a real
archive of the claim registry on Arweave.

We estimate: 1 day for the bundle format, 3 for the verifier, 3 for the substitution test.

**What we need:** which of the three you would cut or reorder, and what you would put first instead — with the
reason in terms of what it *proves* that the other two do not. If your answer is "build the verifier", say what
the verifier must do that a bundle plus a shell script cannot.

**What changes:** if the answer is "none of these proves anything until a stranger uses it", the plan becomes
one pilot with one consumer, and the code becomes its by-product.

### Q2. Selling a measured, not proved, guarantee — is that a product?

Our honest best level for legacy systems is `ENFORCED_TESTED(R)` with a coverage scalar of about 0.79 and a
measured detector recall of about 0.71. `PROVEN` requires coverage 1.0 and is not available for any real
application.

**What we need:** a named class of buyer who pays for "enforced and measured at recall 0.71", or a statement
that no such buyer exists and what the minimum honest level would be for one to exist. Concrete procurement
language would be ideal: what a contract would have to say for this to be the thing it buys.

**What changes:** if no buyer exists below `PROVEN`, the product narrows to the small systems where completeness
is provable, and the legacy branch becomes a service, not a guarantee.

### Q3. What breaks when an agent implements a formal specification?

We assume the failure is "plausible implementation of a misread paragraph, with tests that pass because they
test the misreading".

**What we need:** the failure modes you have actually seen when a coding agent implements a specification or a
formal model — not the ones you expect. For each: the cheapest gate that catches it, and whether that gate is
mechanical or requires a human. If you have shipped this way, say what fraction of defects were caught by tests
written independently versus by reading the diff.

**What changes:** if the dominant failure is misreading, the plan invests in a different artifact — a
machine-checkable conformance suite derived from the spec, not tests written by another agent from the same
spec.

### Q4. The claim table — eight columns, and what it does not buy

We adopted: `claim_id · sentence · instrument · evidence_type · strongest_wording · not_claimed · artifact ·
snapshot`, with `strongest_wording` derived mechanically from `evidence_type` and a linter failing on mismatch.

**What we need:** what this construction still cannot catch. Name a false statement that passes all eight
columns. If the answer is "a claim whose instrument is itself wrong", say how a reader is supposed to notice,
and whether `snapshot` helps or merely documents the error.

**What changes:** if the residual hole is instrument correctness, the next artifact is not a registry but an
instrument audit protocol — and our own checker's three self-caught errors become the case study.

### Q5. The method itself — what would make you abandon it?

Our method: spec first, review cycles with independent models, typed claims, eliminations, a sibling repository
as external node, and development by coding agents under pre-registered thresholds.

**What we need:** the evidence that would make you say "this way of working will not produce a product", and how
many days of no measurable output should trigger it. Give a number. We have spent six cycles and produced no
measurement; tell us at what point that stops being diligence.

**What changes:** this is the question that can kill the project, and it is asked deliberately.

### Q6. The one question we have not asked

Across six cycles the reviewers' questions converged on design, pricing, formal methods and agent workflows.
Name the question we still are not asking — the one you would ask if you had one and we had to answer it in
public.

**What changes:** everything, potentially. This is the cheapest way to find the blind spot.

---

## Part 5. How to run this round

Give the model, in this order:

1. `docs/FLOWGUARD-MASTER-v2.md` — the design, whole.
2. `docs/STATUS-v0.md` — what exists and what does not, including the section on what it does not claim.
3. `docs/CLAIMS.md` — the typed registry.
4. `docs/95-CLOSED-LOOP.md` — the loop and its two brakes.
5. `docs/96-INTEROP.md` + `interop/2026-10-27-flowguard-to-vecdht-4.md` — the sibling channel and what it
   corrected.
6. This file.

Ask for answers per question, and explicitly for a table where each answer carries: `answer · evidence or named
practice · what it would change · confidence`. Discard answers that are only the first column.

## Part 6. What we will do with the answers

- Any answer that names a buyer, a procurement practice, or a measured failure mode becomes an `E-` card before
  it becomes a plan.
- Any answer that says the plan is wrong gets an ADR, not a vote — including if it contradicts this file.
- Q5 is binding: if it produces a date, that date goes into `STATUS-v0.md` as the review point for the method,
  and the method is judged by whether a measurement exists by then.
