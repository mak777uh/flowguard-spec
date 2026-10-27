# Closed loop: the product is the showcase, the approach is the factory

The product does not sit downstream of the method, and the method is not a document written once. They are
two nodes of one loop, and every review round moves an edge of that loop. This file defines the loop, its
two guard conditions, its cadence, and the rule that keeps it from becoming self-referential.

If the loop is not closed with a measurable delta per turn, it degenerates into churn: rounds of prose that
feel productive and change nothing. That failure mode is the default one, not the exceptional one.

---

## 1. The loop

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
        ┌───────────────────────┐                    ┌───────────────────────┐
        │   M — METHOD          │   (1) dictates     │   P — PRODUCT         │
        │   lab loop, typed     │───────────────────▶│   attestation,        │
        │   claims, eliminations│                    │   verifier, stand     │
        │   sensitivity arithmetic                   │   engagements         │
        └───────────────────────┘                    └───────────────────────┘
                    ▲                                          │
                    │                                          │
                    │   (3) amends               (2) produces │
                    │   hypotheses,              measurements,│
                    │   eliminations,            disputes,    │
                    │   thresholds               incidents    │
                    │                                          ▼
        ┌───────────────────────┐                    ┌───────────────────────┐
        │   R — REVIEW          │◀───────────────────│   D — DATA            │
        │   external rounds,    │   (4) attacks      │   E-cards, M-series,  │
        │   models + consumers  │   claims           │   dispute log,        │
        │   + independent impl  │                    │   exclusion ledger    │
        └───────────────────────┘                    └───────────────────────┘
```

Four edges, each carrying **artifacts, not opinions**:

| Edge | What crosses it | Artifact that proves it crossed |
|---|---|---|
| **(1) method → product** | the shape of everything the product emits: verdict ladder, typed claims, preregistered experiments, elimination ledger | a product artifact that did not exist before: `verdict.json` schema, `CLAIMS.md` entry, `E-` card |
| **(2) product → data** | real numbers: minutes per finding, recall, disputes, exclusions per engagement | one `R-XXXX` result with a command that re-shoots it |
| **(3) data → method** | what the numbers refuted: thresholds, K, the death criterion, the review gate | one `ADR-XXXX` that changes a rule, plus one `X-` entry in `eliminations.md` |
| **(4) review → everything** | attacks on claims; independent reimplementation from documents alone | a `CLAIMS.md` diff: evidence type moved, wording downgraded, or a claim withdrawn |

**A round counts only if at least one of the four artifacts exists afterwards.** No artifact — the round is
recorded as `no-delta` in the loop ledger, and the cadence slows down instead of repeating.

---

## 2. The two guard conditions

Without them the loop closes on itself and proves nothing. Both are mandatory.

### Guard A — an external node, not us

Our method validating our product, and our product validating our method, is circular. One node must be
outside the loop. Three acceptable external nodes, in order of strength:

1. **An independent implementation made from the documents alone.** Someone who never read `crates/` or
   `src/` rebuilds the verifier from `fg-bundle/1` and `CLAIMS.md`, and the two agree byte for byte. This is
   the strongest guard. It has a **near**-precedent in this workspace, and the difference matters: in
   [VecDHT](https://github.com/mak777uh/VecDHT) `E-0113` caught seven defects — six in the rule text, one in
   the checking instrument itself — but it was a pre-freeze cross-check, comparing that repository's bytes to
   its own frozen numbers. A cross-check audits the instrument; only a rebuild by someone who never saw the
   code tests the documents. Both repositories have the first kind and neither has the second, which is why
   M7 remains a gap rather than a solved problem.
2. **A consumer who changes a decision** because a bundle exists: an insurer, auditor, bank, counterparty.
   Our own escrow does not count — that is the loop biting its own tail.
3. **An external reviewer with a measurement**, not an opinion: a round that arrives with a number we did not
   have.

If none of the three is present in a round, the round's output is `advisory` and may not change the spec's
claims — only its prose.

### Guard B — a stop path

A loop that can only refine is a runaway. The kill criteria must live **inside** the loop, and they must be
triggerable by data, not by mood:

| Trigger | Where it is written | What it stops |
|---|---|---|
| reproducible false `PROVEN` | `CLAIMS.md` C-01…C-15 | the guarantee product; analysis tool may continue |
| `closure_complete < 50%` on 10 pilots | `eliminations.md` X-04 revival clause | the legacy branch |
| no external node in 2 consecutive rounds | this file, Guard A | the whole guarantee line, downgraded to instrumentation |
| acceptance throughput flat while writing speed triples | `eliminations.md` X-14 | the plan, not the principle |

The stop path is not pessimism. It is what lets the loop run fast: knowing there is a brake, you can press
the accelerator.

---

## 3. The rule that closes the loop at engineering level

> **No feature without a claim. No claim without an experiment card.**

Concretely:

- A pull request that adds capability must add a row to `CLAIMS.md` — with an evidence type and the strongest
  wording that type permits.
- That claim must reference an `E-` card. A claim referencing a card that does not exist fails the linter
  (`lab/check-claims.py`).
- A claim whose evidence type is `observation` may not be referenced in any customer-facing surface.
- Removing a capability does not remove its claim: the claim becomes `withdrawn` with a reason.

This is the same rule the product sells to its customers — a statement may never be worded more strongly
than its evidence — applied to ourselves. That is what "the product is the showcase of the approach" means
literally, not metaphorically.

---

## 4. Cadence

| Turn | Period | What happens | Deliverable |
|---|---|---|---|
| **measure** | weekly, while a pilot runs | `M`-series measurements become `R-` results | one number with a re-shoot command |
| **amend** | per result | a result either supports, refutes, or is `inconclusive`; refuted → `ADR` + elimination | one `ADR`, one `X-` entry |
| **attack** | quarterly | external review round: models, an independent implementation, or a consumer | `CLAIMS.md` diff |
| **audit the method** | yearly | does the method still predict? Compare preregistered thresholds with what actually happened | a `method-audit` note; if predictions were worse than coin-flips, the method is the defect |

The yearly audit is the loop's own falsification test. A method that never fails its own prediction check is
not being used — it is being recited.

---

## 5. Loop ledger

One file, append-only, one row per turn. This is the only place where "we are making progress" can be
checked without reading prose.

| turn | date | edge moved | artifact | delta | external node? |
|---|---|---|---|---|---|
| 001 | 2026-10-27 | (1) method → product | `CLAIMS.md`, `eliminations.md` | 18 claims typed, 15 eliminations | no — `advisory` |
| 002 | — | (4) review → everything | round 3 answers | *pending* | to be declared |

Columns that matter:

- **edge moved** — exactly one of (1)(2)(3)(4); a turn claiming more than one edge is usually moving none.
- **delta** — a number, a moved evidence type, a withdrawn claim. Not a summary.
- **external node** — `no` marks the turn `advisory`: prose may change, claims may not.

Two consecutive `advisory` turns are a signal: the loop has no external input and is talking to itself.

---

## 6. How this changes the review rounds

Each future round must open with a declaration, in three lines:

```
edge:       (2) product → data
artifact:   E-M2 result, 30 findings, p50/p90
external:   independent reviewer measured on our corpus (Guard A, node 3)
```

And close with the `CLAIMS.md` diff. A round that opens without a declaration is not a round; it is a
conversation, and it goes in the ledger as `no-delta`.

This also changes what we ask models. Previous rounds asked "what is weak". The next ones ask:

1. Which edge does this answer move, and what artifact does it produce?
2. What is the external node, and why is it outside the loop?
3. What would make the loop stop — and is that condition measurable this quarter?

---

## 7. Failure modes of the loop itself

| Failure | How it looks | Detection | Countermeasure |
|---|---|---|---|
| **churn** | rounds produce polished prose and no artifact | ledger shows `no-delta` twice | slowdown rule: cadence drops to monthly until an artifact lands |
| **self-reference** | we validate our method with our product | every row has `external: no` | Guard A: block claim changes |
| **ossification** | eliminations only accumulate, never revive | `X-` entries older than a year with no revival attempt | yearly audit must test one revival per year |
| **drift** | spec says one thing, code another | `check-claims.py` sees a claim without a card | the linter, not discipline |
| **scope creep as progress** | edge (1) moves constantly, (2) never | ledger column distribution | require edge (2) at least once per quarter |
| **marketing leak** | a `judgment` claim appears in a deck | grep for reserved words outside `proof`/`test` | reserved-word linter |

---

## 8. The first turn of the loop

To start the loop honestly, one turn must complete all four edges with a real artifact. The cheapest such
turn is already specified:

1. **(1)** The method says: a claim needs an evidence type. → type C-01…C-18 (done).
2. **(2)** Run `E-M9` — the substitution test: swap code/build/config/identity, keep signatures; the offline
   verifier must reject all four. **This is 3 days of work and produces a number.**
3. **(3)** If the verifier accepts even one substitution, C-08 moves from `judgment` to **`false as stated`**,
   an `ADR` changes T1's mitigation, and `eliminations.md` gains an entry.
4. **(4)** Publish the result and hand the documents to someone who never read the code: can they rebuild the
   verifier and agree byte-for-byte?

That is a complete loop in one week, and it produces the only thing that matters at this stage: **the first
measured statement about whether the trust chain actually holds.**
