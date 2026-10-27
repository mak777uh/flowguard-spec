# SPEC v0.1 — flowguard (open core)

**Status:** first version, design specification. Prepared for criticism cycles.
**Confidence tags:** `[PROVED]` — proved by machine verification · `[MEASURED]` — measured/reproduced · `[HYPOTHESIS]` — hypothesis, requires verification.
**What this is:** a specification of the minimal vertical slice that 3–4 people can implement in 12–16 weeks and that is already useful to the public.
**What this is not:** a security promise. v0.1 issues a verifiable claim with an explicit boundary, not "the system is secure".

---

## 1. Frame: why exactly this way and what is included

### 1.1. The context from which the priority follows

Mass attacks by agents change the economics of defence: finding a defect has become cheaper than fixing it, and "a list of possible vulnerabilities" has ceased to be a signal. The only thing that retains value is **a verifiable claim with a boundary**. That is why the first release is neither a scanner nor a guarantee, but **publicly verifiable machinery**: a claim format, its verifier, and three invariants that can be checked on someone else's contract without permission.

### 1.2. Key consequence for v0.1 (changes the plan)

**The on-chain flow does not require a microVM.** The EVM environment (`anvil`) is an ordinary process and runs on macOS, Linux and Windows. Hence the full cycle "inventory → invariants → 10 attacks → bundle → verify → replay" **runs on a laptop**, without KVM, without hardware, without an NDA.

Hence the decision: **v0.1 is entirely about on-chain (escrow), end-to-end, locally.** Legacy in v0.1 is static inventory and policy checking only, without dynamics.

### 1.3. What is included in v0.1

| Included | Not included (later) |
|---|---|
| `flowguard.yml` (normative schema) | Legacy dynamics: witness, eBPF, DB trigger |
| `scan` for escrow contracts: fund-flow paths, roles, proxy | Mediator and `Permit` (v0.2) |
| static `scan` for repositories: writers, IaC, OpenAPI | Verus proof of the mediator (v0.3) |
| `check`: policy → SMT (Z3), invariants → Foundry/Halmos | Certora (v0.4, commercial backend) |
| `attack`: 10 scenarios on an `anvil` fork | Automatic payouts and escrow (v0.5, commercial) |
| `attest`: bundle assembly, Ed25519 signatures | Multichain beyond L1+L2 |
| `verify`, `replay`, `diff`, `badge` | Browser UI |
| 3 escrow invariants + 10 attacks + finality | Legacy Z of 12 elements in full |

### 1.4. What v0.1 does not promise — in plain words

- Does not find "all vulnerabilities" and is not an audit.
- Does not guarantee the absence of attacks outside the declared closure `Z`.
- Does not work on targets for which bytecode and state cannot be obtained.
- Does not provide a legal guarantee: the signature in v0.1 is technical, not contractual.
- Does not cover: bridges, oracles, MEV, upgrade paths left active (this is an `INVALID` condition, not "covered").

---

## 2. Domain model

Seven entities. Everything else is derived.

| # | Entity | Definition | Existence invariant |
|---|---|---|---|
| 1 | **Flow** | the protected flow: a resource that moves from input to output | has a `flow_id`, a domain and an owner |
| 2 | **Resource** | an addressable value: an escrow balance, a ledger row, a token | is addressed through a `StateProvider`, not by a "table" and not by a "contract" |
| 3 | **Subject** | who initiates an action | identified only from a verified source, never from the request body |
| 4 | **Policy P** | what the subject is permitted to do with the resource | expressed in a DSL; deny-beats-allow; default deny |
| 5 | **Closure Z** | the set of paths along which the resource can change | exhaustive enumeration; **a non-empty set of unknown paths forbids `PROVEN`** |
| 6 | **EnforcementPoint M** | the single decision point | every path in Z passes through M, or is declared outside the guarantee |
| 7 | **Attestation** | a signed bundle: claim + proofs + boundaries | verified offline without trusting the issuer |

**Domain rule.** Any domain-dependent field lives in `subject`, not at the root of the bundle:

```json
{"kind": "chain.escrow", "chain_id": 1, "address": "0x…", "code_hash": "0x…",
 "block": 21174321, "finality": "FINAL"}
{"kind": "legacy.flow",  "repo": "github.com/org/repo", "commit": "9f3a1c",
 "lockfiles": ["package-lock.json"], "toolchain": "node@22"}
```

---

## 3. `flowguard.yml` format (normative)

Keywords: **MUST** — mandatory, **MUST NOT** — forbidden, **DEFAULT** — default value. Unknown fields in the `policy`, `closure`, `enforcement`, `evidence` sections **MUST** be rejected (fail-closed), so that a typo does not silently widen the boundary.

```yaml
schema_version: "1.0"            # MUST, ^1\.\d+$

flow:
  id: "escrow.payout"            # MUST, immutable, included in the hash
  domain: onchain                # MUST: onchain | legacy
  assets:                        # MUST, ≥1
    - kind: token                # MUST: token | money | data | access
      id: "ERC20:USDC"           # MUST
      criticality: high          # MUST: low | medium | high

subject:                         # MUST
  kind: chain.escrow             # MUST: chain.escrow | chain.contract | legacy.flow
  chain_id: 1                    # MUST for chain.*
  address: "0x…"                 # MUST
  code_hash: "0x…"               # MUST, runtime bytecode hash
  proxy:                         # MUST
    type: none                   # MUST: none | transparent | uups | beacon
    implementation: null         # MUST if type != none
    admin: null                  # MUST if applicable; active admin ⇒ INVALID

policy:
  id: "escrow-release-v1"        # MUST
  version: 1                     # MUST
  fail_closed: true              # MUST; false is forbidden for attestation
  invariants:                    # MUST, ≥1, from the catalogue §8.2
    - id: "INV-1"
  rules_file: null               # optional for legacy

closure:
  declared_paths: [ … ]          # MUST, ≥1; empty list is forbidden
  excluded:                      # optional
    - path: "bridge"
      reason: "outside the guarantee"     # MUST, if path is specified
  unknown_behavior: INCONCLUSIVE # MUST, fixed value

enforcement:
  mode: onchain_guard            # MUST: in_process | single_writer | onchain_guard
  mediator_hash: "0x…"           # MUST for in_process/single_writer
  permit:                        # optional
    algorithm: Ed25519           # DEFAULT Ed25519
    max_ttl_seconds: 900         # DEFAULT 900
    nonce_required: true         # DEFAULT true
    audience_required: true      # DEFAULT true; false is forbidden

evidence:
  observation_channels: [chain_event, chain_state]   # MUST, ≥1
  finality_rule: l1_finalized    # MUST for onchain: l1_finalized | l2_optimistic | l2_zk
  finality_min: null             # DEFAULT per the rule; a block count as the sole criterion — MUST NOT
  reorg_behavior: INVALID        # MUST, fixed value
  prover_backend: [foundry, halmos]                  # MUST, ≥1
  require_replay: true           # DEFAULT true

attestation:
  expires_after_seconds: 86400   # DEFAULT 86400
  signatures_required: 4         # DEFAULT 4
  signer_roles:                  # MUST, ≥4, all different
    - product_owner
    - custody_quorum             # replaces infra_owner for on-chain
    - security_lead
    - verifier
  bundle_format: "fg-bundle/1"   # MUST

limits:                          # optional
  max_compute_seconds: 1800      # DEFAULT 1800
  max_source_bytes: 5000000      # DEFAULT 5 MB
  max_contract_size_bytes: 24576 # DEFAULT 24 KB (EIP-170)

# FORBIDDEN (the validator MUST reject):
# - secrets / private_keys / api_tokens / passwords in any form
# - a verifier signature matching another role
# - "PROVEN" as an input value
# - wildcard trust in addresses or roles
# - excluded without reason
# - active proxy admin without explicit declaration in closure.excluded
```

---

## 4. Attestation bundle (normative)

```
bundle/
├── manifest.json            # hashes of all files, JCS canon, SHA-256
├── flowguard.yml
├── subject.json             # domain, address, code_hash, proxy, block
├── chain/
│   ├── block.json           # number, hash, state_root, chain_id, timestamp
│   ├── finality.json        # rule, source, checkpoint/proof
│   ├── state.json           # slots: roles, owner, proxy impl, balances
│   └── privileged-paths.json
├── closure/
│   ├── declaration.json     # Z: paths, exclusions, unknown_behavior
│   └── reachability.json    # what has been checked, what has not
├── policy/
│   └── invariants.json      # predicates, domains, expected properties
├── proof/
│   ├── results.json         # backend, version, status, proof hash
│   ├── counterexamples/     # if any were found
│   └── assumptions.json     # assumptions ledger + TCB
├── attacks/
│   └── results.json         # 10 scenarios: result, trace, replay_cmd
├── replay/
│   └── manifest.json        # pins, seed, command, environment
├── verdict.json             # status, reason, policy_hash, expiry
└── signatures/
    ├── product_owner.sig
    ├── custody_quorum.sig
    ├── security_lead.sig
    └── verifier.sig
```

| File | Mandatory fields | Who signs |
|---|---|---|
| `manifest.json` | `bundle_id`, `schema`, `created_at`, `file_hashes[]`, `merkle_root` | verifier |
| `subject.json` | `kind`, `chain_id`, `address`, `code_hash`, `proxy`, `block` | verifier |
| `chain/finality.json` | `rule`, `source`, `checkpoint_ref`, `status ∈ {FINAL, PROVISIONAL}` | verifier |
| `closure/declaration.json` | `declared_paths`, `discovered_paths`, `diff`, `excluded[]`, `unknown_behavior` | security_lead |
| `policy/invariants.json` | `id`, `predicate`, `domain`, `expected` | author of the proof |
| `proof/assumptions.json` | `assumptions[]`, `tcb[]` | verifier |
| `attacks/results.json` | `attack_id`, `expected`, `observed`, `replay_cmd` | security_lead + verifier |
| `verdict.json` | `status`, `reason_code`, `policy_hash`, `finality`, `expires_at` | verifier |
| `signatures/*` | `role`, `key_id`, `signed_digest` | the corresponding role |

**Signature rule:** the signature covers **the canonical digest of the whole bundle** (JCS → SHA-256 → Ed25519), not just `verdict.json`. Otherwise the verdict could be transplanted into another bundle.

---

## 5. Verdict: the formal rule

Four values, no "generally fine":

| Value | Condition |
|---|---|
| `PROVEN` | all five predicates below are true |
| `NOT_PROVEN` | an invariant has been refuted by a counterexample |
| `INCONCLUSIVE` | insufficient evidence: unknown path, unreachable bytecode, `PROVISIONAL` finality, timeout |
| `INVALID` | the evidence is broken: code mismatch, reorg, bad signature, `address`/`chain_id` mismatch |

```
PROVEN(x) ⟺
      attacks_all_blocked(x)          # 10/10 attacks yielded BLOCKED
    ∧ invariants_discharged(x)        # every invariant: proved OR offered+passed
    ∧ closure_complete(x)             # unknown_paths(x) = ∅
    ∧ witness_intact(x)               # all channels signed, nonce matched
    ∧ finality_is_final(x)            # not PROVISIONAL
    ∧ policy_matches(x)               # policy_hash matches the signed one

closure_complete(x) ⟺ ∃p ∈ discovered_paths(x): p ∉ declared_paths(x) = ∅
```

**The rule that all five reviewers supported and that becomes formal here:** an unknown path yields `INCONCLUSIVE`, not `PROVEN`. Silent widening of the boundary is the most dangerous defect, therefore `unknown_paths ≠ ∅` **blocks** attestation rather than "warning".

`PROVISIONAL` is not a separate verdict but a field of `finality`. An attestation with `finality: PROVISIONAL` cannot be used to release money, but is valid as a report.

---

## 6. CLI: commands, behaviour, return codes

| Command | What it does | Return codes |
|---|---|---|
| `flowguard init [--template escrow]` | creates `flowguard.yml` with a draft | 0 |
| `flowguard scan` | inventory: fund-flow paths, roles, proxy, writers | 0 |
| `flowguard check` | invariants and policy: Z3 / Foundry / Halmos; prints counterexamples | 0 ok · 1 violation · 3 usage |
| `flowguard attack` | 10 scenarios on an `anvil` fork | 0 all blocked · 1 any passed |
| `flowguard attest` | assembles the bundle, computes the manifest, requests signatures | 0 |
| `flowguard verify <bundle>` | offline verification | **0 PROVEN · 1 NOT_PROVEN · 2 INCONCLUSIVE · 4 INVALID** · 3 usage |
| `flowguard replay <bundle>` | reproduces from scratch at the pinned block | 0 matched · 5 mismatch |
| `flowguard diff <a> <b>` | what changed between attestations | 0 |
| `flowguard badge <bundle>` | SVG for the README | 0 |

Return codes are part of the contract: in CI, `flowguard verify` with code 2 or 4 must stop the build just as 1 does.

---

## 7. Engine

### 7.1. `scan` — inventory

**On-chain.** Sources: ABI, runtime bytecode (EOF/legacy), storage slots, event logs, keeper registries.
Method: `slither` (AST + modifiers) → `cast` (reading EIP-1967 slots) → `evm disassembler` (the `DELEGATECALL`, `SELFDESTRUCT` and value-bearing `CALL` opcodes) → role enumeration via `RoleGranted` logs.
Output: `privileged-paths.json` — a list with the fields `path_id`, `kind`, `evidence`, `discoverable_by`, `gaps[]`.

**Legacy (static only).** `semgrep` (SQL writes, calls), `terraform/k8s` parsers, an OpenAPI parser, extraction of authorisation rules via AST.
Output: `writers.json` — `(service, cred, resource, write type)`.

**Honesty rule:** every discovered path carries `gaps[]` — "what this method does not see". A path without `gaps` counts as an analyser defect.

### 7.2. `check` — policy and invariants

- Legacy: YAML → SMT-LIB → Z3. `deny-beats-allow` is encoded as `allow ∧ ¬deny`. `unsat` = no contradictions, `sat` = a counterexample with concrete values.
- On-chain: the invariant is encoded into a Foundry invariant test + a Halmos symbolic check. `halmos --function check_INV_1` yields `pass`/`fail`/timeout; a timeout → `INCONCLUSIVE`, never `PROVEN`.

### 7.3. `attack` — 10 scenarios

Executable scripts, not agents. Each one: `(setup, action, expected=BLOCKED, replay_cmd)`. Run on `anvil` with a fork at the pinned block. A failed attack = **a failed attestation**, not a "remark".

### 7.4. `prove` — proof

The `Prover` interface (port): `prove(invariant, artifact) → {status, certificate, assumptions[], tcb[]}`.
v0.1 backends: Foundry (property/invariant), Halmos (symbolic). v0.4 — Certora (commercial).
Rule: `assumptions ≠ ∅` is acceptable, but each one lands in `assumptions.json` with a `what_breaks_if_false` field.

---

## 8. First target: escrow

### 8.1. Why escrow (3 of 5 answers)

A small TCB (250–500 lines), a state machine of three states, public reference implementations, and — decisively — **escrow is the first consumer of our own automatic payout**. We test the mechanism on a product we sell ourselves. `[HYPOTHESIS]` that this will yield sufficient commercial demand.

### 8.2. Three invariants (consolidated from three independent sets)

| ID | Predicate | What it catches | Provability |
|---|---|---|---|
| **INV-1** Conservation | `∀a: balanceOf(escrow,a) ≥ Σ_{e∈{LOCKED,DISPUTED}} amount[e][a]` and `totalDeposited = totalReleased + totalRefunded + Σlocked` | drainage, hidden mint/burn, bypass of accounting | arithmetic over storage, induction over `deposit/release/refund` `[HYPOTHESIS]` 3–5 person-days |
| **INV-2** Monotonicity | `released[e] + refunded[e] ≤ deposited[e]`; transitions only `CREATED→LOCKED→{RELEASED|REFUNDED|DISPUTED}`, with no reverse ones | double payout, refund after release | a 3-state automaton, all transitions through a single guard `[HYPOTHESIS]` 2–4 person-days |
| **INV-3** Release precondition | `release(e) ⇒ status[e]=LOCKED ∧ att_PROVEN ∧ att.subject=e.subject ∧ att.recipient=e.recipient ∧ att.amount=e.amount ∧ final(att.block)` | payout against someone else's / non-final / forged attestation | a single transition + field comparison `[HYPOTHESIS]` 3–5 person-days |

**A caveat that must not be lost:** INV-1 in the `≥` form holds only for tokens without rebasing and fee-on-transfer. Such tokens require a separate model; without it the invariant yields `INCONCLUSIVE`.

### 8.3. Privileged paths (minimal enumeration)

| Path | How it is found | Tool | What it misses |
|---|---|---|---|
| owner / admin / roles | AST modifiers + `RoleGranted` logs + slot reads | slither, cast | hand-rolled authorisation (`tx.origin`, admin signature) |
| upgrade proxy | EIP-1967 slots, `slither-check-upgradeability` | cast, slither | non-standard proxies, a diamond without loupe |
| `delegatecall` | opcode scan + target taint | disassembler, slither | a target computed at runtime |
| `selfdestruct` | opcode scan of the implementation | bytecode scan | behaviour after EIP-6780 |
| external value calls | value-bearing `CALL`, `transfer/approve/permit` | static + 4byte decoding | dynamically assembled calldata |
| keeper / callback | automation interfaces, registries | interface detection | an off-chain keeper without an on-chain role |
| sweep / rescue functions | ABI: functions that move an arbitrary token | ABI scan | an "admin" rescue under a role |

**An active `proxy admin` ⇒ `INVALID`**, not "covered": if the implementation can be replaced, the attestation refers to different logic a minute later.

### 8.4. Finality

| Network | Rule | What `verify` yields |
|---|---|---|
| Ethereum L1 | `finalized` checkpoint (≈2 epochs, ~12.8 min). A block counter as the sole criterion — **MUST NOT** | `FINAL` only for a block ≤ finalized head |
| L2 optimistic | batch publication + L1 anchor finalisation + expired challenge period | `PROVISIONAL` until the anchor |
| L2 zk | the proof is verified on L1 and the L1 block is finalised | `FINAL` |
| Reorg between the run and the signature | re-fetch the block by number, compare `block_hash` | mismatch → `INVALID` |

In the bundle: `chain_id`, `block_number`, `block_hash`, `state_root`, `finality_proof`, `code_hash`, `tx_hash` (if there was one).

### 8.5. Ten attacks for escrow

| # | Attack | Expectation | Failure |
|---|---|---|---|
| A1 | `release` from an unauthorised address | revert | the release went through |
| A2 | double `release` of the same escrow | revert | double payout |
| A3 | `release` before the condition/deadline has elapsed | revert | release too early |
| A4 | `release` with an attestation from another escrow (replaying `subject`) | revert | a foreign attestation accepted |
| A5 | `release` with an attestation on a `PROVISIONAL` block | revert | a non-final block accepted |
| A6 | `refund` after `release` | revert | refund after payout |
| A7 | token withdrawal through `sweep`/`rescue` outside `Z` | revert or an entry in `unknown_paths` | the withdrawal went through |
| A8 | role escalation (`grantRole` to self) | revert | the role was granted |
| A9 | implementation substitution through the proxy | `INVALID` | the code did not match `code_hash` |
| A10 | drain through an external call / reentrancy / permit abuse | revert | the funds left |

---

## 9. Legacy in v0.1: static only

Supported: `scan` (writers from code, IaC, OpenAPI), `check` (authorisation rules → Z3), `plan` (a draft Z of 12 elements).
Not supported: witness, eBPF, DB trigger, `Permit`, dynamic attacks. All of this yields `INCONCLUSIVE` with the reason `dynamic_not_available`, and this is **printed explicitly**, not hushed up.

---

## 10. Determinism and reproducibility

| Requirement | How it is ensured |
|---|---|
| One input → one output | JCS canonicalisation, SHA-256, sorting of keys and lists |
| Environment pinning | `chain_id` + `block_number` + `block_hash`; versions of `slither`, `foundry`, `halmos` in the manifest |
| No time in the hash | `created_at` outside the signed digest; `expires_at` as a separate signed field |
| Format versioning | `fg-bundle/1`; `verify` supports **all** past versions forever |
| No hidden non-determinism | no network access during `verify`; `replay` works on a local RPC/fork |

**Release gate:** `flowguard attest` + `flowguard replay` on the reference escrow produce a **byte-for-byte** identical bundle on the second run. A red gate means the release does not ship.

---

## 11. Security of the tool itself

| Threat | Measure |
|---|---|
| Input substitution (someone else's repo/address) | proof-of-control: OAuth read-only / address signature / commit challenge |
| Bundle substitution | signature over the whole digest; `verify` reads nothing outside the bundle |
| Attack through the target's content (prompt injection in comments) | in v0.1 the LLM takes no part in the verdict at all; the analysis is deterministic |
| Attack through `flowguard.yml` | unknown fields are rejected; `PROVEN` cannot be set by an input; there is no `eval` |
| Supply chain of the tool itself | signed releases, SBOM, reproducible build |
| Leakage of a private repo | the analyser does not write code to logs; the bundle contains no sources, only hashes |

---

## 12. v0.1 acceptance criteria

Ten verifiable items. Everything else is "done if green".

1. `flowguard scan` on the reference escrow finds **all** 7 path classes from §8.3, each with a non-empty `gaps[]`.
2. `flowguard check` proves INV-1..3 on the reference escrow and finds a counterexample in a deliberately broken version.
3. `flowguard attack` yields `BLOCKED` on all 10 scenarios for the reference one and ≥7/10 `PASSED` for the broken version.
4. `flowguard verify` returns 0 on a valid bundle and **4 on a bundle with a substituted `code_hash`**.
5. `flowguard replay` reproduces the bundle byte-for-byte on a clean machine.
6. An attestation on a block above the `finalized head` yields `finality: PROVISIONAL` and return code 2, not 0.
7. A reorg simulation (changing `block_hash` in the RPC cache) yields `INVALID`.
8. An active `proxy admin` yields `INVALID` with no way to bypass it with a flag.
9. `flowguard.yml` with an unknown field in `closure` is rejected with code 3.
10. The whole cycle on the reference escrow runs on macOS and Linux, without KVM, in ≤30 minutes.

---

## 13. Roadmap

| Version | Timeline `[HYPOTHESIS]` | Content |
|---|---|---|
| **v0.1** | 12–16 weeks | on-chain escrow end-to-end on a laptop; legacy static |
| **v0.2** | +8 weeks | legacy dynamics: no `anvil` analogue is needed for repos, but a microVM + eBPF + witness is |
| **v0.3** | +8 weeks | mediator + `Permit` + PL/pgSQL trigger + Verus |
| **v0.4** | +6 weeks | Certora backend, 5 policies, the `fg-bundle/1` format frozen |
| **v0.5** | +8 weeks | automatic payout with escrow, dispute window, bonds |

---

## 14. Known weaknesses (a synthesis of five independent assessments)

This section is mandatory: it is not a footnote but a list of claims that are likely to turn out to be wrong.

| # | Weakness | Mechanism | Horizon | Early signal |
|---|---|---|---|---|
| **W1** | **Incompleteness of the path enumeration** (5/5 reviewers) | a path through hand-rolled authorisation, an off-chain keeper or an external admin key is not found by automation | the first 3–10 real targets | an incident on a `PROVEN` target with a path outside `Z` |
| **W2** | **Proof budget** (4/5) | dependency modelling, prover setup and proof-fixing eat the budget faster than a reusable pipeline appears | the first 5 targets | median effort > plan; re-attestation > 15 min |
| **W3** | **Economics of automatic payouts** (3/5) | the bond and the cap are small for large deals; correlated verifier errors produce a run of clawbacks | 6–12 months | the reserve goes negative on the first run |
| **W4** | **Witness noise / `INCONCLUSIVE` inflation** (2/5) | unstable channels, provider disagreement on finality | the pilot | median `PROVEN` < 2 because of technical `INCONCLUSIVE`s rather than violations |
| **W5** | **Closure drift after a hotfix** (3/5) | a new endpoint/role appears outside the re-attestation window | 30–90 days after the pilot | `code_hash` diverges, the path is absent from `declaration.json` |
| **W6** | **L2 finality** (2/5) | accepting state before a reliable L1 anchor | the first 2 weeks | a dispute citing a non-final block |
| **W7** | **Monorepos/polyglot break automation** (2/5) | the share of manual exceptions and the cost grow | 60–90 days after sales start | >30% of scans require manual intervention |

**The decision on W1, taken before any code:** the rule `unknown_paths ≠ ∅ ⇒ INCONCLUSIVE` already closes half the risk. The other half is a public list, in every bundle, of the path classes the analyser **does not see**.

---

## 15. Licence, governance, versioning

- **Code:** Apache-2.0.
- **Format specification:** CC-BY-4.0, so that others can implement the format. This is not a loss: the more independent implementations, the more valuable the signature.
- **Versioning:** `fg-bundle/MAJOR`; MAJOR changes only on an incompatible change; `verify` supports all versions forever.
- **Governance:** BDFL at the start, a public RFC for format changes, breaking changes only with a migration test.
- **What is not allowed:** closing the verifier, requiring our server for `verify`, changing the meaning of `PROVEN` retroactively.

---

## Appendix A. Glossary

| Term | Meaning |
|---|---|
| `Z` (closure) | the set of all resource-change paths, declared and discovered |
| `M` (mediator) | the single decision point through which a path passes |
| `Permit` | a signed non-transferable token of authority, bound to the object, version and policy |
| `PROVEN` | all five predicates of §5 are true; does not mean "secure" |
| `PROVISIONAL` | valid but not final; not suitable for payouts |
| `unknown_path` | a discovered but undeclared path; blocks `PROVEN` |
| `assumptions ledger` | the list of assumptions whose falsity voids the claim |

## Appendix B. Bundle reviewer checklist

1. Does `manifest` match byte-for-byte? (recompute)
2. Does `code_hash` match the bytecode at `block`?
3. `finality.status = FINAL`?
4. Is `closure.declaration.diff` empty (no unknown paths)?
5. All 10 attacks `BLOCKED`?
6. Every invariant: `proved` or `offered+passed`? Is a timeout marked as `INCONCLUSIVE`?
7. `assumptions.json`: does every assumption have `what_breaks_if_false`?
8. Is there no active `proxy admin`?
9. Four signatures from four different keys?
10. Is `expires_at` in the future and not extended "silently"?
