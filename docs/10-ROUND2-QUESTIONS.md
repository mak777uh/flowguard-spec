# 10. Second round: a question pack for running across models

> **How to use this.** There are two parts below. Part 1 is a ready-made prompt; paste it whole and identically into every model. Part 2 is how to consolidate the answers; do not show it to the models, otherwise they will start playing to the rubric.
> The second round differs from the first in that the models **do not design the architecture from scratch** but are obliged to make decisions about ours. Otherwise we get nine more essays and zero convergence.

---

# PART 1. PROMPT FOR THE MODELS (copy in full)

## Role and rules

You are not the author of the architecture. You are a reviewer who is obliged to **make decisions**. The architecture has already been assembled from nine independent proposals; your job is to stress-test it and close the open questions.

Hard rules for the answer:

1. **Forbidden** to answer "it depends on the context", "a balance is needed", "everything matters", "this is a complex question". If the choice genuinely depends on a condition, state the **condition in one line** and still pick the default branch.
2. **Forbidden** to propose a new architecture from scratch. The maximum is a targeted amendment to the proposed one.
3. The answer "I don't know" is **permitted and valued** — but then it is mandatory: how you would measure it and in how many days.
4. **Forbidden** to cite benchmarks or figures without a source. If the figure is your own estimate, write `[estimate]`. If you are not sure of a fact, do not cite it at all.
5. Each answer is **no more than 120 words**. The justification is shorter than the answer. Padding lowers the score.
6. Do not restate the question. Do not apologise. Do not summarise at the end.

## Context: what the product is

A service for automated security assessment and safe remediation. Inputs: a git repository, an archive, an SBOM, a container image, IaC, an API spec, and also — under a signed authorisation — a live target (URL/API). Output: a report with evidence and **several remediation options**, from a hotfix to migration onto a formally verified core, each with a passport: what it closes, what it breaks, what is proven, what remains, what it costs, how to roll it back.

The agent runs in a sandbox (Linux + harness: microVM, deny-all network, no secrets). For regulated domains (avionics, automotive, medicine, industry, payments) automatically checkable tools are connected: Lean 4, Dafny, Verus, Creusot, Kani, SPARK/Ada, Frama-C, TLA+.

## Context: what is already decided (you may contest it only with the argument "why this is wrong")

**Seven axioms:**

- **C1.** The agent proposes, a deterministic checker decides, a human signs. Everything called "verified" is produced by deterministic code, not by a model.
- **C2.** A finding without a reproducible artefact is a hypothesis, not a finding. In the report these are two different classes, never mixed in one list.
- **C3.** What is sold is a ladder of fixes, not a patch.
- **C4.** Formal methods are a narrow premium track for a separable critical core, not the basis of a mass-market product.
- **C5.** Isolation: a microVM per run, deny-all network, zero secrets in the sandbox.
- **C6.** Destructive action on production is forbidden; the scope is a signed manifest.
- **C7.** The contents of the repository or site are hostile data, not instructions to the agent.

**Three invariants (violation = sales stop):**

- **I1.** "Verified" = produced by deterministic code.
- **I2.** Everything shipped is replayed by a third party offline and yields the same result.
- **I3.** Every statement is bounded by an explicit negative scope (what was not tested).

**The technical core is the PoC contract.** A finding is described as `⟨F, A, T, O, V, S⟩`: environment fingerprint, preconditions, exact trigger, machine-checkable oracle over the observation, verdict function, signature. The `PROVEN` verdict requires triple control on K=10 fresh VMs: **C** (trigger without payload) — no effect; **T** (full trigger) — effect present; **N** (semantic mutation) — no effect. The oracle is sealed (the agent does not write the predicate), each VM is given a random canary nonce that the PoC is obliged to return. A fix is accepted only if the PoC goes dark, all mutations go dark, the regression is green, diff-fuzz shows no new signatures, and the perf budget is met.

**Remediation ladder:**

| R | Essence | What is proven |
|---|---|---|
| R0 | mitigation (WAF/flag/ACL/rotation) | the attack from the bundle does not pass |
| R1 | targeted patch | PoC goes dark + variant suite goes dark + regression |
| R2 | hardening + permanent detector (sanitisers, fuzzing) | no hits on the corpus over T CPU-hours |
| R3 | module refactoring | no UB on domain D + the attack class is unreachable |
| R4 | memory-safe rewrite | no-UB + contracts + equivalence to the old one on D |
| R5 | verified core | invariants + correctness + design properties + assumptions ledger |

**Our configuration (this is what you review):** first release V1 (offense-gated, repo-only, SaaS) in 8–10 weeks → V2 (root-cause graph, peer generation of R0–R3, verifier farm outside the agent's write-scope, Pareto front) in 4–6 months → V3 (certifiable change, on-prem, one property class) in 9–15 months. Default placement is hybrid (panel outside, runner in the client's VPC), from day one. Two parallel lanes in the report: Lane A (coverage, status `HYPOTHESIS`, not billed) and Lane B (proven, billed). Human signature — 100% PROVEN in v1, with a published `human_review_coverage` metric.

**Seven open divergences** (these are exactly what has to be closed): where the moat is in the first 12 months; offense-gated vs coverage-first; six ladder levels vs five; the real cost of a validated finding; how much human is in the loop; R5 — product or R&D; whether to sell the harness instead of findings.

## BLOCK A — Forced decisions (12)

Format of each answer: **letter + confidence 0–100 + why not the alternative (one phrase)**.

- **A1. What goes into the "findings" section?** (a) only `PROVEN`; (b) `PROVEN` + a separate "hypotheses" appendix; (c) a single list with confidence labels.
- **A2. Who signs the report in v1?** (a) our named assessor; (b) the client's engineer; (c) nobody, a platform statement.
- **A3. The first sellable input?** (a) repository/archive only; (b) repository + container/SBOM/IaC; (c) plus live URL/API.
- **A4. Where is the moat in the first 12 months?** (a) signature + artefact acceptance by an auditor; (b) the evidence plane (reproducibility); (c) the proof harness; (d) detection capability.
- **A5. The v1 pricing model?** (a) per scope; (b) per finding; (c) subscription to evidence freshness; (d) per fix.
- **A6. `human_review_coverage` in v1?** (a) 100%; (b) risk-based 30–50%; (c) 0% with disclosure.
- **A7. Default placement?** (a) SaaS; (b) hybrid: panel outside, runner in the client's VPC; (c) on-prem.
- **A8. Formal methods in v1?** (a) no; (b) one template case as a reference; (c) a full track.
- **A9. Live testing of a production target in v1?** (a) never; (b) read-only GET/HEAD only; (c) with approval and rate-limit.
- **A10. What to do with a PoC that did not reproduce at the client?** (a) outcome `NRE`, do not bill, publish with the reason; (b) discard silently; (c) hand over as a hypothesis.
- **A11. Who owns the specification for R5?** (a) us; (b) the client; (c) jointly, with a mandatory independent reviewer.
- **A12. The client demands the wording "no vulnerabilities were found" in the report.** (a) refuse the order; (b) provide it with explicit limitations alongside; (c) provide it as asked.

## BLOCK B — Numbers (10)

Format: **value + the method by which you would measure it + 1 line of assumptions**. If you do not know — "I don't know" + what you would measure it with and in how many days. Mark every number `[estimate]`.

- **B1.** Blended cost of one validated finding in v1 (repo-only, a mid-sized application, 100–200 kLOC).
- **B2.** p90 cost of a finding in the "dynamic PoC synthesis" class (a stateful application).
- **B3.** `time-to-first-validated`, p50 and p95.
- **B4.** The wall-clock limit per run beyond which the run is economically dead.
- **B5.** Target `repro rate` in the client's CI.
- **B6.** Target `fix-acceptance` (the share of patches accepted without semantic edits).
- **B7.** The price of S1: one web application, ≤50 endpoints.
- **B8.** Target gross margin for R1 and for R3.
- **B9.** The typical number of validated findings per S1 engagement — and why exactly that many.
- **B10.** The team and the time to the first paying client (person × months).

## BLOCK V — Analysis of our configuration (the main part)

- **V1.** **Five places where this configuration breaks fatally.** For each: the failure mechanism, the cheapest test that will detect it, and what exactly must be changed (one amendment). Not "risks" but concrete mechanisms.
- **V2.** **The three amendments that give the largest gain in quality per unit of effort.** For each: what we change, what it costs in person-weeks `[estimate]`, what we lose.
- **V3.** **One statement from C1–C7 or I1–I3 that you consider wrong.** Explain why it is wrong and what will happen if we hold on to it.

## BLOCK G — What to cut

**G1.** You have 8 weeks and 3 engineers. From the list below **cut seven items** and explain what will survive without them and what will die. Leave five.

`(1)` microVM sandbox · `(2)` PoC contract with triple control C/T/N · `(3)` sealed oracle · `(4)` canary nonce · `(5)` evidence plane with hash-chain · `(6)` offline replay kit · `(7)` live DAST by URL · `(8)` root-cause graph · `(9)` peer generation of R0–R5 variants · `(10)` verifier farm outside the agent's write-scope · `(11)` formal track · `(12)` named signatory / human gate.

Format: a list of the five kept + one sentence each on "why without this the product stops being sellable" + one each on "what we lose by cutting it".

## BLOCK D — Death prediction

**D1.** In how many months and from what mechanism will this product die, if the team does everything "right" according to this spec? Name **one** main mechanism, the month and the **early indicator** that is visible one month before death (metric + threshold).

## BLOCK E — What we forgot

**E1.** One question that is not in this pack but that we were obliged to ask. Formulate it and give your own answer.

---

# PART 2. HOW TO CONSOLIDATE THE ANSWERS (do not show to the models)

## 2.1. What counts as a strong answer

| Attribute | Strong | Weak |
|---|---|---|
| Form | letter + confidence + "why not the alternative" | a paragraph of reasoning with no choice |
| Numbers | value + measurement method + assumptions | a range "from and to" with no basis |
| Criticism | failure mechanism + cheap test | "it might be risky" |
| Not knowing | "I don't know" + a measurement plan | a plausible fabrication |
| Contesting axioms | the argument "why it is wrong" | "I would add one more layer" |

## 2.2. Summary table (fill in for each model)

| Question | Model 1 | Model 2 | Model 3 | Model 4 | Model 5 | Consensus | Spread |
|---|---|---|---|---|---|---|---|
| A1 | | | | | | | |
| A2 | | | | | | | |
| … | | | | | | | |

**Interpretation rules:**

- **4–5 of 5 agree → we adopt it as a decision**, even if it contradicts ours. That is the cheapest way to remove founder bias.
- **3/2 → we decide ourselves**, but record in the spec that this is contested, and assign a test.
- **A spread of 2/2/1 → the question is badly posed**, not "the models are stupid". Reformulate it or convert it into a measurable one (Block B).
- **All "I don't know" → the question requires data, not opinions.** It goes into the pilot, not the spec.

## 2.3. Red flags in answers (they disqualify the answer)

1. Gave numbers without a measurement method → strike out the number.
2. Proposed a new architecture instead of a decision → the answer to the question does not count.
3. Answered "it depends" with no condition → does not count.
4. Cited a benchmark without a source → verify it; if it does not hold up, mark it as a fabrication and **lower trust in the whole answer**.
5. In Block G left ≥9 components out of 12 → cannot cut scope, and their architectural judgements are less valuable.
6. In Block D predicted death "never" or "in 5 years" → failed to name a mechanism.

## 2.4. What to do with the result

| Outcome | Action |
|---|---|
| Consensus on A1–A12 | carry it into the spec as `DECIDED`, update `00-SYNTHESIS.md` §3 |
| Divergence on A | assign a cheap experiment (≤5 days) that distinguishes the options |
| Consensus on B | calibrate the economics model, replace `[estimate]` with the measured value after the pilot |
| V1 (five fatal places) | each becomes a prioritised task if it matched in ≥3 models |
| V3 (contested axiom) | if the argument is strong, we revise the axiom; this is the only legitimate way to touch it |
| G1 (the cut list) | the intersection of five models = the real scope of v1. The union = a planning failure |
| D1 (death prediction) | early indicators → into the dashboard, thresholds → into kill criteria |

## 2.5. One question worth asking after consolidation

If in ≥3 models the **same** death mechanism matches in Block D, that is not a hypothesis but a forecast. Then the only correct next step is not a third round of questions, but **a test for that mechanism within the first 30 days**, even at the cost of delaying the release.
