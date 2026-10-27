# 30. Third round: synthesis of five answers and final artifacts

> Input: five independent answers to `11-ROUND3-QUESTIONS.md`. Unlike the second round, the synthesis here proceeds **by artifact compatibility**, not by votes: two contracts that cannot be implemented together are a signal of a hole in the specification, not a "2 against 3".
> The result below is what can be handed to implementation. Everything that remains a hypothesis is marked.

---

## 1. Classes: 3/2, and what decides is not the vote but the conflict with an invariant

| Class | Votes | Outcome |
|---|---|---|
| SQL injection | **5/5** | **v1** |
| IDOR / BOLA | **5/5** | **v1** |
| path traversal | **3/5** (№2, №3, №5) | **v1** |
| SSRF | 2/5 (№1, №4) | roadmap, first candidate |
| deserialization, XSS, secrets, CVE, TOCTOU, business logic | 0/5 | outside v1 |

Formally, path traversal passes (3/2). But a vote is a weak argument here, so I check it technically: the SSRF oracle requires the application to **itself make an outbound request** to an internal canary-listener. This directly conflicts with C5/C6 (deny-all egress, no live traffic in v1) and means that for SSRF one must either weaken the network policy or stand up a separate route — that is, pay for the class with infrastructure risk rather than for the finding.

**Decision: SQLi + IDOR/BOLA + path traversal.** Not by majority, but because the third class does not break the isolation invariant. SSRF is first in line for expansion once a controlled internal segment exists.

---

## 2. Oracle contract: five versions converged, except on the status vocabulary

The five contracts differed in form but not in semantics. Four of the five are compatible (№1, №3, №5 — almost verbatim; №2 and №4 map onto it). There is one incompatibility — **four different status vocabularies**:

| Source | Statuses |
|---|---|
| №1 | `PROVEN` / `NOT_PROVEN` / `INVALID` |
| №2 | `PASS` / `FAIL` / `INCONCLUSIVE` |
| №3 | `PROVEN` / `REJECTED` / `INCONCLUSIVE` |
| №4 | `PROVEN` / `HYPOTHESIS` / `REJECT` |
| №5 | `PROVEN` / `NOT_PROVEN` / `INDETERMINATE` |

This is not a disagreement but a sign that **two different entities** had been glued together in the specification. I separate them:

- **the oracle verdict** — binary by nature: the predicate holds or it does not, the evidence is sufficient or it is not, the witness is intact or it is corrupted;
- **the candidate status** in the pipeline — `HYPOTHESIS` (not yet run), `IN_REVIEW`, `DISPUTED`, `RETRACTED`.

In №4, `HYPOTHESIS` ended up in the oracle verdict by mistake: it is the state of a candidate before the oracle, not its outcome. The oracle cannot return a "hypothesis" — it either checked or it did not.

### 2.1. The adopted verdict — four values

| Value | What it means | What to do |
|---|---|---|
| `PROVEN` | all predicates hold: `!C ∧ T ∧ !N`, the witness is intact, the fingerprint matched | into findings, into billing, to signing |
| `NOT_PROVEN` | the predicate does not hold, or C/N produced an effect | into Lane A as coverage data, do not bill |
| `INCONCLUSIVE` | evidence is insufficient: the witness is incomplete, the run flaked, the fingerprint did not match | retry within budget; afterwards — into Lane A |
| `INVALID` | the witness is corrupted: the nonce did not match, the signature is wrong, the binding to the run is broken | an incident, not a retry; treat as an attempted deception |

`INVALID` is separate from `INCONCLUSIVE` (this was `INVALID` in №1 versus `INCONCLUSIVE` in №2/№3). They are different phenomena: one is about a lack of data, the other about forgery. №2 correctly noted that `PASS` does not entitle anyone to issue an invoice — that is already a billing step, not an oracle one.

### 2.2. The final contract

```python
ORACLE_CONTRACT = "1.0"

@dataclass(frozen=True)
class OracleInput:
    task_id: str
    oracle_id: str            # "authz.object_id"
    oracle_version: str       # semver, mandatory
    target_fingerprint: str   # sha256(commit + lockfiles + build_args + runtime)
    candidate: Candidate      # trigger + expected_effect + negative_mutations[>=1]
    controls: Controls        # refs to runs C, T, N (not the content!)
    negative_scope: list[str] # what is deliberately not covered

@dataclass(frozen=True)
class Witness:
    witness_id: str
    nonce: str                # verifier-owned, single-use
    observations: list[Observation]  # tap / db_digest / identity / fs_overlay
    merkle_root: str
    signer_id: str            # key outside the agent's VM
    signature: str

@dataclass(frozen=True)
class Verdict:
    status: Literal["PROVEN", "NOT_PROVEN", "INCONCLUSIVE", "INVALID"]
    reason_code: str
    c: bool; t: bool; n: bool
    evidence_digest: str
    oracle_digest: str        # hash of the oracle code + dependencies
    input_digest: str
    negative_scope: list[str]
    expires_at: str           # metadata, NOT part of the hash
    signature: str

def evaluate_oracle(inp: OracleInput, w: Witness) -> Verdict: ...

# signed_hash = sha256(JCS({
#   contract_version, oracle_id, oracle_version, oracle_digest,
#   target_fingerprint, candidate_hash, controls_hash,
#   witness.merkle_root, status, c, t, n, negative_scope
# }))
```

**Rules (all five agreed, apart from the form of notation):**

1. `PROVEN` only when `!c ∧ t ∧ !n` **and** an intact witness (`nonce` matched, the signature is valid, binding to the current run).
2. The oracle executes **outside the agent's VM**; the signing key is not available to the agent.
3. The agent supplies only the candidate and references to the runs. **It does not supply assertions about the effect** — otherwise the oracle would be checking a story, not a fact.
4. Canonicalization — **RFC 8785 (JCS)**; hash — **SHA-256**; signature — **Ed25519**.
5. **Timestamps are not part of the signed hash** (otherwise non-reproducibility). `expires_at` lives alongside, signed separately.
6. Versions are immutable: a change in predicate semantics → MAJOR, and all previously issued verdicts are re-checked. A change to witness fields → MINOR. Cosmetics → PATCH.
7. The same input yields a **byte-for-byte** identical verdict. 20 repeated runs — identical.

The cost of building this contract into the implementation: 1–2 days (test vectors + schema). This is the cheapest part of the whole project.

---

## 3. Oracle library: the cost converged at 4–8 days

| | №1 | №2 | №3 | №4 | №5 | Outcome |
|---|---|---|---|---|---|---|
| Days per oracle | 8 | 2–5 | 3 | 4 | 8 | **plan 4, worst 8** |
| Payback | ~6 findings | — | — | ~10 findings | 20–40 findings | **not counted in findings** |

The spread in payback (6 / 10 / 20–40) is not a disagreement but a consequence of everyone computing it through an unknown quantity (the cost of manual review). №3 is the only one who noticed this and proposed the correct metric: **total time saved relative to the manual process**, not the number of findings.

**Adopted:** a library of three oracles = **12–24 engineering days** (3 × 4–8). This is a P0 investment, and a cheap one: two to three weeks of a single engineer.

### 3.1. Mutation set: 5 mandatory + 2 additional

Intersection of the five sets (№1 — 7, №2 — 5+additional, №3 — 7, №4 — 7, №5 — 6):

**Mandatory (named by ≥3):**
1. **Trigger removal** — the input is replaced with a safe one, the effect must disappear.
2. **Effect removal** — the trigger is present, the effect is suppressed → `NOT_PROVEN`.
3. **Semantic mutation** — the input is changed so that the vulnerable condition is broken → `NOT_PROVEN`.
4. **Witness substitution** — data from a different run/repository, the signature not recomputed → `INVALID`.
5. **Nonce replay** — an old witness in a new check → `INVALID`.

**Additional:** substitution of `oracle_version`/`oracle_digest`, fingerprint drift (a different version of a dependency), subject/object substitution for BOLA, a flaky effect (two runs give different C/T/N).

**Criterion for accepting an oracle into the library** (the strictest of the five, №1, in numerical form):
- **0** false `PROVEN`;
- **≥90%** true `PROVEN` on a corpus of ≥20 vulnerable + ≥20 fixed cases;
- **≥95%** of mutants killed;
- **20 of 20** repeated runs give an identical verdict.

CI runs the set on every `oracle_version` bump, and a merge is blocked on any discrepancy.

---

## 4. Witness plane: 12 days, three channels

Five tables, intersection:

| Channel | Votes | Cost | Outcome |
|---|---|---|---|
| network tap outside the VM | 5/5 | 2–5 d | **mandatory** |
| DB digest / WAL outside the VM | 5/5 | 2–7 d | **mandatory** |
| independent principal identity (IdP-stub outside the VM) | 3/5 | 2–3 d | **mandatory** |
| filesystem overlay-diff | 2/5 | 1–4 d | backlog (not needed for BOLA) |
| process graph / syscall | 2/5 | 2–3 d | backlog |
| verifier-owned nonce sink | 2/5 | 1 d | part of the verifier |

**Total 9–16 days, plan 12.** All five gave a spread but converge on the order: 9 (№5), 12 (№1), 8–14 (№3), 16 (№4). The estimates cannot be added up (№2 and №3 noted this) — the channels share infrastructure.

**Why identity and not overlay-diff:** the class is BOLA. The effect here is "A read object B", and that is a statement about **ownership**, not about files. Without an independent identity channel one cannot prove that the request came from A specifically and that the object belonged to B specifically. Overlay-diff proves access to a file — that is for a different class.

### 4.1. Acceptance test for the witness plane: two tests, not one

№2 caught something important: **a nonce catches replay but does not prove observer independence.** So there are two tests.

**Test A — witness integrity (nonce/replay).**
- *Given:* the agent controls the VM but not the signing keys or the witness log; the nonce lives in the witness plane.
- *When:* the agent presents an old witness with a new nonce, substitutes the object, writes the nonce into its own log.
- *Then:* the verifier returns `INVALID` and records a `reason_code`.
- *Failure:* any forged/replayed/foreign witness received `PROVEN`.

**Test B — observer independence.**
- *Given:* the agent has full root rights inside the VM.
- *When:* the agent attempts to change the configuration of the witness plane, substitute its binary, disable a channel.
- *Then:* the channel lives on the host/outside the VM network, the change is recorded as an incident, and the run is marked `INVALID`.
- *Failure:* the agent can disable or alter the witness and still obtain `PROVEN`.

Separately, a residual boundary is recorded (№3): **the witness does not protect if the testbed itself or the identity system is compromised.** This goes into the negative scope.

---

## 5. Review card: 7 elements + signature

Intersection of the five sets:

| # | Element | Votes | What it catches |
|---|---|---|---|
| 1 | fingerprint + `oracle_id`/`version` | 5/5 | carrying evidence over to a different version |
| 2 | C/T/N: results and hashes of the runs | 5/5 | absence of causality |
| 3 | witness: channels, nonce, hashes | 5/5 | forgery of an observation |
| 4 | negative scope | 5/5 | overclaim |
| 5 | replay kit + a single command | 5/5 | unverifiability |
| 6 | the proposed R0/R1 + re-test result | 3/5 | a fix that does not exist |
| 7 | the claim + access model/preconditions | 3/5 | a signature on the wrong claim |

**The eighth block is not content but signing metadata:** the assessor's name and qualifications, a conflict-of-interest check, the verdict's validity period, the path for contesting it. Added on №4's initiative — the only one who thought about **who** signed and what to do when the client disagrees.

### 5.1. What does not go on the card (3/5 against the rest)

**Must not be compressed** (intersection): **negative controls C/N** · **provenance of the witness** · **negative scope**. Three different classes of error; they cannot be merged into a single "score".

**Does not go on the card** (a unique and correct point from №1): **the agent's reasoning**. A persuasive narrative biases the assessor — a plausible false finding will slip through. The card contains evidence, not a story. This is a UI design rule, not a wish.

Also from №1: **a list of other findings and hypotheses** does not go on the card — otherwise what gets signed is not what was reviewed.

### 5.2. 15 minutes is a product goal, not a fact

№2 and №3 independently noted: 15 minutes is a target requirement and must be verified by a series of blind assessments. **Accepted as a hypothesis with a verification date**, not as a constant in the plan. If it is in fact 35 minutes, the economics of mode A fall apart (see §7), and that changes the product, not just the UI.

---

## 6. TAM: the numbers did not converge, so we take the minimum

| Segment | №1 | №3 | №4 | №5 | Median | **Plan** |
|---|---|---|---|---|---|---|
| open-source | 25% | 40% | 30% | 55% | 35% | **25%** |
| product 50–500 people | 15% | 25% | 45% | 35% | 30% | **15%** |
| enterprise legacy | 3% | 10% | 15% | 12% | 11% | **3%** |

№2 gave no number at all and proposed an experiment — methodologically correct.

The spread of 3–15% for enterprise and 25–55% for OSS means that nobody has the data. **Rule for numbers without a basis: take the minimum**, because erring downward is cheaper (we did not build something unnecessary). Plan: **25 / 15 / 3 %.

**What this means commercially.** At 4 findings and a price of $7.5–12k, the effective TAM compresses by ~6 times. This is not a detail: if the share passing the filter is 15%, then €3M/year in revenue requires ~6 times more engagements than the nominal TAM suggested. This is verified by a preflight audit on samples of 50 repositories — 3–5 days of work, and that is cheaper than any error in pricing.

---

## 7. The 30-day test: the plans do not add up to their own estimates

This is the main finding of the synthesis, and it has to be accepted before implementation, not after.

| | Oracles | Witness | Verifier | Total before runs start | Fits in 30 days? |
|---|---|---|---|---|---|
| №1 | 3×8 = 24 | 12 | 3 | **39** | no |
| №2 | 3×(2–5) = 6–15 | 10–22 | 2–4 | **18–41** (11 allotted in the plan) | no |
| №3 | 3×3 = 9 | 8–14 | — | **17–23** (7 in the plan) | no |
| №4 | — | 16 | — | not broken down | — |
| №5 | 3×8 = 24 | 9 | — | **33** (in 30 days including runs) | no |

**Five out of five do not add up.** Three answers directly contradict themselves: the plan allots fewer days to the build than their own estimates.

So it is one of two things: either the 30-day test does not include the witness and checks only "whether the oracles work" (that is, **skips the main risk** — the impossibility of forgery), or the deadline is not 30 days.

### 7.1. The adopted two-phase scheme

**Phase 1 (30 days) — one class, end to end, with proof of independence.**

| Days | What | Resource |
|---|---|---|
| 1–5 | corpus: **12 repositories** (6 with confirmed vulnerabilities + 6 control), fixing the commit and ground truth | 3 person-days |
| 6–13 | **one** IDOR/BOLA oracle + verifier process | 8 person-days |
| 14–25 | witness plane: tap + DB digest + identity | 12 person-days |
| 26–28 | blind runs + both acceptance tests (A and B) | 2 person-days |
| 29–30 | independent re-check of every `PROVEN`, publication | 2 person-days |

Total **27 person-days**; it fits.

**Phase 1 thresholds:**
- median `PROVEN` per repository **≥2**;
- `repro rate` **≥90%**;
- **0 false `PROVEN`** on the control repositories (any one — immediate failure);
- both witness plane tests passed;
- `HYPOTHESIS/PROVEN ≤ 10`.

**Phase 2 (weeks 5–10) — three classes, finding density.**
We catch up the SQLi and path traversal oracles (8–16 days), then a corpus of 20 repositories and a threshold of **median ≥4 `PROVEN`**.

**Why this way:** phase 1 tests the hypothesis "is it possible at all to produce unforgeable evidence" — that is, the main risk. Phase 2 tests the hypothesis "are there enough findings for the economics" — the second risk. They cannot be mixed into one 30-day sprint: a failure on finding density says nothing about trustworthiness, while a failure on trustworthiness makes any density result meaningless.

---

## 8. The "do not build" condition: 5/5 provided one, and they agree

| | Formulation |
|---|---|
| №1 | median `<1 PROVEN` after manual review on 10+ validatable repos |
| №2 | no class yields reproducible `PROVEN` with an independent witness within budget |
| №3 | `PROVEN` is achieved only by manual intervention or by weakening the criteria |
| №4 | median `<1` with `repro <80%` on 10 repos |
| №5 | median `<2` with working oracles and witness on 20 repos |

**Consolidated condition (adopted):**

> If, on a corpus of repositories that passed the validatability contract, with a **working** witness plane and passed acceptance tests, the median of confirmed `PROVEN` is **less than 2**, then the product as claimed is not built.

№3's qualifications are accepted separately and matter more than the number: if the threshold is reached only through manual intervention in every result or through weakening the proof criteria, **the hypothesis of an automatable product is not confirmed regardless of the median**.

---

## 9. What remains not fully settled

| # | What | Why | How to close |
|---|---|---|---|
| 1 | The share passing the validatability contract (25/15/3) | nobody has the data | preflight audit on samples of 50 repos, 3–5 days |
| 2 | The real duration of a review (15 min?) | a goal only, not a measurement | a series of blind assessments on 30 findings |
| 3 | Payback of the human-sealed oracle | depends on the unknown cost of review | after item 2 |
| 4 | Whether overlay-diff/process graph is needed | not needed for BOLA, probably needed for other classes | in phase 2, when path traversal is added |

---

## 10. Summary: what can be handed to implementation

| Artifact | Status | Readiness |
|---|---|---|
| Oracle contract + 4-value verdict | **ready** | paste into code, 1–2 days for the schema and test vectors |
| Three classes: SQLi, IDOR/BOLA, path traversal | **fixed** | with the rationale for declining SSRF |
| Mutation set (5 + 4) and the acceptance criterion | **ready** | into CI |
| Witness set: tap + DB digest + identity, 12 days | **ready** | into implementation |
| Two witness plane acceptance tests | **ready** | into CI |
| Review card: 7 elements + signature block | **ready** | into the UI spec |
| Repository validatability contract | **ready** | publish as input requirements |
| Positive coverage attestation | **ready** | into the report template |
| Two-phase experiment with thresholds | **ready** | launch it |
| TAM 25/15/3 | **hypothesis** | preflight audit |
| 15 minutes per review | **hypothesis** | blind assessments |

**The next step is not a question but code:** phase 1, days 1–5, a corpus of 12 repositories with ground truth fixed. Everything else is already specified to the point that development can begin without going back to the models.

---

# 11. The sixth answer: confirmed six decisions and broke one deadline

## 11.1. What was confirmed (6/6)

| Decision | Votes after №6 |
|---|---|
| SQLi + IDOR/BOLA + path traversal | **4/6** (SSRF 2/6) — the choice is stable |
| Mutation set C/N/witness/fingerprint | 6/6, identical in composition |
| Card: fingerprint → C/T/N → witness → replay → fix → negative scope | 6/6 |
| Median ≥4 `PROVEN` as the phase 2 threshold | 5/6 |
| Any false `PROVEN` on a clean control = failure | 6/6 |
| TAM: 25% OSS, 15% mid-market | **matched the planning floor** |
| The "do not build" condition | 6/6; the adopted `<2` is stricter than the proposed `<1` — we keep `<2` |
| Witness: tap + DB digest + identity | 6/6 in composition |

## 11.2. One substantive strengthening: the oracle does not issue the final verdict

№6 proposed the status **`PROVEN_CANDIDATE`** instead of `PROVEN`: the oracle confirms the candidate, and the final verdict is issued by a separate deterministic aggregator that combines C/T/N. This is better than the adopted contract for one reason: **the oracle ceases to be a composite judge**.

In our version the oracle received the C/T/N triple and returned `Verdict{c,t,n}` — that is, it decided the composition itself. In №6's version the agent submits **three separate claims**, one per control, and each is judged in isolation; the composition is assembled by an aggregator that executes and interprets nothing, and only applies `!C ∧ T ∧ !N`.

Why this matters: if the oracle judges the triple as a whole, the agent can pick C and N such that the composition "comes together" with a wrong T. Three isolated judgments + a dumb aggregator remove that gap. **Adopted as a refinement of the contract** that does not break compatibility:

```
agent → 3 claims (one per C, T, N) → 3 isolated verdicts → aggregator → PROVEN
```

`PROVEN_CANDIDATE` = the oracle's verdict on a single control; `PROVEN` = the aggregator's result. This adds one more barrier between the agent and the signature — that is, it strengthens I1.

## 11.3. What broke: the cost of the witness

| Source | Three channels | Comment |
|---|---|---|
| №5 | 9 days | tap 3 + DB 2 + overlay 1 + proc 2 + nonce 1 |
| №1 | 12 days | tap 4 + DB 5 + identity 3 |
| №3 | 8–14 days | tap 2–4 + identity 2–3 + DB 2–4 + run log 2–3 |
| №4 | 16 days | tap 5 + DB 7 + overlay 4 |
| **№6** | **30 days** | **tap 10 + DB 12 + identity 8** (plus build 4, nonce 5) |

A spread of 9–30 days for **the same three channels**. And here the rule opposite to the TAM rule applies:

> **For TAM we take the minimum** (erring downward is cheaper — we will not build something unnecessary). **For cost we take the maximum** (erring downward is more expensive — we will miss the deadline).

Planning value for the witness: **16–30 days, plan 20**. №6's figure is backed by a per-channel breakdown (10 / 12 / 8), and it is the only answer where it is visible what a day is made of — the others gave a total without supporting detail.

**Consequence: phase 1 no longer fits in 30 days.**

```
before: 5 (corpus) + 8 (oracle) + 12 (witness) + 4 (runs) + 2 (re-check) = 31 days
after:  5 (corpus) + 8 (oracle) + 20 (witness) + 4 (runs) + 2 (re-check) = 39 days
       + verifier process and aggregator (3–4 days)                                 = 42–43 days
```

**The decision is to move the deadline, not the test.** Thirty days was an arbitrary number chosen for discipline. The arithmetic gives **6 weeks**. Cutting the witness for the sake of a handsome deadline is not allowed: without the DB digest one cannot prove the ownership of object B, that is, the BOLA class itself is lost and the test starts checking the wrong thing. The honest answer: phase 1 is **45 days**, and that is recorded in the plan as a decision, not as a slip.

## 11.4. What did not change

- Three classes, the card, the mutants, the thresholds, the TAM floor, the kill condition — unchanged.
- The contract in §2 remains in force and is supplemented by the aggregator from §11.2.
- Phase 2 (three classes, median ≥4) is unaffected: its timeline was computed without the witness (it is already built in phase 1).
