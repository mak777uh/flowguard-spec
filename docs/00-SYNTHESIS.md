# 00. Synthesis: what has been assembled, where the sources agree, where they diverge, and what follows from that

> The document records **decisions**, not opinions. Everything below marked `DECIDED` is settled and carried over into the spec.
> Everything marked `PILOT` is not decided by text; it is decided by measurement.

---

## 0. Map of the package

| File | What is inside | For whom |
|---|---|---|
| `00-SYNTHESIS.md` (this one) | analysis of 9 sources, consensus, 7 real divergences and their resolution, scoring | everyone |
| `01-VARIANTS.md` | 3 architectures (A/B/C) + 2 strategic options, diagrams, cost, when which | the architect, the investor |
| `02-GRID.md` | a single ladder of fixes R0–R5 × confidence levels L0–L5 × SKU, the "variant passport" | product, engineers |
| `03-EVAL-ROADMAP.md` | eval suite, acceptance thresholds, kill criteria, 3 horizons, economics, hiring | the founder |
| `../proposals/*.md` | the 6 original team proposals in full (not edited) | for the record |

---

## 1. Sources: nine independent bets

Three external proposals (sent by the client) + six internal ones (each written by a separate model in a separate context, with no access to the others).

| # | Source | The main bet — in one phrase |
|---|---|---|
| **S1** | Ext. "Orchestrator + subagents, R0–R4, tier verification" | A multi-agent orchestrator around classical tools; the formal tool is a separate Tier 3 |
| **S2** | Ext. "Proof-Carrying Remediation + Security Improvement Graph" | A fix = an evidence package; knowledge lives in a typed graph of causes and risks |
| **S3** | Ext. "4 variants: fast loop / patch factory / formal pipeline / hybrid with arbitration" | Rust→Lean and C→SPARK as the product track; everything else is scaffolding |
| **T1** | Int. `01-offense-repro` | A finding does not exist without a PoC; a fix does not exist without a killed PoC and a variant suite |
| **T2** | Int. `02-formal-core` | We sell invariants, not patches; the boundary of the provable runs along property classes |
| **T3** | Int. `03-platform` | 80% of quality is the control plane; the model is replaceable, the artifact is eternal |
| **T4** | Int. `04-product` | Findings are free; the scarce thing is a signature with a name, a format for a third party, a fix that actually lands |
| **T5** | Int. `05-critic` | A product is killed not by missed bugs but by false findings, broken fixes and an unprovable run |
| **T6** | Int. `06-high-assurance` | In a regulated domain an LLM's output cannot be evidence at all — only a hypothesis about where to look for evidence |

---

## 2. Consensus — no longer a dispute but a foundation

Seven propositions are supported by 7–9 of the 9 sources. They are not up for discussion and go into the spec as axioms.

**C1. The agent proposes, a deterministic checker decides, a human signs.**
No artifact that enters a report as "verified" may be produced by a probabilistic model. In a regulated domain (T6) this is elevated to a hard rule: the agent physically has no right to write to the evidence store — the only writer is a deterministic arbiter, and this is an access right in the sandbox, not a policy. T5 names violation of this rule failure mode F03 (reward hacking of the verifier) — the most frequent mechanism of a product's quiet death.

**C2. A finding without a reproducible artifact is not a finding but a hypothesis.**
The wording differs ("PoC bundle" in T1, "status: demonstrated" in T4, "evidence record" in T6, "verification matrix" in S1/S2), but the conclusion is one: the report must physically separate the two classes — *proved* and *assumed* — and never mix them in one list.

**C3. The product sells a ladder of fixes, not a patch.**
All nine sources independently arrived at a gradation of 4–6 levels. The divergence is only in the number of levels and in what counts as the lower bound (see §3.3).

**C4. Formal methods are a narrow premium track, not the basis of a mass product.**
Even the most ardent proponent (T2) writes honestly: "it does not pay off on a CRUD backend", "formal methods are an expensive special-purpose tool for a narrow class". External confirmation: the Rust→Lean 4 pipeline on Charon/Aeneas + AI provers (Aristotle, Aleph) **works** on production crypto code, but the authors of the experience report explicitly list the unresolved engineering holes — Lean 4 toolchain drift, the limits of Aeneas/Hax extraction, `unsafe` Rust outside coverage. See `03-EVAL-ROADMAP.md`, §5.

**C5. Execution isolation — microVM/sandbox, deny-all network, zero secrets in the sandbox.**
Consensus without exceptions. Docker/runc was rejected by everyone who considered it (T3 provides a table "technology → what it protects → what it does not protect → cost").

**C6. Destructive action on prod is forbidden; the scope is a signed manifest, not "the URL someone sent".**
T5 formulates this as F06/F07 with an explicit rule: by default a clone/test stand, write traffic is classified by a proxy, a checksum of the canary table before/after.

**C7. Input data (repository, site, comments in code) is hostile content.**
Prompt injection through the target artifact is a standard vector for a security product, not a rare case. Technical prevention (a split model, "a reader without tool access" + policy in the harness code + egress allowlist) is supported by T3, T5, S1.

---

**C8 (added in the second round, by reviewers #1 and #2 independently). The checker is itself an object of verification.**
Determinism is a necessary but not sufficient condition. Deterministic code can check the wrong predicate: an oracle that consistently classifies an effect incorrectly turns a reproducible error into a **systematic** error of the product, and from the inside it is indistinguishable from truth. Therefore C1 is reformulated: "verified = produced by deterministic code **and** that code has itself passed verification by an independent reference corpus, mutation testing of the oracle, and review of the implementation". Requirements: the oracle's version is pinned in the bundle, the oracle cannot be modified by the agent, every vulnerability class has a negative control (a sanitized input that **must not** fire).

## 3. Seven real divergences and how they are resolved

This is the most useful part of the synthesis: this is exactly where the nine proposals are incompatible, and exactly where the architectural decision is taken.

### 3.1. Where is the moat: capability / control plane / signature / proof?

**Positions.** T1: the moat is a library of exploit primitives and deployment adapters. T3: the moat is reproducibility of the run. T4: the moat is a signature with a name and acceptance of the artifact by an auditor. T2: the moat is a reusable proof harness. S3: the moat is the formal pipeline.

**Resolution `DECIDED`.** These are not four answers to one question but four **different horizons**:

| Horizon | What constitutes the moat | Lifetime |
|---|---|---|
| 0–12 months | **Signature + evidence format accepted by a third party** (T4). Capability is copied in a quarter; a signature and a contract with an auditor are not | eternal, but requires a deal |
| 12–24 months | **Evidence plane** (T3): reproducibility, hash-chain, replay kit. Copied, but expensively and without immediate benefit to a competitor | 2–4 years |
| 24–48 months | **Proof harness over 3–5 property classes** (T2/E-level) + a library of deployment adapters (T1) | 5+ years, if maintained |
| always | Detection capability | **not a moat at all** — a commodity |

Consequence: you cannot build a company on capability, and you cannot start with proof. The correct order of investment is counter-intuitive: first the signature and evidence (cheap, creates price), then the control plane (expensive, creates protection), then proof (very expensive, creates a category).

**Second-round correction.** Both reviewers independently put the **evidence plane** first, not the signature (A4: 60 and 93 confidence). The argument: an auditor will not accept a signature without reproducibility, that is, the signature is packaging, not a moat. Revision: the 0–12-month moat is the **evidence plane**, and the signature is the commercial form in which it is sold. The order of investment does not change because of this (they are built together), but in contested decisions priority goes to reproducibility.

### 3.2. Offense-gated (PoC) vs static/taint coverage: what is the "entry into the report"?

**Positions.** T1: only what is proved; better to decline a true bug than to ship a false one — precision ≥98%, recall is deliberately sacrificed. S1/T2/T6: a broad static pass as a source of hypotheses and a coverage map, PoC — where possible. T5: both classes are needed, but with different statuses, otherwise the client does not see 70% of the surface.

**Resolution `DECIDED`: two parallel tracks in one report.**

```
Lane A (Coverage)   static / taint / SCA / secrets / IaC / config
                    → status HYPOTHESIS, not billed, forms the surface map
                    → purpose: not to miss a class entirely, to give the client completeness

Lane B (Proof)      the agent drives a candidate to an observable effect
                    → status PROVEN / CONDITIONAL, billed, enters "findings"
                    → purpose: to create trust and price
```

Publication rule: **Lane A never improves the precision figure and is never mixed with Lane B in one list.** This simultaneously resolves the conflict between T1 (we do not ship lies) and T5 (we do not hide blind spots): the client sees both what is proved and "we looked here but did not prove it".

This also removes the main weakness of offense-first that T1 itself admits: "it measures reachability for our agent, not risk".

### 3.3. How many levels in the ladder: 4, 5 or 6?

**Positions.** T1: L0–L4. T2: A–E (5). T4: S1–S5 (5, commercial). T6: F0–F5 (6, certification). S1: R0–R4. S2: 5 grids. S3: 4 grids.

**Resolution `DECIDED`: one technical lattice R0–R5, two projections onto it.**
There are six technical levels, because T6 proved: in a regulated domain "change nothing, but prove it" (F0) and "change only configuration/data" (F1) are **different products at different prices**, and they do not reduce to a patch. There are five commercial SKUs (S1–S5), six certification ones (F0–F5), and both projections map onto R0–R5 without loss. The full table is in `02-GRID.md`.

### 3.4. Economics: `$8` or `$50–500` per validated finding?

**Positions.** T5 sets the GA threshold at `cost per validated ≤$8` (p50) and `≤$40` per run of 100 kLOC. T1 estimates `$50–500` per validated bug. T4 — `€200–1500` of compute per S1 engagement.

**Resolution `PILOT` + recording the contradiction.** The figures are incompatible by an order of magnitude, and this is not a rounding error — these are different definitions:

- `$8` — **the average cost across all confirmed findings, including cheap ones** (SCA/secrets/config: a finding in minutes, cost close to zero). With 15–30 findings per run and $40 of compute, the average does indeed go into single-digit dollars.
- `$50–500` — **the cost of one expensive finding** with PoC synthesis on a stateful application (hours of LLM tool loop + bringing up the environment).

Both numbers are true and both are useless as a single metric. `DECIDED`: we count a **histogram by class** (SCA / secrets / config / static-logic / dynamic-PoC / memory-corruption / formal), not a single number. The single KPI for management is the **blended `cost per validated`** and separately the **p90 for the `dynamic-PoC` class**. The T5 threshold of `$8` is reclassified as "blended across all classes"; the T1 range — as "p90 for dynamic-PoC". Until it is measured — **do not promise a price per finding** (T4 has already forbidden this: "price for scope and decision, never for finding").

**Refinement after the second round (reviewer #1).** The reviewer's hypotheses close the dispute arithmetically: **blended ≈ $400 per validated finding at ≈ 4 findings per engagement**. Hence:

- `$8` as a threshold is **arithmetically incompatible** with PROVEN-only v1: that is $32 for the whole engagement at 4 findings, which does not even cover review (25 min × $80/h = $33 for one finding). The T5 threshold remains valid only for a high-volume SCA/secrets mix, which v1 does not have.
- The correct unit of management is the **cost of an engagement** (compute + review + sandboxes), not the cost of a finding: there are few findings and their number is not controllable.
- Consequence for price: at €12k per scope and ≈$400 × 4 ≈ $1.6k of cost plus review, the economics work out, but **only if the engagement finds at least 1 finding at all**. Hence the failure mode "empty report" (see below) and a product correction: **zero findings must be sellable** — as a coverage attestation with replayable proof, and not as a failure.
- `$50–500` (T1) is confirmed as the order of magnitude for p50; `$3 000` p90 for stateful is the reviewer's estimate and requires measurement on 30 applications.

### 3.5. How much human is in the loop?

**Positions.** T4: a named signatory is mandatory already in S1 — "an auto-generated PDF is marketing, one signed by a human is proof". T3: humans dominate only in high-assurance, the mass run must be unattended. T5: the share of sampled human verification must be disclosed (the risk of "the system tested it, I checked 20%").

**Resolution `DECIDED`: a human signature on every v1 report, the share of manual verification as a published metric.**
In v1 a human checks 100% of PROVEN findings before shipping: that is expensive, but that is exactly what is being sold. As automation grows the share falls, and the product must print in the report `human_review_coverage: 100% | 40% | 20%` — not as marketing but as a limitation on the claim. The transition from "I tested it" → "the system tested it, I checked X%" is a product decision with a legal consequence, and it cannot be silent.

### 3.6. S5 (migration to a safe core): product or R&D?

**Positions.** T4: GM 19%, a six-month cash cycle → "a credibility asset, not a product", at most 1–2 a year. T2: it is the main differentiator and source of revenue, sold as "a licence for the proof + its maintenance".

**Resolution `DECIDED`: both, but separated in time.**
S5 in v1 is an R&D investment with a negative margin, sold at cost as a reference (T4 is right on the economics). Its **real** product is not a separate project but the **reusable proof harness** (T2 is right on strategy): if the harness covers 3–5 property classes (memory safety of a parser, no-panic, constant-time crypto, access invariants, protocol state machine), then S5 turns from 19% GM into 55%+ and becomes reproducible. The criterion for moving from R&D to product is **a second client on the same property class with ≥70% reuse of the harness**. Until then — do not scale.

### 3.7. An underrated option: sell the harness, not the findings

**Position.** None of the 8 "product" sources considers it; T3 in fact describes it but does not make it a conclusion.

**Resolution `DECIDED AS STRATEGIC OPTION E`.** If appsec agents become commoditized (and the trend is exactly that: the hyperscalers already have an agentic security researcher in preview), then value shifts to the layer that **proves** other people's findings. This protects against the main existential risk named by T4: "a hyperscaler will package AI review + attestation into a platform". The option does not launch in v1, but the architecture must allow it: the evidence plane and the verifier farm are designed as a **separate service with an external API**, not as an internal module. The cost of this decision is zero now; the option is a whole company later.

---

## 4. Scoring against the T5 rubric

The rubric and weights are from `proposals/05-critic.md`. Scoring is only on artifacts: claimed without a mechanism = 0. Maximum 5.00. Knockout at ≤1 on criteria 1/3/4.

| Source | 1. Trust (18) | 2. Fix (14) | 3. Audit (12) | 4. Legal (12) | 5. TTV (10) | 6. Econ (9) | 7. Injection (8) | 8. Isolation (7) | 9. Scale (5) | 10. Impl. (5) | **Σ** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **T1** offense-first | 5 | 5 | 4 | 4 | 5 | 3 | 5 | 4 | 3 | 4 | **4.36** |
| **S1** orchestrator+subagents | 4 | 3 | 3 | 3 | 4 | 4 | 2 | 3 | 4 | 5 | **3.44** |
| **T3** control plane | 2 | 3 | 5 | 4 | 2 | 3 | 5 | 5 | 4 | 3 | **3.43** |
| **T6** high-assurance | 4 | 5 | 5 | 5 | 1 | 1 | 3 | 3 | 1 | 1 | **3.36** |
| **S2** proof-carrying | 4 | 4 | 3 | 3 | 2 | 2 | 3 | 2 | 3 | 3 | **3.06** |
| **S3** 4 variants / Rust→Lean | 3 | 4 | 2 | 3 | 3 | 3 | 2 | 4 | 3 | 3 | **3.01** |
| **T2** formal-core | 3 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | 3 | 2 | **2.79** |

**How to read the table.** No source scores above 4.4 — and that is expected: each proposal was optimized for its own bet. The winner by total (T1) is at the same time **not** the winner on audit (3rd place) or on isolation (2nd), while T3 leads exactly where T1 is weak. T2/T6 score low precisely because they are honestly narrow — and their low score on TTV/economics **does not** mean "not needed", it means "cannot be the core".

**Conclusion `DECIDED`:** the synthesis does not choose a winner, it **assembles layers** — and this is the only configuration that passes all three knockouts at once.

```
Decision layer     ← T1  (PoC contract, C/T/N, sealed oracle, fix gate)
Evidence layer     ← T3  (content addressing, hash-chain, replay kit, isolation)
Deployment layer   ← S1  (subagent DAG, peer models, dedup)
Commerce layer     ← T4  (signature, negative scope, SKU ladder)
Assurance layer    ← T2+T6 (proof obligations, L0–L5, traceability, TCB)
Refusal discipline ← T5  (eval, thresholds, kill criteria, F01–F19)
```

---

## 5. What was discarded from the submitted proposals and why

Honesty matters more than completeness: some of the claims in the external proposals I do **not** carry over into the spec.

| Claim | Status | Why |
|---|---|---|
| "MAAP — 70.3% successful patches on 120 CVEs", "RAVEN — 83.13% on 160 CVEs" | **not confirmed** | I did not find a primary source with these numbers. Similar figures exist in AutoPatch/agentic work, but comparability of the benchmarks is not proven. Do not use in sales |
| "Nemesis: Red Team / Blue Team / Judge" as a ready-made pattern | **to verify** | The pattern is useful (it went into Var C as adversarial arbitration), but the specific system is not verified |
| "pwnkit with verifiable artifacts" | **not confirmed** | Not confirmed |
| PentestGPT/Strix/CAI as an "operationally fit core" | **partially** | PentestGPT has been rebranded as "autonomous", but an independent analysis (verification-gap) raises the question: does the tool *prove* the finding or *assert* it. This is exactly the gap we sell — therefore they cannot be taken as a core, only as sources of techniques |
| "Chrome full chain in 6 days, $250K" (XBOW) | **accepted as a market fact** | Published by the vendor; use as a reference point, not as a promise |
| "AIxCC: 86% of synthetic found, 68% patched, $152/task" | **accepted** | Official DARPA release, 8 Aug. 2025. Key reference point: **on 54M lines, average patch 45 minutes** — this is a bar that cannot be ignored |
| Rust→Lean 4 (Charon/Aeneas + Aristotle/Aleph) | **accepted with limitations** | Confirmed by an experience report (Runtime Verification, 2026): works on production crypto, but `unsafe` is outside coverage, toolchain drift, manual lemmas |
| "Autoharness: 16 748 harnesses, 11 970 verified" | **accepted as an automation reference point** | It shows that auto-generation of proof obligations scales; generics (9 600 skipped) and concurrency remain uncovered |

Practical consequence `DECIDED`: **any figure in commercial material must have either a reference to a primary source or the label "model".** The team's internal estimates (cost, timelines, GM) are already labeled as hypotheses — leave them that way.

---

## 6. Open questions that only the pilot decides

Do not try to settle these with text. Each item is a measurable task for the first 90 days.

| # | Question | How we measure | Threshold at which the architecture changes |
|---|---|---|---|
| Q1 | The real cost of a validated finding by class | 20 runs, actual invoices | p90 dynamic-PoC > $600 → cut depth, not price |
| Q2 | Reproducibility of the PoC at the client | 20 bundles replayed in its CI | < 90% → the evidence plane does not work, stop sales |
| Q3 | Deployment fidelity: the share of targets that came up at all | log `DEPLOY_FAILED` | < 70% → the product applies only to containerizable targets, change the TAM |
| Q4 | Patch acceptability | 60 fixes, % accepted without semantic edits | < 50% → the fix track is not sold separately |
| Q5 | Obedience to injection | canary corpus N=200 | > 2% → stop autonomous runs |
| Q6 | Regression after a fix | client CI | > 3% → mandatory canary rollout in the product |
| Q7 | Contamination: public vs private delta | time-split after the model cutoff | gap > 20 pp → withdraw efficacy claims |
| Q8 | The cost of one S5 migration with harness reuse | 2 cases, one property class | reuse < 70% → S5 remains R&D |
| Q9 | Acceptance of the evidence package by an auditor | 1 firm, 5 packages | refusal → redo the report format, not the sales |
| Q10 | Willingness to pay for a trigger (not for size) | 15 interviews on 5 triggers | < 30% "would buy" on a trigger → change segment |

---

## 7. The final decision on one page

**`DECIDED`.** We build **Variant B "Remediation Factory"** (`01-VARIANTS.md`), designed so that the following plug into it without rework:

1. **from below** — Variant A (thin offense-first) as the first release in 8–10 weeks;
2. **from above** — Variant C (high-assurance, "certifiable change") as the second product in 9–15 months;
3. **from the side** — Variant E (evidence plane as a service) as insurance against commoditization.

Three invariants that must not be violated in any variant:

- **I1.** Everything called "verified" is produced by deterministic code, not by a model.
- **I2.** Everything shipped is reproducible **within the declared fingerprint** (images, versions, configuration, seed, network policies, time). Outside the declared fingerprint the status is `HYPOTHESIS`, not `PROVEN`. The claim "reproduces always" is never made. *(Third-round wording: 3 of 5 reviewers independently showed that an absolute "same result" is false for stateful and distributed effects, and that the fingerprint must be a **contractual boundary** of the proof, not a technical detail.)*
- **I3.** Everything asserted is bounded by an explicit negative scope.

Violation of any of the three is not a backlog bug but a stop-sales event (`03-EVAL-ROADMAP.md`, kill criteria K1–K5).

---

## 8. Addendum: sources S4 and S5 (arrived after the first synthesis)

Two external proposals arrived later. Neither overturned §2–§4, but each added one important dimension.

### S4 — "SaaS / hybrid with a client runner / fully local" (NIST SSDF frame)

**What is new.** The deployment topology is declared an **architectural axis**, not an operational detail: SaaS → hybrid (panel outside, runner in the client's VPC) → full local installation, with the recommendation "start with hybrid, but from day one design packages and updates so that they can be delivered locally". Plus a strict methodological discipline: SARIF as the primary format, a draft PR instead of applying, "do not promise to find everything", metrics = share confirmed / share FP / share of patches that passed re-verification / reproducibility of tasks.

**What it confirmed.** C1, C2, C5, C6 — independently and in almost the same words. Separately valuable: "treat repository contents and scanner results as untrusted data, not as instructions" — this is C7, formulated as a harness rule rather than as advice.

**What is missing.** No answer to "where is the moat" (none of the four horizons of §3.1), no estimate of the economics, no mechanism for proving causality (the PoC contract is absent — only "repeat the analysis"). This is an honest baseline, not a differentiator.

### S5 — "4 variants + Assurance Factory + remediation-first" (with external references)

**What is new.** Three things that no one else had:

1. **The product formula in one line:** "AI finds and proposes; the sandbox reproduces; formal methods prove; a human approves; CI records". This is the best of the formulations encountered — I take it as the external positioning statement.
2. **Confidence level as a field of every fix:** `reproduced` / `static-only` / `formally-proven` / `human-approved`. It matches the L0–L5 lattice from T6 but is simpler for the client — I take it as the client-facing representation and keep the L-lattice as internal language.
3. **A "Permission engine" with capability rights** (`read_repo`, `run_tests`, `start_sandbox`, `execute_poc`, `open_pr`) and the rule "actions with consequences require approval". This is an operationalization of T3 and at the same time an answer to T5 question #4, "what is the trusted instruction base".

**What it confirmed.** Multi-agent structure, the sandbox gate, "do not rewrite everything in Lean — isolate the TCB", TLA+/Quint for protocols, red-teaming of the agent itself.

**What is missing.** The same failure as S4: no PoC contract with a negative control (C/T/N), no model of the economics, no answer on signature and liability. Plus — this is already the second source that ranks "remediation-first" above "finding-first" in sellability without citing a single figure.

### What changes in the synthesis because of S4/S5

**One structural change `DECIDED`.** "Architecture variants" are not competing projects but **a point in a three-dimensional matrix**:

```
Axis 1 — Assurance level:  offense-gated  →  remediation factory  →  certified change
Axis 2 — Placement:        SaaS           →  hybrid runner       →  on-prem / air-gap
Axis 3 — Coverage:         repo-only      →  +API +container      →  +live targets  →  +formal core
```

This dissolves the apparent "cloud vs on-prem" contradiction (it is not a variant but an axis), explains why the 9 sources looked incompatible (they stood at different points), and yields a product line instead of three mutually exclusive bets. The full matrix is in `01-VARIANTS.md`.

A second, smaller change: **the deployment topology brings with it a requirement on the evidence plane**. If the runner sits in the client's VPC, the replay kit must work **without access to our infrastructure and without a network** — this was already in T1 (`--offline`), but now it becomes a hard architectural constraint rather than a wish.

---

## 9. Readiness for the second round

The first round produced nine philosophies and one synthesis. It **did not** answer the 10 questions of §6 and did not resolve 4 of the 7 divergences (3.4, 3.5, 3.6 remained hypothesis-decisions, 3.1 — a bet-decision). Therefore the second round is built not as "ask about the architecture once more" but as **forcing falsifiable commitments**: the same input for everyone, the same questions, numbers and a choice required, not philosophy.

Package for the run: `10-ROUND2-QUESTIONS.md`.
