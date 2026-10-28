# What the PutnamBench agent teaches a verifier of documents

Source: [`nearai/putnambench-deepseek`](https://github.com/nearai/putnambench-deepseek) — an agent that solved all
672 PutnamBench problems in Lean 4, reported at roughly $112 total, mean $0.17 per problem. Read from the README;
no part of it was run here.

## The four transferable ideas

### 1. The harness owns the stopping rule, not the model

> "There is no step or token budget, and the harness owns the stopping rule: if the model stops without finishing,
> it is told to continue."

One problem was solved at step 5,105 after **3,423 refused attempts to quit**. That is the single most important
design choice in their report, and it is the defect in mine.

My cross-family attackers are free to answer "NO BREAK FOUND" after twenty minutes, and two of five did exactly
that — `gpt-6-luna` returned nothing at all and I recorded it as "did not find anything", which is
indistinguishable from "did not look". The fix is cheap and mechanical: an attack run does not end until the
agent has executed a stated minimum number of probes **and** pasted their outputs, or the harness keeps asking.
Their number is not mine to copy (thousands of turns is affordable at $0.17/problem), but the principle is.

### 2. The verifier gates the finish, not the reviewer

`completed()` runs the checker; a failure returns the verifier's exact output and the turn continues. My attackers
report findings to me, and I verify afterwards — so a claim that does not reproduce costs a round of my attention
instead of costing the agent another turn.

Transfer: when a cross-family agent claims a break, it should have to run **both cores itself** and paste the two
verdicts. Two of my four agents did that voluntarily; the harness should require it.

### 3. Semantic re-validation, not textual diffing

> "the solved theorem's fully-elaborated type must be character-identical to the pristine statement's, which
> defeats statement-rewriting exploits that textual diffs miss."

This is the exact analogue of the attack I have **not** closed: a claimant can rewrite the *question* rather than
the answer. Concretely, in this repository a claimant chooses `declared_control_point` — and nothing stops them
from declaring a control point that nothing bypasses, or from narrowing the target table until coverage looks
good. The theorem statement is the target; rewriting the target is the exploit.

The Putnam answer is to freeze the statement and compare against it semantically. For us the equivalent is a
**frozen target**: the table plus the control point are what a consumer relies on, so they must be pinned by the
party who relies on them, not by the party who analyses. That is `inventory_attestation` in the schema — reserved,
unused, and now with a concrete reason.

### 4. A defective benchmark is a real finding

Two of the 672 problems had **defective formalisations** — one statement was false (proved `statement → False`
with clean axioms), one pinned the wrong metric. The agent's failure was the benchmark's fault, and they proved
it rather than asserting it.

Our analogue is the honest case: a claim can be *unfalsifiable* rather than false — coverage 0 with no paths, an
exclusion that removes the only money path, a control point nothing can reach. `NC-01`…`NC-11` are the vocabulary
for saying so, but the checker does not test "the claim is vacuous". That is a rule worth adding: a claim whose
covered set is empty must not be able to carry a level, because it is true for a trivial reason.

## What does not transfer

- **Math ≠ systems.** A Lean proof is about a statement; our verdict is about a document describing a database.
  Proving our arithmetic (docs/22) is worth a week; it does not tell anyone whether the inventory is complete.
- **The cost argument is theirs, not ours.** $0.17 per problem is a good number for problems with a machine
  checker. Our attacks have no oracle that says "this one succeeded", which is why the cross-family round is run
  on change rather than continuously.
- **Their stopping rule is only safe with a verifier.** "Never let it quit" works because Lean says pass or fail
  with no judgement. An agent told "never stop until you find a break" will hallucinate one; the harness must keep
  the verifier in the loop, which is exactly idea 2.

## What I will do from this

1. `lab/cross-family-attack.py` — an attack harness with a **minimum probe count and pasted outputs** before a
   "no finding" answer is accepted, so "did not look" stops being recordable as "did not find".
2. Require an attacker that claims a break to run both cores and paste both verdicts.
3. Add the vacuity rule to both cores: a claim whose covered set is empty cannot carry a level.
4. Leave `inventory_attestation` as the reserved answer to target rewriting, and say in the page that a control
   point chosen by the analyst is a statement the analyst can weaken.

Items 1 and 2 are process; 3 is a rule; 4 is the same open question as `ADR-0010` and needs an outside party.
