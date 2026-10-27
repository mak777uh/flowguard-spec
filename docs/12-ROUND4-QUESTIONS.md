# 12. Fourth round: protected flows — closure, mediator, price in days

> **What is new.** Three rounds designed the product as a "proven bug". A different unit of work has appeared: the **protected flow** (money, PII, traffic, storage access) and a guarantee on it. This answers the main death mechanism from the second round (starvation of `PROVEN`): a guarantee on a flow is a positive, bounded, checkable claim, not "we did not find".
> **Two blocks** close what has remained unresolved: the price of the witness (a spread of 9–30 days for the same channels) and the price of the mediator proof.
> **We do not re-ask about Block A and the classes** — closed (5/5 and 6/6).

---

# PART 1. PROMPT (copy in full, do not change between runs)

## Role and rules

You are an engineer who turns an idea into an implementable plan. What is wanted from you are **artifacts**, not opinions.

1. An answer = a finished artifact (list, table, specification, plan). Reasoning — no more than one line per item.
2. **No more than 150 words** per answer, except where a table is required.
3. Do not dispute what has been decided (see below). Do not propose new architectures.
4. "It depends on the context" is forbidden without a one-line condition.
5. If you do not know — `I don't know` + what you would check it with and in how many days.
6. Numbers — with `[estimate]`. Metrics — with a definition.

## What is already decided (do not revisit)

**Product v1 (three rounds of review):**
- a finding = `PROVEN` only after triple control `!C ∧ T ∧ !N`, the witness outside the agent's VM, a human signature;
- three classes: SQLi, IDOR/BOLA, path traversal;
- the oracle runs outside the VM; the keys are held by the verifier; canonical JSON, SHA-256, Ed25519, timestamps are not part of the hash;
- minimum witness for BOLA: network tap + DB digest + independent identity;
- 3–7 findings per engagement, price $7,5–12k, R1 margin ~65%;
- the fatal risk: starvation of `PROVEN` due to the absence of machine oracles;
- remediation levels R0 (mitigation) … R5 (verified core).

**The new direction that has to be designed.** The unit of work is the **protected flow F**: a valuable resource (money, PII, tokens, traffic, storage access) along the whole path from entry to exit. The product asserts not "there are no bugs", but:

> **For flow F and policy P a mediator M is designated; it is proved that M implements P; and it is proved, or demonstrated by the red team, that in closure Z there is no path bypassing M. Outside Z the guarantee does not hold.**

Three levels, of which two are provable:
- **A — policy:** contradictions, implicit allows, a delegation cycle, deny-beats-allow. SMT, cheap.
- **B — mediator:** the code refines the policy, without TOCTOU. Verus/Dafny/SPARK, the mediator is small (hundreds of lines).
- **C — closure:** that nothing goes past the mediator. **Not provable** for a cloud application — only measured by an ingress audit and the red team.

Seven known paths for bypassing the wrapper: batch/cron/ETL · admin console/support · backup and restore · partner/mobile API · direct DB access with a shared credential · logs and analytics with a copy of PII · CI and supply chain.

---

## BLOCK 1 — Closure Z (the weakest point of the idea)

**1.1.** For the "money" flow (balance, transfer, limit), list the **minimal closure Z**: 7–10 elements, each one 'what must be inside, otherwise the assertion "there is no bypass" is false'. Format: a numbered list, one line per element. `[list]`

**1.2.** How should Z be declared so that a year later the client does not say "but you forgot the batch job"? Describe an **artifact** (its fields and who signs it), not a principle. Format: 6–8 fields of the artifact + one wording of the contractual limitation. `[artifact]`

**1.3.** Five red-team attacks on the closure that **must fail** for Z to count as verified. For each: what it attacks, how it is caught, what counts as a failure. Format: a table of 5 rows. `[table]`

---

## BLOCK 2 — Mediator M

**2.1.** Specify the mediator for ownership control (BOLA/ownership) in such a way that it can be proved: the interface, what it decides, where it takes the subject from, where the object from, where it makes the decision. Format: signature + 6 lines of contract. `[specification]`

**2.2.** Five typical policies that cover ~80% of real flows (for example: tenant isolation, object ownership, amount limit, PII class, permitted state transition). For each: whether it is provable by an SMT check, whether a proof harness is needed, how many days `[estimate]`. Format: a table `policy | SMT | harness | days`. `[table]`

**2.3.** Where the mediator should physically sit: sidecar · API-gateway · in-process library · separate service. For each: what is provable more cheaply, what is more expensive in migration, what bypass path remains. Format: a table of 4 rows. `[table]`

---

## BLOCK 3 — Seven bypass paths

**3.1.** For each of the seven paths (batch · admin panel · backup · partner API · direct DB access · logs/analytics · CI): choose one — **mediate / forbid / declare outside the guarantee**, and why in one line. Format: a table of 7 rows. `[table]`

---

## BLOCK 4 — Economics and falsification

**4.1.** What is sold in v1 and in what order: (a) diagnosis with oracles, (b) migration to the mediator, (c) a guarantee with a proof. Give a **SKU with a price and a term** for each, and state what is bought first. Format: 3 lines `SKU | price [estimate] | term | what is proved`. `[SKU]`

**4.2.** The kill condition **for the flow product** (not for the scanner): one observable condition under which the guarantee on a flow should not be sold at all. Format: one sentence + how to detect it within 6 weeks. `[condition]`

**4.3.** A pilot plan over **45 days** (not 30): one flow, one mediator, one closure. Format: 6 lines `days | what | resource`, total ≤45 days and ≤25 person-days. `[plan]`

---

## BLOCK 5 — Closing the price spread (this is not an opinion, but hard data)

**5.1.** The witness plane for BOLA, three channels (tap, DB digest, identity): give a **day-by-day breakdown** — what exactly the engineer does on each of the days, so that the total is not "12" and not "30" but a verifiable number. Format: a table `channel | day 1 | day 2 | … | total`. If a day cannot be described by work — do not count it. `[breakdown]`

**5.2.** The proof of a mediator of ~500 lines (policy + code) in Verus/Dafny/SPARK: a breakdown of **spec / annotations / proof-fixing / acceptance** in person-days. Format: 4 lines + total. `[breakdown]`

---

# PART 2. HOW TO CONSOLIDATE (do not show to the models)

## 2.1. What counts as a strong answer

| Question | Strong | Not credited |
|---|---|---|
| 1.1 | 7–10 elements, each with "otherwise false" | "API, DB, network" without justification |
| 1.2 | artifact fields + who signs | "a contract is needed" |
| 1.3 | 5 attacks × (what / how caught / failure) | "run a pentest" |
| 2.1 | signature + contract | "the mediator checks permissions" |
| 2.2 | a table with days | a list of policies without numbers |
| 2.3 | 4 rows with the residual bypass | "gateway is better" |
| 3.1 | 7 decisions, each one of the three | "mediate everything" |
| 4.1 | 3 SKUs + what comes first | "sell it as a package" |
| 4.3 | 6 lines, total ≤45 | "do a pilot" |
| 5.1 | by day, with work in every day | a total without hard data |
| 5.2 | 4 lines with numbers | "it depends on the code" |

## 2.2. Consolidation rules

- **Priority — §5.** Block 5 exists in order to kill the spread with hard data. An answer where 5.1 is given without a day-by-day breakdown does not go into the price consolidation, even if the rest is good.
- **For cost we take the maximum, for TAM the minimum.** These are different directions of conservatism: underestimating TAM is cheaper than underestimating the term.
- **Block 1 is a veto zone.** If ≥3 models call the same closure element "mandatory, otherwise the assertion is false" — it enters the mandatory minimum regardless of cost.
- **Block 3 is decided once.** Any path that ≥4 models leave "outside the guarantee" is declared outside the product publicly.

## 2.3. Red flags

1. 1.1 gives elements without "otherwise false" → the closure is not designed but merely enumerated.
2. 3.1 "mediate" for all seven → it does not understand that part of the wrapper cannot be mediated, and the closure will be false.
3. 5.1 without a day-by-day breakdown → the price is not closed, block 5 has failed.
4. 4.3 total > 45 days → the plan does not fit, the answer is not credited.
5. 4.2 "if we do not find clients" → it does not know how to falsify the product.
6. Any answer that re-argues the classes or the contract → lower confidence in the whole answer (three rounds have already closed this).

## 2.4. What we do with the result

| Outcome | Action |
|---|---|
| Closure elements named by ≥3 → mandatory minimum Z | into the closure declaration artifact |
| Five red-team attacks → intersection | into the pilot's acceptance set |
| Policies with day estimates | into the calculation of the guarantee price |
| Mediator placement → compatibility with 2.2 | into the architecture |
| Decisions on the seven paths | into the product's public negative scope |
| Breakdown 5.1 → median | **closes the 9 vs 30 days dispute**, we put it in the plan |
| Breakdown 5.2 → first estimate of the proof price | decides whether R5 is sold as a product |

## 2.5. When the fourth round is closed

Closed when there are: (a) a minimal Z with a justification for each element, (b) the artifact declaring Z and who signs it, (c) a mediator specification + 5 policies with prices, (d) decisions on the seven paths, (e) three SKUs with prices and a sales order, (f) two day-by-day breakdowns closing the price dispute, (g) a 45-day plan ≤25 person-days.

After this — implementation. The next round of questions will be a sign that we have not started building.
