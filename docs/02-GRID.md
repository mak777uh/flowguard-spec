# 02. The unified remediation ladder ("grids") and the confidence grid

> Nine sources produced 4, 5 and 6 levels. Here is one technical grid R0–R5 onto which both commercial SKUs (S1–S5) and certification levels (F0–F5) project without loss.

---

## 1. Why six, and not four or five

Four levels (T1, S1) glue together "change nothing" and "change the configuration" — in the mass segment that is acceptable, in the regulated one it is not: T6 showed that F0 (finding + proof, we do not touch the code) and F1 (configuration/data only) are **different products with different prices and different impact analysis**. Five levels (T2, T4) glue together "hardening" and "refactoring", and these are different classes of work: the first reduces reachability, the second removes the root cause.

Six is the minimum number at which every level has **its own class of proof obligation**. That is the criterion: a level is determined not by the size of the diff, but by what exactly can be proved about it.

---

## 2. The R0–R5 grid

| R | What we do | Proof obligation (what is proved) | What this does NOT prove | Automation | Human | Certification price | Price range |
|---|---|---|---|---|---|---|---|
| **R0 Mitigation** | WAF rule, security header, feature flag, rate limit, network ACL, secret rotation, endpoint disablement | "the attack from the bundle does not pass after the change"; the variant suite goes quiet | nothing about the root cause; bypassed by changing the encoding/path | high (silencing the PoC) | check that legitimate traffic did not drop off | ~0 | €0.5–3k |
| **R1 Patch** | parameterized query, bounds check, output encoding, allowlist, order of authorization checks, dependency update | "the patch applies to commit X; the PoC goes quiet on K (adaptive 3→10); the variant suite goes quiet; regression is green" | absence of behavior changes outside the tests | high | review of idiomaticity, API semantics | impact analysis + re-run of the affected verification | €1.5–4k |
| **R2 Hardening + detector** | sanitizers in CI, a permanent fuzzing loop, coverage, secure defaults, CIS profiles | "no ASan/UBSan/MSan/Miri findings on corpus C over T CPU-hours; coverage ≥ target" | absence of unobservable defects; guarantees on uncovered paths | almost complete | minimal (corpus setup) | new tool in the baseline → qualification evidence | €8–25k/year |
| **R3 Module refactoring** | change of the trust boundary, centralization of authz (ABAC/ReBAC), deserialization allowlist, moving the parser out into a process | "the module has no UB on domain D" (Frama-C WP / Kani bound / Miri) **and** "the attack class is unreachable by construction" | that domain D covers the real input | medium (annotations, counterexamples) | loop invariants, aliasing, domain acceptance | architecture change → allocation review | €25–60k |
| **R4 Memory-safe rewrite** | module in Rust/Ada/Go, WASM sandbox for the parser, seccomp/landlock, CFI | "new module: no-UB + contracts (Verus/Creusot/SPARK)" **and** "equivalent to the old one on D" (diff-fuzz + property-based + translation validation) | equivalence outside D; performance (only measured) | medium-high | the boundary of D, contested edge cases, support of two implementations during the transition | new component in the baseline + qualification of its tools | €60–150k |
| **R5 Verified core** | invariant-carrying core (Lean 4 spec + Verus/SPARK/Dafny code), extracted code, conformance against legacy | the set: safety invariants, functional correctness, design properties (TLA+), equivalence on D, **assumptions ledger + TCB + anti-vacuity** | correctness of the specification itself (**spec risk** — not automated); side channels; the binary under an unverified compiler | a significant part of the lemmas | choice and ratification of the specification; independent reviewer | DO-333 credit at L4; a package for the authority | €150–400k+ |

**Three rules without which the grid turns into a price list:**

1. **The level is assigned by the class of obligation, not by volume.** A one-line patch provable via Kani on a domain is R3 in guarantees and R1 in price. Write it that way.
2. **Every level is obliged to print what it does NOT prove.** The column above is not an appendix, it is part of the verdict.
3. **R4/R5 without equivalence is not a fix but a replacement.** Diff-fuzz and translation validation are mandatory, otherwise "rewrote" = "broke it differently".

---

## 3. The client-facing view: the confidence grid

The internal language (L0–L5 from T6) is too heavy for a report. To the client we show four labels — they are also the fields of every fix option (S5):

| Label | What it means | Internal level | Statement formulation |
|---|---|---|---|
| `static-only` | pattern/taint/dependency; reachability not proved | L0 | "looks like a vulnerability in this version" |
| `reproduced` | reproduced in a sandbox, a bundle exists | L1 | "there exists an input under which…" |
| `reasoned` | exhaustive check within bounds (BMC / model checking / bound B) | L2 | "for all inputs within bounds B" |
| `formally-proven` | deductive proof under assumptions A1..An | L3 | "for all inputs under assumptions A" |
| `human-approved` | signed off by a qualified engineer | procedural | "I attest to the process and the evidence" |

**L3 ≠ L4 and this must be written explicitly.** A proof about the model is not a proof about the binary. The gap is closed by enumerating the trusted base: parser and IR semantics, compiler, linker, SMT solver, proof-checking kernel, coverage tools, orchestrator, signing infrastructure — and the **human reviewer**, who is also part of the TCB and therefore must be trained and calibrated.

Rule: no option may be upgraded in its label automatically because another option has been proved. And no label turns into a "security score".

---

## 4. The fix option passport (mandatory fields)

Every fix option is an object with a passport, not a paragraph of text. Without a passport an option does not make it into the commercial proposal.

| Field | Content |
|---|---|
| `fix_id` / `level` | identifier and R0–R5 |
| `closes` | which findings/root causes/classes it closes (references to graph nodes) |
| `leaves_open` | what will remain after application — in plain words |
| `diff_or_plan` | diff, PR draft or migration plan |
| `po_list` | discharged proof obligations with id and verdict (`PROVEN`/`DISPROVED`/`NOT COMPLETED`/`OUT OF SCOPE`) |
| `assumptions` | assumptions A1..An: owner, justification, method of validation |
| `tcb` | what is not verified and why that is acceptable |
| `checks_passed` / `checks_not_run` | which checks passed, which could not be run and why |
| `regression_risk` | expected risk + perf/behavior budget |
| `rollback` | how to roll back, and in how long |
| `effort` | person-days (explicitly as an estimate, not as a fact) |
| `confidence` | the label from §3 |
| `artifact_digest` | binding to the commit/image digest/toolchain/spec |

**Prohibited:** a single number instead of a passport; "high/medium/low security" without grounds; a recommendation without `leaves_open`.

---

## 5. How the price is computed

```
price(option) = Σ(obligation × complexity_class)
              + human_at_gate
              + support (for R4/R5 — mandatory retainer)
```

- Complexity classes are calibrated on pilots, not invented.
- To the client we give **three forks**, not one figure: (R0+R1), (R2+R3), (R4+R5). The forks are needed so that the decision is informed rather than "take the big one".
- **Never a price per finding** — that incentivizes finding inflation and kills trust. A price per scope, per change, per subscription to the freshness of proofs.
- For R4/R5 — not "work" but **a license for the proof plus its maintenance**: a proof is obliged to survive commits, otherwise in six months it is a historical document.

---

## 6. Projection onto commercial SKUs and regulated levels

| R | SKU (T4) | Regulated (T6) | Who signs |
|---|---|---|---|
| R0 | S1 "proven bug" (partially) | F0 finding / F1 configuration | named assessor |
| R1 | S2 "patch" | F2 patch without a requirement change | our engineer; merge — the client's tech lead |
| R2 | S3 "hardening" | F5 architectural mitigation (sometimes) | our architect + platform lead |
| R3 | S3/S4 "refactoring" | F3 requirement/architecture change | architecture decision — **the client**, we own the re-assessment verdict |
| R4 | S4 | F4 replacement with a verified core | formal-methods lead + external reviewer |
| R5 | S5 "migration + proof" | F4 + qualification kit | formal lead + independent reviewer + the client's certification engineer |

Responsibility separation rule: **we do not take design authority.** We own the verdict "this change closes it provably", not someone else's architecture. That is a direct road to responsibility for decisions we do not control.

---

## 7. What the client must see in the report next to the ladder

1. **Negative scope** — what was not tested (social engineering, physical access, DoS, third-party SaaS). Without it the report does not bound the claim and is useless to an auditor.
2. **Coverage map** — the share of the surface actually exercised, by class. Mandatory always, even when it is ugly.
3. **Share of human review** — `human_review_coverage: 100% | 40% | 20%`. Not as marketing, but as a limitation of the claim.
4. **Residual risk in four quadrants**: proved / assumed / not verified / not modeled.
5. **A "what we did not look at" section** — the direct difference from a scanner, which implicitly claims completeness.
