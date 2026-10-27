# 90. Development, the sober picture, and the next round

**Document status:** round 2 summary (five reviews) + development method + round 3 questions.
**Spec references:** [master v2](FLOWGUARD-MASTER-v2.md) · [on-chain detail](SPEC-v0.1.md) · [legacy detail](SPEC-v0.2-LEGACY.md) · [pricing doctrine](80-PRICING-DOCTRINE.md) · [claims register](SPEC-CRITIQUE.md)

---

# 1. What round 2 produced: one cross-cutting requirement and three rulings

## 1.1. The cross-cutting requirement stated by one reviewer and supported by the rest

> **Every product claim must carry an externally anchored denominator that the paying party cannot change silently.**

This is the best thing said across two rounds. Let us break it down into four applications:

| Claim | Denominator | Who anchors it |
|---|---|---|
| "there is no bypass" | the set of `discovered` paths and the coverage ratio `covered/discovered` | machine + independent manual enumeration (M1) |
| "the finding is confirmed" | `C/T/N` on fresh VMs, K runs, the oracle's FP ceiling | the verifier, not the agent |
| "the target is the one in the attestation" | hash of the deployed artifact **from an external source**, not from the bundle | blockchain / OCI registry / node |
| "X% of money flow is covered" | `Σvalue(covered) / Σvalue(all paths)` | observed traffic, not a declaration |

Without a denominator, any "PROVEN" of ours is `covered/discovered` without `discovered`. **This is exactly T3 (vacuous PROVEN), translated from a risk into an architectural rule.**

## 1.2. Three rulings we will have to accept

**Ruling 1. Closure completeness is not provable — only measurable.**
5/5 reviews: `unknown_paths = ∅` proves the absence of the unknown *inside the analyzer's model*. Therefore `PROVEN` without an explicit detector and a measured recall is a false claim. Already fixed in [master v2 §1.2–1.3](FLOWGUARD-MASTER-v2.md): the verdict became `PROVEN(R)` with a coverage scalar. **But this is not a solution, it is an honest formulation** — recall has to be measured (M1), and it will almost certainly be 0.6–0.8 rather than 1.0.

**Ruling 2. Legacy in its current form does not pass its own death criterion.**
All five estimated the median number of findings at ≈1 against our threshold of `<2`. Plus a separate remark that removes the criterion itself: **zero findings output is a success for a guarantee and a "death" by the metric.** The metric was serving two different products.
Consequence: **we narrow the scope to an isolated ledger core** and change the metric to `closure_complete` + SKU conversion. Detail — [SPEC-v0.2 §3.1–3.4](SPEC-v0.2-LEGACY.md).

**Ruling 3. The question is not whether we can issue a guarantee, but who needs one.**
One reviewer's formulation: if no **external consumer** — insurer, auditor, bank, counterparty — changes a decision in writing given the bundle, then offline verifiability solves a non-existent problem, and pricing off `value_at_risk` loses its basis. Our own escrow does not count as a consumer: that is circular validation.
This is measurement **M8** and probably the main filter: without it the product is a tool, not a guarantee.

## 1.3. Where the reviews diverged, and how it was decided

| Question | Split | Decision |
|---|---|---|
| Narrow the scope (a) / change the metric (b) / remove the criterion (c) | (a) 2, (b) 3 | **Hybrid: (a) as the scope, (b) as the metric.** The core is an isolated ledger; the metric is `closure_complete` on the core; `G25` (findings yield) is demoted to a SKU-1 metric |
| Minutes per finding | 20, 25, 35, 38, 45 | **plan 35–40**, the target of 15 is unreachable for a signer (all five agreed) |
| "Do not build" condition | 5 different ones | **a set of three, all accepted**: (i) ≥6/10 customers do not exclude DBA/superuser from the threat model; (ii) a reproducible false `PROVEN`; (iii) `closure_complete < 50%` across 10 pilots |
| Who signs the on-chain attestation | 4 options | **product owner (multisig) · custody quorum · security lead · verifier**; for immutable — confirmation that no roles exist instead of custody |
| Auto-payout ceiling | $500…$25k | **$500 at the start**, a ladder up to $25k by track record; at the start it is the ceiling that protects, not the bond |

---

# 2. How to develop this: method, not talent

The code is written only by AI agents in a harness on a single machine. The main consequence follows from this: **quality is determined by the process, not by the executor's skill.** An agent has no memory of yesterday's decisions, no sense of shame about a broken test, and no reason not to fit the check to the result.

So the process must be such that fitting is **mechanically impossible**. Such a process already exists — in [VecDHT](https://github.com/mak777uh/VecDHT): hypothesis → experiment card with a threshold fixed **before** the run → ADR decision. Below it is carried over to FLOWGUARD.

## 2.1. The laboratory loop (ported as is)

```
H-XXXX  hypothesis: what exactly we are testing, in one sentence
E-XXXX  experiment card: method, corpus, threshold, failure criterion — BEFORE the run
R-XXXX  result: numbers, log, verdict (supports | refutes | inconclusive)
ADR-XXXX decision: one spec edit following from R-XXXX
```

Five rules that make the loop insurmountable for sloppy work:

1. **The threshold cannot be invented after the result.** A changed threshold is a new experiment; the old one remains with its verdict.
2. **A negative result stays in `lab/` forever** with the verdict `refutes`. Records are append-only.
3. **The oracle (test) is also run on the version before the fix**, and its output is committed: a prediction is checked by a number, not by memory.
4. **A fact qualifies for a verdict only if it is identical across two runs of an unchanged tree.**
5. **Only a measured fact edits the spec**, in a separate commit, together with a human-readable mirror.

The last rule answers the question "how are research and the spec connected". Right now there is no connection: `[HYPOTHESIS]` numbers live in the text and nobody forbids changing them. What is introduced: **every number in the spec has an `E-id`. A number without an `E-id` is not a number but an opinion, and it does not go into commercial material.**

## 2.2. What carries over to FLOWGUARD directly

| VecDHT element | In FLOWGUARD | Why |
|---|---|---|
| `lab/hypotheses/H-*.md` | `lab/hypotheses/` | hypotheses: detector recall, K and flakiness, minutes per review, share of validatable targets |
| `lab/experiments/E-*.md` | `lab/experiments/` | the M1–M9 cards from [master §7](FLOWGUARD-MASTER-v2.md) move here as E-cards |
| `lab/adr/ADR-*.md` | `lab/adr/` | one decision each: "K≥5", "a $50k ceiling", "core instead of flow" |
| `docs/METRICS.md` | `docs/METRICS.md` | every number + `E-id` + the re-measurement command |
| `docs/STATUS-v1.md` | `docs/STATUS-v0.1.md` | the five v0.1 conditions and an honest "not done" list |
| `AGENTS.md` | `AGENTS.md` | the contract for executing agents (§2.4) |
| `lab/check-*.sh` | `lab/check-*.sh` | cheap guards: spec mirror, text cleanliness, inventory, cross-check of vectors |
| counter generation | `lab/inventory.py` | numbers in the README are generated, not typed by hand |
| from ["-"](https://github.com/mak777uh/-) | run manifests + reports | the run manifest as a first-class artifact: without a manifest a run does not count as having happened |

## 2.3. Release conditions for v0.1 (they replace the "roadmap")

Five conditions, each verified from the outside:

| # | Condition | Measured by |
|---|---|---|
| **C1** | The oracle contract and the bundle are implemented, `verify` works offline | `fg verify` on the reference bundle, network off |
| **C2** | The three escrow invariants are proved or refuted on the reference contract | `fg check` + Foundry/Halmos |
| **C3** | Ten attacks yield `BLOCKED`, and on the broken version they do not | mutation test of the attack set |
| **C4** | Byte-for-byte reproducibility: `attest` + `replay` twice | hash comparison |
| **C5** | Claims register v2 is closed: every `[HYPOTHESIS]` has an `E-id` or a "not measured" label | `lab/check-claims.py` |

Until all five are met, the version does not exist, regardless of what works.

## 2.4. Contract for executing agents (`AGENTS.md`)

Rules that prevent an agent from "pretending":

1. **You may not change the threshold, the acceptance criterion, the spec or the test in order to pass.** Such a change only through an `ADR` with an `E-id`.
2. **Tests are written by a different agent** from the implementation, and from the spec, not from the code. The testing agent does not see the implementation.
3. **Every claim in a PR carries a reference**: `E-id` (measured), `H-id` (hypothesis) or `ADR-id` (decided). A PR without a reference is accepted only as a document or a bug fix.
4. **`--no-verify`, `#[ignore]`, `skip`, `xfail`, weakening an assert are forbidden.** Their presence in a diff is an automatic reject, not a remark.
5. **You may not write to `tests/`, `spec/`, `lab/` or the check scripts** — only to `src/`. These paths are read-only for the agent implementing a feature.
6. **"Not checked here" ≠ "passed".** If a gate was not run in the environment, the status is `not_checked`, and that is written down.

Rule 2 is the main one. It turns "an agent wrote a test that passes" into "an agent wrote a test from the spec, having not seen the implementation".

## 2.5. The hole that must be named out loud

In [VecDHT](https://github.com/mak777uh/VecDHT) it is honestly recorded: "the formal loop (Verus, Kani, Lean) proves statements about models, and the model↔code correspondence is not checked by an executable tool". We will have **the same hole**, and it is more dangerous than it seems: Verus will prove a property about the Rust code that is written, not about the one described in the spec.

Three measures that narrow it (and none closes it):
- **translation validation**: extracting the model from the code (Charon/Aeneas) and proving about it — that is, we prove about what is actually compiled;
- **property tests from the spec**: the same predicates are run as executable ones under fuzzing, independently of the proof;
- **`assumptions.json` with `what_breaks_if_false`** — every assumption carries the price of its being false.

The honest formulation for the attestation: "proved about the model extracted from the code of version X, under assumptions A". Not "proved".

## 2.6. What follows from this for timelines

If agents write the code, the bottleneck is not writing but **verification**. Estimates:

| Stage | Written by an agent | Verification and acceptance | Total `[HYPOTHESIS]` |
|---|---|---|---|
| v0.1 on-chain escrow | 2–3 weeks | 2–3 weeks | **5–6 weeks** |
| legacy dynamics | 3–4 weeks | 4–5 weeks | **8–9 weeks** |
| mediator proof | 1 week | 3 weeks | **4 weeks** |

That is, agents speed up the first column several times over, while the second barely compresses: acceptance is done by people and tools. **Plan by the right-hand column.**

---

# 3. The sober picture: what actually exists

Without consolation, as of now.

**What actually exists.**
1. A product formulation that is checkable: "within the declared closure you cannot get past the control point", with a mandatory coverage scalar and a relative detector.
2. The distinction between proved / measured / hypothetical, carried through to a separate section in every attestation.
3. A bundle format that can be implemented and verified offline — that is 4–6 weeks of engineering work, not a dream.
4. A development process (the laboratory loop) that makes fitting mechanically impossible.
5. An understanding of exactly where the product breaks: path completeness, the trusted release loop, vacuous PROVEN, the absence of an external consumer for the attestation.

**What does not exist and will not soon.**
1. **`PROVEN` in the strong sense** — unprovable for an arbitrary system. The maximum is `ENFORCED_TESTED(R)` with a measured recall.
2. **A median of ≥2 findings** on a legacy target — all five reviews gave ≈1. That is why legacy is narrowed to the core.
3. **An external consumer of the attestation** — never tested once. While there is none, what is sold is a tool, not a guarantee.
4. **Detector recall** — not measured. While it is not measured, `PROVEN(R)` must not be printed.
5. **A legal guarantee** — there is neither insurance, nor actuarial data, nor a contractual basis.

**What this means, honestly.** The product in its current form is **a tool for constructing a verifiable claim about a control boundary**, with an honestly limited scope. Not "security", not "a guarantee against vulnerabilities", not "we checked everything". Anyone who reads the master document and decides that we are selling protection against compromise will be disappointed — and that is fine, because the disappointment comes while reading, not after an incident.

**The one thing that makes the product valuable and that competitors do not have:** an attestation that **can be checked without believing us**, and that **cannot be passed off as more than it is** — because the denominator is printed in the header.

---

# 4. Round 3: questions

The method is the same: hit by ID, three verdicts, do not paraphrase. The first two rounds closed the product model and the technical claims. The third is about development, method, and who this is sold to.

**A. Development by agents.** List **three** mechanisms by which an AI agent in a harness can circumvent the rules of §2.4 (without noticing it) and push through a false result. For each: how it would show up in the diff and which automatic guard catches it. Not "hallucinations" — concrete workarounds.

**B. The method's weak point.** The laboratory loop has a "model↔code" hole. Find a **second** hole of the same class — a place where the check formally passes but there is no guarantee. For each: how to narrow it.

**C. Denominator.** Choose **one** denominator from §1.1 that is hardest for the paying party to fake, and **one** that is easiest. For the easy one: how to anchor it externally.

**D. Release threshold.** The five conditions of §2.3 are checkable but not ranked. Order them by "what is most likely to fail first" and name, for the first one, a failure threshold in numbers.

**E. One "do not build"** — about development, not about the product: an observable condition under which a team of AI agents **will not be able** to bring this to v0.1 in a reasonable time.

**F. One question that is missing.** Formulate a question we should have asked in this document, and answer it.

**Rules:** ≤200 words per item · no "it depends on the context" · "I don't know" is allowed · do not propose new architectures · do not retell the document.
