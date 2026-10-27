# 20. Second-round decisions: a digest of two reviews

> Input: two independent answers to `10-ROUND2-QUESTIONS.md` (reviewer #1 and #2), neither with access to the other.
> Rules: 2/2 → accept; divergence → assign a measurement, not a vote; consensus against our spec → fix the spec.
> Below is only what **changed** the documents. Contested and unresolved items are moved to §9.

---

## 1. Block A: 11 of 12 decisions — consensus

| Question | #1 | #2 | Outcome |
|---|---|---|---|
| A1 what goes in "findings" | b (80) | a (99), but the rationale = "hypotheses as a separate appendix" | **Accepted: only `PROVEN` in findings, hypotheses — a separate appendix.** With #2 the letter diverges from the rationale; substantively — agreement |
| A2 who signs | a, our assessor (80) | a (78) | **2/2 — accepted** |
| A3 first entry point | a, the repository (75) | a (91) | **2/2 — accepted** |
| A4 where the moat is at 12 months | b, the evidence plane (60) | b (93) | **2/2 — accepted, spec corrected** (see §5.1) |
| A5 pricing model | a, per scope (70) | a (86) | **2/2 — accepted** |
| A6 human review | a, 100% (90) | a (91) | **2/2 — accepted**, the highest agreement of the round |
| A7 deployment | b, hybrid (60) | b (89) | **2/2 — accepted** |
| A8 formal methods in v1 | a, no (65) | a (96) | **2/2 — accepted** |
| A9 live tests | a, never (85) | a (89) | **2/2 — accepted** |
| A10 non-reproducible PoC | a, NRE, do not bill (80) | a (94) | **2/2 — accepted** |
| A11 spec for R5 | c, jointly + independent reviewer (70) | c (90) | **2/2 — accepted** |
| A12 "no vulnerabilities" | b, with explicit limitations (85) | b (98) | **2/2 — accepted** |

**What this means.** The dispute about the product model is closed: a narrow repo-only service with a proven result, human signature, hybrid deployment and per-scope pricing. It no longer needs to be asked about again — it needs to be measured.

---

## 2. Block B: the numbers — where they converged, where they spread

| Metric | #1 | #2 | Spread | Decision |
|---|---|---|---|---|
| B1 cost of a validated finding | $400 | $150 | 2.7× | **The `$8` threshold is removed for good.** The order of magnitude is hundreds of dollars; we manage the cost of the **engagement** |
| B2 p90 dynamic-PoC | $3 000 | $1 000 | 3× | Kept as a separate class in reporting, not averaged |
| B3 time-to-first-validated | 6 h / 48 h | 4 h / 24 h | 1.5–2× | **Accepted: p50 ≤6 h, p95 ≤48 h.** The previous 15 min threshold was a spec error |
| B4 wall-clock cap | 24 h | 8 h | 3× | **8 h** — product SLA, **24 h** — asynchronous batch tier |
| B5 repro rate | ≥90% | ≥95% | close | **≥95%** as the threshold, 90% as the minimum for release |
| B6 fix-acceptance | 60% | 60% | **exactly matched** | **60% accepted** for v1 (not 70%); 70% is the target after 20 engagements |
| B7 price of S1 | $12 000 | $2 000 | **6×** | **Not decided by models.** Goes to buyer interviews, not to the spec |
| B8 margin R1 / R3 | 70% / 55% | 60% / 35% | 10–20 pp | We plan on the lower bound: **R1 ≥60%, R3 ≥35%** |
| B9 findings per S1 | 4 | 3 | **matched** | **We plan for 3–4.** The key number of the whole economics |
| B10 up to the first client | 4 people × 4 months = 16 person-months | 3 people × 2 months = 6 person-months | 2.7× | **We plan for 12 person-months.** 6 person-months is reachable only for a repo-only SaaS without the hybrid, which contradicts A7 |

**The main conclusion of Block B.** Both reviewers independently said the same thing: findings are few (3–4), each one is expensive ($150–400), therefore **the economics is determined by engagement cost, not by efficiency per finding**. This overturns the first-round metric.

---

## 3. Block C: fatal mechanisms confirmed by two votes

| Mechanism | Who named it | Votes | Action |
|---|---|---|---|
| **Non-hermetic dependencies:** the build reaches the network, `DEPLOY_FAILED`, zero findings; the replay does not reproduce at the client | #1 (p.2), #2 (p.4) | **2/2** | **P0 task:** a dependency prefetch stage through an allowlist mirror **before** sealing + all dependencies and checksums in the replay kit |
| **The oracle checks the wrong semantics:** C/T/N passes, but the predicate is wrong; a systematic, reproducible error | #1 (p.4), #2 (p.1) | **2/2** | **P0 task:** an independent reference corpus + mutation testing of the oracle + implementation review → became axiom **C8** |
| **The economics breaks on hard findings:** one dynamic-PoC = days of manual work at a fixed price | #1 (p.1, p.5), #2 (p.5) | **2/2** | **P0 task:** adaptive K (3→10), an execution budget inside the price, "heavy" classes — a separate tier |
| 100% signing as a linear load (a queue) | #1 (p.3) | 1/2 | Accepted as a scaling constraint: a one-page review card + auto-replay, a 15 min ceiling |
| An empty report: 0 findings at full price | #1 (p.5) | 1/2 | **Accepted as a product:** "coverage attestation" — a sellable zero result |
| Out-of-scope actions via injection | #2 (p.2) | 1/2 | Already covered by C7 + egress deny-all at the infrastructure level |
| The fix passes the tests but breaks business logic | #2 (p.3) | 1/2 | Accepted: a client behaviour contract in the mandatory R1 acceptance |

**Changes per unit of effort** (the intersection): a hermetic bundle with dependency pinning (2 weeks) · full-cycle economics instrumentation (1 week) · adaptive K (1 week) · an independent reference corpus (3 weeks). The order is by decreasing ratio of "risk removed / effort".

---

## 4. Block D: the real scope of v1 (intersection, not union)

**To keep (4 components named by both):** `(1)` microVM · `(2)` PoC contract C/T/N · `(3)` sealed oracle · `(6)` offline replay kit.

**Each reviewer added one:** #1 — `(12)` named signatory; #2 — `(5)` evidence plane with a hash-chain.

**v1 outcome:** the four agreed + `(5)` + `(12)`. At the same time #2 states explicitly: cutting `(12)` is permissible **only for an internal prototype**; for a commercial V1 the signature is mandatory. That is, substantively — agreement.

**Cut by both:** `(4)` canary-nonce · `(7)` live DAST · `(8)` root-cause graph · `(9)` peer generation of R0–R5 · `(10)` verifier farm · `(11)` the formal track.

### One decision against consensus (documented)

**`(4)` canary-nonce stays in v1, despite a 2/2 "cut it".** Rationale: both #1 and #2 assume that a sealed oracle makes the observation unforgeable. That is wrong. The oracle checks a **predicate** over an observation, but the observation itself is produced inside the VM that the agent controls: the agent need not "invent a bug", it can **fabricate an observation** — print a line into the log that the oracle will take as proof. Canary-nonce costs one day of work (a random token in a synthetic table) and closes exactly this vector; without it the whole defence reduces to the agent's honesty.

The cost of an error in the other direction: if we are right, then without the nonce the very first "inventive" run will ship a false proof to the client — and that is K3 (false verification) and the end of the product. The asymmetry is 1 day against the company. We keep it. **A candidate for the third round** — the question is formulated in §9.

---

## 5. What changed in the documents

| Change | File | Reason |
|---|---|---|
| 5.1 Moat at 0–12 months: **the evidence plane**, the signature — commercial packaging | `00-SYNTHESIS.md` §3.1 | A4: 2/2 |
| 5.2 New axiom **C8**: the verifier itself is under verification (independent corpus, oracle mutation, implementation review) | `00-SYNTHESIS.md` §2 | C3: 2/2 dissent against C1 |
| 5.3 **I2 reformulated**: "the same verdict with the declared repro rate ≥ p", not "the same result" | `00-SYNTHESIS.md` §7, `10-ROUND2-QUESTIONS.md` (do not change — see §8) | C3 #1 |
| 5.4 **K is adaptive**, 3→10 instead of a fixed K=10; K is printed in the bundle | `01-VARIANTS.md`, `02-GRID.md` | C1 #1: 3 branches × 10 VM × restarts = a cost explosion |
| 5.5 A **dependency prefetch** stage through an allowlist mirror before sealing | `01-VARIANTS.md` (V1) | C1 #2 + C1 #4: 2/2 |
| 5.6 The `cost per validated ≤$8` threshold is **removed**; the governing metric is engagement cost | `03-EVAL-ROADMAP.md` §2 | B1: $150 and $400 |
| 5.7 `time-to-first-validated`: **≤6 h p50 / ≤48 h p95** instead of 15 min | `03-EVAL-ROADMAP.md` §2 | B3: 2/2 |
| 5.8 `fix-acceptance` **60%** for v1 instead of 70% | `03-EVAL-ROADMAP.md` §2 | B6: exact match |
| 5.9 **K6** (output collapse) and **K7** (renewal collapse) added | `03-EVAL-ROADMAP.md` §3 | D1: 2/2, different mechanisms of one family |
| 5.10 A new product, **"coverage attestation"**, for a zero result | `01-VARIANTS.md` (V1), see §6 below | C1 #5 |
| 5.11 **Report withdrawal procedure**: withdrawal, notification, deadlines, correction of what was already issued | see §7 below | E1 #2 |

---

## 6. The "empty report" as a product, not as a failure

With 3–4 findings per engagement and a strict `PROVEN` filter, a significant share of orders will yield **zero findings**. Selling such a report as "we found nothing" means a lost client. The decision (accepted on C1 #5):

**Coverage attestation** is a separate sellable deliverable that is bought *instead of* findings:
1. A surface map: what exactly was tested, with digests and timestamps.
2. A list of the attack classes the run covered, and the result for each (`not detected` / `not reachable` / `not tested`).
3. Replayable proof: the client replays the run and confirms that the checks really were performed.
4. A negative scope — as contractual text, not a footnote.

The key point: "we did not find" sells only together with proof that we **looked**. This is what distinguishes us from a scanner whose empty report is indistinguishable from a broken scanner.

---

## 7. Liability (E1, both reviewers)

They agreed: liability capped at the fee until the first large deal + E&O insurance + a negative scope as **contractual** text.

Added by #2 and accepted as a product requirement: the **report withdrawal procedure** — mandatory elements:

| Element | Requirement |
|---|---|
| Withdrawal trigger | an oracle/verifier error is found, or a replay divergence beyond the declared repro rate |
| Notification | all recipients of the affected report; the deadline is fixed in the contract |
| Content | what exactly is wrong, which statements are withdrawn, which remain in force |
| Correction | re-run and re-sign; the old report is marked as withdrawn but not deleted |
| Record | a withdrawal register available to the auditor and the insurer |

Without this mechanism a "signed report" is not liability but an imitation of it: a signature that cannot be withdrawn cannot be insured either.

---

## 8. The instrument is frozen

`10-ROUND2-QUESTIONS.md` is **not edited** to match the second-round decisions, although it now contains formulations that are known to be outdated (K=10, I2 "the same result", the 15 min threshold). This is deliberate: the question set is a measuring instrument, and changing the instrument in the middle of a series breaks comparability of the answers. All corrections live in the spec (`00`, `01`, `02`, `03` and this file).

When the instrument may be updated: after the third round, together with a new question set.

---

## 9. What remains open and goes to the third round

A 2/2 split or a 6× spread does not mean "the models are stupid", it means "the question needs data or is posed wrongly". Hence only four items, none of them about architecture.

| # | Question | Why it is not settled | How to close it |
|---|---|---|---|
| Q1 | **Price of S1: $2k or $12k** (6×) | Not decided by opinion — only by willingness to pay | 10 buyer interviews by trigger (attestation / release gate / M&A), not with models |
| Q2 | **Hybrid runner: timeline and minimum scope** (6 vs 16 person-months) | A direct contradiction: A7 = hybrid by default, B10 #2 = 6 person-months, which cannot accommodate the hybrid | Ask: the minimum runner that clears the procurement blocker — is it 2 weeks or 8? |
| Q3 | **Canary-nonce: keep or cut** (2/2 against, we are against consensus) | A technical and narrow dispute: is the observation forgeable under a sealed oracle | The question is in §9.1 — put it to all third-round models |
| Q4 | **Which leads: output or renewal** (month 10 "empty" vs month 6 "not renewing") | Two indicators of one family; it is unclear which fires first | Both in the dashboard from the first pilot; in 3 months the data will speak for itself |

### 9.1. The third-round question (the only technical one)

> The agent executes in a microVM and fully controls the processes inside it. The oracle is sealed: the agent does not write the predicate, it only supplies the data from which deterministic code computes `O`. Can the agent obtain `PROVEN`, **without finding a vulnerability**, by fabricating an observation (writing into the log/response a string, a file or an effect that the oracle will take as proof)? If yes — what minimal mechanism closes this and what does it cost in person-days? If no — why exactly, naming the specific barrier.

The answer to this question decides Q3, and Q3 is the difference between "proven" and "the agent said it is proven".

---

# 10. Third reviewer: what changed

> §10 supplements and, where contested, **replaces** §1–§2. Three independent answers instead of two is no longer a vote but a robustness check.

## 10.1. Block A: 12 of 12 — full consensus

All three reviewers gave **the same letter on all twelve questions**. Not "similar" but identical: A1 b, A2 a, A3 a, A4 b, A5 a, A6 a, A7 b, A8 a, A9 a, A10 a, A11 c, A12 b.

This means: the product model is definitively closed, and further rounds on these questions are a waste of time. Block A can be removed from the instrument; there is no place for it in the next question set.

The only substantive divergence is **confidence**, and it is informative: on A4 (where the moat is) the spread is 60 / 93 / 80, on A1 — 80 / 99 / 90. That is, everyone agrees on *what* to do but not on *how obvious* it is. For planning this means: A4 is the riskiest of the "settled" items.

## 10.2. Block B: a 40–65× spread is not a disagreement but different definitions

| Metric | #1 | #2 | #3 | Spread |
|---|---|---|---|---|
| B1 cost of a validated finding | $400 | $150 | **$6 000–10 000** | **40–65×** |
| B2 p90 dynamic-PoC | $3 000 | $1 000 | $18 000–30 000 | 18–30× |
| B3 time-to-first | 6 h / 48 h | 4 h / 24 h | **48 h / 120 h** | 8–12× |
| B4 wall-clock cap | 24 h | 8 h | 8 h | 3× (2/3 for 8 h) |
| B5 repro rate | 90% | 95% | 90% | **converged** |
| B6 fix-acceptance | 60% | 60% | 70% | **converged (~60–70)** |
| B7 price of S1 | $12k | $2k | $10k | 6× |
| B8 margin R1 / R3 | 70 / 55 | 60 / 35 | 70 / 45 | moderate |
| B9 findings per S1 | 4 | 3 | 6 | **3–6** |
| B10 person-months | 16 | 6 | 10–12 | median 12 |

**Three numbers converged and can be trusted:** findings per engagement 3–6, `repro rate` ~90–95%, `fix-acceptance` ~60–70%. This is the core of the economics, and it is stable.

**Three numbers diverged by tens of times — and that is a defect of the question, not of the answers.** Diagnosis:

- #1 and #2 computed the **marginal** cost (compute + triage up to a validated finding).
- #3 computed **full load** (assessor $120/h × 4–8 h per finding + validation + review).
- Since A6 = 100% human review is consensus, **definition #3 is the correct one**. The human is the cost.

**But #3's number does not add up with itself arithmetically.** Cross-check:

```
assessor:  4–8 h × $120/h           = $480–960 per finding
per engagement (6–10 findings)      = $2 900–9 600
plus compute (#1: $220–1 650)       = $3 100–11 250
÷ 6–10 findings                     = $520–1 130 per finding  ← matches #1
```

And #3 claims $6–10k per finding, that is $36–100k per engagement — with its own S1 price of $10k and its own 70% margin (which means a cost of $3k). **A 12–30× contradiction inside a single answer.** Most likely, $6–10k is not "per finding" but the engagement cost divided incorrectly.

**The accepted value: $500–1 200 of fully loaded cost per PROVEN finding**, with a median of ≈ $800. This confirms #1 ($400 as marginal) and refutes #3 (as arithmetic), not as expertise.

**The main consequence is not in the number but in what follows from it.** The dominant cost line is **assessor hours**, not compute. Therefore:

> A one-page review card with auto-replay and a 15 minute ceiling is not a UX improvement. **It is the margin.** Cutting review from 6 hours to 15 minutes lowers the cost of a finding from ~$800 to ~$100 and turns the product from loss-making into profitable.

No reviewer formulated this as an economic conclusion; #1 proposed the card as a way to unload the queue. This is the most valuable derivative of the whole round.

## 10.3. Time-to-first: two different SLAs, not one number

The 4–48 h spread is explained by the same definition defect:

| Metric | What it measures | Who gave it | Accepted |
|---|---|---|---|
| `time-to-validated` | repo accepted → machine verdict `PROVEN` | #1 (6 h), #2 (4 h) | **p50 ≤6 h** |
| `time-to-signed` | repo accepted → **signed** report | #3 (48 h / 120 h) | **p50 ≤48 h, p95 ≤120 h** — this is the promise to the client |

**Commercial consequence:** you cannot sell a "result in hours" if the signature takes two days. We sell: "a signed report within two business days" — still 15–30× faster than a human pentest (4–10 weeks), and it is true.

## 10.4. What the third reviewer changed substantively

Five points the first two did not have, all accepted.

**1. The verifier farm is needed in V1, not in V2.** A unique and the sharpest argument: if the verifier lives in the same sandbox as the agent, the agent can influence the verifier — and **I1 stops being an invariant and becomes a wish**. Both #1 and #2 cut the verifier farm while keeping the sealed oracle; this is inconsistent (see §10.5). Accepted: a minimal verifier service **outside** the agent's microVM, in V1, +2–3 person-weeks.

**2. V1 narrows to stateless / deterministically oracleable classes.** Mechanism: offense-gated on a stateful application gives a high NRE and few `PROVEN` → revenue starves. This is the third independent formulation of what #1 ("empty report") and #2 ("the economics breaks on hard findings") wrote. **Three votes → a decision:** in V1 we sell only the classes for which a deterministic oracle exists (injections, authorization bypass, path traversal, secrets, known CVEs, insecure configurations). Races, business logic, DoS are outside V1.

**3. Lane A is not free.** A hole in our two-track scheme: we declared the coverage track "not billed" but did not cap its cost. Compute and support for Lane A go into COGS with zero revenue. Accepted: **a hard compute budget for Lane A per engagement**; on overrun — either a paid extended triage or a truncated coverage map with an explicit mark.

**4. A public refusal list.** "Which class of vulnerabilities do we **publicly refuse** to sell in v1, even if we find one". #3's answer: logic/business vulnerabilities without a deterministic oracle — only in Lane A, free of charge, without promises. This is not a limitation but a **trust product**: a public refusal of a class is the only proof that we do not sell noise. Accepted, see `03-EVAL-ROADMAP.md`.

**5. R5 is paid R&D, not a V3 promise.** Consistent with §3.6 of the synthesis but harsher: not "a credibility asset with a transition criterion" but "paid R&D with no timeline promise". Accepted: V3 has no date in commercial materials.

## 10.5. The key linkage all three missed

`(4)` canary-nonce and `(10)` verifier farm are **complementary, not alternative defences**, and both cannot be cut:

| Defence | What it protects against |
|---|---|
| Verifier outside the agent's VM | the agent **cannot substitute the verdict function** |
| Canary-nonce | the agent **cannot fabricate an observation** that the verifier will dutifully check |

The second vector is real and is not closed by the first: the agent can write a `role=admin` row into a database it controls and legitimately read it back — the verifier honestly records the effect, the oracle honestly returns `PROVEN`, and the finding does not exist.

All three reviewers cut canary-nonce (3/3), two cut the verifier farm (2/3). Following both cuts, **the agent controls both the observation and the verdict** — that is, I1 is false.

**A final decision against consensus:** in V1 **both** stay. The cost is 1 day (canary) + 2–3 weeks (verifier). This is the only pair where 3 weeks of engineering separate "proven" from "the agent said it is proven". The difference is in the cost of an error: K3 — false verification — is irreversible.

## 10.6. Block D: the intersection is stable, v1 = 6 components

Three "keep" sets: `{1,2,3,6,12}` · `{1,2,3,5,6}` · `{1,2,3,5,12}`.

| Component | "Keep" votes | Status |
|---|---|---|
| (1) microVM | 3/3 | **v1** |
| (2) C/T/N | 3/3 | **v1** |
| (3) sealed oracle | 3/3 | **v1** |
| (5) evidence plane / hash-chain | 2/3 | **v1** |
| (6) offline replay kit | 2/3 | **v1** |
| (12) named signatory | 2/3 | **v1** (#2 qualified: only for the commercial offering) |
| (10) verifier farm | 1/3, but the strongest argument | **v1** (see §10.5) |
| (4) canary-nonce | 0/3 | **v1** (see §10.5) |
| (7) live DAST · (8) graph · (9) peer-gen · (11) formal methods | 0/3 | **V2+** |

**Outcome: 8 components in v1, of which 6 are consensus.** The difference from the previous digest (§4) is that the verifier farm moved from V2 to V1: #3's argument is stronger because it is about an invariant, not about convenience.

A note on #3: it cut `(6)` replay kit while keeping `(5)` hash-chain, with the rationale "without a hash-chain there is no offline acceptance". But offline acceptance requires the replay kit itself; a hash-chain without it gives only tamper-evidence. I consider this an inconsistency of wording, not a position — we keep both.

## 10.7. D1: two of three named month 10 and `PROVEN` starvation

| | Month | Mechanism | Indicator |
|---|---|---|---|
| #1 | 10 | collapse of PROVEN output | >50% of orders with ≤1 finding, 2 months |
| #2 | 6 | they do not buy again | <30% pay for a re-run |
| #3 | 10 | few PROVEN + free Lane A eats the economics + sales do not convert | **PROVEN per S1 < 3 and HYPOTHESIS/PROVEN > 10** |

**2/3 on month 10 and on `PROVEN` starvation** → this is already a forecast, not a hypothesis. #3's indicator is better than both: it is **relative** (the ratio of hypotheses to proven), so it does not depend on the engagement size and is visible in month 9.

Accepted in `03-EVAL-ROADMAP.md` as K6 with a ratio indicator.

## 10.8. E1: the refusal list as a contractual artefact

#3 added a dimension that was missing: not only "who is liable" but also **"what we refuse to sell"**. A public list of non-deliverable classes is at the same time:

- a limitation of liability (no claim can be brought for a class we did not sell);
- proof of honesty (we did not "fail to find", we "do not take it on");
- protection of I1 (we do not promise `PROVEN` where there is no deterministic oracle).

All three reviewers agreed on the liability cap + E&O + a negative scope as contractual text. A fourth element is added: **the public refusal list**.

## 10.9. Third-round agenda: two questions

| # | Question | To whom | Why it is not settled |
|---|---|---|---|
| Q1 | Price of S1: $2k / $10k / $12k (6×) | **not to models** — to buyers | Only willingness to pay; 10 interviews by trigger |
| Q2 | Hybrid runner: the minimum scope that clears the procurement blocker — 2 weeks or 8? | models + 2 procurement interviews | A direct contradiction between A7 and B10 |
| Q3 | Is the observation forgeable under a sealed oracle **and** a verifier outside the VM? | models (a narrow technical question) | Decides whether canary-nonce is needed; answers #1–#3 did not close it, since all three cut canary and two cut the verifier |

Q4 (output vs renewal) is closed: 2/3 for "output", both indicators into the dashboard, the pilot decides.

**What to remove from the instrument:** the whole of Block A (12/12, closed), Block B in its current formulation (a definition defect — cost must be counted in assessor person-hours, not in "cost of a finding"), Block D in its current formulation (the intersection is stable across two independent digests).

**What to add:** questions about the **minimal verifier service** (its boundaries, what it observes, how it is proven to be outside the agent's control) and about the **review card** (what can be compressed to 15 minutes without losing signature quality). These are the two points where 3 weeks and 15 minutes turn into margin.

---

# 11. Fourth reviewer: the round is closed

## 11.1. Block A: 4/4 substantively

| Question | #1 | #2 | #3 | #4 | Outcome |
|---|---|---|---|---|---|
| A1 | b | a* | b | a | **4/4 substantively**: only `PROVEN` in findings. The letter divergence concerns packaging: an appendix with hypotheses (b) or a separate Lane A artefact (a) |
| A2 | a | a | a | a | 4/4 |
| A3 | a | a | a | a | 4/4 |
| A4 | b | b | b | **a** | **3/1** — see §11.2 |
| A5–A11 | — | — | — | — | 4/4 on all |
| A12 | b | b | b | a* | **4/4 substantively**: only with a negative scope, never as an absolute |

`*` — the letter diverges from the reviewer's own rationale; substantively a match.

**Block A is closed.** Eight questions — unanimous, four — unanimous substantively. Further rounds on the product model are pointless.

## 11.2. A4: 3/1, but both answers are right about different things

#1–#3: the evidence plane, because **an auditor will not accept a signature without reproducibility** → reproducibility is a *precondition*.
#4: the signature and auditor acceptance, because **reproducibility can be copied, but the contract with an auditor cannot** → that is the *moat*.

**Reconciliation (accepted):** the evidence plane is a **precondition**, signature + auditor acceptance is the **moat**. They are built simultaneously (one is meaningless without the other), but in contested decisions reproducibility has priority, and in strategy the relationship with the auditor does. This removes the apparent contradiction and confirms §5.1.

## 11.3. Block B: four values, a 65× spread — the metric is broken

| Metric | #1 | #2 | #3 | #4 | Spread |
|---|---|---|---|---|---|
| B1 cost of a finding | $400 | $150 | $6–10k | $1,8–3,5k | **65×** |
| B2 p90 dynamic-PoC | $3k | $1k | $18–30k | $8–20k | 30× |
| B3 time-to-first | 6 h | 4 h | 48 h | **20–40 min** | **72×** |
| B4 wall-clock cap | 24 h | 8 h | 8 h | **45 min** | **32×** |
| B5 repro | 90% | 95% | 90% | 95% | **converged** |
| B6 fix-acceptance | 60% | 60% | 70% | 70% | **converged** |
| B7 price of S1 | $12k | $2k | $10k | $7,5–12k | 6×, median ≈ $10k |
| B8 margin R1/R3 | 70/55 | 60/35 | 70/45 | 60–70/35–45 | **converged** |
| B9 findings per S1 | 4 | 3 | 6 | 3–7 | **converged: 3–7, median 4** |
| B10 person-months | 16 | 6 | 10–12 | 9 | **converged: 9–16, median 11** |

**Five of ten numbers converged** (B5, B6, B8, B9, B10) — that is the stable core. Decisions are made on them: 3–7 findings (plan 4), R1 margin 60–70%, R3 35–45%, a team of ~11 person-months, fix-acceptance 60–70%, repro 90–95%.

**Five diverged by orders of magnitude — and that is a defect of the metric, confirmed in four independent ways.** The final conclusion:

> "Cost of a finding" does not exist as a measurable quantity: findings are lumpy (1–7 per engagement) and the cost is almost entirely fixed (build, SCA/SAST, run, review, support). Dividing fixed costs by a random number of findings is not a metric but noise.

**Replacement metric (final):**
1. `engagement_cost` — the full cost of one engagement (compute + sandboxes + assessor hours + support).
2. `assessor_minutes_per_finding` — person-minutes per signed finding.
3. `findings_per_engagement` — as a fact, not as a KPI.

The cost of a finding is a derivative of these three, and it cannot be discussed separately.

## 11.4. Two internal inconsistencies in #4 — more important than the numbers themselves

**First: B4 (a 45 minute cap) contradicts B2 ($8–20k per dynamic-PoC).** If the run is capped at 45 minutes, heavy PoC synthesis is physically impossible; if it is possible, the cap is not 45 minutes. Probably B3/B4 describe a narrow case (without a build from source or without dynamic checking). The B3/B4 values are rejected as incomparable; of the four time estimates we take the **median**: `time-to-validated` p50 ≤6 h, `time-to-signed` p50 ≤48 h (§10.3).

**Second, and it is serious: A7 (hybrid by default, 4/4) against C1 #4 ("a hybrid from day one requires IaC, VPC support and client secrets — that is not 8 weeks").**
This is not a disagreement between reviewers but a **contradiction inside the consensus**: all four want the hybrid, and one of them says plainly that the hybrid does not fit into v1. Plus the arithmetic of §10.2 (B10 #2: 6 person-months, into which the hybrid does not fit).

**Decision:** A7 remains the strategic default (the product is designed as hybrid), but **v1 ships as SaaS with an ephemeral runner**, and the hybrid runner is enabled in the second release. We separate "the architecture must permit the hybrid" and "v1 must ship the hybrid" — the first yes, the second no. This is the only way not to miss the deadline and not to lose the enterprise segment.

## 11.5. Block C: the oracle is the bottleneck, confirmed 4/4

| Mechanism | #1 | #2 | #3 | #4 |
|---|---|---|---|---|
| **The oracle/verifier is the weak link** | p.4 "a sealed oracle limits the classes" | p.1 "the oracle checks the wrong semantics" | p.1 "the agent influences the verifier" | p.1 **"the oracle cannot be sealed for most bugs: there is no universal predicate"** |

The fourth reviewer formulates what the others described indirectly: **for most vulnerability classes there is no machine predicate for "exploitation succeeded"**, so the agent either writes the predicate itself (a violation of I1) or the finding does not become `PROVEN`. Hence two consequences, both accepted:

**(1) v1 narrows to classes with a ready sealed oracle — three classes.** Injections (SQLi/NoSQLi/command), authorization bypass, path traversal / unsafe path handling. Plus secrets and known CVEs as a separate, already deterministic layer. Everything else is Lane A without promises. A library of standard oracles: 4–6 person-weeks, a P0 investment, not a "someday".

**(2) A verifier outside the VM is not an option but a consequence.** If the oracle for some classes is written by a human (human-sealed), the only protection against the agent substituting the predicate or forging the observation is to execute the verdict out of the agent's reach. The dispute in §10.5 is closed in favour of **keeping both the verifier and canary-nonce**: 3/4 reviewers cut the verifier, but their own arguments (the oracle is weak, the agent influences the verifier) require the opposite.

## 11.6. Three new corrections the first three did not have

**1. Do not sell a ladder that cannot be produced.** In v1 peer generation of R0–R5 is V2, so v1 physically produces **only R0 and R1**. Promising R3–R5 in commercial materials is an I3 violation at the level of the offer. Accepted: v1 sells R0/R1, the rest is a roadmap without dates.

**2. C4 is formulated incorrectly.** "Formal methods are a narrow premium track" reads as "can be added later". It cannot: the specification, the assumptions ledger and toolchain versions determine the **evidence plane data schema** from day one. Holding on to the current C4 means V3 will require rewriting the evidence plane. Correction: **C4 → "the formal track is not implemented in v1, but its data contract is laid down in v1"**. Accepted, see `00-SYNTHESIS.md` §2.

**3. We hand the client a working exploit — that is a separate liability vector.** The only one who noticed. Consequences, accepted as product requirements:
- classification of every PoC by danger (`read-only` / `state-changing` / `destructive`);
- `destructive` is not delivered at all, `state-changing` — only with the client's explicit approval;
- an `assertion-only` mode: a PoC without a payload that checks only the precondition and the observation;
- a ban on auto-executing a PoC on the client's infrastructure without their signature.

## 11.7. D1: the mechanism converged, the month did not

| | Month | Mechanism | Indicator |
|---|---|---|---|
| #1 | 10 | output collapse | ≤1 finding, 2 months |
| #2 | 6 | they do not renew | <30% repeat |
| #3 | 10 | few PROVEN + Lane A eats the economics | PROVEN <3 and HYPOTHESIS/PROVEN >10 |
| #4 | **4–6** | the oracles do not cover real classes, the PROVEN stream is empty | **PROVEN <2 over 10 consecutive engagements** |

**3/4 name the mechanism: `PROVEN` starvation due to inadequate oracles.** This is already a forecast. The month diverges (4–6 against 10), but the indicators of #1 and #4 almost coincide in form ("fewer than two-to-one findings per engagement") and fire **earlier** than the death date — in month 3–4.

**Accepted into K6:** the indicator `PROVEN per engagement < 2 over 10 consecutive engagements` + `HYPOTHESIS/PROVEN > 10`. Both are relative, both are independent of engagement size, both are visible before clients start leaving.

## 11.8. The outcome of four reviews

**What is definitively settled** (4/4): the product model (A1–A12), the v1 core of six components plus the verifier and canary, three vulnerability classes in v1, R0/R1 as the only producible tiers, the hybrid as architecture but not as a v1 delivery, the sale of a zero result as coverage attestation.

**What is settled and is no longer discussed because it is measured:** all the numbers from the "converged core" (B5, B6, B8, B9, B10).

**What remains and is not decided by models:** two items.

| # | Question | How to close it |
|---|---|---|
| Q1 | Price of S1: $2k / $7,5k / $10k / $12k — median $10k, but a 6× spread | 10 buyer interviews by trigger. Models are useless here |
| Q2 | Hybrid runner: the minimum scope that clears the procurement blocker | 2 procurement interviews + an installation dry-run at 1 client |

**The instrument is exhausted.** Four independent answers gave: 100% agreement on the product model, convergence on five of ten numbers, 4/4 pointing at the oracle as the bottleneck and 4/4 pointing at a wrong axiom — even though each of the four axiom claims turned out to be correct. A fifth answer makes sense only if it **contradicts** something in §11.8; if it confirms, it is no longer information but repetition.

**The main conclusion of the round, worth keeping in mind:** four experts independently said that the product will die not from competition and not from technology but from a **shortage of verifiable findings due to the absence of machine oracles**. So the first 4–6 weeks of work are not about the agent, not about the sandbox and not about formal methods, but about a **library of oracles for three classes**. Everything else is secondary.

---

# 12. Fifth reviewer: the round is definitively closed

## 12.1. Block A: 10 of 12 — unanimous by letter, 12 of 12 — substantively

| Question | #1 | #2 | #3 | #4 | #5 | Outcome |
|---|---|---|---|---|---|---|
| A1 | b | a* | b | a | b | 3/2 on packaging, **5/5 substantively**: hypotheses never in the same list as `PROVEN` |
| A4 | b | b | b | a | b | **4/1** evidence plane |
| A12 | b | b | b | a* | b | 4/1 by letter, **5/5 substantively**: only with a negative scope |
| the other 9 | — | — | — | — | — | **5/5 unanimous** |

`*` — the letter diverges from the rationale. Two cases across five reviews: this is not a disagreement but an ambiguity in the wording of the option. **Block A is closed and is removed from the instrument.**

## 12.2. Block B: five values revealed not a spread but two different businesses

| Metric | #1 | #2 | #3 | #4 | #5 | Median |
|---|---|---|---|---|---|---|
| B1 cost of a finding | $400 | $150 | $6–10k | $1,8–3,5k | $3 000 | **$1,8–3,5k** |
| B2 p90 dynamic-PoC | $3k | $1k | $18–30k | $8–20k | $12k | ~$12k |
| B3 time-to-first | 6 h | 4 h | 48 h | 20–40 min | 4 business days | — |
| B4 wall-clock cap | 24 h | 8 h | 8 h | 45 min | 6 h | **8 h** |
| B5 repro | 90 | 95 | 90 | 95 | 95 | **95** |
| B6 fix-acceptance | 60 | 60 | 70 | 70 | 60 | **60–70** |
| B7 price of S1 | $12k | $2k | $10k | $7,5–12k | **$25k** | **$10–12k** |
| B8 margin R1/R3 | 70/55 | 60/35 | 70/45 | 60–70/35–45 | 65/35 | **65/35** |
| B9 findings per S1 | 4 | 3 | 6 | 3–7 | 4 | **4** |
| B10 person-months | 16 | 6 | 10–12 | 9 | 30 | **10–12** |

**Converged (5/5) and accepted as a fact for planning:** 4 findings (range 3–7), `repro` 95%, `fix-acceptance` 60–70%, R1 margin ~65%, R3 ~35%, a team of 10–12 person-months, wall-clock cap 8 hours.

**Did not converge: the cost of a finding ($150–10 000) and the price ($2k–25k).** But with five points a structure appears rather than noise:

```
Mode A — "cheap review, many findings"
  R1 $400, R2 $150  ×  4 findings =  $600–1 600 cost
  price $2k–12k                   →  margin 75–87%
  condition: review ≤15 min per finding (card + auto-replay)

Mode B — "expensive review, deep proof"
  R4 $1,8–3,5k, R5 $3 000  ×  4 findings =  $7–14k cost
  price $25k                       →  margin ~44–72%
  condition: senior reviewer, deep validation, enterprise client

Mode C — "the middle" (almost everything lands here by accident)
  $3k × 4 = $12k cost at a $10–12k price         →  margin 0–15%
  R3 plainly: $6–10k × 6 = $36–60k for $10k     →  deeply negative
```

> **The product has two viable modes and one lethal middle.** The choice between A and B is not a question of technology but of what the product is: **review automation** (A) or **depth of proof** (B). An attempt to take the middle yields a $10k report that costs $12k.

**The decision for v1 is mode A**, because A6 (100% human review) is a 5/5 consensus, which means the live throughput constraint is set by reviewer time. Hence the single critical path of the product is not the agent and not the sandbox:

> **A one-page review card with auto-replay and a 15 minute ceiling is the main feature of v1.** It moves mode C into A and changes the margin from 0% to 75%. This is confirmed in two independent ways: by arithmetic (R1: "100% signing as a linear load") and by economics (R5: "manual review eats the margin").

**B3 is rejected as incomparable** — five values from 20 minutes to 4 days mean the metric is again undefined. The pair from §10.3 remains in force: `time-to-validated` ≤6 h, `time-to-signed` ≤48 h.

**B10: 30 person-months from #5** is not an outlier but an honest estimate for a full hybrid with two design partners. This is the third independent confirmation that **the hybrid does not fit into v1**.

## 12.3. Block C: votes on the fatal mechanisms (out of 5)

| Mechanism | Votes | What we decide |
|---|---|---|
| **The oracle does not cover / cannot be sealed** | **4/5** (#1p4, #2p1, #4p1, #5p4) | v1 = 3 classes with ready oracles + human-sealed for the rest. The oracle library is P0 |
| **The environment does not match: the PoC dies at the client** | **3/5** (#1p2, #2p4, #5p3) | the fingerprint is part of the contract; outside it → `HYPOTHESIS` |
| **The economics on heavy findings** | **3/5** (#2p5, #3p3, #4p2) | mode A + a separate tier for heavy classes |
| **Manual review eats the margin** | 2/5 (#1p3, #5p2) | a 15 min review card — the critical path |
| **The repository does not build** | 2/5 (#1p2, #5p1) | a **preflight buildability gate** + a public contract of validatability |
| **The hybrid does not fit into v1** | 2/5 (#4p4, #5p5) | v1 = SaaS with an ephemeral runner; the hybrid is the second release |
| **The ladder sold but not produced** | 1/5 (#4p3) | in v1 we deliver only R0/R1 |

## 12.4. Block D: v1 = six components, a third independent digest gave the same answer

"Keep" votes across five sets: `(1)` 5/5 · `(2)` 5/5 · `(3)` 5/5 · `(12)` 4/5 · `(5)` 3/5 · `(6)` 3/5 · `(4)` 0/5 · `(10)` 0/5 · `(7)(8)(9)(11)` 0/5.

**The v1 core (stable across three independent digests):** microVM · C/T/N · sealed oracle · evidence plane · replay kit · named signatory.

**The dispute about the verifier farm is closed — and this is not a concession but a clarification.** Five out of five cut *the farm as a service* (a scalable multi-tenant verifier, +2–3 weeks). None objected to *the function*: the oracle is executed by a process **outside the agent's VM** and the agent has no write rights into it. This function is a direct consequence of `(3)`, which all five kept. Therefore:

> **A verifier as a separate process outside the sandbox — in v1 (≈3 days). A verifier farm as a service — V2.** I defended the function, they cut the service; both decisions are correct at the same time.

**Canary-nonce has been reclassified: it is not a feature but an acceptance test of the witness plane.** Until the test passes, "an observation outside the agent's control" is not proven, and `PROVEN` remains an assertion. In this form it cannot be argued against: 1 day of work, and its status is a test, not a component.

## 12.5. Block E: 5/5 named one mechanism

All five: **`PROVEN` starvation**. Months 4–6 (2), 6 (1), 10 (2), 12 (1) — median ≈10.

#5 added what nobody else had: death comes not technically but **on the buyer's side** — "coverage without a purchase": the reports are technically correct, but the procurement officer demands *manageable coverage*, and a negative scope does not convince them.

| Indicator (into the dashboard from the first pilot) | Threshold |
|---|---|
| `PROVEN per engagement` | <2 over 10 consecutive engagements |
| `HYPOTHESIS / PROVEN` | >10 |
| requests for a "coverage statement" instead of signing the negative scope | ≥3 of 5 pilots |
| pilot → paid conversion | <20% with ≥5 pilots |

**Consequence for the product:** coverage attestation must be a **positive** statement ("here is what was checked, here is the reproducible proof of the run"), not a negative one ("we found nothing"). The buyer does not accept a negative statement — confirmed by the only reviewer who looked at procurement.

## 12.6. I2: the final formulation (3/5 called it wrong)

Three of five independently said the same thing: the absolute "the same result" is false for stateful, distributed and temporal effects. The best formulation is #5's:

> **I2.** Everything shipped is reproducible **within the declared fingerprint** (images, versions, configuration, seed, network policies, time). Outside the declared fingerprint the status is `HYPOTHESIS`, not `PROVEN`. The claim "it always reproduces" is never made.

This makes the fingerprint a **contractual boundary** of the proof rather than a technical detail. Accepted and incorporated into `00-SYNTHESIS.md`.

## 12.7. Two product artefacts that did not exist before this round

Both came from reviewers, and both are about the product boundary, not about technology.

**1. A public refusal list** (#3): classes we do not sell in v1, even if we find them. Logic/business vulnerabilities without a deterministic oracle — Lane A only, without promises. This is at once a limitation of liability, a proof of honesty and a protection of I1.

**2. A validatability contract** (#5): the minimum input requirements under which a repository is accepted into v1 at all:
- a reproducible build;
- lock files;
- a test command **or** a health oracle;
- an image/runner without secrets.

If something is missing — Lane A only or a refusal. This is a direct answer to the "the repository does not build" mechanism (2/5) and at the same time a **preflight buildability gate** that removes `DEPLOY_FAILED` before it eats the budget.

Both artefacts are published. Together they do what no scanner does: **declare in advance what the product does not undertake to do.**

## 12.8. The round is closed: a summary of decisions

| Decision | Status |
|---|---|
| Product model A1–A12 | 5/5, closed |
| v1 core: 6 components + verifier process + canary as a test | three independent digests, stable |
| v1 = 3 vulnerability classes with ready oracles | 4/5 |
| v1 = R0/R1 | 1/5 explicitly, but a consequence of A8+A3 5/5 |
| v1 = SaaS with an ephemeral runner, the hybrid is the second release | 2/5 explicitly + the B10 arithmetic |
| Mode A (cheap review) as the economic basis of v1 | the arithmetic of five estimates |
| A 15 min review card — the critical path | 2/5 + arithmetic |
| I2 — within the fingerprint | 3/5 |
| C4 — the data contract is laid down in v1 | 1/5, accepted |
| C8 — the verifier under verification | 1/5, accepted |
| The refusal list + the validatability contract | 1/5 each, accepted |

**Not decided by models and going to interviews:**

| # | Question | To whom |
|---|---|---|
| Q1 | Price: mode A ($7,5–12k) or mode B ($25k) | 10 buyer interviews by trigger |
| Q2 | The minimum scope of the hybrid runner that clears the procurement blocker | 2 procurement interviews + 1 dry-run |

**A fifth round is not needed.** Five independent answers gave: 100% agreement on the product model, convergence on seven of ten numbers, 4/5 on the oracle as the bottleneck, 5/5 on `PROVEN` starvation as the death mechanism and 5/5 on the presence of a wrong axiom (even though all five claims turned out to be correct and all were accepted).

Further questions to models will produce ever more confident answers to ever less important questions. **The next step is not text but two interviews and a library of oracles for three classes.**
