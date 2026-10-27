# 01. Architecture variants: not three projects but a matrix

> The main conclusion of the first round: "cloud vs on-prem" is **not an architecture variant** but a deployment axis. The nine sources seemed incompatible because they stood at different points of one matrix. Below is the matrix and three named products within it.

---

## 1. Three axes

```
AXIS 1 — GUARANTEE LEVEL (what we sell)
  V1 offense-gated      → "proven bug + proven fix"
  V2 remediation factory→ "ladder of fixes with an evidence passport"
  V3 certified change   → "minimal certifiable change + package for the authority"

AXIS 2 — DEPLOYMENT (where it runs)
  D1 SaaS               → everything on our side; fastest of all, trust not bought with code
  D2 hybrid runner      → dashboard on our side, code and tooling in the client's VPC   ← default
  D3 on-prem / air-gap  → nothing leaves; sold as a license

AXIS 3 — SCOPE (what goes in)
  S1 repo / archive / SBOM / image
  S2 + API-spec / IaC
  S3 + live targets (signed scope)
  S4 + formal core (spec + proofs)
```

The product line = three named packages, each available in three deployments:

| | V1 "Proven bug" | V2 "Remediation factory" | V3 "Certifiable change" |
|---|---|---|---|
| Axis 1 | offense-gated | offense-gated + grid + evidence | + deterministic evidence engine in the TCB |
| Axis 3 | S1–S2 | S1–S3 | S1–S4 |
| Axis 2 | D1, D2 | D1, D2, D3 | D2, D3 (D3 mandatory) |
| Time to first client | 8–10 weeks | 4–6 months | 9–15 months |
| Deal size | €8–15k | €15–60k + retainer | €150–500k, annual contract |
| Margin | high | medium → high with catalogization | low in v1, IRR on the third client |

---

## 2. V1 — "Proven bug" (first release)

**Bet:** we sell not a report but a **bundle** that the client replays on its own side in 4 minutes and gets the same result.

```
 intake ──► scope manifest (signed) ──► run compiler
                                              │
                          ┌───────────────────┴───────────────────┐
                          ▼                                       ▼
                 Lane A: coverage                        Lane B: proof
                 SAST / SCA / secrets / IaC              agent presses the candidate
                 → HYPOTHESIS (not billed)               → C/T/N × K (3 → 10)
                          │                                       │
                          └───────────────┬───────────────────────┘
                                          ▼
                            evidence plane (content-addressed)
                            manifest · hash-chain · replay kit
                                          │
                                          ▼
                            named assessor SIGNS → report
```

**What it proves:** "there exists an input under which effect X is observed, and it disappears after patch Y on commit Z".
**What it does NOT prove:** the absence of other vulnerabilities, the absence of breakage outside the tests, the security of the system. Never phrase it otherwise.

**Minimal composition (mandatory core, everything else is cut):**

| Component | Minimum for V1 | Why it cannot be cut |
|---|---|---|
| Sandbox | Firecracker microVM (Tier A — untrusted target code), gVisor runsc (Tier B — our own tooling), per-run, deny-all egress. **Bare-metal nodes: we avoid nested virtualization**, otherwise the point of the microVM is lost | without it there is neither PoC nor legal protection. The price of this decision is that bare metal is more expensive than cloud, a direct correction to the unit economics (see `03-EVAL-ROADMAP.md` §5) |
| PoC contract | ⟨F,A,T,O,V,S⟩ + C/T/N × **adaptive K**: 3 by default, escalation to 10 only under ambiguity; K is printed into the bundle | this is the product; without it, it is yet another scanner. A fixed K=10 × 3 branches × N restarts of a stateful target is the main source of cost explosion (reviewer no. 1's estimate) |
| Dependency prefetch | allowlist mirror of the registries, warm-up **before** sealing | deny-all by default breaks the build: dependencies are pulled from the network, `DEPLOY_FAILED` yields zero findings |
| Sealed oracle | templates per stack, the agent does not write the predicate | the only barrier against "I decided this is a bug" |
| Canary-nonce | per run, in the canary-store outside the VM | makes a hardcoded PoC physically impossible |
| Evidence plane | sha256 + manifest + offline replay kit | without it there is no signature, and without a signature there is no price |
| Named signatory | a human, 100% PROVED before shipment | this is what is being bought |
| Negative scope | a mandatory section | without it the report does not bound the claim |

**Failure modes that V1 accepts deliberately:** systematic false negatives (long business chains, multi-tenant, data requirements); races and DoS — only statistically; `DEPLOY_FAILED` on monoliths with unclear deployment.

**When V1 is optimal:** there is a deployable instance; the client has FP fatigue; an artifact is needed for audit/insurance/dispute with a contractor; C/C++ with prioritization by exploitability.

---

## 3. V2 — "Remediation factory" (recommended core)

**Bet:** a finding is an input, and the product is **a comparison of fix variants with evidence passports**. V1 inside, plus four new subsystems.

```
                              ┌──────────────────────────┐
   V1 (offense-gated) ───────►│  ROOT-CAUSE GRAPH        │
                              │  asset·threat·finding·   │
                              │  cause·invariant·fix·    │
                              │  artifact·verification·  │
                              │  residual-risk·decision  │
                              └───────────┬──────────────┘
                                          ▼
                    ┌─────────────────────┴─────────────────────┐
                    ▼                     ▼                     ▼
              R0–R2 (cheap)         R3 (refactoring)      R4–R5 (core)
              hotfix / patch        class, not instance    memory-safe / proof
                    └─────────────────────┬─────────────────────┘
                                          ▼
                            VERIFIER FARM (outside the agent's write-scope)
                            PoC quashing · variant suite · regression ·
                            diff-fuzz · perf budget · proof-check
                                          │
                                          ▼
                            PARETO FRONT (not "the best fix")
                            + a passport for each variant
                                          │
                                          ▼
                            client decision → PR / migration plan
```

**Four subsystems that V1 lacks:**

1. **Root-cause graph.** Typed nodes and edges (`caused_by`, `violates`, `mitigates`, `verified_by`, `introduces_risk`), each edge with provenance: code / tool result / explicit hypothesis. It answers questions the scanner does not answer: which fixes close several findings; what will remain after the minimal patch; which pieces of evidence go stale when a file changes.
2. **Peer generation of variants.** R0–R5 are generated by different models/seeds in isolated branches that do not see each other (protection against correlated error). A conflict is not a textual merge but a substantive conflict for the report.
3. **Verifier farm.** Everything that verifies lies in read-only, outside the agent's write-scope; an attempt to write to `tests/`, `spec/`, CI is an incident, not a trifle. The agent may edit only `src/` and only in its own branch.
4. **Pareto front instead of a rating.** No "security 97/100". Each variant is a vector: closes / breaks / provable / costs / rolls back / residual risk.

**V2 economics (a model, not a fact):** R0–R1 — a commodity with high margin and the entry into the account; R2 — the best ROI; R3 — the main differentiator; R4–R5 — piecemeal premium. Catalogizing R0–R2 into packaged "packs" is the only way not to slide into consulting margin.

**When V2 is optimal:** product teams with CI; clients that already have scanners and are hurting not on "find" but on "close and prove"; any segment with an audit.

---

## 4. V3 — "Certifiable change" (moat and second product)

**Bet:** in a regulated domain the agent **cannot** be the author of the evidence. It is a search heuristic over a formally defined objective function. The only writer into the evidence store is the deterministic arbiter.

```
CLIENT: VPC / on-prem / air-gap, the source does not leave the perimeter
   │
[1] INTAKE ── baseline: SCI, manifest, scope letter,
    class (DAL / ASIL / IEC 62304 class / SIL / PCI scope), certification basis
   │
[2] EVIDENCE ENGINE ← deterministic, PART OF THE TCB
    reproducible build · coding standards (MISRA/CERT-C) · analyzers ·
    coverage (including MC/DC pair independence) · fuzzers+sanitizers ·
    SBOM · configuration index
    → signed immutable evidence records = FACTS
   │
[3] AGENT LAYER ← OUTSIDE TCB, read-only on the source, writes only to scratch
    hypotheses: where to look for evidence, which PO to discharge
   │
[4] ARBITER ← deterministic, the only writer
    checks the POs, builds the package, computes coverage and residual risk
   │
[5] HUMAN SIGN-OFF ── certification engineer / DER liaison
   │
[6] CERTIFICATION PACKAGE: traceability · PO register · assumptions ledger ·
    TCB · "what we did not look at" · impact analysis
```

**The unit of work is not a vulnerability but a certification objective.** CWE is metadata. If a finding does not map to a goal of the standard, it is irrelevant, however true it may be.

**Why "just a patch" is often forbidden here:** a code change is a regression of the certification basis; even a semantically neutral edit devalues the evidence previously collected for the affected block. That is why what is sold is **the minimal certifiable change** with a precomputed price, including the honest option "accept the risk with a compensating control and a signature" as a separately paid item.

**Economics:** in v1 — 19% GM and a six-month cash cycle. It is not a product but a **credibility asset**. It becomes a product once the criterion is met: a second client on the same class of properties with a reuse of the proof harness ≥ 70%.

**When V3 is optimal:** avionics, automotive, medicine, industry, payments; the client already buys verification (the budget line is not discretionary); the horizon is years.

---

## 5. Why not the other way round: the order of bets

| Order | What we build | Why exactly so |
|---|---|---|
| 1 | V1 + signature + evidence | gives price and trust in 10 weeks; without it there is nothing to sell V2 on |
| 2 | V2 (graph, grid, verifier farm) | turns a one-off finding into a subscription; creates the Pareto front |
| 3 | V3 on one class of properties | the only way to get a moat; but it requires money from V2 |
| in parallel | axis D2 → D3 | hybrid runner from day one, otherwise enterprise deals are out of reach |
| option | evidence-plane as a service | insurance against commoditization of agents; costs 0 now if the API is designed up front |

The reverse order (V3 straight away, or "a platform for other people's agents" straight away) is a typical mistake: there is neither trust, nor data, nor money for evidence.

---

## 6. What no variant does

- Does not guarantee the absence of vulnerabilities — and must not phrase the report so that this can be read into it.
- Does not deploy to prod and does not merge PRs.
- Does not test systems the client does not own.
- Does not certify compliance — supplies evidence, not certificates.
- Does not promise "proven constant-time": functional verification does not cover side channels.
- Does not publish a "security score" as the main deliverable.
