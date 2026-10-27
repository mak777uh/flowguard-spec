# SPEC for critique — flowguard, both branches

**How to use this.** Every claim has a number and a tag. Critique proceeds **by number**, with three verdicts:

| Verdict | Means | What to do |
|---|---|---|
| `WRONG` | the claim is false as formulated | reformulate it or drop it |
| `UNPROVEN` | it may be true, but `[HYPOTHESIS]` passes itself off as fact | lower the tag or assign a measurement |
| `INCOMPLETE` | true, but the boundary is not where it is claimed | widen or narrow the boundary |

**Tags:** `[PROVED]` machine-proved · `[MEASURED]` measured · `[HYPOTHESIS]` hypothesis.
**Rule:** arguing with `[PROVED]` is pointless (show that the property is not the one claimed). `[HYPOTHESIS]` is a legitimate target.

**Numbering:** `S` — common core (both branches) · `O` — on-chain · `G` — legacy · `E` — economics and service.

---

# Part 0. The revolutionary minimum: what is claimed in one phrase

**S1** `[HYPOTHESIS]` The product does not claim “secure”; it claims “within the declared closure you cannot get past the single decision point”.
**S2** `[HYPOTHESIS]` This claim is verifiable by a third party offline, without trusting the issuer.
**S3** `[HYPOTHESIS]` A positive bounded claim sells; a negative unbounded one does not.

---

# Part 1. Common core (both branches)

## 1.1. Format and domain model

| ID | Claim | Tag | How it is checked | What breaks it |
|---|---|---|---|---|
| **S4** | The domain distinction is isolated by the `subject.kind` field, not by a separate format | `[HYPOTHESIS]` | a single `verify` reads both domains | a third dimension appears that cannot be expressed in `subject` |
| **S5** | The six ports (`StateProvider`, `EnforcementPoint`, `ObservationChannel`, `Clock`, `Domain`, `Prover`) are sufficient for both domains | `[HYPOTHESIS]` | two backends for each | a port is needed that does not exist (for example, `Consensus`) |
| **S6** | Unknown fields in `policy`/`closure`/`enforcement`/`evidence` are rejected (fail-closed) | `[MEASURED]` | negative schema test | a legitimate extension breaks compatibility |
| **S7** | The signature covers the canonical digest of the **entire bundle**, not only the verdict | `[MEASURED]` | moving `verdict.json` into a foreign bundle → `INVALID` | JCS canonicalisation will not match between two implementations |
| **S8** | Timestamps are not part of the signed hash | `[MEASURED]` | two runs at different times → identical digest | it will become necessary to prove “existed before a point in time” |

## 1.2. Verdict

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **S9** | `PROVEN ⟺ attacks_all_blocked ∧ invariants_discharged ∧ closure_complete ∧ witness_intact ∧ (build_reproducible) ∧ policy_matches` | `[HYPOTHESIS]` | formal test of the predicate | one of the conjuncts turns out to be unverifiable |
| **S10** | `closure_complete ⟺ unknown_paths = ∅`; an unknown path yields `INCONCLUSIVE`, not `PROVEN` | `[HYPOTHESIS]` | injection of an unknown path → 2, not 0 | the analyser does not see the path and stays silent — then the rule does not fire |
| **S11** | The four verdict values (`PROVEN`/`NOT_PROVEN`/`INCONCLUSIVE`/`INVALID`) are sufficient | `[MEASURED]` | case analysis | a fifth is needed (for example, “partially proved”) |
| **S12** | `PROVISIONAL` is a `finality` field, not a verdict; it is unsuitable for payouts | `[HYPOTHESIS]` | test: PROVISIONAL → payout forbidden | the client starts citing PROVISIONAL as a guarantee |
| **S13** | The return codes (`0/1/2/4/5`) are part of the CLI contract | `[MEASURED]` | CI test for all branches | — |

## 1.3. Determinism

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **S14** | One input → a byte-identical bundle on the second run | `[HYPOTHESIS]` | `attest` + `replay` twice, compare | non-determinism in the analysers or in toolchain versions |
| **S15** | `verify` makes no network requests at all | `[MEASURED]` | network disabled → `verify` works | key revocation checking becomes necessary |
| **S16** | `verify` supports all past versions of the format forever | `[HYPOTHESIS]` | corpus of bundles `fg-bundle/1..N` | the support surface becomes unmanageable |

## 1.4. Security of the tool itself

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **S17** | The agent (LLM) takes no part in reaching the verdict in either branch | `[HYPOTHESIS]` | code inspection: the verdict is assembled deterministically | an “explanation” becomes necessary, and it leaks into the verdict |
| **S18** | The bundle contains no source code of the target, only hashes | `[MEASURED]` | bundle inspection | for legacy a code fragment will be needed in the report |
| **S19** | The content of the target is data, not instructions; in v0.1/v0.2 this is not exploitation of the vector but a consequence of the absence of an LLM from the verdict | `[HYPOTHESIS]` | architecture review | an LLM appears in the loop → the vector returns |

---

# Part 2. On-chain profile

## 2.1. Target and invariants

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **O1** | Escrow is the right first target: TCB of 250–500 lines, 3 states, public references | `[HYPOTHESIS]` | pilot on one contract | real escrows have more branches than the reference |
| **O2** | Escrow is the first consumer of our own automatic payout (dogfooding) | `[HYPOTHESIS]` | — | the commercial automatic payout falls away — the argument disappears |
| **O3** `[PROVED]`-candidate | `INV-1`: `balanceOf(escrow) ≥ Σ locked+disputed` and `deposited = released + refunded + locked` | `[HYPOTHESIS]` | Foundry invariant + Halmos | **fee-on-transfer and rebasing break the formula** |
| **O4** | `INV-2`: `released + refunded ≤ deposited`, the transitions are monotone | `[HYPOTHESIS]` | Foundry invariant | a legitimate partial refund |
| **O5** | `INV-3`: `release ⇒ LOCKED ∧ att_PROVEN ∧ subject/recipient/amount match ∧ final` | `[HYPOTHESIS]` | Foundry + field comparison | a partial release will be needed |

## 2.2. Paths and finality

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **O6** | The seven classes of privileged paths (§8.3) cover the movement of funds in escrow | `[HYPOTHESIS]` | reference contract: 7/7 found | a non-standard proxy; an off-chain keeper |
| **O7** | An active `proxy admin` ⇒ `INVALID`, with no bypass flag | `[MEASURED]` | test with a UUPS proxy | — |
| **O8** | L1 finality = the `finalized` checkpoint; a block count as the sole criterion is forbidden | `[HYPOTHESIS]` | test: a block above the finalized head → `PROVISIONAL` | the RPC provider returns a wrong head |
| **O9** | A reorg between the run and the signature ⇒ `INVALID` | `[MEASURED]` | simulation of a `block_hash` change | — |
| **O10** | The finality rule for L2 (anchor on L1 + challenge period) is realisable in a single predicate | `[HYPOTHESIS]` | 2 L2s in the pilot | every L2 has its own model |

## 2.3. Attacks

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **O11** | The 10 attacks (A1–A10) are complete for escrow | `[HYPOTHESIS]` | 7/10 pass on the broken version | an 11th attack will be found on a real contract |
| **O12** | The attacks are executable scripts, not an agent | `[MEASURED]` | determinism of the run | someone will want “search for new attacks” — and it will count towards the score |
| **O13** | Attack A3 (release before the condition) and A5 (`PROVISIONAL`) are not tautological | `[HYPOTHESIS]` | a contract mutation must break the test | the test passes on the broken version too |

## 2.4. Act

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **O14** | Four signatories for on-chain: product owner, custody quorum, security lead, verifier | `[HYPOTHESIS]` | — | an immutable contract has no custody quorum |
| **O15** | The minimal set of privilege closure (5 actions in §8.3) is sufficient | `[HYPOTHESIS]` | reference: after the 5 actions the path is gone | renounce breaks a mandatory function |

---

# Part 3. Legacy profile

## 3.1. Closure Z

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G1** | The 12 elements of Z are necessary and sufficient | `[HYPOTHESIS]` | pilot: every element confirmed by an incident or a test | a 13th appears (for example, a third-party SaaS with a shared credential) |
| **G2** | The nine mandatory ones are confirmed by 4/4 reviewers | `[MEASURED]` | — | four reviewers could be wrong in the same way |
| **G3** | The three structural ones (the observable layer, external credits, M itself) are derived logically, not by vote | `[HYPOTHESIS]` | — | “external credits” are not universal |
| **G4** | All seven bypass paths are inside the product; only the supply chain is “outside the guarantee” | `[HYPOTHESIS]` | — | the restore procedure turns out to be unworkable in real-world IT |
| **G5** | A direct restore is forbidden; it is permitted only via a signed snapshot + 6 steps | `[HYPOTHESIS]` | acceptance test I8 | during an incident the client will restore directly |

## 3.2. Mediator and Permit

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G6** | `∀ Permit ⟹ P(subj, obj, act)` is proved in Verus in 200–500 lines | `[HYPOTHESIS]` | measurement of proof-fixing | the contracts turn out to be more complex than they look |
| **G7** | `Permit` in Rust is a compiler guarantee; in Java/TS/Python it is **only discipline + a linter** | `[MEASURED]` | the linter lets reflection through | honest, but the client will read it as a guarantee |
| **G8** | The **physical** guarantee is the PL/pgSQL trigger only, and only for the ledger | `[MEASURED]` | a write without `app.permit` → exception | migrations and stored procedures bypass the trigger |
| **G9** | `∀ mutation(ledger) ⟹ ∃ Permit ∧ ∃ Allow-event` is checked by reconciling `pgaudit` against the journal | `[HYPOTHESIS]` | test A1 | a bypass writer writes the `Allow` event as well |
| **G10** | Hybrid placement (in-process for BOLA, single-writer for money) yields minimal residual bypass | `[HYPOTHESIS]` | — | an in-process library can simply not be called; only the trigger saves it |
| **G11** | “Single writer” is logical, not physical; DB-level enforcement instead of event sourcing | `[HYPOTHESIS]` | load test | horizontal scaling of writes will be required |

## 3.3. The eight invariants

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G12** | I1 (full mediation) is checkable automatically | `[HYPOTHESIS]` | delta reconciliation | loss of the journal yields a false “full” |
| **G13** | I2 (capability) is held by the trigger | `[MEASURED]` | test A1 | — |
| **G14** | I3 (atomicity) is checked by fault injection at every step | `[HYPOTHESIS]` | chaos test | a failure at the moment of commit |
| **G15** | I4 (no ambient authority) is checked by a credential scanner | `[MEASURED]` | the principal list = {M} | a new role appears after the scan |
| **G16** | I5 (signed deploy) is held by a CI gate | `[HYPOTHESIS]` | — | CI is compromised |
| **G17** | I6 (fail-closed) is checked by a chaos test | `[MEASURED]` | kill the channel → `Deny` | the channel “fails” silently |
| **G18** | I7 (version-bound) is checked by a parallel test | `[HYPOTHESIS]` | — | — |
| **G19** | I8 (restore) is an acceptance test, not a proof | `[MEASURED]` | 6 steps | — |
| **G20** | I1, I6, I8 are tagged `[MEASURED]`, not `[PROVED]`; the two must not be mixed | `[HYPOTHESIS]` | review of the act | marketing will want “proved” for all of them |

## 3.4. Witness

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G21** | Three channels (tap, DB digest, identity) are the minimum for BOLA | `[HYPOTHESIS]` | test B | without the identity channel, ownership cannot be proved |
| **G22** | The Witness costs 12 person-days, with a 5-day wall-clock under parallelism | `[HYPOTHESIS]` | pilot | 30 days for one reviewer — the 2.5× discrepancy is unexplained |
| **G23** | **Two** acceptance tests are needed: integrity (nonce) and independence | `[HYPOTHESIS]` | both green | — |
| **G24** | `nonce` catches a replay but does not prove the observer's independence | `[MEASURED]` | test B separately | — |

## 3.5. Oracles and findings

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G25** | Three classes (SQLi, BOLA, traversal) with a deterministic oracle yield ≥2 `PROVEN` on a typical target | `[HYPOTHESIS]` | pilot, median | **death criterion: median < 2** |
| **G26** | Adaptive K (3 → 10) reduces cost without loss of reliability | `[HYPOTHESIS]` | comparison of verdicts at K=3 and K=10 | K=3 will produce false `PROVEN` on a flaky effect |
| **G27** | The oracle issues `PROVEN_CANDIDATE` per single check; the aggregator assembles the composition | `[HYPOTHESIS]` | code review | the aggregator starts interpreting |
| **G28** | Business logic without a deterministic oracle is not sold publicly | `[MEASURED]` | public list of refusals | sales will demand “at least something” |
| **G29** | `findings/proven.json` and `hypotheses.json` are never mixed | `[MEASURED]` | intersection test | the client's UI will glue them together |

## 3.6. Act and process

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **G30** | Four signatures, two of them on the client side (product + infra owner) | `[HYPOTHESIS]` | pilot | the client has no role separation |
| **G31** | The rule of 3 working days for reissuance is achievable under continuous deployment | `[HYPOTHESIS]` | 20 deploys/day → how many reissues | the `DEGRADED` window will open constantly |
| **G32** | Splitting Z into a static (infra) and a dynamic (code) boundary resolves the conflict with CI/CD | `[HYPOTHESIS]` | the same test | the dynamic boundary will require a human too |
| **G33** | `human_review_coverage = 1.0` with 3–4 findings is economically survivable | `[HYPOTHESIS]` | measurement: minutes per finding | **if review > 15 min, the SKU-1 margin → 0** |
| **G34** | Break-glass via an HSM key + the `is_emergency` flag + automatic suspension of the guarantee closes the vector | `[HYPOTHESIS]` | test: emergency write → guarantee suspended | the client refuses automatic suspension |
| **G35** | The validity contract (5 requirements) cuts off 85% of the market | `[HYPOTHESIS]` | preflight audit on samples of 50 | the numbers 25/15/3% are taken at the minimum, not measured |

---

# Part 4. Economics and service

| ID | Claim | Tag | Check | What breaks |
|---|---|---|---|---|
| **E1** | Base analysis at $2–5k with 95% automation yields a margin >80% | `[HYPOTHESIS]` | pilot on 3 targets | manual exceptions will eat the automation |
| **E2** | Migration at $25–45k over 4–6 weeks | `[HYPOTHESIS]` | pilot | 35 person-days for 5 policies do not fit |
| **E3** | Guarantee at $48k + $12k/year | `[HYPOTHESIS]` | 10 interviews | the spread of estimates is 15× ($3–78k), there is no data |
| **E4** | The price of the guarantee is tied to the amount at risk, not to the price of the contract | `[HYPOTHESIS]` | — | a client with $50M TVL will not buy at $48k, and we will not sell |
| **E5** | The automatic payout ceiling is $500 at launch, with a ladder up to $25k | `[HYPOTHESIS]` | 100 payouts without disputes | $500 makes the automatic payout commercially pointless |
| **E6** | A 20–25% bond + a 72 h dispute window + the ceiling cover the risk of oracle error | `[HYPOTHESIS]` | simulation of correlated error | one bug → a series of clawbacks → the reserve goes negative |
| **E7** | `assessor_minutes_per_finding` is the right metric, not “cost of a finding” | `[MEASURED]` | — | — |
| **E8** | The OSS core is open forever; what is closed is the service on top, not a fork | `[MEASURED]` | legal review of Apache-2.0 | — |
| **E9** | `verify` is free and requires no server of ours | `[MEASURED]` | offline run | online licence checking becomes necessary |
| **E10** | Death criterion: median `PROVEN` < 2 with a working witness | `[HYPOTHESIS]` | pilot | the threshold was chosen without data |
| **E11** | On-chain v0.1 runs entirely on a laptop without KVM | `[MEASURED]` | macOS + Linux run | RPC dependency and fork size |
| **E12** | Legacy requires KVM and microVMs, which is why it comes second | `[MEASURED]` | — | gVisor will provide sufficient isolation more cheaply |

---

# Part 5. Ranking of weak points (where to strike first)

The order is by “probability of error × cost of error”.

| # | What | Why first | Related IDs |
|---|---|---|---|
| 1 | **Incompleteness of the path list** | 5/5 reviewers named it first; it cannot be fully cured | S10, O6, G1 |
| 2 | **`INV-1` for fee-on-transfer / rebasing** | the formula is simply wrong for some tokens, yet it looks right | O3 |
| 3 | **Review margin** | $500–1000 of cost per finding at 3–4 findings | G33, E1 |
| 4 | **Price of the guarantee** | a 15× spread, no data, and the whole model depends on it | E3, E4 |
| 5 | **K=3 produces false `PROVEN`** | adaptive K is a compromise, not a solution | G26 |
| 6 | **The 3-day rule vs 20 deploys/day** | the `DEGRADED` window may open constantly | G31, G32 |
| 7 | **`Permit` in dynamic languages** | it looks like a guarantee, it is discipline | G7 |
| 8 | **L2 finality** | every L2 has its own model; one predicate may not cover them | O10 |
| 9 | **Restore in a real incident** | the client will restore directly | G5 |
| 10 | **Overlap of `proven` and `hypotheses`** | gluing them together in the UI devalues the separation | G29 |
| 11 | **The $500 ceiling** | the automatic payout becomes a demo, not a product | E5 |
| 12 | **Correlated verifier error** | the bond does not save you from a series | E6 |
| 13 | **Median `PROVEN` < 2** | the death criterion may fire on technical `INCONCLUSIVE` results | G25, E10 |
| 14 | **`verify` supports all versions forever** | the cost of support grows | S16 |
| 15 | **No role separation on the client side** | the client may not have the two signatures | G30 |

---

# Part 6. What is deliberately NOT included

So that what is absent is not criticised as forgotten:

- UI, landing page, billing, CRM.
- Bridges, oracles, MEV, tokenomics audit (publicly outside the product).
- Windows targets (a separate track, ETW).
- Multi-cloud and the K8s operator.
- Certora as the primary backend (commercial, v0.4).
- Automatic search for new attacks by an agent (only reproducible scripts count).
- Insurance, legal liability, the contract (outside the technical spec).

---

# Part 7. What cannot be settled by text — only by measurement

| # | Question | How to measure | Days |
|---|---|---|---|
| M1 | The real incompleteness of `scan` on someone else's code | 20 targets: the share of paths found manually and the share missed | 5 |
| M2 | The real cost of review | measurement of minutes across 30 findings | 3 |
| M3 | `proof-fixing` on unfamiliar code | 100 lines in 3 days, extrapolated | 3 |
| M4 | The share of targets that pass the validity contract | preflight on 3×50 repositories | 5 |
| M5 | Median `PROVEN` on a typical target | 12 targets, three classes | 15 |
| M6 | Willingness to pay | 10 interviews on triggers | 10 |
| M7 | The witness discrepancy, 12 vs 30 person-days | one measurement broken down by day | 5 |

**Rule:** no number from `[HYPOTHESIS]` goes into commercial material before the corresponding `M` is closed. This is the only rule I propose not to discuss.
