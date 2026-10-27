# Verifiable AI Needs More Than a Hash: Every Claim Needs a Type

*I am an independent researcher. I check claims against primary sources — a transaction hash, deployed bytecode, a pinned commit — and publish what the check found, including "not confirmed". This is the record of the check I ran on my own specification, and the three places where it failed.*

---

## The hash proves the file, not the sentence

Last week I published [ModelProof](https://hackernoon.com/tagged/decentralize-ai), a way to store an AI model so that anyone can verify it in a browser tab: bit-exact bytes, permanently stored on Arweave, hash checked by the reader. The model cannot be quietly swapped. That part works.

Then a harder question arrived. The hash proves the file did not change. It says nothing about the claim attached to the file. "Trained on this data." "Evaluated on that benchmark." "Cannot be modified." "Safe to run." A permanent hash will faithfully preserve any of those sentences, forever, whether or not any of them is true.

This is the same class of problem the Arweave ecosystem already solved for bytes and has not solved for meaning. Permanent storage gives you [content-addressed immutability](https://arweave.org); it does not give you a semantic contract. And in security, semantics is where the money is.

So I did the thing I do: I wrote a specification for a product that makes one narrow, verifiable claim — not "this system is secure", which is unfalsifiable, but *"inside a declared boundary, no value moves past the single control point"* — and then I paid reviewers to destroy it. Six cycles, four to five independent reviews per cycle, none of them seeing the others' answers.

They destroyed a lot. Below is what broke, what I deleted permanently, and the one rule I now consider non-negotiable for anything that calls itself verifiable.

## Three things that broke, all of them mine

**First: the word "proven" was doing three jobs at once.** In one section it meant "no bypass exists inside the boundary". In another it meant "this exploit reproduced" — which is the *opposite*, since a reproduced exploit means a vulnerability **exists**. In a third it meant "our tests passed", which proves nothing about a system. A reader will pick one meaning. A footnote cannot fix that; only a rename can.

**Second, and worse: my rule worked backwards in the most dangerous case.** I had written an integrity rule I was proud of:

> An unknown path blocks a strong verdict. If the set of undiscovered paths is non-empty, the answer is inconclusive, not proven.

All five reviewers in that cycle, independently, said the same thing: this only proves no unknown path exists *inside the analyzer's model*. A blind spot does not announce itself. The analyzer that fails to see a path returns an empty unknown-set — and the rule then *awards* the strongest verdict exactly where it knows the least. This is the same failure Adrian Colyer and others have documented for static analysis for a decade: [the tool reports what it can see, and silence is read as absence](https://blog.acolyer.org).

**Third: I called a database trigger a "physical guarantee".** It is configuration of the same DBMS. It covered only `UPDATE`; it is bypassed by `INSERT`, by `DISABLE TRIGGER`, by logical replication, by a restore, and by the superuser session. Four of five reviewers flagged it. The word is withdrawn.

## Three failure mechanisms nobody had modelled

The reviews did not just find errors in my reasoning. They found failure modes I had not written down at all.

**The trusted release contour.** A signature proves the integrity of what was signed. It does not prove the statement inside is true, and it does not prove the binding between the bundle, the real target, and the version actually running. [SLSA provenance](https://slsa.dev) exists precisely because artifact identity and build identity are separate problems, and [Sigstore's Rekor](https://www.sigstore.dev) exists because a signature without a transparency log can be shown to one person and denied to another. A correctly signed "proven" can attest a target that was swapped five minutes ago.

**Policy drift.** You prove the implementation conforms to policy P. You do not prove that P matches what the business intended. A legal, permitted, harmful release passes every check you have, and the audit goes green while the loss happens. Formal verification has always had this boundary: the [reference monitor](https://csrc.nist.gov/glossary/term/reference_monitor) formulation of Anderson (1972) gives you complete mediation, tamper-proofness and verifiability — about the mechanism, never about the intent behind it.

**The vacuum.** The party paying for the attestation chooses the boundary and the policy, and is incentivised to narrow both. A narrowed boundary produces a beautiful verified statement about almost nothing. The market will read the badge, not the exclusions list.

That third one is not a bug in code. It is the product working exactly as designed, used to manufacture confidence. Every verification product has this hole. Most do not write it down.

## The fix: put the denominator in the header

The repair was not a better analyzer. It was making the verdict **relative** and its denominator **visible**, in the first line a human reads:

```
verdict: ENFORCED_TESTED(R2)
coverage: 11/14 (0.79)   excluded: 3   unknown: 0
detector: slither+cast+manual | recall 0.71 (corpus 20)
```

Three things moved into the header at once. The verdict now carries its detector. The coverage scalar is not in an appendix. The recall is a measured number on a declared corpus. The same discipline the [DARPA AI Cyber Challenge](https://www.darpa.mil/news/2025/aixcc-results) forced on every competing cyber reasoning system — 54 million lines analysed, 18 real vulnerabilities patched at a reported average of 45 minutes and roughly $152 per task — applies here in the opposite direction: a system that reports what it found must also report what it could not see.

Then I added a rule that applies to every claim in the project, including this article's:

| Evidence type | Strongest wording permitted |
|---|---|
| `proof` | "proved for the model of version X under assumptions A" |
| `test` | "holds for the declared boundary on the test corpus" |
| `statistics` | "observed k of n; does not generalise beyond the corpus" |
| `observation` | "observed once" — may never carry a guarantee word |
| `judgment` | "my position is" — may never appear in an attestation |

Three words — *proven*, *tested*, *guarantee* — are reserved for the first two rows. A linter enforces it, and it does not care how senior the author is.

The distinction between proved and measured is not pedantry. [seL4](https://sel4.systems) is the benchmark here: a microkernel with machine-checked functional correctness, integrity and confidentiality proofs — and even that result is a statement about a model, extracted from code by tools whose own correctness is an assumption. When [Verus, Kani, Creusot and their peers](https://rustfoundation.org/media/how-the-rust-standard-library-verification-contest-scaled-past-manual-proof-engineering) are applied to the Rust standard library, the honest reporting separates what was proved, what was bounded, and what was skipped. A vendor that does not make that separation is not doing verification; it is doing typography.

## The most useful file is the list of what I gave up

I keep a document of eliminated positions. Fifteen of them now, each with the evidence that killed it and **what would revive it**.

- "Three runs are enough" — no, for a flaky effect. Five by default, ten when the flake rate is unknown.
- "Fifteen minutes per review" — consensus across reviewers: thirty-five to forty. Fifteen is a target for a repeat finding on an already-onboarded target, nothing more.
- "Price per finding" — eliminated on principle: it rewards inflating findings and destroys the trust the product sells.
- "A formal proof covers model-to-code correspondence" — marked `false as stated` in my own registry. The proof is about the model; the correspondence is an assumption.

A registry of eliminated ideas does something a roadmap cannot: it makes a review round cost something. Re-assert a killed position and you must address the evidence that killed it, or your round is a repeat, not a review.

## Why this is infrastructure, not a blog post about a startup

The decentralized AI stack solves permanence and compute. [Arweave](https://arweave.org) gives you a record that cannot be quietly rewritten; [Nosana](https://nosana.com) gives you GPUs without a waitlist. Both are necessary. Neither gives you **semantics**: what a claim about a model is allowed to say, given the evidence behind it.

That gap is the actual bottleneck for verifiable AI systems. A permanent model card whose claims are untyped is a durable piece of ambiguity. Store the weights, store the hash, and store a claim registry that says, for each sentence, what kind of evidence backs it and what wording that evidence permits — and you have something a third party can act on years later, without trusting the author.

This is also where the current wave of AI-assisted security work is thinnest. The tooling improved dramatically: [OpenAI's Aardvark](https://openai.com/index/introducing-aardvark), Google's Big Sleep and CodeMender, and the open-source cyber reasoning systems released after AIxCC all find real defects at a speed that did not exist three years ago. What did not improve at the same rate is the **claim layer**: what a finding is allowed to be called, and who is accountable when the label is wrong. A faster finder with an untyped label is a faster source of unfalsifiable statements.

## What you can check right now

I am not going to end with a roadmap. Here is the verifiable evidence:

- **The repository, open:** [github.com/mak777uh/flowguard-spec](https://github.com/mak777uh/flowguard-spec) — the specification, six review cycles, the claim registry, the eliminations registry, and the development method.
- **Three instruments that run in CI on every push:** a secret scanner over files *and the whole commit history*, a link checker, and the claim linter that rejects a claim worded more strongly than its evidence. Green here: [workflow runs](https://github.com/mak777uh/flowguard-spec/actions).
- **The false claims, stated as false:** the registry contains a claim marked `false as stated` (that a formal proof covers model-to-code correspondence) and one marked `withdrawn` (the "physical guarantee"). I left them in, with reasons.
- **The elimination with the reasoning:** [docs/eliminations.md](https://github.com/mak777uh/flowguard-spec/blob/main/docs/eliminations.md) — what would revive each killed position.

What does **not** exist yet: product code. I could dress this up as a demo and it would be a mockup. The next deliverable is a three-day experiment that swaps code, build, configuration and identity while keeping valid signatures, and reports whether an offline verifier catches all four substitutions. If it misses one, a claim in the registry moves from `judgment` to `false as stated`, and I publish that.

Everything is in the open, including the pricing doctrine and the margin caps — a transparency claim that hides the commercially embarrassing parts is just a different kind of marketing. The only secret in the repository is secrets, and a CI guard enforces it across the entire history.

If you want to break the spec, the master document is written to be pasted into a model whole, and the review protocol is documented. The useful answer is the one that leaves an artifact behind.

---

*Tags: #decentralize-ai-hackathon #ai #verification #security #open-source #arweave #decentralized-ai #software-engineering*
