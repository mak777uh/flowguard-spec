# 50. The Rig: technical implementation, minimal human involvement

> Goal: turn the spec "flow → closure → mediator → proof → act" into a working installation where the human does only what the machine cannot, and quality does not depend on the operator's qualification.
> The key thought at the start, because the entire economics depends on it.

---

## 0. Where exactly the gain from automation appears

The naive expectation: "we automate it and the first project becomes cheap". That is wrong. A client's first migration is **engineering**: inventory, mediator, credential revocation, proof. It cannot be automated down to zero; it will remain 45 days / 24 person-days.

The gain is elsewhere, and it is enormous:

| | First attestation | Re-attestation (annual and on change) |
|---|---|---|
| What is done | inventory, migration, mediator, proof, red-team | re-run of the same rig on a new commit |
| Time | 45 days | **15 minutes** |
| People | 24 person-days | **2 signatures of 10 minutes each** |
| Artefact | Declaration Z v1 | Declaration Z vN with a new hash |
| Margin | 35–45% | **>90%** |

**That is why the rig is designed not for the first migration but for making re-attestation a single command.** This is the meaning of "auto work": the $12k/year subscription is sold not for "support" but for the client pressing a button and receiving a fresh guarantee by morning.

If the rig cannot do that, it is consulting, and the automation will never pay off.

---

## 1. The automation boundary: four gates

Everything that produces **evidence** is done by the machine. The human only **ratifies**. Authorship is the bottleneck; ratification takes 10 minutes.

| Gate | Who | What they do | Time | Why not a machine |
|---|---|---|---|---|
| **G1. Boundary** | the client's product owner + infra owner | approves the draft register of write paths proposed by the rig | 20 min | the machine does not know that "this batch is temporary, it will be removed in March" |
| **G2. Policy** | our security engineer + the client | approves draft P (who may do what) | 30 min | policy is a business decision, not a derivation from code |
| **G3. Proof** | our lead verifier | accepts the proof package: checks the `assume`/`trusted base`, not the lemmas themselves | 30 min | checking assumptions is a judgement; the kernel checks the lemmas |
| **G4. Signature** | 4 signatories | sign the act | 10 min × 4 | a legal act |

**Total human time: ~2 hours for the first attestation, ~40 minutes for re-attestation.** Everything else is the DAG.

Critical: **at every gate the human sees a diff, not an empty field.** The rig generates a draft and shows "here is what I found, here is what I propose, here is what I do not know". Filling in from scratch is what eats 24 person-days.

---

## 2. Rig architecture: 12 components

```
                          ┌─────────────────────────────────────────┐
   client repo/rig        │  RUN COMPILER                           │
   ──────────────────────▶│  canonical manifest, hashes, DAG        │
                          └──────────────┬──────────────────────────┘
                                       ▼
        ┌──────────────────────────────────────────────────────────────┐
        │  ORCHESTRATOR (Temporal) — durable DAG, budget, retries      │
        └───┬────────┬────────┬────────┬────────┬────────┬────────────┘
            ▼        ▼        ▼        ▼        ▼        ▼
   ┌──────────┐┌─────────┐┌────────┐┌────────┐┌────────┐┌──────────┐
   │1 INVENT  ││2 POLICY ││3 MEDIAT││4 WITNESS││5 REDTEAM││6 PROOF  │
   │  eBPF    ││  SMT    ││ Permit ││  tap/DB ││ scripts ││ Verus/   │
   │  pgaudit ││  Z3     ││  + DB  ││  /IdP   ││  fixed  ││ Dafny    │
   │  IaC/API ││  model  ││ trigger││         ││  suite  ││          │
   └────┬─────┘└────┬────┘└───┬────┘└────┬────┘└────┬────┘└────┬─────┘
        └───────────┴─────────┴─────────┴──────────┴──────────┘
                                 ▼
                    ┌────────────────────────────┐
                    │ 7 EVIDENCE PLANE (CAS+WORM)│
                    │ 8 AGGREGATOR (verdicts)    │
                    │ 9 DECLARATION GENERATOR    │
                    └────────────┬───────────────┘
                                 ▼
              ┌───────────────────────────────────┐
              │ 10 GATE UI (4 signatures, diff)   │
              │ 11 REATTEST CLI (one command)     │
              │ 12 EVAL HARNESS (self-check)      │
              └───────────────────────────────────┘
```

| # | Component | What it does | Automation |
|---|---|---|---|
| 1 | **Inventory** | finds all writers: eBPF over syscalls, `pgaudit`, IaC/OpenAPI parser, network-policy linter, call graph | full |
| 2 | **Policy engine** | draft P from the code + SMT check (Z3): contradictions, implicit allows, delegation cycles | full, the human only ratifies |
| 3 | **Mediator builder** | generates the mediator skeleton + `Permit` + DB trigger for the specific stack | draft, finished by hand |
| 4 | **Witness plane** | tap on the host, DB digest, interception of IdP assertions | full |
| 5 | **Red-team suite** | a **fixed set of scripts** (not an agent) — 7 attacks, each of which must fail | full |
| 6 | **Proof pipeline** | Verus/Dafny: spec → annotations → proof-fixing (LLM + a human at G3) | semi-automatic |
| 7 | **Evidence plane** | CAS + WORM + hash-chain, every artefact by sha256 | full |
| 8 | **Aggregator** | reduces the C/T/N verdicts into `PROVEN`; does not execute and does not interpret | full |
| 9 | **Declaration generator** | assembles act Z from the bundles, prepares the diff for the 4 signatures | full |
| 10 | **Gate UI** | 4 screens, each with a diff "proposed / changed / not checked" | human 10–30 min |
| 11 | **Re-attest CLI** | `attest --z z-042 --commit abc123` → a full re-run | **one command** |
| 12 | **Eval harness** | the rig's self-check: mediator mutants, canary attacks, determinism | full, in CI |

**Why the red-team is scripts and not an agent.** An attack that is not deterministic proves nothing: if an agent "tried to bypass it and could not", that is not evidence. Seven attacks are seven executable files with an expected result of `BLOCKED`. An agent may *search* for new attacks, but only those that reproduce go into the act.

---

## 3. Stack: concrete decisions

| Layer | Choice | Why exactly this |
|---|---|---|
| Isolation | **Firecracker microVM**, bare-metal | the decision from circle 2; nested virtualisation kills the point |
| Orchestration | **Temporal** | durable state, idempotent steps, retries without double effects |
| Inventory | **bpftrace + pgaudit + trivy/config parser** | eBPF sees the real syscalls, pgaudit the real writes; the IaC parser sees what is declared |
| Policy | **Z3** + our own DSL (YAML → SMT) | SMT gives free counterexamples for incorrect policies |
| Mediator (proof track) | **Rust + Verus** | the best balance: memory for free, provable contracts, industry acceptance |
| Mediator (brownfield) | a **library for the client's stack** (Java/TS/Python) with a private constructor + CI linter | these languages have no linear types — we emulate them with discipline + a linter |
| Last line | **Postgres `BEFORE INSERT/UPDATE` trigger** that verifies the `Permit` signature | bypass at code level is impossible: the DB physically rejects the transaction |
| `Permit` | an **Ed25519-signed token** + TTL + binding to `object_id`/`version`/`policy_hash` | allows the right to be checked outside the process — both in the DB and in a sidecar |
| Witness | **eBPF tap + WAL digest + IdP-assertion capture** | three channels = three different classes of forgery |
| Proof | **Verus** (Rust), **Dafny** (algorithms), **Lean** (policy invariants) | by task class, not "one tool for everything" |
| Evidence | **S3 Object Lock (WORM) + Rekor** | an external timestamp that cannot be rewritten |
| Reports | **JCS canonicalisation, SHA-256, Ed25519, SARIF + PDF** | canonicalisation so that the hash is reproducible |

---

## 4. Run DAG: 9 steps, who does what

| # | Step | Input | Output | Who |
|---|---|---|---|---|
| 1 | `compile` | repo/rig | manifest, DAG, budget | auto |
| 2 | `inventory` | manifest | **draft of register Z**: all writers, credentials, inputs | auto |
| 3 | **G1** | draft Z | signed register | **human: 20 min** |
| 4 | `policy` | register Z + code | draft P + SMT counterexamples | auto |
| 5 | **G2** | draft P | approved policy | **human: 30 min** |
| 6 | `mediate` | P + stack | skeleton M, `Permit`, DB trigger, credential migration | auto + finishing |
| 7 | `witness` | Z | three channels + A/B acceptance tests | auto |
| 8 | `attack` | Z, M | 7 attacks, each → `BLOCKED` | auto |
| 9 | `prove` | M | proof package, assumptions ledger, TCB | semi-automatic |
| 10 | **G3** | proof package | accepted / returned | **human: 30 min** |
| 11 | `declare` | everything | act Z + bundles | auto |
| 12 | **G4** | act | 4 signatures | **human: 10 min × 4** |

**Re-attestation** is steps 1, 2, 6, 7, 8, 9, 11 on a new commit, with G2/G3 in "the diff has not changed" mode (then ratification is one click) and G4 automatic if the hashes match the reference and nothing in Z has changed. Hence 15 minutes.

---

## 5. Four blind spots and how they are closed technically

### 5.1. `Permit` in legacy code

Java/TS/Python have no linear types — the compiler will not prevent bypassing the mediator. Three levels of protection, from cheap to expensive:

1. **Private constructor** in the client library: `Permit` is created only inside `Mediator`. A bypass requires reflection — which is already a visible, noisy act.
2. **CI linter**: forbids `INSERT/UPDATE` into ledger tables unless they go through `LedgerRepository.save(..., Permit)`. This catches 90% of bypasses at merge.
3. **DB trigger**: `BEFORE UPDATE` verifies the `Permit` signature in the transaction context (`SET LOCAL app.permit = '...'`). This is a **physical** guarantee — the last line, and it is exactly what turns "discipline" into "closure".

The order is mandatory: without the third level, the first two are organisational measures.

### 5.2. Single writer as a SPOF

"One writer" is a **logical**, not a physical unit. Two ways:

- **Event sourcing**: clients emit `IntentToTransfer` into a queue; the writer is a consumer partitioned by `tenant_id`. It scales, but adds latency and complexity.
- **DB-level enforcement**: there are many writers, but the trigger with `Permit` verification prevents a write without a valid right. Simpler, cheaper, and preferable for the pilot.

For the pilot: **the second option**. It gives the same property (no mutation without a `Permit`) without distributed transactions.

### 5.3. "Three days" versus continuous deployment

The three-day rule kills CI/CD if it is applied to every endpoint. The solution is to **split Z into two boundaries**:

| Boundary | What changes | How it is updated | SLA |
|---|---|---|---|
| **Static (infra)** | a new writer, a new DB, a new channel, new credentials, a new queue | 4 signatures | 3 working days |
| **Dynamic (code)** | a new endpoint inside an existing service | automatically: the M hash and policy_hash are baked into the build artefact | **real-time** |

A deploy with a mismatched M hash physically does not pass (CI gate + a check on the M side at startup). That is, **the code boundary cannot change unnoticed** — while the infrastructure one requires signatures.

And for the duration of the window a **`DEGRADED`** state is introduced: new paths — deny by default; money paths — full deny until re-issuance. Three days must not be a window of legal bypass.

### 5.4. The break-glass paradox

The point of emergency access is to work when the mediator is broken. So it cannot be mediated. The solution is a **cryptographic emergency token**:

- a hardware key (HSM/YubiKey) held by the client's CISO, not in the system;
- the DBA signs raw SQL with this key → the DB accepts it but sets the flag `is_emergency = true`;
- the witness immediately generates a critical-level alert;
- **the guarantee is suspended automatically** until reconciliation and signing of the incident act.

This is honest: emergency access exists, it is visible, it is documented, and it suspends the guarantee. Hiding it means getting a bypass that is discovered only after an incident.

---

## 6. Invariants as executable checks

Every decision from circle 4 must become a check, otherwise it remains text.

| # | Invariant | How it is checked automatically |
|---|---|---|
| **I1** Complete mediation | every ledger mutation passes through M | reconciliation of the `pgaudit` delta with the log of `Allow` events; any discrepancy → failure |
| **I2** Capability enforcement | an operation is accepted only with a valid `Permit` | the DB trigger rejects a write without a signature; an attempt without a `Permit` → `BLOCKED` |
| **I3** Atomic authorisation | the check, the `Permit`, the event and the mutation are one transaction | a test with fault injection at each step: nothing must be left "authorised but not executed" |
| **I4** No ambient authority at the DB | write access to the ledger only for M | credential scanner: the list of principals with `INSERT/UPDATE` = {M} |
| **I5** Signed deploy | M, policy and migrations only when the hashes match | CI gate + hash check at M startup |
| **I6** Fail-closed audit | unavailability of the log/witness → `Deny` | chaos test: kill the channel, expect a denial, not a success |
| **I7** Version-bound decision | a decision is valid only for the version of the object and of the policy | concurrent test: change the object between the `Permit` and the write → `BLOCKED` |
| **I8** Restore procedure | restore only via a signed snapshot + re-issuance of Z | a run of the 6-step procedure as an acceptance test |

**Three of the eight invariants are not a "proof" but a test.** I1, I6, I8 cannot be proved formally for an arbitrary system, but they can be checked on every run. This is exactly the "proved / measured" distinction that we fixed in circle 3, and it must not be blurred in the act.

Beyond the eight, the reviewers gave an important refinement: `∀ Permit ⟹ P` is **insufficient**. A second invariant is needed:

> **∀ mutation(ledger) ⟹ ∃ Permit ∧ ∃ signed `Allow` event**

The first says "the mediator does not lie". The second says "nothing went past the mediator". Without the second, the typical protection remains a library that can simply not be called. This is I1+I2 together, and they must be checked separately.

---

## 7. How to get "super quality" without a human: the eval harness

Quality must not depend on the operator, so the rig checks itself on every change.

| Rig test | What it catches | Frequency |
|---|---|---|
| **Mediator mutation testing** | 20+ mutants: comparison inversion, removal of the version check, bypass of `deny` | every PR |
| **Canary attacks** | 7 scripts, all must be `BLOCKED` | every release |
| **Witness plane test A** (replay/substitution) | forgery of an observation | every release |
| **Witness plane test B** (independence) | an agent cannot disable the channel | every release |
| **Determinism** | 20 repeated runs of one task → identical hashes | every release |
| **Negative corpus** | repositories with no vulnerability → 0 false `PROVEN` | every release |
| **Acceptance regression** | act Z assembled yesterday is reproduced byte for byte | every night |

**The main quality principle: act Z is reproducible byte for byte.** If yesterday's act cannot be reassembled and give the same hash, the rig is non-deterministic, and no signature under it is worth anything. This is the test that catches everything else.

---

## 8. Re-attestation: one command

```
$ flow-attest --z z-042 --commit 9f3a1c --sign
  [1/9] compile ........ manifest hash 3b7e…
  [2/9] inventory ...... 14 writers, Δ = 0     ← no boundary change detected
  [3/9] policy ......... SMT ok, Δ = 0
  [4/9] mediate ........ M 1.4.2, hash matched the proved one
  [5/9] witness ........ 3 channels ok, A/B acceptance tests passed
  [6/9] attack ......... 7/7 BLOCKED
  [7/9] prove .......... re-verification: 0 sorry, 0 new assume
  [8/9] declare ........ act Z-042 v7, hash 8d21…
  [9/9] gate ........... Δ empty → auto-signature allowed by the owner
  ✓ Guarantee extended to 2027-10-27
```

**15 minutes, 2 signatures.** This is the product people pay a subscription for. If even one step showed `Δ ≠ 0`, the rig stops and requires G2/G3 — that is, the human joins exactly when something has actually changed.

---

## 9. Day 1: a Hello World that tests the whole hypothesis

Do not start with the platform. Start with one flow and 500 lines.

| Day | What we do | Artefact |
|---|---|---|
| 1 | take an open-source "bank" (or 500 lines from the client repo under NDA): balance mutation | repo + commit |
| 2 | `inventory`: bpftrace + pgaudit → draft register of writers | 14 lines of the register |
| 3 | draft P + SMT: "only the owner/system changes the balance" | a counterexample or `unsat` |
| 4–6 | `Permit` + mediator in Rust/Verus (~150 lines) + DB trigger | a working M |
| 7–9 | witness: tap + digest + identity on this same rig | 3 channels |
| 10 | 7 attack scripts | 7 × `BLOCKED` |
| 11–13 | proof of M in Verus: **measurement of proof-fixing** | the figure "days per 100 lines" |
| 14 | act Z + signatures, re-attestation with one command | a reproducible act |

**What this proves in 14 days:** (a) inventory can be automated, (b) `Permit`+trigger physically block bypass, (c) the proof costs what we estimated, (d) re-attestation takes minutes.

**What it refutes if it does not work out:** if on day 10 even one attack passes, the whole "closure" hypothesis is false, and that must be learned on day 10, not on day 45.

---

## 10. What it costs and who is needed

| Item | Pilot (45 days) | Rig (ongoing) |
|---|---|---|
| People | 24 person-days | 0.5 FTE for rig maintenance |
| Infrastructure | 1 bare-metal node + object storage | $1.5–3k/month `[estimate]` |
| LLM | proof-fixing and skeleton generation | $200–800 per engagement `[estimate]` |
| Proof tools | Verus/Dafny/Z3 — open source | 0 |

**Minimum team:** 1 platform/sandbox, 1 formal-methods, 1 AppSec. Three people are exactly those who close G2 and G3 and build the rig. Without a formal-methods person the pilot is impossible: the proof of the mediator is the one thing that cannot be delegated.

---

## 11. What we deliberately do not build in v1

| Not building | Why |
|---|---|
| Five policies at once | the pilot needs two: ownership and limit. The rest — after the first client |
| Event sourcing / distributed writer | the DB trigger gives the same property more cheaply |
| Our own proof assistant | Verus/Dafny/Lean exist and are cheaper than in-house development |
| Automatic search for new attacks by an agent | only reproducible scripts go into the act; the agent is out of scope |
| Support for 10 stacks | one stack for the pilot, the second — if the client pays |
| SaaS multi-tenancy | one client, one rig, one act |

---

## 12. Summary

The rig is not "an agent that does everything". It is **a pipeline that produces evidence, and four screens on which the human ratifies it**. Three things make it automatic in substance:

1. **Drafts instead of empty fields** — the human always sees a diff, never writes from scratch.
2. **Scripts instead of agents** in whatever goes into the act — because a non-deterministic check is not a check.
3. **Re-attestation with one command** — the whole gain from automation lives here, and it is what turns a one-off project into a subscription.

And "super quality" is provided not by people but by the fact that **yesterday's act is reproduced byte for byte**. If that holds, the signature under it means something. If not, it is a PDF.
