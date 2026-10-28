# READINESS — what works, who can use it, and when to show it to someone

Every number here is produced by `python tools/fg_readiness.py`, which scores a fixed checklist from artifacts in
this repository. It cannot be argued upward: a check either finds its evidence or scores zero.

```
python tools/fg_readiness.py           # table, tier, percentages
python tools/fg_readiness.py --json    # machine-readable
```

## The tiers

| tier | name | requires | means |
|---|---|---|---|
| **T0** | nothing runs | — | documents only |
| **T1** | works for its author | E1, E2, E6 | the tools run on the author's machine |
| **T2** | reproducible by an outsider on a database they already run | T1 + E3, E4, E5, E7 | **no outsider has done it.** The seven engine checks pass on the author's machine against a PostgreSQL the author runs; there is no install step and no third-party transcript |
| **T3** | trustworthy for someone else's decision | T2 + P1, P2 | an independent party rebuilt the artifact and a consumer said what changes |
| **T4** | a guarantee someone may rely on | T3 + P3, P4 | risk acceptance is signed and the corpus comes from another author |

## The checks and their weights

| id | group | wt | criterion | evidence the tool looks for |
|---|---|---|---|---|
| E1 | engine | 10 | all guards and negative controls green | four guard commands exit 0 |
| E2 | engine | 8 | the verifier executes and refuses | `fg_verify` returns a verdict on a probe |
| E3 | engine | 12 | acceptance scenarios pass | `lab/e-m12-run.py` exits 0 (25 scenarios) |
| E4 | engine | 8 | grant enumerator measured on a planted fixture | `lab/e-m11-run.py` exits 0 |
| E5 | engine | 8 | attribution measured, decoy not fooled | `lab/e-m13-run.py` exits 0 |
| E6 | engine | 8 | bundle with Ed25519 verifies under both anchors | sample bundle returns `SIGNED_AND_CONSISTENT` |
| E7 | engine | 6 | mutation corpus measured | `lab/e-m10-run.py` exits 0 |
| P1 | product | 15 | a **third party, not an AI agent**, rebuilt a bundle | `rebuild_result: agreed|differed by a third party / human / organisation` in an experiment card |
| P2 | product | 10 | a named consumer documented the decision | `docs/M8-CONSUMER.md` exists |
| P3 | product | 8 | risk acceptance signed | a `risk_acceptance` signature role in a bundle |
| P4 | product | 7 | corpus from another author | `external_corpus:` marker in a card |

Engine = 60 points, product = 40. The split is deliberate: a working engine with no consumer is a tool, not a
product, and the number should say so.

## What can be applied **today** (tier T2)

These are usable by someone who has a Postgres database and reads the README. Each entry states what it does and
what it does not do — copy the second half when you talk about it.

**1. Find the ways to write a table that bypass a declared control point.**
`enumerators/grants-pg` lists direct privileges, writer functions, disabled triggers, view triggers and trigger
chains. Measured: 8 of 8 planted bypasses on the fixture, row precision 11 of 12.
*Does not do:* application-level checks, writes from other services, dynamic SQL with a runtime table name.

**2. Attribute a write path to the control point it passes through.**
`enumerators/pgcalls` builds a PL/pgSQL call graph, follows it up to depth 8, and marks the paths that reach the
declared control point. Measured: 2 of 2 legitimate callers attributed, 0 of 9 false, including a decoy named like
the flow that writes the table directly.
*Does not do:* calls through variables or `EXECUTE`, C functions, depth beyond 8, anything outside the database.

**3. Build, sign and verify a bundle.**
`tools/fg_bundle.py` produces `fg-bundle/1` with Ed25519. Verification is evidence **only** with two anchors
supplied from outside: a trusted key list and the target the caller is actually looking at (`ADR-0010`).
Measured: 6 of 6 substitution cases with anchors, 3 of 6 without; 102 generated mutants, 0 false rejections.
*Does not do:* prove the claim true. It proves the documents agree under an external key and a supplied target.

**4. Get a machine-checkable verdict and refusal.**
`tools/fg_verify.py` recomputes coverage from the inventory, binds exclusions to real paths, refuses levels without
the required `not_claimed` codes, and refuses an upgrade when the weighted risk outside the core is too large.
Measured: 25 acceptance scenarios, all passing.
*Does not do:* decide what a system is worth. It decides what may be said about it.

**5. Weight the perimeter.**
`tools/fg_perimeter.py` classifies every path (money / personal data / files / other / unclassified) by ordered
rules from `policies/risk-classes.json`, and publishes `outside_weighted_risk` with the policy digest. Unclassified
paths are weighted 3, never 0.
*Does not do:* make the weights objective. They are a recorded convention, and the digest ties a verdict to the
exact weights it used.

## The share gate — when to post this in a developers' chat

All four must hold:

1. **T2 reached** — ✅ *the author's seven engine checks pass; no outsider has reproduced them, and the harnesses assume a running PostgreSQL on a given port with a `postgres` role*.
2. **Reproducible in under ten minutes** — one install line, one fixture command, one expected number.
3. **Known false positives published** — the string-literal case in the grant enumerator, the depth-8 limit in
   attribution, the "a reason can be a lie" limit on exclusions. Published, not hidden.
4. **The honest limitation travels with the pitch** — the sentence that must accompany any share:

> This finds the paths that bypass a declared control point **inside a Postgres database**, and verifies claims
> about them. It does not see application-level controls, it does not prove a system safe, and its inventory is a
> merge of sources with declared blind spots.

What to show: the fixture with eight planted bypasses and the measurement table. What not to show: the deck, the
pricing, or the word "attestation" without the sentence above.

## The README stays current by rule

`lab/check-readme.py` fails if any document under `docs/` is not linked from `README.md`. It runs in CI and in the
negative controls, where a planted orphan document must be caught. That is how "keep the front page current"
becomes a check instead of an intention: a new document cannot land without a line on the front page.

## Current numbers

Read them from the tool, never from this page — this page explains the criteria, the tool reports the state.
