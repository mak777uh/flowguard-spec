---
id: E-M10
hypothesis: H-M10
status: planned
base_commit: ""
started: ""
finished: ""
environment: "unset at pre-registration; the corpus generator runs in an environment that has no access to the verifier source"
command: "unset at pre-registration; recorded at run time together with the corpus sha256"
threshold: "Declared before generation: at least 100 mutated bundles across 6 declared defect classes, plus at least 30 valid bundles. Required: detection >= 0.95 on classes D-1a..D-1d combined, detection >= 0.90 on D-2a/D-2b, false-rejection <= 0.05 on the valid set. Any class below its threshold fails the experiment; the miss list is published verbatim."
result: "not run"
verdict: pending
---

# E-M10 — instrument evidence: is the verifier's reject actually a detector?

## Why this card exists

`E-M9` asks whether the verifier rejects six substitutions we thought of. That is a contract, not a measurement.
Five reviewers of round 6 said the same thing in different words: the residual hole is not claim wording, it is
**instrument correctness** — and a corpus of cases chosen by the author cannot measure it.

This card is the Evidence-Based Testing half of the answer: a mutation corpus with declared classes, declared
before any of it is generated, and three numbers per class.

## Pre-registration (before generation)

**Corpus, declared now.**

| class | what is mutated | how it is generated | count |
|---|---|---|---|
| D-1a | code artifact bytes | flip a run of bytes in `objects/<sha256>`, keep the signature | ≥ 20 |
| D-1b | build metadata | change the build digest field, keep everything else | ≥ 20 |
| D-1c | configuration | change one configuration key, keep canonical form valid | ≥ 20 |
| D-1d | identity | swap the signing identity for another trusted one | ≥ 20 |
| D-2a | whole pair | bundle signed for target A, presented with target B | ≥ 10 |
| D-2b | whole pair, consistent numbers | as D-2a, with the manifest internally consistent under A | ≥ 10 |
| V | valid bundles | unmodified, generated independently of the mutation tool | ≥ 30 |

**Generator independence.** The mutation tool is written without reading the verifier source. Its author may read
the bundle format specification and nothing else. This is written down because the alternative — a generator that
knows the verifier — measures the generator's knowledge, not the verifier.

**Thresholds, fixed now.**

- D-1a…D-1d combined: detection **≥ 0.95**
- D-2a, D-2b: detection **≥ 0.90**
- V (valid): false-rejection **≤ 0.05**
- Any class below its threshold fails the experiment.

**What is published regardless of outcome:** the full corpus sha256, the per-class confusion (detected / missed /
false-rejected), and **the verbatim list of missed mutations**. A miss list is the most useful artifact this
repository can produce, because it is the only one that tells a reader where the instrument is blind.

**Why these numbers and not higher.** 1.00 is not a threshold, it is a hope: a corpus that yields 1.00 is either
too easy or too small. 0.95 and 0.90 leave room for the honest possibility that a mutation class is genuinely
undetectable from inside the bundle — and if that happens, the class is moved to `not_claimed`, not deleted.

## Run

Not run. The verifier does not exist yet; this card exists so that the thresholds are not chosen after the result.

## Result

Not run.

## What this card does NOT do

- It does not measure the verifier against real-world attacks, only against mutations we can generate.
- It does not validate the instrument that *produces* bundles (the generator layer), only the one that checks them.
- It does not show the bundle's binding to a running deployment; that is out of scope by ADR-0001.
- It does not make `E-M9` redundant: `E-M9` is the contract the verifier must satisfy first, `E-M10` is the
  measurement of how well it satisfies it.
