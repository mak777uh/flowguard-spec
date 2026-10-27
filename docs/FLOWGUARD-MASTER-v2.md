# FLOWGUARD — master document v2

**What this is.** A self-contained file for external review: the product, both branches, formats, verdicts, the economics, the pricing doctrine, the claim registry, known weaknesses, mandatory measurements, questions.
**What is new in v2.** The first round of five reviews closed some of the claims and exposed three failure mechanisms that v1 did not have. Everything below has been rewritten with that in mind; at the end there is a new set of questions.
**Tags:** `[PROVED]` machine-proven · `[MEASURED]` measured/reproduced · `[HYPOTHESIS]` hypothesis.
**All `[HYPOTHESIS]` numbers are planning estimates, not facts.**

---

# 0. What changed after the first round

| Found by review | Votes | How it was fixed in v2 |
|---|---|---|
| **`unknown_paths = ∅` does not prove the absence of a bypass** — only the absence of one in the analyser's model | **5/5** | A coverage scalar and the relativity of the verdict were introduced: `PROVEN(R)` with measured recall. See §1.2 |
| **`INV-1` is false for fee-on-transfer/rebasing** | 4/5 | Behavioural token preflight; non-standard token → `INCONCLUSIVE`. §2.1 |
| **"Physical guarantee" is the wrong word**: the trigger can be switched off, it covers only UPDATE, and it is bypassed by replication and by superuser | 4/5 | Triggers on all of DML + DDL-event, delta hash in `Permit`, superuser monitoring, logical replication prohibited. The word "physical" has been dropped. §3.3 |
| **Reconciling `pgaudit` with `Allow` does not distinguish a bypassing writer** | 4/5 | `Allow` must be bound to the `Permit` signature (nonce+version), reconciled in one transaction. §3.4 |
| **K=3 gives no statistical guarantee against flake** | 4/5 | K≥5 by default, K=10 when the flake rate is unknown; a published upper FP bound per oracle. §3.6 |
| **15 minutes per review is unproven** | 3/5 | Planning value **35–40 min**; 15 is a target, not a fact. SKU-1 with pass-through of review cost until M2 closes. §4 |
| **The pricing formula has no empirics, and the $12k floor is below witness cost** | 4/5 | Price with a confidence interval on `v`; refusal when the spread is >3×; ceiling lowered to **$50k** for v1. §4.1 |
| **The death criterion measures the wrong thing** — zero finding output is a success for a guarantee | 3/5 | Metrics separated: finding yield (SKU-1) and the share of targets with `closure_complete` (SKU-4). §6 |
| **Toolchain and signer compromise** — a signature proves integrity, not truth | 2/5 (new) | New section §5.5, mechanism `T1` |
| **Policy drift** — we prove "conforms to P", not "P conforms to intent" | 1/5 (new) | Mechanism `T2` |
| **Vacuous `PROVEN`** — the client itself chooses Z and P, and it is in its interest to narrow them | 1/5 (new) | Mechanism `T3` + `excluded` ceiling + a minimum set of invariants |
| **The word `PROVEN` means three different things** | 1/5 (new, destructive) | Separated: `PROVEN`/`ENFORCED_TESTED` for the verdict, `CONFIRMED`/`HYPOTHESIS` for findings. §1.2 |
| **Four manual gates are incompatible with CI/CD** | 2/5 | Manual gates only at onboarding; at runtime, a fail-closed machine. §1.6 |

---

# 1. Core

## 1.1. Seven entities

**Flow** (the protected flow) · **Resource** (addressable value) · **Subject** (initiator, from a verified source only) · **Policy P** (deny-beats-allow, default deny) · **Closure Z** (all paths that change the resource) · **EnforcementPoint M** (the single decision point) · **Attestation** (signed bundle).

The domain distinction is isolated by the `subject.kind` field (`chain.escrow` / `legacy.flow`). Six ports: `StateProvider`, `EnforcementPoint`, `ObservationChannel`, `Clock`, `Domain`, `Prover`.

## 1.2. Verdict — fixed after review

**Three changes, each of them fundamental:**

**(1) `PROVEN` is no longer the only level.** The ladder:

| Level | Condition | What it is good for |
|---|---|---|
| **`PROVEN(R)`** | all conjuncts `[PROVED]`; every completeness claim rests on a proven mechanism, not on a test | the highest guarantee |
| **`ENFORCED_TESTED(R)`** | the control mechanism is present on **every** declared money path, but some properties are verified by test `[MEASURED]` rather than proven | an honest level for legacy systems where completeness is unprovable |
| **`INCONCLUSIVE`** | evidence is insufficient | a report without a guarantee |
| **`INVALID`** | the evidence is broken | an incident |

**(2) The verdict is always relative to a detector.** It is written `PROVEN(R)`, where `R` is the class of path-discovery methods with **measured recall** (M1). The wording in the act: "there is no bypass relative to methods D with recall r on corpus C", not "there is no bypass".

**(3) The word `PROVEN` is separated by meaning.** The review showed that in v1 a single word meant three different things, including the opposite one ("exploit reproduced" = the vulnerability **exists**). Now:

| Concept | Status |
|---|---|
| There is no bypass in the closure | `PROVEN(R)` / `ENFORCED_TESTED(R)` — the `verdict.json` verdict only |
| Finding reproduced | **`CONFIRMED`** (was `PROVEN`) — `findings/confirmed.json` |
| Finding conjectured | **`HYPOTHESIS`** — `findings/hypotheses.json` |

The files `confirmed.json` and `hypotheses.json` physically cannot be mixed: different schemas, different sections of the report.

## 1.3. Coverage scalar — new, mandatory

Introduced after the 5/5 remark that `unknown_paths = ∅` proves only the absence of the unknown **inside the analyser's model**.

```
coverage = covered_paths / discovered_paths
```
It is printed **in the verdict header**, next to the level:

```
verdict: ENFORCED_TESTED(R2)
coverage: 11/14 (0.79)   excluded: 3   unknown: 0
detector: slither+cast+manual | recall 0.71 (M1, corpus 20)
```

Rules:
- `PROVEN` requires `coverage = 1.0` **and** `excluded = 0` for money paths.
- `ENFORCED_TESTED` requires `coverage ≥ 0.9` and an `excluded` ceiling of ≤ 10% of discovered paths.
- `excluded` with a `reason` shorter than the declared threshold and without a confirming test **is not accepted**.
- An external call outside the declared allowlist → **`INVALID`**, not `INCONCLUSIVE` (otherwise any contract with an oracle gets a perpetual `INCONCLUSIVE`).

## 1.4. `flowguard.yml` format — extended

```yaml
verdict_requirements:
  min_coverage: 1.0                 # MUST for PROVEN; 0.9 for ENFORCED_TESTED
  max_excluded_ratio: 0.0           # MUST 0 for money paths
  detector_recall_min: 0.7          # MUST, from M1 on the reference corpus
external_calls:
  allowlist: []                      # MUST; call outside the list → INVALID
  unknown_behavior: INVALID
token_classes:                       # on-chain
  accepted: [standard_erc20]
  others_behavior: INCONCLUSIVE
```

## 1.5. Bundle — extended

New mandatory files: `verdict.json{level, coverage, detector, recall, excluded}` · `findings/confirmed.json` · `findings/hypotheses.json` · `trust/` (toolchain hashes, signature, independent replica — §5.5).

## 1.6. Human in the loop — fixed

| Context | Who decides |
|---|---|
| Onboarding (SKU 2–3): the boundary of Z, policy P, acceptance of the proof | a human, 4 gates of 10–30 min each |
| **Runtime and CI/CD** | **a machine, fail-closed**: the Z-diff does not converge → the deploy is blocked, the act is marked `DEGRADED` |
| Incident | break-glass with an HSM key and automatic suspension of the guarantee |

The review rightly pointed out: enterprise will not read formal verification artefacts on every release. Manual gates only where the guarantee is created, not where it is applied.

---

# 2. On-chain: escrow

## 2.1. Three invariants — with a token gate

| ID | Predicate | Refinement after review |
|---|---|---|
| **INV-1** | `∀a: balanceOf(a) ≥ Σ_{locked,disputed} amount[a]` and `deposited = released + refunded + Σlocked` | **true only for `standard_erc20`**. Behavioural preflight before the run: fee-on-transfer, rebasing, pausable, blacklist, upgradeable → **`INCONCLUSIVE`** if the token cannot be wrapped |
| **INV-2** | `released + refunded ≤ deposited`; transitions are monotone | a partial refund is a separate model |
| **INV-3** | `release ⇒ LOCKED ∧ att_VERDICT_OK ∧ subject/recipient/amount match ∧ final(block)` | compare the **amount**, not only the entitlement |

**New rule:** the mutability of the token itself (pause/blacklist/upgrade) is a path outside `Z`. A token with such capabilities requires them to be declared, or it yields `INCONCLUSIVE`.

## 2.2. Paths, finality, attacks

Seven path classes (owner/roles · upgrade-proxy · delegatecall · selfdestruct · value-calls · keeper/callback · sweep/rescue); each with `gaps[]`. An active `proxy admin` → `INVALID`.

Finality: **L1** — a `finalized` checkpoint, with a block count as the sole criterion prohibited; **L2** — not a single rule but **verifiable per-network adapters** (the review is right: each L2 has its own model and configuration); a reorg → `INVALID`.

10 attacks A1–A10 — executable scripts, not an agent. Each attack must **break the test on the broken contract** (a check for tautology).

## 2.3. Signatories

product owner (multisig) · custody quorum · security lead · verifier. For an immutable contract, `custody quorum` is replaced by "confirmation that no privileges exist", with proof via the absence of roles in storage.

---

# 3. Legacy: a service with a DB

## 3.1. Closure Z — 13 elements

Twelve from v1 plus a thirteenth per the review: **outbound integrations and shared secrets** (third-party SaaS with a shared credential, shadow integrations). It was not named because everyone was looking inside the perimeter.

## 3.2. Seven bypass paths

Unchanged: batch · admin panel · restore (only via a signed snapshot + 6 steps) · partner API · direct DB access (prohibited) · logs/analytics (writes prohibited) · CI/supply chain (data credentials prohibited).

## 3.3. The trigger — rewritten after review

**The phrase "physical guarantee" has been dropped.** A trigger is part of the mutable DBMS configuration, not an independent boundary against an administrator.

What is now mandatory:

| Requirement | Why |
|---|---|
| Triggers on **all of DML** (`INSERT/UPDATE/DELETE/TRUNCATE`), not only `UPDATE` | v1 covered only `UPDATE` — the review is right |
| A **DDL event trigger** on `ALTER/DROP TRIGGER`, `ALTER TABLE` | otherwise the trigger is switched off with a single command |
| **Delta hash in `Permit`**: not only "the entitlement" but also **what exactly changes** (old → new) | otherwise the `Permit` is for an entitlement without an amount, the review is right |
| **Monitoring of superuser sessions** as a separate witness channel | `rds_superuser`/`postgres` can do anything |
| **Logical replication prohibited** on money tables | replication applies changes past the triggers |
| `session_replication_role` kept under control, a change = incident | the classic trigger bypass |

**Condition for asserting the guarantee:** a guarantee at the `ENFORCED_TESTED` level is admissible only under an **explicitly declared privilege model** in which the database administrator is excluded from the threat model. If the admin is in the threat model, the level is no higher than `INCONCLUSIVE`, and this is written in the act.

## 3.4. The `Allow` event — cryptographically bound

It was: "reconciling `pgaudit` with the `Allow` journal". The 4/5 review rightly pointed out that a bypassing writer will write the `Allow` entry as well.

It became: the `Allow` event must contain `permit.nonce`, `permit.resource_version` and `permit.signature`, and the reconciliation must verify the **cryptographic link** "event ↔ `Permit` ↔ mutation" within one transaction. The presence of an event without a valid signature is `INVALID`, not "confirmation".

## 3.5. Witness — plus two requirements

Three channels (tap, DB digest, identity) · 12 person-days `[HYPOTHESIS]` · two tests (A — integrity, B — independence).

Added after review:
- **a target-substitution test**: replace the code/build/config/identity of the target and check that the end-to-end link target → artefacts → digest → signatures → offline verify catches it (this is mechanism `T1`);
- **channel independence is verified individually**: a journal is not considered independent if it is written by the same process as the mutation.

## 3.6. Oracles — strengthened

Three classes (SQLi, BOLA, traversal). `CONFIRMED` requires `C=false ∧ T=true ∧ N=false`.

Changed after the 4/5 remarks:
- **K ≥ 5** by default; **K = 10** when the flake rate is unknown;
- **any discrepancy** between runs → escalation to 10 → if the discrepancy persists, `INCONCLUSIVE`;
- **a published upper FP bound** per oracle, measured on a negative corpus;
- a separate `nondeterministic_oracle` mode: it lays no claim to `CONFIRMED`, only `HYPOTHESIS` with a histogram.

## 3.7. The rest, unchanged

7 attacks · 8 invariants (I1, I6, I8 — `[MEASURED]`, not `[PROVED]`) · two separate claims (`∀ Permit ⟹ P` and `∀ mutation ⟹ ∃ Permit ∧ Allow`) · an act of 8 fields with 4 signatures, two of them with the client · the 3-day rule + `DEGRADED` · break-glass via HSM · the validity contract.

---

# 4. Economics and price

## 4.1. SKU — with the review taken into account

| # | SKU | Price | Term | Key edit |
|---|---|---|---|---|
| 1 | Basic analysis | $2–5k | 3–5 d | **pass-through of review cost** until M2 closes; do not promise a margin >80% |
| 2 | Patches | $5–10k | 2 wk | — |
| 3 | Migration | $25–45k | 4–6 wk | — |
| 4 | Guarantee | `clamp(v×k, $25k, $50k)` for v1 | 45 d | **ceiling lowered to $50k**; floor raised to $25k (the $12k floor was below witness cost) |
| 5 | Re-attestation | in the subscription | 15 min | — |

**Pricing rule after review:** a proposal must contain a **confidence interval on `v`**. If the spread is >3× — either refuse the guarantee (analysis only), or recalculate after refining `v`. The price list must not be published before actuarial track record has been accumulated.

`k`: 0.60% up to $10M · 0.30% up to $100M · 0.15% above that. `value_at_risk` is the daily unmitigated flow, not market capitalisation. Recalculate after M7: with a witness of 30 person-days, SKU-4 is loss-making up to `v ≈ $5–7M`.

## 4.2. Pricing doctrine — substantively unchanged, with a review amendment

P1–P6 stand (no price per finding · margin ceiling 45/70% · automation dividend 50/50 · the price falls on a schedule · no fear premium · critical infrastructure at cost).

**Amendment:** `assessor_minutes_per_finding` — the planning value is **35–40 minutes** (consensus of the five reviews: 20, 25, 35, 45, 45), while 15 minutes is a target achievable no earlier than the tool's second quarter. The conditional price commitment (a 10%/yr reduction) remains, but is counted **from the measured value**, not from the target one.

The automation dividend recalculated in numbers: at 40 → 15 min the saving per engagement ≈ `(0.67 − 0.25) × 120 × 4 = $200` `[HYPOTHESIS]` — that is, for now the dividend is small, and this must be admitted rather than promised.

---

# 5. Claim registry

**Protocol:** strike by ID, with a verdict of `WRONG` / `UNPROVEN` / `INCOMPLETE`. The "status" column holds the result of the first round.

## 5.1. Core

| ID | Claim | Tag | Status after round 1 |
|---|---|---|---|
| S1 | What is asserted is not "safe" but "within the closure one cannot get past the control point" | `[HYPOTHESIS]` | accepted |
| S2 | The claim is verifiable offline by a third party | `[MEASURED]` | **INCOMPLETE**: `DEGRADED`, break-glass and key revocation are online states → a signed suspension feed and a short TTL were added |
| S10 | `unknown_paths = ∅ ⇒ INCONCLUSIVE` | `[HYPOTHESIS]` | **INCOMPLETE, 5/5** → the relative verdict `PROVEN(R)` with a coverage scalar was introduced |
| S12 | `PROVISIONAL` is a field, not a verdict | `[HYPOTHESIS]` | accepted |
| S14 | Byte-for-byte reproducibility | `[HYPOTHESIS]` | remains `[HYPOTHESIS]` |
| S17 | The LLM does not participate in the verdict | `[HYPOTHESIS]` | accepted |

## 5.2. On-chain

| ID | Claim | Tag | Status |
|---|---|---|---|
| O3 | `INV-1` is true | `[HYPOTHESIS]` | **WRONG, 4/5** → token gate, non-standard token → `INCONCLUSIVE` |
| O6 | Seven path classes cover the movement of funds | `[HYPOTHESIS]` | accepted with `gaps[]` (not confirmed) |
| O10 | L2 finality by a single predicate | `[HYPOTHESIS]` | **INCOMPLETE** → per-network adapters |
| O11 | 10 attacks are complete for escrow | `[HYPOTHESIS]` | remains `[HYPOTHESIS]`; a tautology check was added |
| O13 | Attacks A3/A5 are not tautological | `[HYPOTHESIS]` | remains `[HYPOTHESIS]`, requires a mutation test |

## 5.3. Legacy

| ID | Claim | Tag | Status |
|---|---|---|---|
| G8 | "A physical guarantee — the trigger only" | `[MEASURED]` | **WRONG, 4/5** → the word dropped; all of DML+DDL, delta hash, superuser monitoring, replication prohibited; the guarantee only under a declared privilege model |
| G9 | Reconciling `pgaudit` with `Allow` proves complete mediation | `[HYPOTHESIS]` | **UNPROVEN, 4/5** → `Allow` is cryptographically bound to `Permit` |
| G26 | Adaptive K=3 does not lose reliability | `[HYPOTHESIS]` | **WRONG/UNPROVEN, 4/5** → K≥5, K=10 when the flake rate is unknown, a published FP ceiling |
| G33 | 100% review at 15 min is economically survivable | `[HYPOTHESIS]` | **UNPROVEN, 3/5** → plan 35–40 min; SKU-1 pass-through |
| G25 | Three classes yield ≥2 findings per typical target | `[HYPOTHESIS]` | **UNPROVEN, 3/5**; and it **measures the wrong thing** → metrics separated |
| G1 | 12 elements of Z are sufficient | `[HYPOTHESIS]` | **INCOMPLETE** → a 13th added: outbound integrations and shared secrets |
| G7 | `Permit` in dynamic languages is a discipline | `[MEASURED]` | **INCOMPLETE**: the client will read it as a guarantee, monkey-patching bypasses it → a runtime module-hash reconciliation hook was added |
| G11 | DB-level enforcement is sufficient | `[HYPOTHESIS]` | **INCOMPLETE**: logical replication and restore bypass it → added |
| G31 | The 3-day rule is workable under continuous deployment | `[HYPOTHESIS]` | **WRONG at 20 deploys/day** → Z-diff in CI: does not change Z — the machine extends; changes it — the deploy is blocked |
| G4 | Only supply chain lies outside the guarantee | `[HYPOTHESIS]` | **INCOMPLETE, 2/5**: restore, emergency DBA, third-party integrations create real paths → state it explicitly |

## 5.4. Economics

| ID | Claim | Tag | Status |
|---|---|---|---|
| E3 | `clamp(v×k, 12k, 250k)` works | `[HYPOTHESIS]` | **UNPROVEN, 4/5** → CI on `v`, refusal when the spread is >3×, ceiling $50k, floor $25k |
| P-1 | The 45/70% margin ceiling holds | `[HYPOTHESIS]` | remains `[HYPOTHESIS]`, requires M2 |
| P-3 | `assessor_minutes_per_finding` is manageable | `[HYPOTHESIS]` | re-estimated: plan 35–40, not 15 |
| P-4 | Regression of `k` does not kill large deals | `[HYPOTHESIS]` | requires M7 |

## 5.5. New mechanisms found by the review

| ID | Mechanism | Horizon | Symptom | Edit made in v2 |
|---|---|---|---|---|
| **T1** | **Compromise of the trusted release circuit** — a signature proves the integrity of what is signed, but not the truth of the claim, nor the link "bundle ↔ actual target ↔ executable version" | from the pilot | a correctly signed `PROVEN` for a wrong link; a cluster of false verdicts with no discrepancy in the signatures | published toolchain hashes · an independent verification replica · cross-checking against reference targets · a **mandatory substitution test** of target/code/build/config with an end-to-end link check |
| **T2** | **Policy drift** — we prove "conforms to P", not "P conforms to intent"; a legal but harmful release passes | the first pilot | `ENFORCED_TESTED` at an incident caused by a permitted action | policy is written from the threat model, not from the code; a mandatory section "what P does not prohibit but should" |
| **T3** | **Vacuous `PROVEN`** — the payer itself chooses `Z` and `P` and has an interest in narrowing them; the market reads the badge, not the exclusion list | 6–12 mo | the share of `excluded` grows relative to discovered paths; the share of clients with `PROVEN` → 100%; the claim "you had a PROVEN" | a coverage scalar in the header · an `excluded` ceiling · a minimum set of invariants by `asset.kind` · publication of "what P does not prohibit" |

---

# 6. Weaknesses — re-ranked

| # | Weakness | Related | Change |
|---|---|---|---|
| 1 | **Completeness of the closure is unprovable** — the main one, 5/5 | S10 | now **openly admitted** through `PROVEN(R)` and coverage; the question is not "to prove" but "to measure recall" |
| 2 | **The trusted release circuit** (`T1`) | new | moved up to 2nd place |
| 3 | **The death criterion measured the wrong thing** | G25 | fixed by separating the metrics; the threshold itself remains `[HYPOTHESIS]` |
| 4 | **Non-standard tokens** | O3 | narrowed but not solved: 80% of DeFi is outside the scope |
| 5 | **Review margin** | G33 | 35–40 min instead of 15; the economics of SKU-1 are in question |
| 6 | **Vacuous PROVEN** (`T3`) | new | requires product constraints that v1 does not have |
| 7 | **A trigger is not a "physical" protection** | G8 | admitted; the guarantee is conditional on the privilege model |
| 8 | **K and flake** | G26 | K≥5, published FP |
| 9 | **`P-drift`** (`T2`) | new | no mechanism for checking "P is right" |
| 10 | **Price and `v`** | E3 | CI on `v`, $50k ceiling |
| 11 | **L2 finality** | O10 | adapters |
| 12 | **`Permit` in dynamic languages** | G7 | a runtime hook, but it is bypassed |
| 13 | **Restore and emergency DBA** | G4 | in practice always a write path |
| 14 | **The 3-day rule** | G31 | Z-diff in CI resolves it |
| 15 | **No external consumer of the act** | new | see §9.E — the most likely way not to build it |

---

# 7. Mandatory measurements

| # | Question | How to measure | Days |
|---|---|---|---|
| **M1** | The real recall of the path detector | 20 targets: paths found manually vs found automatically; **publish as a number** | 5 |
| **M2** | Minutes per finding by class | 30 findings, 3 reviewers, a timer up to signature; report median/p90; onboarding time separately | 3 |
| **M3** | `proof-fixing` on unfamiliar code | 100 lines in 3 days, extrapolation | 3 |
| **M4** | The share of targets passing the validity contract | 3×50 repositories, broken down by the first failed criterion | 5 |
| **M5** | The median findings and the share of targets with `closure_complete` | 12–20 targets, three classes, thresholds fixed in advance | 15 |
| **M6** | Willingness to pay | 10 interviews on triggers | 10 |
| **M7** | Witness 12 or 30 person-days | measurement broken down by day | 5 |
| **M8** | **Is there a consumer of the act** | 10 interviews: is an insurer/auditor/bank/counterparty prepared to change a decision **in writing** given a bundle | 10 |
| **M9** | **Substitution test** (`T1`) | replace the code/build/config/identity; end-to-end verification must catch it | 3 |

---

# 8. What is not included

UI, billing, CRM · bridges, oracles, MEV · Windows targets · a K8s operator · Certora as the primary backend · agent-driven automatic attack discovery · insurance and contract · the automatic payout subsystem with disputes (described separately, not assessed here).

---

# 9. What is needed from you (round 2)

The first round delivered the main point: **all five reviews estimated the median findings at ≈1**, that is, by its own death criterion legacy in its current form cannot be built. The second round must decide **what exactly we change**, not re-check the same thing.

**A. What to change in the product.** Of the three options responding to the failure of criterion `G25`:
 (a) narrow the scope to an isolated ledger core, everything else outside the guarantee;
 (b) change the metric: not finding yield but the share of targets with `closure_complete`;
 (c) accept that the guarantee is sold even at zero findings, and drop `G25` altogether.
Choose one, justify it in 3 lines and state what it breaks.

**B. Three proofs without which the guarantee cannot be sold** (round 1 result: completeness of the closure, independence of the evidence, absence of a false `PROVEN`). For each: **one** cheap experiment (≤5 days) with a failure threshold.

**C. `T3` — vacuous PROVEN.** Give three constraints that stop the client from narrowing `Z`/weakening `P` and at the same time do not make the product unsellable. Numbers, if you can.

**D. `T1` — the trusted circuit.** What must be in the bundle so that a verifier can satisfy itself of the link "target ↔ artefact ↔ verdict" without trusting us? List the fields and one substitution test.

**E. One "do not build".** One observable condition under which the product should not be built in this form. Do not repeat the condition from §7.M8 — give your own.

**F. One number.** `assessor_minutes_per_finding` — your estimate and the way to check it. If you believe 15 minutes are unattainable in principle, say so plainly.

**Rules:** ≤200 words per item · "it depends on the context" without a condition is prohibited · "I don't know" is allowed and valued · do not propose new architectures, only edits · do not retell the document.
