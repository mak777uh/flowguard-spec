# STATUS — generated, not edited

*Produced by `python tools/fg_status.py` at 2026-10-28 03:29 UTC from commit `57f475b`. Editing this file by
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
| metric rows, each with a command | 62 |
| experiment cards | 35 (refutes 2, supports 33) |
| decisions | 14 |
| markdown links checked | 117, broken 0 |

## Method kit

Conformance measured by `lab/check-interop.py`: **7/7**

| item | state | evidence |
|---|---|---|
| M1 experiment cards | present | 35 experiment cards, 0 hypothesis cards, 0 unclassified |
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

## Open findings, from the cards

- E: **high** — `check-secrets.sh` scans history for token shapes only, and the local-path rule covers four extensions;
- E: **high** — `lab/check-claims.py` still treats a missing artifact as a warning rather than a failure in CI (the rule
- E: **high** — `STATUS-v0.md` still contradicts itself in several rows (M1 absent vs present; 84 links vs 122; "three
- E: **medium** — four METRICS rows carry digests that match no file in `lab/logs/` (E-M21 and three others). The numbers
- E: **medium** — the same GitLab dump is counted as 1436 and 1102 tables in two logs, and Pagila as 20 and 15; no counting
- E: **medium** — E-M21's 0.4 s has no artifact and the only logged run of the same command says 1.5 s.
- E: **medium** — `fg_readiness.py` prints hard-coded result strings ("E-M11 recall 8/8") whenever a harness exits 0, which
- E: **medium** — The harness named in E-M19's command field does not exist (the card now points at the merge and verify commands instead).
- E: **low** — DOSSIER truncates quoted results mid-word (`result[:300]`).
- E: **low** — four METRICS merge commands omit `--out` and cannot run as written.

## What this page is not

- Not a claim of security. Every verdict carries `NC-01`…`NC-11`; the vocabulary is in
  [NOT-CLAIMED.md](NOT-CLAIMED.md) and the verifier refuses a claim that omits its required codes.
- Not a review. Reviews come from outside: [the exchange protocol](../interop/REVIEW-EXCHANGE.md) and
  [the ledger](../interop/reviews/LEDGER.md).
- Not written by hand. `python tools/fg_status.py --check` fails when this file and the tools disagree.

