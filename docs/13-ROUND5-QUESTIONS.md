# 13. Fifth round: the last one before the full spec

> The task of this round is to close what is missing before a detailed spec can be written. Not philosophy, not "what if", but concrete artefacts: schemas, numbers, rules, boundaries.
> After the answers the **full spec** is written, and then come the critique cycles. That is why block 6 separately asks "what here is most likely wrong" — the spec will be designed for refutation, not for defence.

---

# PART 1. PROMPT (copy in full, do not change between runs)

## Role and rules

You are an engineer who brings the design to the state where "code and contract can be written". What is required from you is **artefacts, schemas and numbers**, not reasoning.

1. Answer = a finished artefact (schema, list, table, rule). Justification — one line, not a paragraph.
2. **No more than 150 words** per answer, except where a schema or table is explicitly required.
3. Decisions listed under "Already decided" are not revisited. Proposing new architectures is forbidden.
4. "Depends on context" is forbidden without a one-line condition.
5. If you do not know — `I don't know` + how you would check and in how many days.
6. Numbers — `[estimate]`. Schemas — in JSON/YAML/pseudocode, not in words.

## Already decided (not to be revisited)

**Product.** A guarantee on the protected flow: for flow F and policy P a mediator M is designated, it is proved that M implements P, and it is verified that within the closure Z there is no bypass path. Outside Z the guarantee does not hold.

**Legacy track.** 12 elements of Z · 8 fields of the act · 4 signatures (product owner, infra owner, security lead, verifier) · reissue within 3 business days · mediator + `Permit` as a signed Ed25519 token + PL/pgSQL trigger as the physical guarantee · hybrid placement (in-process for BOLA, single-writer for money) · 5 policies (35 person-days max) · 7 bypass paths · witness 12 person-days · mediator proof 24 person-days · pilot 45 days / 24 person-days.

**Crypto is in scope from day one.** Six domain-agnostic ports (`StateProvider`, `EnforcementPoint`, `ObservationChannel`, `Clock`, `Domain`, `Prover`), `subject.kind` in the bundle format, mandatory finality (`block` + `finality`, reorg → `INVALID`), 10 attacks instead of 7, a double grid R0–R5.

**Economics.** SKU: base analysis $2–5k (95% automation) → patches $5–10k → migration $25–45k → guarantee $48k + $12k/year; re-attestation 15 min.

**OSS.** The core is open for good (format, verifier, replay, policy DSL, reference mediator, attacks); what is closed is the service on top, not a fork.

**Death criterion.** Median `PROVEN` < 2 with a working witness plane → do not build the product.

---

## BLOCK 1 — Crypto: the first target and invariants (4)

**1.1.** Choose **one** contract class as the first target from: vault · streaming payments · escrow · token · staking · DEX pool · multisig. Criterion: provability of invariants × volume of money on the flow × code size (≤800 lines) × availability of a public repo. Format: `class | why | what we lose by deferring the rest`. `[choice]`

**1.2.** For the chosen class — **three invariants**, formally (a predicate over state and calls) that (a) actually catch the loss of money, (b) are provable within ≤12 person-days. Format: `ID | invariant in one line | which attack class it catches | why it is provable`. `[3 invariants]`

**1.3.** A method for enumerating **privileged paths** on-chain: list the minimal set of checks that yields a complete list of what can move funds (roles, ownership, upgrade proxy, `delegatecall`, `selfdestruct`, keeper, external calls). For each — how it is detected automatically. Format: table `path | how to find | tool | what it misses`. `[table]`

**1.4.** Finality rule: for Ethereum L1, for L2 and for the case "a reorg happened between the run and the signature" — how many confirmations count as final and what exactly `verify` does. Format: 4 rule lines + one line "what goes into the bundle". `[rules]`

---

## BLOCK 2 — Crypto: the act and signatures (2)

**2.1.** In legacy the act is signed by the product owner and the infra owner. On-chain there is no infrastructure owner. Who signs the act instead of them: the multisig signers, the auditor, us, the contract developer? Format: a list of signers with the subject of responsibility of each. `[list]`

**2.2.** The on-chain analogue of "revoking write credentials": `renounceOwnership`, `transferOwnership` to the multisig, timelock, signature threshold. Give the **minimal set of actions** after which it can be asserted that "there is no privileged path outside M". Format: 5 lines, each — what we do and what it closes. `[5 lines]`

---

## BLOCK 3 — Automatic payouts without people (3)

**3.1.** The condition for automatic release of escrow. What exactly is checked by machine so that the payout does not require a human? Format: a predicate in 5 lines + what happens on `INVALID` and `INCONCLUSIVE`. `[predicate]`

**3.2.** Dispute without an arbitrator: the mechanics. Who pays for an oracle error, how long the window lasts, what happens to what has already been paid out. Format: 5 lines + table `who | what they lose | on which outcome`. `[mechanics]`

**3.3.** Numbers: the cap on automatic payout, the size of the executor's bond, the length of the dispute window, the service fee. Format: 4 numbers with `[estimate]` and one line of justification for each. `[4 numbers]`

---

## BLOCK 4 — Formats (2)

**4.1.** The complete grammar of `flowguard.yml`: all fields, which are mandatory, which default, which are forbidden. Format: a YAML schema with comments on obligatoriness. `[schema]`

**4.2.** The schema of the attestation bundle: list the files and, for each, the mandatory fields. Format: a tree + table `file | mandatory fields | who signs`. `[schema]`

---

## BLOCK 5 — Service boundaries (3)

**5.1.** Five cases that **break** the automation of the base analysis (monorepo, polyglot, no IaC, no tests, generated code, a service without a database…). For each: how it is detected before the sale and what we do. Format: table `case | detector | decision (refusal / manual mode / surcharge)`. `[table]`

**5.2.** Protection against abuse of the free/cheap analysis: who pays for compute, how the flow is limited, what prevents uploading someone else's repositories. Format: 5 rules, each on one line. `[5 rules]`

**5.3.** How to prove the right to the analysis: the client uploads a repository or a contract address. What counts as proof of ownership for (a) a private repo, (b) a public repo without rights, (c) a contract on-chain. Format: 3 lines. `[3 lines]`

---

## BLOCK 6 — Resilience to criticism (2)

**6.1.** The three **strongest** buyer objections to this design, and an answer to each in 2 lines. Formulate the objections harshly, the way a sceptical CTO would. Format: 3 pairs `objection | answer`. `[3 pairs]`

**6.2.** What in the described design is **most likely wrong** and will break in reality? Give your own list of 3 items: the failure mechanism, on what horizon, and how it will be visible. Not "risks in general", but concretely. Format: 3 items × 3 lines. `[3 items]`

---

# PART 2. HOW TO CONSOLIDATE (do not show to the models)

## 2.1. What counts as a strong answer

| Question | Strong | Not counted |
|---|---|---|
| 1.1 | one class + what we lose | a list of 4 "important" |
| 1.2 | predicates, not words | "balance conservation invariant" without a formula |
| 1.3 | a table with "what it misses" | an enumeration without boundaries |
| 1.4 | 4 rules + bundle contents | "wait for finality" |
| 2.1 | signers with a subject | "multisig" |
| 3.1 | predicate + behaviour on `INVALID` | "if the check passed" |
| 4.1 | a schema with obligatoriness | a list of fields |
| 5.1 | detector + decision | "it can be difficult" |
| 6.1 | an objection that is unpleasant | soft objections |
| 6.2 | mechanism + horizon + signal | "scaling will be difficult" |

## 2.2. Rules of consolidation

- **Block 6 takes precedence over the others.** If one item from 6.2 coincides across ≥3 models, it becomes a "known weaknesses" section in the spec, not a footnote.
- **Block 4 is accepted by compatibility**, not by votes: two schemas that do not fit together mean the format is underspecified. We assemble one.
- **Blocks 1 and 2 are a veto zone for crypto**: if ≥3 models choose the same contract class, it is fixed. If they split 2/2, we take the one with less code and simpler roles.
- **Numbers from 3.3 — the minimum cap and the maximum bond** (conservatism towards less risk for us).
- An answer that argues against "already decided" does not count for that question.

## 2.3. Red flags

1. 1.2 gives an invariant without a predicate → unsuitable for proof.
2. 1.3 without a "what it misses" column → the method is incomplete and that is hidden.
3. 2.2 proposes "keeping the owner for convenience" → closure is impossible, the answer does not count.
4. 3.1 without behaviour on `INVALID`/`INCONCLUSIVE` → the automatic payout is unsafe by construction.
5. 5.2 no compute limit → the free analysis will eat the margin in a week.
6. 6.2 empty or general words → lower trust in the whole answer.

## 2.4. What comes after consolidation

The **full spec** is written, made up of the sections:

1. Product and boundaries (what we guarantee, what we do not).
2. Domain model: legacy and on-chain, ports, `subject.kind`.
3. Formats: `flowguard.yml`, bundle, verdicts, act. **Schemas in full.**
4. The closure Z and the declaration artefact for both domains.
5. Mediator, `Permit`, enforcement points, invariants.
6. Evidence: channels, finality, acceptance tests.
7. Proof: obligations, assumptions ledger, TCB, Verus/Certora backends.
8. Attacks: 10 scenarios, failure criteria.
9. The R0–R5 ladder for two domains and the prices.
10. Service: SKU, automation, applicability boundaries, anti-abuse.
11. Economics, team, 90-day roadmap.
12. **Known weaknesses** (from block 6.2) — as a separate section, not a footnote.

The spec will be written **for refutation**: every statement is numbered, tagged `[PROVED]` / `[MEASURED]` / `[HYPOTHESIS]`, and every section has "what would break this statement". It must be criticised precisely by these labels.
