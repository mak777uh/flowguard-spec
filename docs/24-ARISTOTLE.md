# Harmonic Aristotle — what it changes here, and what it does not

Source: [`harmonic.fun/aristotle`](https://www.harmonic.fun/aristotle/). Read from the product page; no access to
the service was attempted.

## What it is

An AI that **formally verifies code** rather than chat: you point it at a C or Verilog file, describe in plain
English what must always hold (or let it propose properties), and it returns each property as
**proved / refuted / open**, with the assumptions behind every proof and what was not covered. Proofs are
machine-checked, so there is no confidence score to interpret. Runs on-prem or in a private cloud; pay per use.
Two case studies are published (a Verilog block, and C from a fusion-control system re-derived from a paper).

## The three possible uses, ranked by distance from today

### 1. It validates our reporting design, today, for free

Aristotle answers with exactly the shape this repository arrived at independently: a three-valued verdict with
**named assumptions** and an explicit statement of what was not covered. That is our `PROVEN / SCOPED_ASSURANCE /
CONSISTENT_DECLARED` ladder, our `NC-01…NC-11` vocabulary, and our refusal codes. A commercial product aimed at
hardware teams converging on the same shape is evidence that the shape is not a local quirk.

Worth one paragraph in the Part 2 article, and worth nothing in readiness: agreement on presentation is not
agreement on substance.

### 2. It can be an outside prover for a small C reference of our algebra — the one experiment worth setting up

Our verdict arithmetic is roughly a hundred lines: distinct paths, a per-level floor, a coverage ratio, a clamp
to the claimed level, a handful of comparisons. `E-M60` and `E-M62` show this arithmetic is where **all** the
adversarial breaks landed — a floor keyed to the wrong string, a denominator counting labels, `min` where `max`
belonged, `NaN` clearing a comparison.

Plan: write the same arithmetic in C as a **reference model**, state four properties in English —
`verdict ≤ claimed`, `more distinct paths never lowers the level`, `no comparison accepts NaN`,
`a claim below the floor is refused` — and give both to Aristotle. Then compare:

- properties it proves that our Python also satisfies (agreement);
- properties it refutes (a real disagreement to investigate);
- properties left `open` (where the model is too weak to decide, which is information about the model).

This is the cheapest way to get an **independent** check of the arithmetic from a party with no stake in my
reasoning, and it needs no Lean toolchain and no hand-written proofs.

### 3. It could verify the eventual safe core, if that core is C

Our migration story ends at "a formally verified safe core". Aristotle verifies C and Verilog today. If that core
is ever C, this is a candidate tool — but it is a **commercial service with no external audit**, which fails the
same test NVIDIA's no-PR model failed: readable, not dependable as infrastructure. It can be a supplier, not a
foundation.

## What it does not do

- It **does not verify Python**, so it cannot look at `fg_verify.py` itself. Any claim that "Aristotle verified
  the gate" would be false.
- It **does not establish that a property is the right property.** Proved/refuted/open says nothing about whether
  the English sentence captured what matters; that judgement stays with whoever wrote the sentence.
- It **does not touch the ceiling.** Soundness still needs an external anchor over the inventory
  (`ADR-0010`, `NC-01`).

## Next step if accepted

`formal/reference/verify_algebra.c` — the arithmetic as a standalone C file with no I/O, plus
`formal/reference/properties.md` in plain English. Run it through Aristotle once, record the three lists
(proved / refuted / open) in a card, and compare against `lab/e-m60-run.py`. Threshold pre-registered: agreement
is expected; **any refuted property is a defect in the Python or in the C, and both get fixed**; an `open`
property is recorded as "the model does not decide this", never as "proved".
