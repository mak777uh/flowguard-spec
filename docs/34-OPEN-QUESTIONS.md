# 34 — Open questions: what is actually still open

**Date:** 2026-10-27. **Purpose:** an honest inventory after round 6, so that the next action is chosen and not
drifted into.

The honest headline: **almost nothing that is still open can be closed by another review round.** Five reviewers
said that in round 6 in five different ways. What follows separates the open questions by *what closes them*,
because that is the only distinction that matters for what to do next.

---

## 0. Counters, so nobody argues with prose

| counter | value |
|---|---|
| claims citing an artifact that does not exist | **16** |
| experiment cards registered / run | **2 / 0** |
| ADRs | 1 |
| kit conformance | **6 / 7** (only M7 missing) |
| measurements produced by this repository | **0** |
| lines of product code | **0** |

---

## 1. Closed in round 6 — do not reopen without new evidence

| question | resolution |
|---|---|
| Build order: verifier first or test first? | test first — `ADR-0001` |
| Is one substitution class enough? | no, two — D-1 tampering, D-2 falsely attested pair |
| Is the browser verifier where the value is? | no — value is recomputing the denominator (`X-16`) |
| Does an offline verifier bind a bundle to a running deployment? | no, and that is now `not_claimed` |
| Is `PROVEN` impossible in principle? | no — only for a whole application under our assumptions |
| Are eight claim columns sufficient? | no — instrument correctness is unaddressed (`X-17`) |
| Is there a buyer at recall 0.71? | no named one; nearest analogue is a disclosed-scope report, not a guarantee |
| Do logs count as evidence? | only when replayed and allowed to fail (`X-19`) |

## 2. Open, and closed only by **executable work**

| # | question | closes when | blocked by |
|---|---|---|---|
| W1 | Does the verifier reject the six substitutions? | `E-M9` run recorded | no code yet |
| W2 | What is the verifier's detection rate per defect class? | `E-M10` run recorded | W1 |
| W3 | Can a bundle be rebuilt by someone who never saw the code? | M7 run by a stranger | W1 |
| W4 | Are the ten on-chain attacks actually blocked? | attack harness vs the escrow model | escrow implementation |
| W5 | Does the witness hold under a bypassing writer? | witness harness (12 pd est.) | legacy target |
| W6 | Is a claim impossible to word above its evidence in practice? | one real report produced under the linter | first client artifact |

None of these six is answerable by a model. All six are dateable work, and two of them are already registered as
cards so their thresholds cannot be fitted afterwards.

## 3. Open, and closed only by **a conversation with a person**

| # | question | why review cannot answer it |
|---|---|---|
| P1 | Who acts differently at `coverage: 11/14`, and what does the publisher lose if the bundle is wrong? | all five reviewers converged on it and none could answer it — they are models, not signatories |
| P2 | Would that person accept measured-not-proved, and at what coverage floor? | a procurement decision, not a technical one |
| P3 | What liability surface does the bundle need — who signs, on what authority, for what period | no framework exists; only a counterparty can define it |
| P4 | What does the incumbent procedure cost them, so our price has a denominator | requires their numbers |

Round 6 named these as central. They stay central. **2026-11-10 exists for P1 and P2 specifically.**

## 4. Open, and genuinely closable by a review round — there are four

These are the only ones where a model's answer has non-zero expected information.

| # | question | what makes it reviewable |
|---|---|---|
| R1 | **What fields must a liability surface have** for a third party to accept a bundle as a basis for payment or admission — and what is the minimal set that a small issuer can honestly sign? | analogous instruments exist (audit opinions, attestations, insurance certificates); a model can compare their clause structure |
| R2 | **How should `not_claimed` be made machine-checkable** rather than a template sentence? | five reviewers flagged that it can be filled with boilerplate; this is a design question with a testable answer |
| R3 | **What is the cheapest corpus-provenance scheme** that a reviewer would accept as "declared before generation" — hash, timestamp, third-party witness, or something lighter? | our `E-M10` pre-registration is only as good as its provenance; this is checkable against practice |
| R4 | **What fails when the same model writes the spec and the mutation corpus?** We have barred the generator from reading the verifier source, but nothing prevents corpus and verifier being written by the same model family — is that a real independence failure, and what is the cheapest test for it? | directly targets our stated independence rule; a model can reason about correlated failure |

### Recommendation

**Do not run a round for all four.** Run one round with R1–R4 only, after `E-M9` exists, so that the answers land
on a working artifact instead of a plan. Before that, expected information is low: R1 needs a real counterparty to
validate, and R2–R3 change code that does not exist yet.

If a round is run now anyway, it should be **four questions, one packet, no design questions** — the failure mode
of rounds 1–5 was volume, and volume is what produced 22 documents and zero measurements.

## 5. Open, and unfairly unassigned

| # | question | status |
|---|---|---|
| U1 | Is the agent-development plan (independent tests, read-only `tests/`, diff gates) actually safe? | **untested**; finding F3. The first honest test is the verifier itself |
| U2 | Does T2 (policy drift) have any mechanism at all? | none. Only stated as a risk |
| U3 | Do T3 countermeasures hold — coverage scalar, excluded ceiling, "what this policy does not forbid"? | specified, never measured |
| U4 | Is the pricing doctrine survivable against a real budget? | never tested; P4 needs their numbers |
| U5 | Does the sibling channel keep working without a human relaying it? | notes work; no automatic trigger beyond one daily reminder |

## 6. What is deliberately not open

- No new document about the design.
- No new ports, no new verdict levels, no new claim columns until the eight-column table has one measured row.
- No seventh review round on design.
