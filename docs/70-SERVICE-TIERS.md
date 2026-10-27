# 70. Services: what to sell first, code as a separate SKU, OSS strategy

> Scheme: OSS core for everyone → a service on top of it (fiat → crypto → automatic payouts without humans).
> Question: which baseline analysis is optimally useful, and whether code can be sold separately.
> Short answer: what must be sold is **the flow map and the contradictions in the rules**, not a "vulnerability scanner". Code — yes, a separate SKU, but with different economics and different liability.

---

## 1. Baseline analysis: what it is

**Not a "vulnerability scanner".** A scanner is a commodity, it is free from the competitors and it does not answer the question "can the money be carried away".

Baseline analysis answers three questions that the client cannot ask himself:

1. **Where money/data can leak from** — the complete list of places where a resource is mutated, including the nightly job, the admin panel, restore, partner access and direct database access.
2. **Which access rules contradict each other** — with a concrete example: "an admin of any tenant can transfer someone else's money".
3. **How much it costs to close** — an estimate in days and money, for each path.

### Why exactly this, and not something deeper

| Property | Why it is critical |
|---|---|
| **Does not require a KVM or a test environment** | it runs on a laptop, the client has no infrastructure requirements |
| **Read-only** | zero legal risk: we do not exploit, do not scan the network, do not touch production |
| **Does not require the client to enumerate the paths himself** | this is the main blocker to selling the guarantee. The machine proposes the list, the client only checks it — the barrier falls |
| **90% automated** | margin >80%, low price, pays for itself from the first client |
| **Naturally sells the next step** | the output is a draft Z Declaration, that is, the entry into migration |

The last point matters more than the others: baseline analysis **produces the entry document** for the next SKU. Not an "upsell", but a continuation of the same work.

### What is in the report (5 artifacts)

1. **Flow map** — the list of write paths with an indication of how each was found: code, IaC, OpenAPI, `pgaudit`, eBPF.
2. **Contradictions in the rules** — up to five counterexamples from Z3, each with concrete attribute values.
3. **Draft Z Declaration** — the path registry + the "out of scope" list with a reason for each line.
4. **Closure estimate** — for each path: days, risks, what will break.
5. **Suitability verdict** — whether you pass the validatability contract and what stands in the way.

**Price:** $2–5k `[estimate]`, 3–5 business days, without installing anything at the client's site.

---

## 2. Code as a separate service

Yes, and it is the right decision — but it has different economics and a different risk. Two tiers, and they must not be mixed.

| | **Patch** (R1) | **Migrate** (R3–R4) |
|---|---|---|
| What | diffs for specific findings | mediator + `Permit` + trigger, credential revocation |
| Volume | 1–10 lines per finding | 200–500 lines + migration |
| Price | $500–1500 per patch | $25–45k `[estimate]` |
| Margin | low, commodity | 35–45%, but this is the core of the product |
| Who is liable | the client merges it himself | we write, the client accepts |
| Risk | "the patch broke production" | "the architecture was changed and the business logic drifted" |
| How to sell | in packs of 10 | only after baseline analysis |

**Three rules for code as a service:**

1. **Draft PR only, never a deploy.** Liability for applying it rests with the client.
2. **Tests are mandatory.** We do not hand over a patch without a test: otherwise "accepted" = "not checked".
3. **Liability cap = the price of the work.** We are not liable for the business logic of someone else's system into which we were let in for a week.

**Why code separately and not bundled.** Everyone buys patches, only a few buy migration. If you mix them into one SKU, the average ticket falls to the patch level while the work grows to the migration level.

---

## 3. The service ladder in full

| # | SKU | Price | Term | Automation | What it sells |
|---|---|---|---|---|---|
| 1 | **Baseline analysis** (map + rules) | $2–5k | 3–5 days | **95%** | "here is where it will leak and why" |
| 2 | **Patch** (pack of 10 findings) | $5–10k | 2 weeks | 80% | "here are the fixes" |
| 3 | **Migration to the mediator** | $25–45k | 4–6 weeks | 40% | "here is the checkpoint through which everything passes" |
| 4 | **Guarantee + proof** | $48k + $12k/year | 45 days | 30% | "here is the proof, check it yourself" |
| 5 | **Re-attestation** | included in the subscription | **15 min** | **98%** | "the guarantee is alive" |

The sales order is strictly 1 → 2 → 3 → 4. Each next one is not sold without the previous one: without the map there is no Z, without Z there is no guarantee.

**Economics:** SKU 1 and 2 — the entry point and cash; SKU 3 — the main ticket; SKU 4–5 — subscription and margin. SKU 1 at 95% automation and a $3k price yields >$2.5k of margin — that is, even giving the maps away for free pays for itself.

---

## 4. Crypto and automatic payouts without communication: why this is possible at all

There is a non-obvious link here that is worth using.

An automatic payout without a human requires three things: (a) a machine-checkable criterion that "the work is done", (b) an irreversible settlement, (c) the absence of a dispute on the merits. Item (a) is usually impossible, which is why a bug bounty always has a triage team.

**But our product produces exactly what is missing for an automatic payout:** a signed attestation that can be verified offline. Therefore:

> **Escrow is released on the event "the attestation passed `verify`".** Not "a manager looked and decided", but a deterministic check of the bundle.

Scheme:

```
customer → escrow (stablecoin wallet or Lightning hold-invoice)
         → executor brings the attestation bundle
         → smart contract/service runs verify(bundle)
         → signatures, hashes, attacks, proof ok  →  payout automatically
         → did not pass                           →  bundle returned, escrow waits
```

**What is mandatory, otherwise it is a hole:**

| Requirement | Why |
|---|---|
| **A 72-hour dispute window** after the payout | protection against an oracle error; revocation via `INVALID` and a re-run |
| **A bond from the executor** | otherwise it pays to bring "passed" on a forged bundle |
| **Address screening** | sanctions, even if we are not a CASP |
| **An automatic payout ceiling** | $5k automatically, above that — a human; otherwise one oracle bug zeroes the till |
| **A public decision log** | without a human the only arbiter is the reputation of the format |

**Why it works without communication at all:** the only thing people usually negotiate in such a deal is "is it proven enough". With us, `verify` answers that, not negotiations. If the answer is machine-generated, communication is not needed.

**What this gives commercially:** a fully automatic marketplace "found → proved → got paid", while without an arbiter role on our side. This is far cheaper than a classic bug bounty and removes the main cost line — triage.

---

## 5. OSS → closed repo: here is the trap

Your formulation "start with OSS, then move it to a closed repo and finish it there" **does not work legally**: Apache-2.0 is irreversible. Everything that has been published stays open forever, and forking is legal. The attempt to "close it back" is the only guaranteed way to lose trust in a product that sells verifiability.

**The correct scheme is not a fork, but a dependency:**

```
repo A (open, Apache-2.0, forever):
    attestation format · verifier · replay · policy DSL ·
    reference mediator · 7 attacks · CLI

repo B (closed):
    managed runs · oracle library · signing authority ·
    client integrations · auditor acceptance · billing
         │
         └── depends on A as a library (not a fork)
```

The key point: **B imports A rather than copying it.** Then the development of A continues publicly, and the value of B is not in code but in what cannot be in code: liability, relationships, the oracle catalogue, the accumulated corpus.

**What constitutes a moat in such a scheme** (in order of strength):

1. **The right to sign and insurance** — cannot be copied.
2. **Acceptance of the format by an auditor** — a contract, not code.
3. **A library of oracles** for classes beyond three (each — 4–8 days of work, accumulating).
4. **The corpus and metrics** on private data.
5. The code itself — **not a moat at all**.

**What must not be done:** "source-available" licences (BSL and similar) for the verifier. The product sells "check it without trusting us"; a closed verifier destroys that statement. Openness here is not altruism but a condition of the product.

---

## 6. What to do in the first two weeks

1. **Days 1–4:** OSS v0.1 — `init / scan / plan / check / verify` on one example. Without this there is no SKU 1.
2. **Days 5–8:** run SKU 1 on three real services (our own or friendly ones) — get three reports that are not embarrassing to show. This is the selling material.
3. **Days 9–12:** a landing page with one phrase and a demo report; price $2–5k, payment by card. Crypto — later, it adds nothing at this stage.
4. **Days 13–14:** decide on escrow: whether it is needed in v1. My recommendation is — **no**. Automatic payouts make sense when there is a flow of executors; at the start there is none, and escrow adds legal and engineering debt.

---

## 7. In one line

**The first product is the flow map and the contradictions in the rules: $2–5k, 3–5 days, 95% automation, zero legal risk and a ready entry into migration.** Code is a separate SKU, only as a draft PR with tests and a liability cap equal to the price. Automatic payouts without humans are possible precisely because our acceptance criterion is machine-checkable — but they must be introduced after a flow of executors appears, not before. And the OSS core stays open forever: what is closed is not the code but the service on top of it.
