# 60. Crypto and autopay: two different "crypto"s and what to lay down now

> Question: make provision in the spec for crypto and autopay. Answer: these are two unrelated things, and they have to be laid down differently.
> **Crypto as payment rails** — a billing adapter; it affects legal and the cash desk, it does not affect guarantees.
> **Crypto as a protected flow** — a new domain where our product works *better* than on legacy, because the witness is the blockchain itself.
> Below: what to abstract in the spec **now**, so that the core does not have to be rewritten a year from now.

---

## 1. Crypto as payment rails (SKU, subscription)

Impact on the architecture: **almost nil**, if billing is made a separate module from the start.

| What | Decision |
|---|---|
| Channels | card (primary), Lightning (bolt11) for fast small transactions, stablecoin on L2 for large ones |
| Who holds | **nobody**: the rate is fixed at the moment of payment, conversion is immediate, we hold nothing on the balance |
| Accounting | invoice in EUR/USD + a record "received N units, equivalent X at the rate on the date" |
| Refunds | card — standard; crypto — only to the same address, per policy, manually |
| Sanctions/KYC | address screening is mandatory even if we are not a CASP; rejection on flags |
| Errors | underpayment/overpayment/wrong chain — states in the invoice state machine, not in code |

### The rule that has to be written into the spec now

> **Billing has no right to influence the evidence plane.** An overdue subscription does not switch off verification of someone else's attestation and does not break `replay`. Otherwise it turns out that the guarantee cannot be checked without paying — and the whole trust model collapses.

### A pleasant side benefit: our licence is a `Permit`

A paid tier for the OSS version must not phone home to a server (that contradicts "verify offline"). Decision: a signed Ed25519 token with the fields `{tier, org, features, exp, domain}` — **the same mechanism we sell to clients**. We eat our own food: the licence is verified offline, embedded in CI, and requires no network. It is also a demonstration: "look, our own product runs on this".

---

## 2. Crypto as a protected flow — and why it is the best domain

The key difference from legacy: **on a blockchain there is no infrastructure that we control**. You cannot revoke the write credentials of a database — anyone can call the contract. Which means:

```
legacy:     enforcement = application + DB trigger     (I4 = revoking credentials)
on-chain:   enforcement = the contract itself + guard  (I4 = absence of privileged paths)
```

On the other hand, **the witness becomes ideal**: blockchain events are immutable, timestamped, and reproducible by any third party. That is, the most expensive and fragile component of our system (evidence collection, 12 person-days per client) is **free and already built** in crypto — it is the chain itself.

| Our component | Legacy | On-chain |
|---|---|---|
| Witness | eBPF + WAL + IdP, 12 person-days | **blockchain events**, 0 days, already immutable |
| Closure Z | all writers in the infra | all paths of fund movement: entrypoints, admin role, upgrade authority, multisig, keeper, bridge |
| "Batch/cron" | nightly job | **keeper / automation bot** — exactly the same hole |
| "Direct database access" | shared credential | **admin role and upgrade proxy** |
| Mediator | function + trigger | **guard contract / invariant check in the contract itself** |
| Proof | Verus on Rust | **Certora / Halmos / Echidna / Foundry invariants** |
| Deployment substitution | CI + artefact hash | **bytecode verification by address + timelock** |

**Conclusion: for on-chain the guarantee is built more cheaply than for legacy.** Only the proof of the contract's invariants and the enumeration of privileged paths remain expensive.

### The map of seven paths for on-chain

| Path | What it is | Decision |
|---|---|---|
| batch | keeper / automation bot | mediate: the keeper goes through the guard, limits on the call |
| admin panel | admin role, `onlyOwner` functions | mediate: multisig + timelock + event |
| backup/restore | — (no analogue) | outside the model; instead **upgrade authority** — forbid it or timelock it |
| partner API | external contracts, integrations, callbacks | mediate: caller verification, reentrancy guards |
| direct database access | any unprivileged calls | this is precisely the public call: the policy must cover **all** entrypoints |
| logs/analytics | indexers, off-chain copies | outside the guarantee (read-only) |
| CI / supply chain | **deploy and upgrade** | bytecode signature + timelock + address verification |

**Note:** "direct database access" and "a public call to the contract" are one and the same. This changes the framing: in legacy we *forbid* the path, in crypto we **cannot forbid it** — which means the policy is obliged to be complete across all entrypoints, and that is proven, not administered.

### Autopay and streaming

Recurring payments (streams, subscriptions, scheduled transfers) add three specific writers: **keeper**, **allowance/approve**, **session keys**. All three are a "batch job" in our terminology, and all three fall into Z. Their typical failures: the keeper executes an expired intent, the approve remains forever, the session key is not revoked. Each one is a separate attack in the set (it becomes 10 instead of 7).

---

## 3. What to abstract in the spec **now** (six ports)

This is the only thing that really has to be done in advance. Everything else is a layer on top.

| # | Port | Interface | Why now |
|---|---|---|---|
| 1 | `StateProvider` | `read(resource, version)`, `history(resource, range)` | so that `resource` is not "a SQL table". Implementations: Postgres, contract, object store |
| 2 | `EnforcementPoint` | `decide(subject, action, resource) -> Permit`, `enforce(permit)` | so that the mediator is not "a function in the process". Implementations: in-process, DB trigger, guard contract, gateway |
| 3 | `ObservationChannel` | `subscribe(filter) -> signed batch`, `capabilities()` | so that the witness is not "eBPF". Implementations: eBPF, WAL, **chain events**, IdP log |
| 4 | `Clock` | `now() -> (timestamp, height)` | on-chain, time is the block number; without the abstraction all deadlines and `exp` will break |
| 5 | `Domain` | `domain_id` in `Permit` and in the signature | **protection against cross-domain replay**: without it a `Permit` from a test network will pass on mainnet. One line now, a migration later — a painful one |
| 6 | `Prover` | `verify(obligations) -> report` | so that we are not nailed to Verus: Rust/Verus, Solidity/Certora, Dafny — different backends, one report format |

Six ports are roughly **a week of work** and zero impact on the current pilot. Without them, crypto a year from now will require rewriting the core.

---

## 4. The recovery grid for on-chain

| R | Legacy analogue | On-chain | Cost/time |
|---|---|---|---|
| R0 | revoking credentials | contract pause, limits on the keeper, revoking approve | hours |
| R1 | patch | fix + upgrade via timelock | days |
| R2 | single writer | guard contract in front of the money, all paths through it | 1–2 weeks |
| R3 | mediator | invariants in the contract (`require` on all entrypoints) | 2 weeks |
| R4 | Permit + trigger | capability roles, no `onlyOwner` on the movement of funds | 2–3 weeks |
| R5 | proof + guarantee | Certora/Halmos on the invariants + enumeration of privileged paths + a signed act | 3–5 weeks |

---

## 5. Liability: here it is more dangerous than in legacy

In legacy a mistake is fixable: you rolled back the deployment, returned the money, the insurer covered it. **In crypto the loss is irreversible** — there is no chargeback, no issuing bank, no "restore as it was".

Hence the hard rules that have to be written down in advance:

1. **The guarantee limit is tied to the amount at risk**, not to the price of the contract. A guarantee for a flow with $50M TVL cannot cost $48k.
2. **Upgrade authority and bridges are outside the guarantee.** These are places where "the rules change after the signature", and there is nothing to prove there. Explicitly in the negative scope.
3. **The client is obliged to have its own cover** (insurance/reserve) — we are not an insurer.
4. **Suspension on an incident** — automatic, on an event from the witness, like break-glass in legacy.

If this is not accepted, crypto will eat the company with a single incident. The product has to be designed so that the largest possible loss is less than the annual revenue.

---

## 6. What we do not take on

| Not taking on | Why |
|---|---|
| Bridges | the most complex and the most breakage-prone part; there is nothing to prove |
| MEV / front-running | outside the model: this is not a bypass of a control but the ordering of transactions |
| Custodial client keys | we must never touch private keys |
| Oracles and their manipulation | a separate class, it needs its own witness (external data) |
| Tokenomics audit | a different product |

---

## 7. Roadmap

| Version | What |
|---|---|
| **v1 (now)** | legacy only. **Lay down the six ports** — a week, and that is it |
| **v1.5** | billing with a crypto channel (Lightning/stablecoin), licence as a `Permit` |
| **v2** | on-chain as a domain: `ObservationChannel` = chain events, `EnforcementPoint` = guard contract, `Prover` = Certora/Halmos. The first client is streaming payments, because there the keeper = a batch job, and we already know how to do that |
| **v3** | autopay as a separate class of flow (streams, subscriptions, session keys) with an expanded set of 10 attacks instead of 7 |

---

## 8. In one line

**Crypto payment is a billing adapter with a legal tail, and it must not touch guarantees. Crypto as a flow is the best domain for the product, because the witness is built into the system, but the worst in terms of liability, because the loss is irreversible.** And in order not to rewrite the core a year from now, what is needed right now is a week for six ports: `StateProvider`, `EnforcementPoint`, `ObservationChannel`, `Clock`, `Domain`, `Prover`.
