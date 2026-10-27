# 11. Round three: questions about what remains undetermined

> **What has changed against round two.** Block A is closed (5/5) — there are no more questions about the product model. Block D is closed (three independent syntheses gave the same result) — we are not asking about the v1 slice. Block B in its previous formulation is broken (a 65× spread showed that "the cost of a finding" is unmeasurable).
> What remains is **five places where nobody has specified anything**, and all of them are decided by the model, not by the buyer. That is the third round.

---

# PART 1. PROMPT FOR MODELS (copy in full, do not change between runs)

## Role

You are a design engineer, not a reviewer. The product decisions have been made; there is no need to discuss them. You are required to **design five concrete mechanisms** in such a way that they can be implemented from your text.

## Rules

1. Every answer is a **finished artifact**, not a discussion: a contract, a table, a list, a schema. If a contract is requested, write a contract that can be pasted into code.
2. **No more than 150 words** per answer, except where a table or a contract is explicitly required (there — as much as needed, but without padding).
3. It is **forbidden** to dispute the decisions taken (see "Already decided"), to propose new architectures, or to cite benchmarks without a source.
4. "It depends on the context" is **forbidden** without stating the condition in one line.
5. If you do not know, write `I don't know` + **how you would check and in how many days**. That is a full answer.
6. Mark numbers as `[estimate]`. Metrics — with a definition, not a word.

## Already decided (do not dispute, do not revisit)

**Product.** An agent in a microVM analyzes a repository; a finding exists only as `PROVEN` — an effect reproduced in the sandbox under triple control **C** (without the payload — no effect) / **T** (full trigger — the effect is present) / **N** (semantic mutation — no effect). The report is signed by a human. Hypotheses (`HYPOTHESIS`) live separately and are not billed.

**v1 — narrow:**
- three vulnerability classes with ready sealed oracles;
- fix levels only **R0** (mitigation) and **R1** (point patch);
- six components: microVM · C/T/N · sealed oracle · evidence plane · replay kit · named signatory;
- the verifier is executed **by a process outside the agent's VM**; the canary-nonce is the acceptance test of the witness plane;
- delivery: SaaS with an ephemeral runner; the hybrid runner is the second release;
- default deployment is hybrid as an architectural requirement, but not as the v1 delivery.

**Economics — mode A:** 3–7 findings (plan 4), `repro rate` ≥95%, `fix-acceptance` 60–70%, engagement price $7.5–12k, R1 margin ~65%. The cost base holds only through **review of ≤15 minutes per finding**; without that the margin goes to zero (mode B — $25k and deep verification — is not our v1).

**Fatal mechanism (5/5):** starvation of `PROVEN` because there are no machine oracles. Indicators: `PROVEN/engagement < 2` for ten engagements in a row, `HYPOTHESIS/PROVEN > 10`, pilot→paid conversion <20%.

**Accepted invariants:**
- **I1** — "verified" is produced by deterministic code, not by a model;
- **I2** — reproducible **within the declared fingerprint**; outside it — `HYPOTHESIS`;
- **I3** — every claim is bounded by a negative scope.

---

## BLOCK 1 — Oracle (the main bottleneck, 4/5 reviewers)

**1.1. Oracle contract.** Write the interface of the sealed oracle in pseudocode so that two engineers can independently implement compatible versions from it. Mandatory parts: what the agent delivers, what the oracle receives from outside (witness), what it returns, which fields enter the signed hash, how it is versioned. Format: signature + 5–8 lines of contract. `[contract]`

**1.2. Three classes.** The matrix of candidates is given: SQLi · authorization bypass (IDOR/BOLA) · path traversal · SSRF · insecure deserialization · XSS · secrets in code · known CVEs in dependencies · races (TOCTOU) · business logic. Choose **exactly three** for v1 by the criterion: oracle decidability × prevalence × willingness to pay. Format: table `class | oracle decidable? (yes/partially/no) | why this one | what we lose by deferring`. `[table]`

**1.3. Human-sealed oracle.** For classes where there is no machine predicate, a human writes the oracle. Describe the operations: how many person-days per oracle, how many findings it covers before it pays for itself, who validates it, what happens when the client disputes the verdict. Format: 5 lines + one figure for "days per oracle". `[estimate]`

**1.4. How to test the oracle itself.** C8 requires "mutation testing of the oracle", but there is no method. Design it: which mutants are fed in (at least 5 types), what counts as a test failure, what the acceptance criterion for an oracle entering the library is, how this is automated in CI. Format: list of mutants + acceptance criterion in one sentence. `[list]`

---

## BLOCK 2 — Witness and the impossibility of forgery (2 questions)

**2.1. Minimum witness-set.** The agent controls everything inside its own VM. List the **minimum** set of observation channels under which it cannot fabricate `PROVEN` for the "authorization bypass" class, and for each channel: what it catches, what it does **not** catch, the cost in engineering days. Format: table `channel (network tap / DB digest / filesystem overlay-diff / process graph / …) | what it protects against | what it does not protect against | days`. `[table]`

**2.2. Acceptance test of the witness plane.** The canary-nonce is accepted as a **test**, not as a component. Write exactly what the test asserts: which attack is simulated, what must happen for the test to be considered failed. Format: 4–6 lines "given / when / then". `[test]`

---

## BLOCK 3 — Review card (the critical path of the margin)

**3.1. What the assessor sees in 15 minutes.** Design a one-page card from which a human signs `PROVEN` in ≤15 minutes. List **exactly 7 elements** and for each — why it is necessary rather than merely agreeable. Format: numbered list with a one-line justification. `[7 elements]`

**3.2. What cannot be compressed.** Name **three** things that cannot enter this card, and explain exactly which class of error will slip through if they are removed. Format: 3 items × 2 lines. `[3 items]`

---

## BLOCK 4 — Product boundaries (2 questions)

**4.1. Validatability contract.** The following requirements are accepted: a reproducible build, lock files, a test command or a health oracle, an image without secrets. Estimate: **what share of real repositories** passes this filter — separately for (a) open-source, (b) the average product of a company of 50–500 people, (c) enterprise legacy. Format: three numbers with `[estimate]` + one line on "what this does to TAM". `[numbers]`

**4.2. Positive attestation of coverage.** The buyer does not accept "we found nothing" (a negative claim). Formulate a **positive** one: what exactly is asserted, on the basis of which artifact, and which phrase in the report makes this claim checkable. Format: one formulation (≤40 words) + list of artifacts + what it does **not** assert. `[formulation]`

---

## BLOCK 5 — Falsification (2 questions)

**5.1. A 30-day test.** Propose **one** experiment that, in 30 days and ≤2 person-weeks, either confirms or kills the hypothesis "a library of oracles for 3 classes yields ≥4 `PROVEN` on a typical repository". State: what we do, on which corpus, which result counts as failure. Format: 5 lines. `[plan]`

**5.2. The killer condition.** Name one observable condition under which this product **should not be built at all** (not "hard", but "should not"). Format: one sentence + how to detect this condition within a month. `[condition]`

---

# PART 2. HOW TO SYNTHESIZE (do not show to the models)

## 2.1. What counts as a strong answer

| Block | Strong | Weak (answer is not counted) |
|---|---|---|
| 1.1 contract | can be implemented without asking questions | a description in words, "the oracle checks" |
| 1.2 classes | exactly three + what we lose | a list of 6 "most important" ones |
| 1.3 human-sealed | a figure in days + who validates | "it depends on complexity" |
| 1.4 oracle test | concrete mutants + criterion | "it needs to be tested" |
| 2.1 witness | a table with "what it does not protect against" | an enumeration without boundaries |
| 2.2 acceptance test | the "given/when/then" formula | "add a canary" |
| 3.1 card | exactly 7 elements | 12 elements "just in case" |
| 3.2 what cannot be compressed | 3 items + the class of error | "everything is important" |
| 4.1 shares | three numbers | "it depends on the industry" |
| 5.1 test | corpus + failure threshold | "run a pilot" |
| 5.2 not to build | one observable condition | "if we do not find PMF" |

## 2.2. Synthesis rules (changed against round two)

Round two was about opinions — "4–5 out of 5 → we accept" worked. Round three is about artifacts, so the rule is different:

- **Compatibility of artifacts matters more than votes.** Two oracle contracts that cannot be implemented together are not 2 votes against 3 but a signal that the contract is underspecified. We count "how many models produced mutually compatible artifacts".
- **The decision is made on the cheapest-to-implement compatible set**, not on the majority. If one answer gives a mechanism in 2 days and four give it in 6 weeks, we take the first and test on it.
- **A divergence in the numbers (4.1) is not put to a vote** — we take the minimum value as the planning figure (an error towards a smaller TAM is cheaper).
- **Block 5 has a right of veto.** If the same "do not build" condition coincides in ≥3 models, that is a stop signal, taking priority over any consensus on mechanisms.

## 2.3. Red flags

1. The answer to 1.1 cannot be implemented → the contract is underspecified; re-ask this item only.
2. In 1.2 there are more or fewer than three classes → the answer is not counted (it cannot cut).
3. In 2.1 there is no "what it does not protect against" column → the mechanism is not understood.
4. In 3.1 there are more than 9 elements → the card will not fit into 15 minutes; the answer is not counted.
5. In 5.2 "do not build" is absent → the model cannot falsify; lower confidence in the whole answer.
6. Numbers in 4.1 without an indication of where they come from (practice / estimate / literature) → strike them out.

## 2.4. What we do with the result

| Outcome | Action |
|---|---|
| A compatible oracle contract in ≥2 models | take as the basis, implement in the first 2 weeks |
| The three classes coincide in ≥3 models | fix as the v1 scope, the rest is roadmap |
| Witness-set: the intersection of the tables | the minimum set for implementation; the difference goes to the backlog |
| Review card: the intersection of the 7 elements | the basis of the UI; divergences are at the assessors' discretion |
| The share passing the filter (4.1) | we recalculate TAM and the engagement price |
| The "do not build" condition recurred ≥3 times | **we stop and check it first of all**, before any development |

## 2.5. When round three is closed

It is closed when there are: (a) one implementable oracle contract, (b) the three fixed classes, (c) a minimum witness-set with a cost in days, (d) a review card of ≤9 elements, (e) three numbers on TAM, (f) one 30-day experiment with a failure threshold.

After that the questions to the models end: what remains is code and interviews with buyers.
