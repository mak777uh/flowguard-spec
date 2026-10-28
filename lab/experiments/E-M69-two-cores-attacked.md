---
id: E-M69
hypothesis: H-M69
status: completed
base_commit: "26c155c"
started: "2026-10-28T18:35:00+03:00"
finished: "2026-10-28T19:45:00+03:00"
environment: "Windows, four model families, two cores (Rust CLI and Python)"
command: "workflow with agent(prompt,{model}) over qwen3.8-flash, glm-5.3-flash, mimo-v2.6-flash, claude-haiku-5-5; then python lab/e-m69-run.py"
threshold: "Pre-registered: attackers are given BOTH cores and asked, in priority order, for a pair where the two return different verdicts, or a pair where both return a strong verdict without the evidence. Every case is reproduced locally before it is accepted. A divergence where one core is wrong is fixed in that core."
result: "Four real divergences, all found by other model families, all in the Rust core, all closed: an invented NC-77 code passed (the port checked only for missing codes, not for codes outside the vocabulary); a claim excluding a path its own inventory put in the core passed with PROVEN (no exclusions were examined at all); an inventory produced solely by the analysing agent reached PROVEN (independent_of_agent was never read); and coverage below the threshold did not cap (the port had no coverage-ratio floor). A fifth difference turned out to be a documented ambiguity resolved by the page: a covered-and-excluded contradiction makes the claim unanswerable, so both cores now answer INVALID. Then, from the PutnamBench agent's report, a rule neither core had: a claim whose covered set is empty is true for a trivial reason and cannot carry a level."
verdict: supports
---

# E-M69 — two cores attacked by four families, and a vacuity rule from an unrelated project

## The four divergences

All four had the same shape: **Rust said PROVEN, Python refused.** That is what a second implementation is for —
not to double-check the reasoning, but to catch the places where the reasoning was never ported.

| divergence | why Rust was wrong |
|---|---|
| an invented `NC-77` passed | the port checked which required codes were missing, never whether a declared code exists in the vocabulary |
| excluding a covered path passed | `claim.excluded` was not read at all |
| a self-analysed inventory reached PROVEN | `independent_of_agent` was never read |
| coverage below the threshold did not cap | no coverage-ratio floor |

The fix for the first is worth naming: the vocabulary is read from `docs/NOT-CLAIMED.md`, and the parser initially
matched backticks while the table writes `**NC-01**`. A parser that fails silently returns `None`, and a missing
check is indistinguishable from a passing one — the code compiled, the tests passed, and the hole stayed open.
It was found by running an invented code through the binary, not by reading the parser.

## The one that was a document question

A claim that excludes a path its own inventory attributes to the control point is a contradiction. The exclusion
table calls it `EXCLUSION_REASON_CONTRADICTION`, which caps a claim; the page also says a path cannot be both
covered and excluded, which makes the claim unanswerable. Both readings are defensible, and the two cores picked
different ones. Resolved on the page's stronger statement: `INVALID`, in both cores, with the reason written in
the code comment so the next reader does not re-litigate it.

## The rule from the PutnamBench agent

Its README says the harness owns the stopping rule — one problem was solved at step 5,105 after 3,423 refused
attempts to quit — and that the solved theorem's elaborated type must be character-identical to the frozen
statement, which defeats statement rewriting. Both ideas transfer:

- **the stopping rule**: my attackers may answer "no finding" after twenty minutes, and one of four did. That is
  indistinguishable from "did not look", and `docs/26-PUTNAM-AGENT.md` sets out the harness change.
- **statement rewriting**: a claimant chooses `declared_control_point`. Nothing stops them from choosing one
  nothing bypasses. `inventory_attestation` is the reserved answer and needs an outside party — the same open
  question as `ADR-0010`.
- **vacuity**, which is the rule added today: a claim whose covered set is empty is true for a trivial reason, so
  it cannot carry a level. Both cores now refuse it. This is the document-level analogue of a theorem that is
  provable because its hypothesis is unsatisfiable.

## What this does not do

- The attackers still cannot be trusted to have looked; that is the harness change in [docs/26](../docs/26-PUTNAM-AGENT.md), not a rule.
- The vacuity rule closes one triviality, not the family of them: a control point that is unreachable, a target
  table that was narrowed, and an exclusion that removes the only money path are all still open, and each needs
  its own line in a document before it can become a line in a checker.
