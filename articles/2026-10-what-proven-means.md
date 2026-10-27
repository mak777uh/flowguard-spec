# Six Cycles of Adversarial Review Broke Our Security Spec. Three of the Breaks Were Ours to Keep.

*A team of reviewers — four to five per round, none of whom had seen the others' answers — spent six cycles trying to destroy a specification for a verifiable security guarantee. This is what survived, what did not, and the one design rule that came out of it. The whole thing is public, including the parts that make us look bad.*

---

## The word that was doing three jobs at once

Our product makes one claim. Not "this system is secure" — that claim is unfalsifiable and every security vendor who makes it eventually gets a bad week. The claim is narrower:

> For one declared value flow — money, personal data, access to a store — nothing moves past the single control point. The closure is declared, the statement is signed, and a third party can verify it offline without trusting us.

One of the reviewers read the document and pointed out that the word **PROVEN** appeared in three places meaning three different things. In the verdict section it meant "no bypass exists inside the closure". In the findings section it meant "this exploit reproduced" — which is the *opposite*: a reproduced exploit means a vulnerability *exists*. And in the legacy section it meant "our tests passed", which is not proof of anything about a system.

A customer will read one word one way. Footnoting does not fix that. We renamed the second meaning to `CONFIRMED`, kept `PROVEN` for the verdict only, and added an intermediate level, `ENFORCED_TESTED`, for systems where completeness genuinely cannot be proved but a mechanism stands on every declared money path.

That was the first lesson, and it was free: **a claim's wording is part of its correctness, not its marketing.**

## The rule that worked backwards in the most dangerous case

Our integrity rule was clean and, we thought, rigorous:

> An unknown path blocks a strong verdict. If the set of undiscovered paths is non-empty, the answer is `INCONCLUSIVE`, not `PROVEN`.

All five reviewers, independently, said the same thing: this only proves that no unknown path exists **inside the analyzer's model**. A blind spot does not announce itself. The analyzer that fails to see a path returns an empty unknown-set, and the rule then *awards* the strongest verdict precisely where it knows the least.

The fix was not a better analyzer. It was to make the verdict relative and the denominator visible:

```
verdict: ENFORCED_TESTED(R2)
coverage: 11/14 (0.79)   excluded: 3   unknown: 0
detector: slither+cast+manual | recall 0.71 (corpus 20)
```

Three changes in one line. The level carries its detector. The coverage scalar sits in the header, not in an appendix. The recall number is measured on a corpus and published, because a claim of completeness without measured recall is an opinion wearing a lab coat.

## Three mechanisms nobody had written down

The reviews did not only find errors in our reasoning. They found failure modes we had not modelled at all. Each of these is now a first-class entry in the specification.

**T1 — the trusted release contour.** A signature proves the integrity of what was signed. It does not prove the truth of the statement inside, and it does not prove the binding between the bundle, the actual target, and the version that is running. A correctly signed `PROVEN` can attest a target that was swapped. The mitigation is boring and expensive: publish toolchain hashes, run an independent verification replica, and add a substitution test that swaps code, build, configuration and identity while keeping the signatures valid. The verifier must reject all four.

**T2 — policy drift.** We prove that the implementation conforms to policy P. We do not prove that P matches what the business intended. A legal, permitted, and harmful release passes every check we have. Audits go green while the loss happens.

**T3 — the vacuum.** The party paying for the attestation chooses the closure and the policy. They are incentivised to narrow both, and a narrowed closure produces a beautiful verified statement about almost nothing. The market will read the badge, not the excluded-paths list. The countermeasures are structural: a coverage scalar in the header, a ceiling on excluded paths for the strongest level, a mandatory minimum invariant set per asset class, and a published section titled *what this policy does not forbid*.

T3 is the one that keeps me up. It is not a bug in our code; it is our product working exactly as designed, used to manufacture confidence. Every verification product has this hole. Most do not write it down.

## What we deleted, and kept deleted

The most useful artifact in the repository is not the specification. It is [`eliminations.md`](https://github.com/mak777uh/flowguard-spec/blob/main/docs/eliminations.md) — fifteen positions we held and then gave up, each with the exact evidence that killed it and **what would bring it back**.

- "A database trigger is a physical guarantee." It is configuration of the same DBMS. It covered only `UPDATE`; it is bypassed by `INSERT`/`DELETE`, by `DISABLE TRIGGER`, by logical replication, by restore, and by the superuser session. The word "physical" is withdrawn. The guarantee is now conditioned on a declared privilege model with the DBA outside the threat model.
- "Three runs are enough." They are not, for a flaky effect. Five by default, ten when the flake rate is unknown, and a published false-positive ceiling per oracle.
- "Fifteen minutes per review." Consensus across reviewers: thirty-five to forty. Fifteen is a target for a repeat finding of a known class on an already-onboarded target, nothing more.
- "Price per finding." Eliminated on principle — it rewards inflating findings and destroys the trust the product sells.

A registry of eliminated ideas with revival conditions does something a roadmap cannot: it makes a review round cost something. If you re-assert a position we killed, you have to address the evidence that killed it. If you cannot, the round is a repeat, not a review.

## Typed claims, and three reserved words

Every claim in the product now carries an evidence type, and the type fixes the strongest wording permitted:

| Type | Strongest permitted wording |
|---|---|
| `proof` | "proved for the model of version X under assumptions A" |
| `test` | "holds for the declared closure on the test corpus" |
| `statistics` | "observed k of n; does not generalise beyond the corpus" |
| `observation` | "observed once" — may never carry a guarantee word |
| `judgment` | "our position is" — may never appear in an attestation |

Three words — `PROVEN`, `ENFORCED_TESTED`, `guarantee` — are reserved for `proof` and `test`. A linter enforces the schema and that cited artifacts exist. A claim that cites a card which does not exist yet is not an error; it is the to-do list, printed.

This is the same rule we sell: **a statement may never be worded more strongly than its evidence.** Applying it to ourselves is not modesty, it is the only way the rule is credible.

## The loop, and why we needed two brakes

The last thing we built is not a feature. It is a loop. The product is the showcase of the method; the method is the factory for the product. Four edges:

method → product (dictates the artifacts) · product → data (real numbers) · data → method (refines thresholds) · review → everything (attacks claims).

A round counts only if it leaves an artifact — a moved evidence type, a withdrawn claim, a number with a re-run command. Otherwise it is logged as `no-delta` and the cadence slows. Polished prose that changes nothing is the default failure mode of every research programme.

Two brakes, without which the loop is self-hypnosis:

1. **An external node is mandatory.** We cannot validate our method with our own product. Acceptable external nodes: someone who rebuilds the verifier from the documents alone and agrees byte-for-byte; a consumer who changes a decision because the bundle exists; a reviewer who arrives with a measurement. Our own escrow does not count — that is the loop biting its tail.
2. **A stop path reachable from data, not mood.** A reproducible false `PROVEN` stops the guarantee product. Two rounds with no external node stop the guarantee line entirely, downgrading it to instrumentation.

## Why this connects to permanence

Permanent storage and verifiable claims fail in different ways, and you need both.

Arweave-style permanence solves a real problem: a claim that cannot be quietly rewritten. A hash of a document that stays where you put it, forever, checkable in a browser tab — that is a genuine advance, and it is the problem ModelProof was about.

But permanence answers *"has this changed?"* It does not answer *"what does this mean, and who had to act on it?"* A hash of a sentence nobody can interpret is a very durable piece of uselessness. The failure is not cryptographic. It is semantic, and it is structural: without an externally anchored denominator and a consumer who must act, verification is theatre with better math.

Our answer to both questions is uncomfortable and therefore probably right: publish the denominator in the header, publish what the closure excludes, publish the list of things you gave up, and never let three words mean nine things.

## What is actually built

Honestly: no product code yet. A specification, six cycles of adversarial review, a claim registry, an elimination registry, a method, and three instruments that run in CI — a secret scanner over files *and history*, a link checker, and the claim linter. The next deliverable is not a document. It is a three-day experiment that swaps code, build, config and identity while keeping our signatures valid, and reports whether the offline verifier catches all four. If it misses one, a claim moves from `judgment` to `false as stated`, and we publish that.

Everything is in the open, including the pricing doctrine and the margin caps, because a transparency claim that hides the commercially embarrassing parts is just a different kind of marketing. There is exactly one secret in the repository: secrets. A CI guard blocks tokens, keys and local paths in files and across the whole history.

**Repository:** [github.com/mak777uh/flowguard-spec](https://github.com/mak777uh/flowguard-spec)

If you want to attack it, the master document is designed to be pasted into a model whole, and the review protocol is written down. The next round is open, and the useful answer is the one that produces an artifact.

---

*Tags: #AI #Security #OpenSource #Verification #Arweave #DecentralizeAI #SoftwareEngineering*
