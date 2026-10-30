# STATUS — generated, not edited

*Produced by `python tools/fg_status.py` at 2026-10-30 05:59 UTC from commit `4579d7f`. Editing this file by
hand is what produced the contradictions a reviewer found (M1 absent and present in one page, 84 links
against 122, three guards against six CI steps). Regenerate it instead; the build fails when it is stale.*

## Where it stands

```
engine (the tool)     100%
product (reliance)    0%
overall               60%
tier                  T2 — usable by an outsider on their own database
next tier             T3 (trustworthy for someone else's decision), blocked by P1, P2
```

The product half is zero because nobody outside has confirmed a finding, rebuilt the bundle as a
third party, or signed an acceptance. That is not modesty, it is the measured state.

## What exists, counted

| artifacts | count |
|---|---|
| metric rows, each with a command | 106 |
| experiment cards | 69 (refutes 8, supports 60) |
| decisions | 17 |
| markdown links checked | 136, broken 0 |

## Method kit

Conformance measured by `lab/check-interop.py`: **7/7**

| item | state | evidence |
|---|---|---|
| M1 experiment cards | present | 68 experiment cards, 0 hypothesis cards, 1 unclassified |
| M2 metrics with commands | present | METRICS.md, 1 command blocks |
| M3 claim registry | present | CLAIMS.md: 18 claims, evidence types used: false as stated, judgment, not established, sta |
| M5 falsifiable status doc | present | STATUS-v0.md |
| M6 guards | present | secrets, links, claims |
| M7 independent-rebuild test | present | E-M39-independent-rebuild.md |

## Readiness checks

| check | what it verifies | earned / weight |
|---|---|---|
| E1 | all guards and negative controls green | 10 / 10 |
| E2 | the verifier executes and refuses | 8 / 8 |
| E3 | acceptance scenarios pass | 12 / 12 |
| E4 | grant enumerator measured on a planted fixture | 8 / 8 |
| E5 | attribution measured, decoy not fooled | 8 / 8 |
| E6 | bundle with Ed25519 verifies under both anchors | 8 / 8 |
| E7 | mutation corpus measured with a declared class set | 6 / 6 |
| P4 | a test corpus written by someone else | 0 / 7 |

## What this page is not

- Not a claim of security. Every verdict carries `NC-01`…`NC-11`; the vocabulary is in
  [NOT-CLAIMED.md](NOT-CLAIMED.md) and the verifier refuses a claim that omits its required codes.
- Not a review. Reviews come from outside: [the exchange protocol](../interop/REVIEW-EXCHANGE.md) and
  [the ledger](../interop/reviews/LEDGER.md).
- Not written by hand. `python tools/fg_status.py --check` fails when this file and the tools disagree.

