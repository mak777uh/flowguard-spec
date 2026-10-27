# 31. Round 4: synthesis across streams (4 responses)

> The first round in which the product was designed not as a "proven bug" but as a **guarantee for a defended flow**. Four independent responses.
> Synthesis rules: for composition — intersection; for TAM — minimum; **for cost — maximum**; the closure block is the veto zone.

---

## 1. Main result: the pilot converged perfectly

| Source | Days | Person-days |
|---|---|---|
| №1 | 45 | 25 |
| №2 | 45 | 24 |
| №3 | 45 | 24 |
| №4 | 45 | 23 |

Four out of four: **45 calendar days, 23–25 person-days**. This is the strongest consensus across all four rounds — stronger than for vulnerability classes (4/6) or for the contract (5/6). That means **the pilot is already planned and needs no discussion**. The number is accepted as is: **45 days / 24 person-days**.

---

## 2. Closure Z: 9 mandatory elements + 3 structural ones

The intersection of the four lists (№1 has 9, №2 — 10, №3 — 10, №4 — 10).

### Mandatory minimum (4/4, veto zone)

| # | Element | "Otherwise false" |
|---|---|---|
| 1 | Synchronous ingress: API, web, mobile, partner, webhooks | otherwise a transfer without check P |
| 2 | Batch / cron / ETL of money operations | otherwise a background write bypassing M |
| 3 | Admin console, support tools, break-glass | otherwise a privileged bypass |
| 4 | Backup, restore, replication, failover | otherwise a rollback or duplication of the balance |
| 5 | All write points into the ledger/balance, including stored procedures and migrations | otherwise a bypass via SQL |
| 6 | Registry of DB principals with write rights | otherwise a shared account writes bypassing M |
| 7 | Queues, retries, idempotency | otherwise a repeat executes without a state check |
| 8 | Policy configuration: limits, flags, override + who changes them | otherwise the limit is changed without reissuing P |
| 9 | CI/CD, secrets, deployment of M and migrations | otherwise code goes to prod that does not match the proven one |

### Three additions backed by one vote each, but logically mandatory

| Element | Who | Why we include it despite 1/4 |
|---|---|---|
| **Observable layer** (tap, DB digest, identity log, M events) | №4 | without it one cannot distinguish a bypass from a failure — that is, Z itself is unverifiable |
| **External credits and reconciliation from the provider** | №3 | incoming money is also a ledger write, and no other response named it |
| **M itself with a signed policy version** | №4 (partly №1) | if M can be substituted outside Z, "no bypass" is false by definition. In №1 this is expressed as "immutable policy hash" in the CI element |

**Total: Z = 12 elements.** Nine mandatory, three structural. The last three are not put to a vote — they follow from the logic of the statement itself.

---

## 3. The declaration artifact: 8 fields, 4 signatures with separation of responsibility

All four gave 8 fields, the composition is almost identical. The synthesis is the best part of two: №3 separated responsibility **by type of statement**, №4 — **by system owner**.

| Field | Content |
|---|---|
| `z_id`, version, artifact hash | identification and integrity |
| Flow F | operations, data, owners, success criterion |
| Path registry: `resource \| path \| owner \| decision` | mediate / forbid / out of guarantee |
| M hash: code, commit, toolchain, proof hash | what exactly is proven |
| Registry of DB principals and their rights as of the signing date | who could write bypassing |
| Method of building the registry | rights audit + 14 days of DB audit + 30 days of ingress logs `[estimate]` |
| List of "out of guarantee" with a reason for each line | negative scope |
| Red-team results with date and M version | confirmation of closure |

**Four signatures, each responsible for one statement** — this is the round's best finding on responsibility:

| Signatory | Responsible for |
|---|---|
| **Client product owner** | completeness of the registry of **product** ingress (API, UI, partner) |
| **Client infra owner** | completeness of the registry of **infrastructure** paths (batch, DB, CI, backup) |
| **Client security lead** | registry of credentials and DB principals |
| **Our lead verifier** | M hashes, the proof, attack runs |

Two owners on the client side, not one — because batch, DB and CI belong to infrastructure, not to the product, and a product CTO physically does not know about the night job. This was the main risk of "batch was forgotten".

**Contractual limitation** (merged from №4 and №3):

> The guarantee applies only to the paths listed in Declaration Z version N. A path that appears or changes after signing is out of guarantee **until the Declaration is reissued, which is mandatory within 3 working days** from the moment the boundary changes.

The three-day rule is an operational mechanism: without it the artifact becomes stale at the moment of signing.

---

## 4. The mediator: consensus on the contract + one idea that changes everything

### 4.1. What converged (4/4)

1. The subject comes **only** from a verified token/IdP; the owner field from the request body is ignored.
2. The owner of the object comes from a trusted store, not from the client.
3. `deny-beats-allow`, default deny, absence of data → `Deny`.
4. Binding to the object version; check and modification are atomic (TOCTOU prevention).
5. The decision is logged (in №4 — a signed event **before** execution).

### 4.2. The idea nobody else had: `Permit` as a non-transferable type

№3 formulated what the whole architecture was missing:

> `Permit` is a non-transferable type, and the data layer accepts an operation **only** with it.

This moves bypass from the plane of policy to the plane of the **type system**: a write without `Permit` does not compile. That is:

- "to bypass the mediator" becomes a **typing error**, not a violation of regulations;
- this is exactly the object-capability model ("no right — no interface") in a concrete implementation;
- the proof reduces to a single statement, which №3 also wrote: `∀ Permit ⟹ P(subj, obj, act)`.

**Accepted as a mandatory design property**, not as a recommendation. Without it, the mediator is a check that can simply not be called.

### 4.3. Two consequences from №3 that also go into the spec

- **`Deny` for a non-existent object is indistinguishable from `Deny` for someone else's** — otherwise the mediator itself becomes an oracle for enumeration.
- **Log failure → `Deny`**. A mediator that keeps working when the audit is unavailable is not a reference monitor.

### 4.4. Placement: a hybrid, not a single option

All four tables agree on the trade-offs. The hybrid was proposed by №3, and it is the only one consistent with the proof:

| What we control | Where | Why |
|---|---|---|
| Object ownership, tenant, state transition | **in-process library** | needed in the same transaction as the operation (TOCTOU), small core — cheap to prove |
| Amount limit and the money itself | **a single writer service** | one writer = one write path; migration is expensive, but bypass is closed by revoking credentials |

The residual bypass is the same in all four options: **direct DB access**. Therefore "revoking write credentials from everyone except service M" is not a finishing touch but a **condition for the existence of the closure**.

---

## 5. Five policies: 20 days at the median, 35 at the maximum

| Policy | №1 | №2 | №3 | №4 | Median | Plan (max) |
|---|---|---|---|---|---|---|
| Tenant isolation | 2 | 2–5 | 6 | 2 | 2 | 6 |
| Object ownership | 6 | 3–6 | 6 | 5 | 5.5 | 6 |
| Amount limit | 3 | 2–4 | 8 | 2 | 3 | 8 |
| PII class | 4 | 3–6 | 10 | 4 | 4 | 10 |
| State transition | 5 | 3–7 | 6 | 6 | 5.5 | 6 |
| **Total** | 20 | 13–28 | **35** | 19 | **≈20** | **35** |

By the "for cost — maximum" rule: **five policies = 35 person-days**. But the pilot needs two (ownership + limit) → **14 days maximum, 9 at the median**.

№3 is systematically 1.5–2 times higher than the others; it is also the only one that accounts for overflow in limit arithmetic and for "all serializers" for PII. It seems the three responses counted the happy path, while №3 counted the real scope. We accept it as the upper bound.

---

## 6. Seven bypass paths: none received 4/4 "out of guarantee"

| Path | Mediate | Forbid | Out of guarantee | **Decision** |
|---|---|---|---|---|
| Batch / cron / ETL | **4** | — | — | **mediate** |
| Admin panel / support | **4** | — | — | **mediate** + dual control |
| Partner / mobile API | **4** | — | — | **mediate**, disable old versions |
| Direct DB access | — | **4** | — | **forbid**, write credentials only for M, break-glass with logging |
| Backup / restore | — | 2 | 2 | **forbid direct restore**; only a signed snapshot + post-reconciliation + reissue of the act |
| Logs / analytics | — | 2 | 2 | **forbid writing into the money path**; a PII copy is a separate flow F, sold separately |
| CI / supply chain | 1 | 1 | 2 | **forbid data credentials** + deploy hash check; compromise of the chain is out of guarantee |

**Total: all seven inside the product, zero "out of guarantee" at the path level.** This is stronger and more honest than declaring part of it out of scope.

The reason: "out of guarantee" for restore would mean that the most dangerous operation (returning an old state with balances) is not covered — and that is exactly the scenario the product exists for. Instead, restore is **forbidden as a direct path** and permitted only through the act-reissue procedure: it is more expensive, but it leaves no hole.

The only thing that remains out of guarantee is **compromise of the supply chain**, and this is stated explicitly: CI has no data credentials (that is, it cannot move money), but the integrity of the build tools themselves is not proven.

---

## 7. SKU: the structure converged, the prices did not

| | №1 | №2 | №3 | №4 | Median |
|---|---|---|---|---|---|
| A. Diagnostics | $9k / 14 days | $2–4k / 5–10 days | $7.5–12k / 2–3 weeks | $9.5k / 10 days | **$9k / 10–14 days** |
| B. Migration to M | $18k / 30 days | $5–10k / 10–20 days | $25–45k / 6–8 weeks | $39k / 30 days | **$27k / 30 days** |
| C. Guarantee | $35k/year / 45 days | $3–7k / 7–15 days | $30–60k + $10–15k/year | $78k / 45 days | **$45k + $12k/year** |

**Converged:** the sales order (4/4 — diagnostics first), and the ratio B ≈ 2–4× A, C ≈ 1.5–2× B.

**Did not converge:** the absolute prices, a 5× spread on B and 15× on C.

**One error that has to be named:** in №2 the price of the guarantee ($3–7k for 7–15 days) is **below its own cost** — he himself estimated the proof at 15 person-days (≈$12k at $80/h). Such a price can only be sold as a loss leader, and if that is the strategy, it must be named a strategy, not a price list.

**Accepted for planning:** A $9k, B $28k, C $48k + $12k/year. Prices are hypotheses, verified by interviews, but **the structure and the sales order are a decision**.

---

## 8. The dispute about the witness price is closed by the figures: 11–12 days

This was the main open question from the previous round (a spread of 9–30 days).

| Channel | №1 | №2 | №3 | №4 | Median |
|---|---|---|---|---|---|
| Network tap | 5 | 3 | 4 | 5 | **4.5** |
| DB digest | 4 | 3 | 3 | 6 | **3.5** |
| Identity | 3 | 3 | 3 | 4 | **3** |
| Package stitching | — | — | 1 | — | 1 |
| **Total** | **12** | **9** | **11** | **15** | **11.5** |

**Planning value: 12 person-days, 5 days wall-clock with parallel work on the channels.**

The previous estimate of "30 days" (the only response with a breakdown by channel in the previous round) was not confirmed: the figures from four independent sources give 11–12. That response was not maliciously inflated but counted a different scope — probably including fixing observability issues and the client granting access. That is a separate line: **+2–5 calendar days for waiting on access, not person-days.**

**Consequence: my decision "phase 1 = 45 days" was based on a single number and turned out to be wrong.**

```
corpus 5 + oracle 8 + witness 12 + runs 4 + re-check 2 + verifier/aggregator 3 = 34 days
```

**Phase 1 = 5 weeks (35 days), not 45.** I roll back the previous decision.

---

## 9. The mediator proof: 24 days, and 40% of them are proof-fixing

| Stage | №1 | №2 | №3 | №4 | Plan (max) |
|---|---|---|---|---|---|
| Specification | 4 | 3 | 3 | 5 | 5 |
| Annotations | 8 | 4 | 6 | 7 | 8 |
| **Proof-fixing** | 10 | 6 | 10 | 9 | **10** |
| Acceptance | 3 | 2 | 3 | 3 | 3 |
| **Total** | 25 | 15 | 22 | 24 | **26** |

Median 23, plan 26. The main point: **proof-fixing is 40% and it is the least predictable**. This is the line item because of which formal verification budgets explode, and no response was able to give a narrow range for it (6–10 days for an estimate of 500 lines).

Practical conclusion: **a proof cannot be sold at a fixed price**, only as an SKU with a budget ceiling and a stop rule. №2 is the only one that referenced a study of Dafny cases: the cost of specification and verification is comparable to implementation and testing. This confirms the order of magnitude: 24 days for the proof versus ~5 days for implementing 500 lines — a ratio of ~1:5.

---

## 10. The "do not sell" condition: 4/4 about one thing, a metric in one

| | Condition |
|---|---|
| №1 | >1 unaccounted ingress that the client neither includes nor closes |
| №2 | within 6 weeks the client cannot provide a complete list of state-changing paths |
| №3 | the audit finds an unaccounted writer at ≥3 of 5 clients |
| №4 | the share of money mutations without a signed `Allow` event > 0 and is not eliminated within 5 days |

All four are about one thing: **if the boundary cannot be enumerated, the guarantee cannot be sold**. №4 supplied what was missing: a **measurable metric**.

**Merged condition:**

> The guarantee is not sold if the pre-sales audit (≤6 weeks) finds at least one state-changing path that is not entered in the registry and is not closed within 5 working days. Metric: `mutations without an Allow event / all mutations` must be **exactly 0** before signing. If this is not achieved at ≥3 of 5 clients, the product in its current form does not scale.

---

## 11. What changes in previously accepted decisions

| Decision | Was | Became |
|---|---|---|
| Phase 1 (oracles, three classes) | 45 days | **35 days** (§8) |
| Witness plane | 20 days, plan | **12 days actual, 5 days wall-clock** |
| Unit of work | a finding | **flow + guarantee** |
| "Out of guarantee" class for restore/CI | under consideration | **rejected**: restore is forbidden as a direct path, CI has no data credentials |
| Mediator | a check that is called | **`Permit` as a non-transferable type** — bypass becomes a typing error |
| Flow-product pilot | was not planned | **45 days / 24 person-days, 4/4** |
| SKU | diagnostics → patches | **diagnostics → migration to M → guarantee** |
| Z signatures | 1–3 without separation | **4 signatures: product owner, infra owner, security lead, verifier** |

---

## 12. Bottom line: what can be built

**Ready to implement without further questions:**

- Z of 12 elements + an artifact of 8 fields + 4 signatures + the 3-day rule;
- the mediator contract with the `Permit` type and hybrid placement;
- 5 policies with prices (14 days for the two needed for the pilot, 35 for all of them);
- decisions on 7 paths (4 to mediate, 3 "forbid + compensation");
- witness 12 person-days;
- the proof 24 days with a mandatory budget ceiling;
- the pilot 45/24;
- the refusal condition with a metric.

**Remaining as hypotheses:** prices (interviews are needed), proof-fixing on someone else's code (a measurement is needed: 100 lines in 3 days), the share of clients able to enumerate the boundary.

**What this means in substance.** Four independent responses planned the pilot identically — 45 days, 24 person-days. This has ceased to be an estimate. The product "guarantee for a flow" now has: a defined unit of work, a verifiable closure, a provable mediator with type-level protection against bypass, seven resolved paths, a price in days and a stop condition. What follows is not questions but the first client with a money flow and a signature from the infrastructure owner.
