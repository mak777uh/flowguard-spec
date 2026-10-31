# The scientific bench: what this repository takes from a research bench, and what it will not

`mak777uh/-` (morphogenesis) is a lab bench before it is a product: every experiment pre-registered with the
criteria committed before the run, sensitivity arithmetic that must show the design *can* produce the difference
before launching, seed anchors that re-run a reference bit-for-bit, an artifact chain from raw run to manuscript
number with `sha256` at every step, and a registry of eliminated hypotheses with what would revive each.

This repository has been doing the same things unevenly: thresholds in cards, two implementations, a ritual, a
refusal vocabulary — but **without the discipline that makes an experiment falsifiable before it is run**. Two of
its own experiments (`E-M73`, `E-M75`) measured a difference their design could not produce, and both were understood
as such only afterwards. That is precisely the failure the sensitivity line exists to refuse.

## What is adopted, in the order it was adopted

| bench mechanism | where it lives here | status |
|---|---|---|
| pre-registration with outcome branches | `lab/card-template.md` + `lab/check-preregistration.py` | **adopted**, applies to cards from 2026-10-31 |
| sensitivity arithmetic before launch (`sensitivity:`) | same template, required field | **adopted** |
| stop rule, including "stop without a result" (`stop_rule:`) | same template, required field | **adopted** |
| analysis plan: which figure from which artifact (`analysis_plan:`) | same template, required field | **adopted** |
| eliminations with revival conditions | `docs/eliminations.md` + `lab/build-eliminations.py` | **adopted** (2026-10-30) |
| retractions published with the same weight as results | `refutes` cards, `docs/eliminations.md` | partial: no single "retractions" page, the registry covers it |
| seed anchors: bit-for-bit re-run of a reference | the sample bundle's address, re-derived in the ritual | partial: re-derived, not compared as a tripwire on every change |
| artifact chain with `sha256` from raw to number | `docs/METRICS.md` log column | **broken**: false for most rows (the laboratory audit's R5), and fixing it is the next priority |
| "skipped is never reported as proven" | `lab/round-check.sh` prints `SKIPPED` for the Rust differential | adopted |
| typed claims with a linter | `docs/CLAIMS.md` + `lab/check-claims.py` (value and ceiling) | adopted |

## The four required fields, and why each of them is not bureaucracy

```yaml
sensitivity:   what difference can this design produce, as a number
branches:      confirm / refute / inconclusive, each as a number
stop_rule:     when to stop early, and when to stop without a result
analysis_plan: which figure comes from which artifact, and by which command
```

- **`sensitivity`** is the one that would have saved two experiments. "Does the artifact improve recall?" cannot be
  answered on a schema whose catalogue already lists every path — the effect size the design could produce was
  zero, and no result from it means anything.
- **`branches`** forces `inconclusive` to exist as an outcome *before* the run. Without it, "we did not reach the
  effect" gets written afterwards as "there is no effect", which is the most common way an experiment lies.
- **`stop_rule`** prevents "run until it passes", which is not a rule but a wish.
- **`analysis_plan`** is what makes a number checkable: it names the command, and the value check in
  `lab/check-claims.py` refuses a number that its own artifacts do not contain.

## The debt this creates, stated rather than hidden

Seventy existing cards predate the rule and are exempt. Rewriting them after the fact would manufacture exactly
the artifact the rule exists to prevent — a pre-registration written with knowledge of the result. The guard
therefore prints the exempt count on every run, so the debt is visible instead of quietly forgotten, and every new
card carries the four fields from now on.

## What this bench does not copy

- **A README ledger generated from a registry.** Our `lab/experiments/INDEX.md` is generated, and that is the same
  mechanism; no second ledger is needed.
- **Lean invariants with Python analogues.** We have two implementations of the same verdict (`E-M66`), which is
  the analogous idea without a proof assistant.
- **The `-` repository's thirty-plus page manuscript.** This repository's equivalent is `docs/` plus the cards; a
  second narrative layer would drift from both.

## The one sentence worth keeping

> A result you can only state after seeing it is a story. Pre-registration is what turns it into evidence.

That sentence is now the first line of `lab/card-template.md`.
