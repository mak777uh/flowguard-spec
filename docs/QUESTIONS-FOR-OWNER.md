# Questions for the owner — the short list

Everything else is being decided and built by the agent. This file holds only what **cannot** be decided here, with
what is blocked, what happens while waiting, and what it costs. Reviewed every round; answers land as edits here.

Last updated: 2026-10-27, after round 8.

---

## Q1 — a real schema to measure on (blocks the first non-synthetic evidence)

**What I need:** permission to point the tool at one real Postgres database, or the name of one.

Every measurement so far is on a fixture **I wrote**. That is the strongest criticism available against this
repository, and it is correct: eight planted bypasses in a schema I designed prove the mechanism, not the utility.

**What I can do alone:** a public schema (Pagila, dvdrental, or any open-source project's migrations) — no secrets,
no client data, fully reproducible. I will start there.

**What I cannot do alone:** anything of yours, or a client's, which is where the real test is.

**Cost of waiting:** the evidence stays synthetic; readiness cannot exceed T2 on synthetic evidence alone.

## Q2 — one consumer conversation (blocks T3, the product half)

**What I need:** one introduction — an auditor, an insurer, a protocol team, or a procurement person — and twenty
minutes. The form is [M8-CONSUMER.md](M8-CONSUMER.md); five lines fill it.

**What is blocked:** the product half of readiness is 0% and cannot move without a named human. `P2` in
[READINESS.md](READINESS.md).

**Cost of waiting:** ten conversations that produce nothing would justify eliminating the product thesis
(`X-21`). Without any conversation, we do not even learn that.

## Q3 — who signs risk acceptance, and with what liability (money decision)

**What I need:** a decision, not information. Three options, in ascending commitment:

1. **No signature.** The bundle carries analysis provenance only; nobody accepts risk; nobody can rely on it. Free,
   and the product is a tool.
2. **Signature with a reliance scope.** A human signs "this may be relied upon for this flow, up to this date, for
   these decisions". This is the reserved field `risk_acceptance` and it is the thing a client would buy.
3. **Signature with an indemnity.** Money at risk. Requires a legal entity, insurance, and a cap.

**What is blocked:** option 2 is designed and unimplemented; option 3 is not designed at all.

**Cost of waiting:** the artifact cannot be sold to anyone who needs recourse, which is most buyers.

## Q4 — publish Part 2 of the hackathon article?

Ready since before the pivot, marked as drafted-not-published. You declined once; the offer stands until the
hackathon closes.

## Q5 — the $70 Nosana credits

Requires your account data to claim. Low value; ignored unless you want it.

---

## Standing decisions I am making while these wait

- **No product claims** in any public surface until Q2 or Q3 resolves. `NC-01`…`NC-10` enforce this mechanically.
- **No pricing, no buyer outreach** — your call, unchanged since round 6.
- **Public schema next** (Q1, alone): Pagila or equivalent, then the same four sources, same thresholds.
- **M7 stays `absent`** until a stranger rebuilds a bundle. Asked of VecDHT (PR #3); no answer yet.
