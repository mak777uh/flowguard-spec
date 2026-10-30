# LongTails: what a Comparator that audits a budget teaches a verifier of coverage

Source: [`k3nfalt/longtails`](https://github.com/k3nfalt/longtails) (Apache-2.0, created 2026-10-14; Tyurin, Pham,
Khrulkov, Oseledets). Read from the README and the setup/theorem files it names; nothing was built or run here.

## What it does, in one paragraph

A **Setup** is a claim about a problem class, written as a Lean structure with four parts: the types of oracle
queries and replies, `valid` (allowed parameter values), `admissible` (the assumptions), and `successful` (the
accuracy criterion). A result is a theorem `result : Convergence spec budget` where `budget` is an **explicit
function of the parameters** counting oracle calls. An independent **Comparator** then audits the theorem *and the
budget* against the Setup. Their framing of what the Comparator stops:

> Agents searching for a method and its proof cannot pass this check by adding assumptions, skipping oracle calls
> in the count, or leaving gaps in the proof.

That sentence is the whole value, and every clause has an exact analogue in this repository — including two we
currently fail.

## The mapping, clause by clause

| LongTails | FlowGuard | how we stand |
|---|---|---|
| `Setup.valid` — allowed parameter values | the claim schema's `target_lock`, `declared_level` | present |
| `Setup.admissible` — the assumptions the result may rely on | the inventory's `sources`, `completeness_claim`, `independent_of_agent` | **weak**: the claimant declares them, and the gate believes them |
| `Setup.successful` — what counts as solved | the verdict condition (coverage ≥ floor, level ≤ claim) | present |
| `budget` — an **explicit** function of the parameters, counted by the proof | the coverage **denominator**: the set of write paths | **weak**: the denominator comes from the claimant's own inventory |
| **Comparator** — independent audit of theorem and budget | `fg_verify` + `core-rs` + the third-party verifier | partial: three implementations, none of them recomputes the denominator |
| "no extra assumptions" | `evidence_tier`, `independent_of_agent` | **fails**: both are self-declared and only checked for internal consistency |
| "no skipped oracle calls" | a path omitted from `paths[]` | **fails**: omitting a path *raises* coverage, and `NC-01` is the only defence |
| "no gaps in the proof" | a refusal code path never exercised | addressed by `check-refusal-coverage`, weakly (see the audit's M6) |
| novelty reviewed separately, with arXiv links, search date, verdict, confidence | `docs/CLAIMS.md` + prior-art rows in the article | partial: no date-and-confidence column |

## The two things worth taking

### 1. A Setup artifact, so an assumption cannot be smuggled

Their Setup is not documentation; it is the thing the Comparator type-checks the theorem against. Our equivalent
of an "extra assumption" is a claim that states `independent_of_agent: true` and `evidence_tier: 2` and is
believed. The fix has the same shape as theirs:

```json
"setup": {
  "assumptions": ["inventory_independent_of_agent", "evidence_tier_2"],
  "counts_as_write": ["privilege", "function", "trigger_chain", "view_trigger", "caller"],
  "success": "coverage >= floor(level) over distinct path kinds in counts_as_write"
}
```

and a refusal `SETUP_ASSUMPTION_NOT_DECLARED` when the verifier uses an assumption that the setup does not list.
This changes canonical bytes, so it is `Q8` for the owner, not an edit I make quietly.

### 2. Count the budget, do not accept it

Their proof must exhibit a function whose value the Comparator recomputes. Ours accepts the denominator from the
same document it is judging. The version of "Comparator" that would matter here is a second enumerator run by a
party other than the claimant — which is `inventory_attestation`, still reserved, still the same `P1` wall.

**Implemented** (E-M81): g_verify --recount DIR runs the migrations enumerator over the same source and unions what it finds, so an omitted path lowers coverage. It is one-directional by construction, and it covers one enumerator, not a live database. The original idea, for the record: when **two** inventories are supplied (the claim's own and
any other, e.g. from the migrations enumerator), the verifier takes the **larger** denominator and reports the
difference. Undercounting then lowers coverage instead of raising it. That is a change of behaviour, not of format,
so it can be tried behind a flag and measured before it is adopted.

## What LongTails does not tell us

- **Coverage is not a budget.** Their budget counts calls a proof must make; our denominator counts paths a
  database may have. A proof cannot skip a call; a claimant can omit a path — and that asymmetry is the whole
  reason `NC-01` exists and why their guarantee is stronger than ours can be.
- **Their setup is formal, ours is prose plus a schema.** Until `admissible` is a Lean predicate, "the assumption
  was declared" is checked by a string comparison.
- **Novelty.** They separate it honestly: "the novelty is disputed, it is reviewed separately with references".
  Our articles quote a recall figure with no interval — the laboratory audit's R4 — which is the same defect in a
  worse form.

## What I take, and what I record as open

Taken: the vocabulary (`setup`, `admissible`, `successful`, `budget`, `comparator`) and the refusal name
`SETUP_ASSUMPTION_NOT_DECLARED`, both written into `Q8`.

Open, and named as such: recomputing the denominator from a second inventory (flagged experiment); a novelty table
with a date and a confidence column (`docs/CLAIMS.md` has the type, not the date); and the honest statement that
our top verdict rests on an assumption their framework does not need to make.
