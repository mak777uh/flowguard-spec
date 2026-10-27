# FLOWGUARD — master document for external review

**What this is.** One self-contained file: the product, both technical branches, formats, verdict rules, economics, pricing doctrine, the register of claims for criticism, ranked weak points, the list of mandatory measurements, and questions for the next round.
**How to use it.** Feed the whole thing to the model. At the end there is a block, "what is needed from you"; the model will answer in a way comparable with the others.
**Confidence tags:** `[PROVED]` machine-proved · `[MEASURED]` measured/reproduced · `[HYPOTHESIS]` hypothesis, requires verification.
**Fixation date:** v1. All `[HYPOTHESIS]` numbers are planning estimates, not facts.

---

# 0. The product in six sentences

1. We do not hunt for vulnerabilities. We prove that within the **declared closure** value cannot be routed past the single decision point — money, data, access.
2. The claim is bounded: outside the closure the guarantee **does not hold**, and this is written into the artifact, not into the fine print.
3. The claim is **verifiable offline** by a third party, with no trust in us: the verifier and the format are open forever.
4. What is sold is a ladder of fixes: from configuration to a proved core, each rung with a passport — what it closes, what it breaks, what is proved, what remains.
5. The human in the loop is four gates of 10–30 minutes each; everything that produces evidence is done by the machine.
6. The economics are built so that the price **falls** while quality grows; money for development comes from saved person-hours, not from a price increase.

**Two branches, one core.** On-chain (escrow) comes first, because it does not require a microVM and runs on a laptop. Legacy (a service with a database) comes second, because it requires a microVM, eBPF and reproducible deployment.

---

# 1. Common core

## 1.1. Seven entities

| Entity | Meaning |
|---|---|
| **Flow** | the protected flow: a resource from input to output |
| **Resource** | addressable value: escrow balance, ledger row, token |
| **Subject** | the initiator of an action; identified only from a verified source |
| **Policy P** | what is permitted; deny-beats-allow, default deny |
| **Closure Z** | all paths that modify the resource; **a non-empty set of unknown paths forbids `PROVEN`** |
| **EnforcementPoint M** | the single decision point; every path either goes through it or is declared outside the guarantee |
| **Attestation** | a signed bundle: claim + evidence + boundaries |

The domain distinction is isolated by the `subject.kind` field, not by a separate format: `{"kind":"chain.escrow","chain_id":1,"address":"0x…","code_hash":"0x…","block":…,"finality":"FINAL"}` or `{"kind":"legacy.flow","repo":"…","commit":"…","build_cmd":"…","runtime":"…"}`.

Six ports for domain independence: `StateProvider`, `EnforcementPoint`, `ObservationChannel`, `Clock`, `Domain`, `Prover` — two backends for each.

## 1.2. Verdict

```
PROVEN ⟺ attacks_all_blocked ∧ invariants_discharged
        ∧ closure_complete ∧ witness_intact
        ∧ build_reproducible ∧ policy_matches

closure_complete ⟺ unknown_paths = ∅
```

| Value | Condition |
|---|---|
| `PROVEN` | all conjuncts are true |
| `NOT_PROVEN` | the invariant is refuted by a counterexample |
| `INCONCLUSIVE` | insufficient evidence: an unknown path, unavailable bytecode, `PROVISIONAL` finality, timeout |
| `INVALID` | the evidence is broken: code mismatch, reorg, invalid signature |

`PROVISIONAL` is a `finality` field, not a verdict; it is not fit for payouts.
CLI exit codes are part of the contract: `0 PROVEN · 1 NOT_PROVEN · 2 INCONCLUSIVE · 4 INVALID · 5 replay mismatch`.

## 1.3. Format of `flowguard.yml` (abridged, normative)

Rule: unknown fields in `policy`/`closure`/`enforcement`/`evidence` **MUST** be rejected (fail-closed).

```yaml
schema_version: "1.0"
flow: {id: "…", domain: onchain|legacy, assets: [{kind: token|money|data|access, id, criticality}]}
subject: {kind: chain.escrow|chain.contract|legacy.flow, …domain fields…}
policy: {id, version, fail_closed: true, invariants: [id…]}
closure: {declared_paths: […], excluded: [{path, reason}], unknown_behavior: INCONCLUSIVE}
enforcement: {mode: in_process|single_writer|onchain_guard, mediator: {…}, permit: {algorithm: Ed25519, max_ttl_seconds, version_bound: true, domain_bound: true}}
evidence: {observation_channels: […], finality_rule: l1_finalized|l2_optimistic|l2_zk, reorg_behavior: INVALID, prover_backend: […]}
attestation: {expires_after_seconds, signatures_required: 4, signer_roles: […], bundle_format: "fg-bundle/1"}
# FORBIDDEN: secrets; "PROVEN" as input; wildcard trust; excluded without reason;
#            active proxy admin without declaration; database_trigger.enabled=false with placement=library
```

## 1.4. Attestation bundle

One format for both domains. The signature covers **the canonical digest of the whole bundle** (JCS → SHA-256 → Ed25519), not just the verdict.

```
manifest.json · flowguard.yml · subject.json
chain/ (block, finality, state, privileged-paths)   ← on-chain only
closure/ (declaration, discovered_vs_declared, db_principals)
policy/ (rules, invariants, counterexamples)
enforcement/ (mediator source, trigger.sql)         ← legacy only
witness/ (tap, db_digest, identity, acceptance/)    ← legacy only
oracles/ · findings/ (proven.json, hypotheses.json) ← legacy only
proof/ (results, assumptions, counterexamples)
attacks/ (results.json)
replay/ (manifest.json) · verdict.json · signatures/
```

**Hard rules:** `findings/hypotheses.json` is never mixed with `proven.json`; `assumptions.json` requires a `what_breaks_if_false` field on every assumption; the bundle contains no source code of the target, only hashes.

## 1.5. Determinism

`attest` + `replay` on a reference target produce a **byte-for-byte** identical bundle. Timestamps do not enter the signed hash. `verify` makes no network requests. `verify` supports all past versions of the format, forever.

---

# 2. On-chain: escrow

**Why escrow.** A TCB of 250–500 lines, three states, public references, and — decisively — escrow is the first consumer of our own automatic payout (we test the mechanism on the product we sell).

**Why first.** The EVM environment (`anvil`) is an ordinary process and runs on macOS/Linux/Windows. The full cycle "inventory → invariants → 10 attacks → bundle → verify → replay" runs **on a laptop**, without KVM and without an NDA.

## 2.1. Three invariants

| ID | Predicate | Catches |
|---|---|---|
| **INV-1** | `∀a: balanceOf(escrow,a) ≥ Σ_{locked,disputed} amount[a]` and `deposited = released + refunded + Σlocked` | draining, hidden mint/burn |
| **INV-2** | `released[e] + refunded[e] ≤ deposited[e]`; transitions `CREATED→LOCKED→{RELEASED\|REFUNDED\|DISPUTED}`, with no reverse transitions | double payout, refund after release |
| **INV-3** | `release(e) ⇒ LOCKED ∧ att_PROVEN ∧ att.subject=e.subject ∧ recipient/amount match ∧ final(block)` | payout against a foreign or non-final attestation |

**Caveat:** INV-1 holds only for tokens without rebasing and fee-on-transfer. For those there is a separate model; otherwise `INCONCLUSIVE`.

## 2.2. Seven classes of privileged paths

owner/admin/roles · upgrade proxy (EIP-1967) · `delegatecall` · `selfdestruct` · external value calls · keeper/callback · sweep/rescue functions.
Each carries `gaps[]` — "what this method does not see". A path without `gaps` is treated as an analyzer defect.
**An active `proxy admin` ⇒ `INVALID`**, not "covered".

## 2.3. Finality

| Network | Rule |
|---|---|
| L1 | `finalized` checkpoint (≈2 epochs, ~12.8 min). A block counter as the sole criterion — **MUST NOT** |
| L2 optimistic | publication of the batch + finalization of the L1 anchor + an expired challenge period; before the anchor — `PROVISIONAL` |
| L2 zk | the proof is verified on L1 and the L1 block is finalized |
| Reorg between the run and the signature | reconcile `block_hash`; a mismatch → `INVALID` |

## 2.4. Ten attacks

A1 `release` by an unauthorized party · A2 double `release` · A3 `release` before the condition · A4 `release` with an attestation from another escrow · A5 `release` on a `PROVISIONAL` block · A6 `refund` after `release` · A7 withdrawal via `sweep`/`rescue` · A8 role escalation · A9 implementation substitution · A10 drain via an external call/reentrancy.
Attacks are executable scripts, **not an agent**: a non-deterministic check is not a check.

## 2.5. Signatories of the attestation

product owner (multisig) · custody quorum (replaces the infra owner) · security lead · verifier. The developer signs only that the bytecode matches the sources, not the attestation. Minimum closure actions: roles → Timelock ≥48 h, revoke roles from EOAs, `renounce` what is not needed, cancel allowances, verify external value calls.

---

# 3. Legacy: a service with a database

**Why second.** It requires three expensive things: a microVM with KVM on bare metal, a dynamic witness (12 person-days per target), and reproducible deployment of the client's application.

## 3.1. Closure Z: 12 elements

Nine mandatory: synchronous inputs · batch/cron/ETL · admin panel/support/break-glass · backup/restore/replication · all write points (including stored procedures and migrations) · registry of database principals · queues/retries/idempotency · policy configuration · CI/CD and secrets.
Three structural: **the observable layer** (without it, a bypass cannot be distinguished from a failure) · **external credits and provider reconciliation** · **M itself with a signed policy version** (substituting M outside Z makes the claim false).

## 3.2. Seven bypass paths and decisions

| Path | Decision |
|---|---|
| batch/cron/ETL | mediate |
| admin panel/support | mediate + dual control |
| **backup/restore** | **forbid direct restore**: only a signed snapshot + post-check + reissue of the attestation |
| partner/mobile API | mediate, disable old versions |
| **direct database access** | **forbid**; write credentials only for M; break-glass with a log |
| logs/analytics | **forbid writes** into the money path; a PII copy is a separate flow |
| CI/supply chain | **forbid data credentials** + deployment hash check; chain integrity is outside the guarantee |

**Result: all seven are inside the product. Exactly one thing is outside the guarantee — supply-chain compromise**, and that is declared.

## 3.3. Mediator, `Permit`, trigger

```
authorize(subject: VerifiedSubject, action, resource: ResourceRef, store) -> Result<Permit, Deny>
```
Rules: `subject` only from a verified source · the resource owner from a trusted store · `deny-beats-allow`, default deny · version binding (TOCTOU prevention) · the decision is logged before execution, a log failure → `Deny` · `Deny` for a nonexistent object is indistinguishable from `Deny` for someone else's.

`Permit := Ed25519 {subject_id, resource_id, resource_version, action, policy_hash, nonce, exp, domain_id}`.
Claim: `∀ Permit ⟹ P(subject, resource, action)`.

| Stack | Non-transferability mechanism | Strength |
|---|---|---|
| Rust | private constructor, not `Clone` | compiler |
| Java/TS/Python | private constructor + factory | discipline + linter |
| **all** | **PL/pgSQL `BEFORE UPDATE` trigger** | **physical** |

The trigger verifies the signature in `current_setting('app.permit')`, the match of `resource_id` and `version`, and `exp`; without that — `RAISE EXCEPTION`. The application must, in the same transaction, execute `SET LOCAL app.permit = '<b64>'`.

**Placement is a hybrid:** membership/tenant/state transition — an in-process library (a single transaction is needed, small core); amount limit and money — a single service writer. "Single" is logical, not physical: there are many writers, but the trigger will not allow a write without a `Permit`.

## 3.4. Eight invariants

I1 full mediation (reconciliation of the `pgaudit` delta with the `Allow` log) · I2 capability (trigger) · I3 atomicity (fault injection) · I4 no ambient authority (the set of write principals = {M}) · I5 signed deployment · I6 fail-closed audit (chaos test) · I7 version-bound (parallel test) · I8 restore procedure (6 steps).

**A distinction that must not be blurred:** I1, I6, I8 are **not proof but a test**: for an arbitrary system they are unprovable, and they are checked on every run. In the attestation they are marked `[MEASURED]`.

**Two invariants that must be checked separately:** `∀ Permit ⟹ P` ("the mediator does not lie") and `∀ mutation(ledger) ⟹ ∃ Permit ∧ ∃ Allow event` ("nothing got past the mediator"). Without the second, the typical protection remains a library that can simply not be called.

## 3.5. Witness: three channels, two tests

tap on the host (real requests/responses) · DB digest/`pgaudit` (actual writes, with the role recorded) · identity (token → principal). **12 person-days**, wall-clock 5 days in parallel.

**Test A** — integrity: a forged/replayed witness → `INVALID`.
**Test B** — independence: an agent with root cannot disable the channel; disabling → `INVALID`.
**Correction:** a `nonce` catches replay but **does not prove independence** — hence two tests.
Residual boundary: the witness does not protect when the stand itself or the IdP is compromised — that goes into the negative scope.

## 3.6. Oracles and findings

Three classes with a deterministic predicate: **SQLi** (a canary string in the DB digest) · **BOLA/IDOR** (A read/modified B's object) · **path traversal** (access to a marker file outside the root).
`PROVEN` requires `C=false ∧ T=true ∧ N=false` on K fresh VMs. **K is adaptive: 3 by default, escalating to 10 on ambiguity**; K is printed in the bundle.
The oracle emits only `PROVEN_CANDIDATE` for a single check; a dumb deterministic aggregator assembles the composition.
**Business logic without a deterministic oracle is not sold publicly** — only the hypothesis track, free, with no promises.

## 3.7. Seven attacks

A1 direct write under a shared credential · A2 batch over the limit · A3 restore+replay · A4 old version of the partner API · A5 deployment that changes the limit · A6 escalation via the admin panel · A7 replay via a queue/retry.

## 3.8. Attestation: 8 fields, 4 signatures

Fields: `z_id`+hash · flow F · path registry (`resource|path|owner|decision`) · hash of M (code, commit, toolchain, proof hash) · registry of database principals as of the date · method of building the registry · list of "outside the guarantee" with the reason · results of the 7 attacks.

Four signatures, **two of them on the client side**: product owner (product inputs) · **infra owner (batch, DB, CI, backup)** · security lead (credentials) · our verifier (hashes, proof, attacks). Two owners is a direct answer to "you forgot the nightly job".

**The three-day rule:** a new or changed path is outside the guarantee until the attestation is reissued, which is mandatory within 3 business days. During the window the state is `DEGRADED`: new paths are `deny by default`, money paths a full deny.

## 3.9. Break-glass

Mediation is impossible by definition. A hardware key (HSM/YubiKey) is held by the client's CISO, not inside the system. The DBA signs the raw SQL; the database accepts it with the `is_emergency = true` flag; the witness alerts; **the guarantee is suspended automatically** until reconciliation and an incident attestation.

## 3.10. Validability contract

Reproducible build · lock files · a test command or a health oracle · an environment without secrets · pinning of the runtime and configuration. If it does not pass — the hypothesis track only, or a refusal.
These break automation: monorepo · polyglot · no IaC · no tests · generated code >30% LOC.

---

# 4. Economics and pricing doctrine

## 4.1. SKU

| # | SKU | Price | Term | Automation |
|---|---|---|---|---|
| 1 | Basic analysis (flow map + contradictions in the rules) | $2–5k | 3–5 days | 95% |
| 2 | Patches (package) | $5–10k | 2 weeks | 80% |
| 3 | Migration to the mediator | $25–45k | 4–6 weeks | 40% |
| 4 | Guarantee + proof | `clamp(value_at_risk × k, $12k, $250k)` | 45 days | 30% |
| 5 | Re-attestation | included in the subscription | **15 min** | 98% |

The sales order is strictly 1 → 2 → 3 → 4. `k`: 0.60% up to $10M, 0.30% up to $100M, 0.15% above. `value_at_risk` **MUST** be defined as the daily unmitigated flow, not as market capitalization.

## 4.2. Doctrine: lower the price and raise quality at the same time

| # | Rule | How it is checked from outside |
|---|---|---|
| **P1** | **Never a price per finding** — only per scope, change or subscription | public price list; no "per finding" line in the contract |
| **P2** | **Margin ceiling:** services ≤45%, subscription ≤70%; the surplus goes into price reductions or a public fund | published reporting once a year |
| **P3** | **Automation dividend 50/50:** saved person-minutes are split half into price, half into R&D | published `assessor_minutes_per_finding` |
| **P4** | **The price falls on a schedule:** the same scope is no more expensive than a year ago minus 10% | public price index with history |
| **P5** | **No premium for fear:** after an industry incident the price does not change | a before/after incident comparison |
| **P6** | **Critical infrastructure at cost or free** (hospitals, utilities, small OSS) | public list and volume |

**The mechanism (P3) in numbers** `[HYPOTHESIS]`: a review of 6 h → 15 min, 4 findings, $120/h ⇒ `savings = (6 − 0.25) × 120 × 4 = $2 760` per engagement; half into price, half into R&D. **Upgrades are financed from saved person-hours, not from a price increase.**

**Four sources of money for development:** the automation dividend (50% of the savings) · a fixed ≥30% of revenue for R&D (in the articles of association) · grants and public funding (the mission is partly a public good) · 2–3 year prepayment (stable cash flow without a price increase). **None of them requires raising the price.**

**A conditional commitment (the key one):**
> We cut the price by 10% a year for the same scope **provided that `assessor_minutes_per_finding` declines**. We publish that number quarterly. If it fails to decline for two quarters in a row, we publish that and **suspend the price promise**, instead of quietly breaking it.

---

# 5. Register of claims for criticism

**Protocol:** strike by number; the verdict is one of three — `WRONG` (false as formulated) · `UNPROVEN` (may be true, but `[HYPOTHESIS]` passes itself off as fact) · `INCOMPLETE` (true, but the boundary is in the wrong place). Arguing with `[PROVED]` is pointless — the only move is to show that the property proved is not the one claimed.

## 5.1. Core

| ID | Claim | Tag | What breaks it |
|---|---|---|---|
| S1 | What is claimed is not "secure", but "inside the closure nothing can pass the single point" | `[HYPOTHESIS]` | the client will read it as "secure" |
| S2 | The claim is verifiable offline by a third party | `[MEASURED]` | an online key-revocation check will be needed |
| S4 | The domain distinction is isolated by the `subject.kind` field | `[HYPOTHESIS]` | a third dimension will appear that is inexpressible in `subject` |
| S5 | Six ports are sufficient for both domains | `[HYPOTHESIS]` | a port will be needed that does not exist |
| S7 | The signature covers the digest of the whole bundle | `[MEASURED]` | JCS canonicalization will not match across two implementations |
| S9 | The `PROVEN` formula of six conjuncts is correct | `[HYPOTHESIS]` | one conjunct turns out to be unverifiable |
| S10 | `unknown_paths ≠ ∅ ⇒ INCONCLUSIVE` | `[HYPOTHESIS]` | the analyzer will not see a path and will stay silent |
| S14 | Byte-for-byte reproducibility of the bundle | `[HYPOTHESIS]` | non-determinism in analyzers/versions |
| S17 | The LLM does not participate in the verdict | `[HYPOTHESIS]` | an "explanation" will be demanded and will leak into the verdict |
| S18 | The bundle contains no source code of the target | `[MEASURED]` | for legacy a code fragment will be needed in the report |

## 5.2. On-chain

| ID | Claim | Tag | What breaks it |
|---|---|---|---|
| O1 | Escrow is the right first target (TCB of 250–500 lines) | `[HYPOTHESIS]` | real escrows have more branches than the reference |
| O3 | `INV-1` is correct | `[HYPOTHESIS]` | **fee-on-transfer and rebasing break the formula** |
| O5 | `INV-3` covers the precondition of release | `[HYPOTHESIS]` | a partial release will be needed |
| O6 | Seven classes of paths cover the movement of funds | `[HYPOTHESIS]` | a non-standard proxy; an off-chain keeper |
| O8 | L1 finality = `finalized` checkpoint | `[HYPOTHESIS]` | the RPC provider will return a wrong head |
| O10 | The L2 finality rule is implementable as a single predicate | `[HYPOTHESIS]` | every L2 has its own model |
| O11 | 10 attacks are complete for escrow | `[HYPOTHESIS]` | an 11th will be found on a real contract |
| O13 | Attacks A3 and A5 are not tautological | `[HYPOTHESIS]` | the test also passes on a broken version |
| O14 | Four signatories are applicable on-chain | `[HYPOTHESIS]` | an immutable contract has no custody quorum |

## 5.3. Legacy

| ID | Claim | Tag | What breaks it |
|---|---|---|---|
| G1 | The 12 elements of Z are necessary and sufficient | `[HYPOTHESIS]` | a 13th will appear (a third-party SaaS with a shared credential) |
| G4 | All seven paths are inside the product; only the supply chain is outside the guarantee | `[HYPOTHESIS]` | the restore procedure is unfeasible in real IT |
| G6 | `∀ Permit ⟹ P` is proved in Verus in 200–500 lines | `[HYPOTHESIS]` | the contracts will turn out to be more complex |
| G7 | `Permit` in Java/TS/Python is discipline, not a guarantee | `[MEASURED]` | the client will read it as a guarantee |
| G8 | The only physical guarantee is the trigger, and only for the ledger | `[MEASURED]` | migrations and stored procedures bypass the trigger |
| G9 | `∀ mutation ⟹ ∃ Permit ∧ Allow` is checked by `pgaudit` reconciliation | `[HYPOTHESIS]` | a bypass writer writes the `Allow` event as well |
| G11 | DB-level enforcement instead of event sourcing is sufficient | `[HYPOTHESIS]` | horizontal write scaling will be required |
| G20 | I1/I6/I8 are marked `[MEASURED]`, not `[PROVED]` | `[HYPOTHESIS]` | marketing will want "proved" for everything |
| G22 | Witness = 12 person-days | `[HYPOTHESIS]` | one reviewer says 30 — a 2.5× discrepancy is left unexplained |
| G25 | The three classes yield ≥2 `PROVEN` on a typical target | `[HYPOTHESIS]` | **death criterion: median < 2** |
| G26 | Adaptive K (3→10) does not lose reliability | `[HYPOTHESIS]` | **K=3 will produce false `PROVEN` on a flaky effect** |
| G31 | The 3-day rule is feasible under continuous deployment | `[HYPOTHESIS]` | the `DEGRADED` window will open constantly |
| G32 | Splitting Z into a static and a dynamic boundary resolves the conflict with CI/CD | `[HYPOTHESIS]` | the dynamic boundary will require a human as well |
| G33 | 100% review at 3–4 findings is economically survivable | `[HYPOTHESIS]` | **if review takes > 15 min, SKU-1 margin → 0** |
| G34 | Break-glass via HSM + auto-suspension closes the vector | `[HYPOTHESIS]` | the client will refuse auto-suspension |
| G35 | The validability contract cuts off 85% of the market | `[HYPOTHESIS]` | the numbers 25/15/3% are taken at the minimum, not measured |

## 5.4. Economics and pricing

| ID | Claim | Tag | What breaks it |
|---|---|---|---|
| E1 | Basic analysis yields a margin >80% | `[HYPOTHESIS]` | manual exceptions will eat the automation |
| E3 | The guarantee price `clamp(v×k, 12k, 250k)` works at all levels of `v` | `[HYPOTHESIS]` | a 15× spread in estimates, and there is no data |
| E5 | The $500 automatic payout ceiling at launch | `[HYPOTHESIS]` | makes the automatic payout a demo, not a product |
| E6 | Bond + 72 h dispute + ceiling close the risk of an oracle error | `[HYPOTHESIS]` | one bug → a series of clawbacks → the reserve goes negative |
| E11 | On-chain v0.1 works entirely on a laptop without KVM | `[MEASURED]` | the RPC dependency and the size of the fork |
| E12 | Legacy requires KVM, which is why it comes second | `[MEASURED]` | gVisor would provide sufficient isolation more cheaply |
| P-1 | The 45%/70% margin ceiling holds | `[HYPOTHESIS]` | R3/R4 yield 35–40%; if review does not shrink, it is unattainable |
| P-2 | The 50/50 automation dividend is real | `[HYPOTHESIS]` | the savings will go into manual exceptions |
| P-3 | `assessor_minutes_per_finding` is measurable and manageable | `[HYPOTHESIS]` | the metric will turn out to be noisy |
| P-4 | The regression of `k` does not kill the economics of large deals | `[HYPOTHESIS]` | at $v>100M the price is below cost |
| P-8 | ≥30% of revenue for R&D can be locked into the articles of association | `[MEASURED]` | investors will not allow it |
| P-10 | Grant funding is applicable to a commercial company | `[HYPOTHESIS]` | a non-profit arm is needed |

---

# 6. Ranking of weak points (where to strike first)

By "probability of error × cost of error".

| # | What | Related IDs |
|---|---|---|
| 1 | **Incompleteness of the path list** — named first by 5/5 reviewers, not curable in full | S10, O6, G1 |
| 2 | **`INV-1` for fee-on-transfer / rebasing** — the formula is wrong for some tokens, yet looks right | O3 |
| 3 | **Review margin** — $500–1000 of cost per finding at 3–4 findings | G33, E1 |
| 4 | **Guarantee price** — a 15× spread, and the whole model depends on it | E3, E4 |
| 5 | **K=3 produces false `PROVEN`** — adaptive K is a compromise, not a solution | G26 |
| 6 | **The 3-day rule vs 20 deployments/day** | G31, G32 |
| 7 | **`Permit` in dynamic languages** — looks like a guarantee, is discipline | G7 |
| 8 | **L2 finality** — each has its own model | O10 |
| 9 | **Restore in a real outage** — the client will do it directly | G4 |
| 10 | **Blending `proven` and `hypotheses` in the UI** devalues the separation | — |
| 11 | **The $500 automatic payout ceiling** — a demo, not a product | E5 |
| 12 | **Correlated verifier error** — a bond does not protect against a series | E6 |
| 13 | **Death from technical `INCONCLUSIVE`**, not from violations | G25, E10 |
| 14 | **`verify` supports all versions forever** — the cost grows | S16 |
| 15 | **No separation of roles on the client side** — the two signatures may not exist | G30 |

---

# 7. What cannot be resolved by text — only by measurement

| # | Question | How to measure | Days |
|---|---|---|---|
| M1 | The real incompleteness of `scan` | 20 targets: paths found manually vs missed | 5 |
| M2 | The cost of review | minutes per 30 findings | 3 |
| M3 | `proof-fixing` on unfamiliar code | 100 lines in 3 days, extrapolation | 3 |
| M4 | The share of targets that pass the validability contract | preflight on 3×50 repositories | 5 |
| M5 | The median `PROVEN` on a typical target | 12 targets, three classes | 15 |
| M6 | Willingness to pay | 10 interviews by triggers | 10 |
| M7 | The witness discrepancy, 12 vs 30 person-days | a measurement broken down by day | 5 |

**Rule:** no number from `[HYPOTHESIS]` goes into commercial material until the corresponding `M` is closed.

---

# 8. What is deliberately not included

UI, landing page, billing, CRM · bridges, oracles, MEV, tokenomics audit (publicly outside the product) · Windows targets (a separate track, ETW) · multi-cloud and the K8s operator · Certora as the primary backend (commercial, v0.4) · automatic discovery of new attacks by an agent · insurance, legal liability, contract.

---

# 9. What is needed from you

**Do not retell the document.** Answer section by section, briefly.

**A. Criticism.** 7 claims you consider the weakest. Format: `ID | verdict (WRONG/UNPROVEN/INCOMPLETE) | in one line why | what to do`. Priority to sections 5 and 6.

**B. What is missing.** One failure mechanism that is in neither section 5 nor section 6, but which worries you most. Format: `mechanism | on what horizon | how it will show`.

**C. Numbers.** For three numbers from `[HYPOTHESIS]`, give your own value and a way to check it: `assessor_minutes_per_finding`, the median `PROVEN` on a typical legacy target, the share of targets that pass the validability contract.

**D. One "wrong".** What in this document is most likely wrong to the point that the decision must be changed, not refined.

**E. One "do not build".** One observable condition under which the product in this form should not be built at all. Not "difficult" — "should not".

**Answer rules:** no more than 200 words per item · "it depends on the context" is forbidden without a one-line condition · "I don't know" + what you would check it with is allowed and valued · mark numbers as `[estimate]` · do not propose new architectures, only corrections to this one.
