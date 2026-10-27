# 61. Crypto in scope from day one: what this changes

> Decision: we take the on-chain domain into work immediately, not in v2. This is not "adding a line to the roadmap" — it changes four things in the core and one in the order of the pilot.
> Below: what is mandatory, what is worth doing, and in what order.

---

## 1. What becomes mandatory (and not "later")

| Was (crypto in v2) | Became (crypto in v0.1) |
|---|---|
| six ports — "a week, someday" | **six ports and two backends for each — the entry ticket** |
| attestation format for git+image+DB | **domain-agnostic format: `subject` describes the kind of target** |
| R0–R5 grid for legacy | **the grid is doubled, from day one** |
| 7 attacks | **10 attacks: 7 common + 3 chain-specific** |
| prover = Verus | **two backends: Verus (Rust) and the Solidity stack** |
| finality was not discussed | **finality/reorg — a new core requirement** |

---

## 2. Six ports, now with two backends each

| Port | Legacy | On-chain | Why it cannot wait |
|---|---|---|---|
| `StateProvider` | Postgres | contract via RPC (pinned block) | `resource` in the policy must be addressable without the assumption "this is a table" |
| `EnforcementPoint` | in-process, DB trigger | **guard contract / `require` in entrypoints** | the proof is written for a specific point; rewriting it = rewriting the proof |
| `ObservationChannel` | eBPF, WAL, IdP | **chain events (logs)** | the channels have different trust semantics; they cannot be merged later |
| `Clock` | system clock | **block number + timestamp** | all `exp`/deadlines in `Permit` will break |
| `Domain` | `org_id` | **`chain_id` + contract address** | without it a testnet `Permit` will pass on mainnet |
| `Prover` | Verus | **Certora / Halmos / Kontrol** | the obligation report format must be one |

Implementing `ObservationChannel` for a chain is the cheapest item on the whole list: events are already immutable, timestamped and reproducible by any third party. In effect it is **the best witness we can have**.

---

## 3. Attestation format: domain-agnostic from v0.1

This is the only thing that cannot be "added later" without a breaking change. `subject` is described as a discriminated union:

```json
{"kind": "git",   "commit": "9f3a1c", "lockfiles": "...", "toolchain": "..."}
{"kind": "chain", "chain_id": 1, "address": "0x…", "bytecode_hash": "0x…",
                  "block": 21174321, "finality": "confirmed"}
{"kind": "container", "image": "sha256:…"}
{"kind": "iac",   "repo": "...", "path": "terraform/"}
```

Rule: **any domain-dependent field lives inside `subject`, not at the root of the bundle.** Otherwise, six months later, a crypto client's bundle will fail `verify` under an old version.

---

## 4. New requirement: finality

In legacy a database write is irreversible. **In a chain an event can disappear** — a reorg. This notion was absent from the spec, and without it one can attest to an event that no longer exists.

Requirements:

1. **`block` and `finality` are mandatory** in every observation.
2. **The finality rule** is set by the domain policy: for Ethereum — N confirmations; for L2 — sequencer finality + disputes.
3. **Re-validation**: if the block a bundle references turned out to be in a reorg — status **`INVALID`**, not `INCONCLUSIVE`. This is a fabrication of state, not a shortage of data.
4. **`Clock` returns `(timestamp, height)`**, and the decision is valid only for the version of state at that height (analogous to I7 from legacy).

Check: a separate test — "attestation at block K, then a reorg, then `verify` must return `INVALID`".

---

## 5. Ten attacks instead of seven

The seven common ones remain (batch→keeper, admin panel→admin role, partner entry→external contract, direct access→public call, restore→upgrade authority, CI→deploy, logs→indexers). Three new ones:

| # | Attack | How it is caught | Failure |
|---|---|---|---|
| 8 | **Role escalation**: a privileged function called from the wrong address | enumeration of `onlyOwner`/`onlyRole` + a call test | the call went through |
| 9 | **Signature reuse** across chains/contracts | `chain_id` + `address` in the signature | a testnet signature accepted on mainnet |
| 10 | **Bytecode substitution** at an address (upgrade/selfdestruct) | cross-checking `bytecode_hash` against the act + timelock check | deployed code ≠ proven code |

**Separately:** keeper/automation is the `batch/cron` path; approve/allowance is "a credential left behind". Both are already in Z, but are formulated in the language of the chain.

---

## 6. Prover: the second backend

| Tool | What it gives | When we take it |
|---|---|---|
| **Foundry** (`forge`, `anvil`, invariant tests) | fast property tests on a fork | Day 1, a cheap check |
| **Halmos** | symbolic execution of the EVM | Day 2–3, catches what the tests did not cover |
| **Echidna** | property fuzzing | medium term |
| **Certora (CVL)** | deductive verification of rules | premium, for a guarantee |
| **Kontrol (KEVM)** | formal semantics of the EVM | if a level above Certora is needed |

Estimate `[estimate]`: **3–5 invariants per a 300–800 line contract = 6–12 person-days**, that is, comparable to Rust (24 days for 500 lines), but cheaper — because contracts are smaller and the toolchain is more mature.

---

## 7. The R0–R5 grid is doubled from the start

| R | Legacy | On-chain |
|---|---|---|
| R0 | credential revocation | contract pause, keeper limit, approve revocation |
| R1 | patch | fix + upgrade through a timelock |
| R2 | single writer | guard contract in front of the money |
| R3 | mediator | `require` invariants on all entrypoints |
| R4 | `Permit` + trigger | capability roles, removing `onlyOwner` from fund movement |
| R5 | Verus + guarantee | Certora/Halmos on invariants + enumeration of privileged paths + the act |

**The key difference to put in the report:** in legacy we **forbid** "direct access"; in a chain a public call **cannot be forbidden**. So the policy must be complete over all entrypoints — and that is proven, not administered.

---

## 8. What this does to the order of the pilot (the most important part)

If crypto is in scope — **the technical pilot should be done on a contract, not on a bank**. Comparison:

| | Legacy bank | Smart contract |
|---|---|---|
| Test environment | stand up a stateful application (days) | `anvil` + fork (minutes) |
| Witness | eBPF+WAL+IdP, 12 person-days | chain events, **0 days** |
| NDA and procurement | 6–12 weeks | public repo, **0** |
| Boundary signatory | product + infra owner | **there is none — the chain is the infrastructure** |
| Reproducibility | pinned images | pinned block, free of charge |
| Proof | 24 days for 500 lines | 6–12 days for a contract |
| Legal risk | low | **high in case of an incident** |

**Conclusion: crypto is the technical beachhead, legacy is the commercial one.** Crypto lets you validate the mechanism in two or three weeks without an NDA; a bank brings a check and auditor ecosystem weight, but the entry is expensive.

**An honest warning:** commercially crypto is **more competitive** — Certora, Trail of Bits, OpenZeppelin, Spearbit are already there, the buyer is more sophisticated, and a "guarantee" carries no insurance weight. Technically simpler, harder to sell.

---

## 9. Recommendation: two tracks on one core

```
core (domain-agnostic, 6 ports, format with subject.kind)
   ├── track A: crypto   — technical pilot, 3 weeks, without NDA
   └── track B: legacy   — commercial pilot, 45 days, with a bank
```

Rule: **track A does not block B and vice versa.** What remains shared: the bundle format, the verifier, the policy, the grid, the act. Only the port backends differ.

---

## 10. The first two weeks (updated plan)

| Days | What | Why |
|---|---|---|
| 1–2 | the bundle format with `subject.kind` and `finality` | without it everything else will have to be redone |
| 3–5 | `ObservationChannel` for a chain: RPC → logs → a signed batch with block/height | the cheapest and the strongest witness |
| 6–8 | `flowguard scan` on a public contract: entrypoints, roles, keeper, upgrade proxy | inventory without an NDA |
| 9–11 | policy DSL → SMT for contract invariants; 3 invariants | policy validation |
| 12–13 | Foundry + Halmos: 3 attacks (role escalation, replay between chains, bytecode substitution) | they must fail |
| 14 | bundle + `verify` + `replay` on a pinned block | the full cycle on crypto |

**Success criterion for the two weeks:** `flowguard verify` checks a bundle against a public contract, and all three on-chain attacks yield `BLOCKED`. This proves the mechanism before the first bank appears.

---

## 11. In one line

**Crypto in scope from day 1 is not a "+domain" but a "+mandatory ports, a domain-agnostic format, finality, a second prover and three new attacks".** In exchange it gives a free witness, a free test environment and a pilot without an NDA — and that is why, technically, it must be done first, and commercially, sold second.
