# 52. The OSS version: what software that anyone can run looks like

> Goal: make it so that a person gets a result on their laptop in 5 minutes, instead of deploying bare-metal with KVM. This changes how the system is sliced: dynamics (microVM, witness, attacks) is optional, while inventory, policy, proof and **verification of someone else's guarantee** work everywhere.
> Working name — `flowguard` (placeholder).

---

## 1. What exactly is opened

Key decision: not only the code is open, but also the **guarantee format**. Otherwise the guarantee is not verifiable by a third party, and an unverifiable guarantee is a PDF with a logo.

| Open forever (Apache-2.0 / CC-BY for the spec) | Commercial |
|---|---|
| Specification of the attestation format | Signature as a **legal act** (our liability, insurance) |
| **Verifier and replay** — `flowguard verify` / `replay` | Oracle library beyond the three classes |
| Policy DSL + SMT checking | Managed runs, SLA, support |
| Reference mediator + Verus proof | Acceptance by an auditor, relations with the regulator |
| Harness (orchestrator, witness, executor) — self-host | Liability under contract (E&O) |
| 7 attacks and eval harness | Acceptance corpora and client integrations |

**Why this way and not "everything closed".** The value of a guarantee is not in the code but in the signature and the liability. Code that cannot be checked devalues the signature. An open verifier is the only way to make the guarantee verifiable, and therefore sellable. This is exactly how `cosign`/Sigstore and SLSA work: the format and the verification are open, trust is sold separately.

The main OSS artifact is **`flowguard verify`**: anyone can verify someone else's guarantee offline without trusting its issuer. This is what makes the project a standard rather than yet another scanner.

---

## 2. The first five minutes

```console
$ brew install flowguard          # or cargo install, or docker run
$ flowguard demo
  ↓ cloning examples/hello-bank (500 lines, money flow)
  ↓ inventory: 14 writers, 3 DB credentials with write access
  ↓ policy: 1 contradiction → counterexample below
  ↓ ...

  ⚠ policy contradiction (policy.yml:12)
     allow transfer when subject.tenant == object.tenant
     allow transfer when subject.role == "admin"       ← admin from another tenant
     counterexample: tenant=acme, role=admin, object.tenant=globex

  ✓ Z-draft: flowguard.declaration.yml (14 paths, 2 outside the guarantee)
  ✓ SMT: 42 rules checked, 1 counterexample
  ✗ dynamics unavailable: no KVM (laptop). 7 attacks were not run.

  Next: fix the policy and run `flowguard check`
         full run: `flowguard run --dynamic` on a Linux host with KVM

$ flowguard verify ./examples/sample-attestation
  ✓ manifest hashes ok (consistent)
  ✓ 4 signatures valid (product_owner, infra_owner, security_lead, verifier)
  ✓ 7/7 attacks BLOCKED (per the recorded results)
  ✓ proof: obligations 23/23, assumptions 2 (in whitelist), sorry 0
  ✓ replay: bundle reproduced, hashes matched
  ✓ guarantee valid until 2027-10-27
```

This is the "wow": in five minutes a person sees **verification of someone else's guarantee** and **a contradiction found in the policy** — without a VM, without a client, without infrastructure.

---

## 3. Four modes: what works where

| Mode | Requires | What it gives | macOS | Windows | Linux |
|---|---|---|---|---|---|
| **audit** | nothing | inventory (static), policy + SMT, Z-draft, plan | ✅ | ✅ | ✅ |
| **dynamic** | Linux + KVM | witness, 7 attacks, `PROVEN` | ❌ | ⚠️ WSL2 unreliable | ✅ |
| **attest** | dynamic + signatures | signed attestation | ❌ | ❌ | ✅ |
| **verify / replay** | nothing | verification of any third-party guarantee offline | ✅ | ✅ | ✅ |

Hence the correct order of value for OSS: **verify > audit > dynamic**. The first two will bring most of the GitHub stars, and they require nothing.

For those without hardware: `flowguard run --dynamic --remote <runner>` — the run goes to a KVM runner over ssh, only the CLI stays local.

---

## 4. Formats: the two files that determine everything

### `flowguard.yml` — what we protect

```yaml
flow: payment.transfer
resources:
  - ledger.balance
  - ledger.entry
policy:
  version: 1
  rules:
    - allow: transfer
      when: subject.tenant == object.tenant && object.version == expected_version
    - allow: refund when subject.role == "system"
    - deny: all
entrypoints:
  - api.transfer
  - api.refund
  - api.partner.callback
declaration:
  signers: [product_owner, infra_owner, security_lead, verifier]
  reissue_within_days: 3
dynamic:
  target: ./docker-compose.test.yml
  witnesses: [tap, db_digest, identity]
```

### The attestation bundle — what the guarantee consists of

```
attestation-042/
├── manifest.json              # sha256 of everything else, JCS canonical
├── declaration.json           # Z: 8 fields, path registry, 4 signatures
├── policy.smt2                # policy in SMT-LIB
├── inventory.json             # writers, credentials, entry points + what found them
├── witness/
│   ├── tap.jsonl.zst          # requests/responses with nonce
│   ├── db-digest.json         # state before/after, hash chain
│   └── identity.json          # token → principal
├── attacks/                   # 7 files, each: BLOCKED + proof
│   ├── 01-direct-write.json
│   └── ...
├── proof/
│   └── mediator.verus.json    # obligations, assumptions ledger, TCB
├── replay.sh                  # one reproduction command
└── signature.sig              # Ed25519, who signed
```

**The bundle is a zip/tar with deterministic packaging.** `flowguard replay bundle.tar.zst` brings up the environment from the published digests, runs it again, compares hashes. A mismatch is either a determinism bug or a forgery; both cases are a stop.

---

## 5. CLI: twelve commands

| Command | What it does | Needs KVM |
|---|---|---|
| `flowguard init` | creates `flowguard.yml` with a draft | no |
| `flowguard scan` | inventory of writers, credentials, entry points | no (static) / yes (runtime) |
| `flowguard plan` | Z-draft + policy draft | no |
| `flowguard check` | SMT: contradictions, implicit allows, cycles; counterexamples | no |
| `flowguard mediate init --stack java` | skeleton of the mediator + `Permit` + PL/pgSQL trigger | no |
| `flowguard attack` | 7 attacks, each must yield `BLOCKED` | yes |
| `flowguard prove` | Verus/Dafny on the mediator, assumptions ledger | no (toolchain required) |
| `flowguard attest` | bundle assembly + signatures | yes |
| `flowguard verify <bundle>` | **verification of someone else's guarantee** | no |
| `flowguard replay <bundle>` | reproduction from scratch | yes |
| `flowguard diff a b` | what changed between two attestations | no |
| `flowguard badge` | SVG badge for the README: `Z-042 · verified 2026-10-27` | no |

`diff` and `badge` are small, but they are exactly what makes the project viral: `flowguard diff` shows in a pull request that a code change did not widen the flow boundary, and the `badge` is placed in the client's README.

---

## 6. What the binary is assembled from

For OSS, ease of installation matters, so — a single static binary, without a daemon.

```
flowguard (one binary, Rust)
├── core: inventory, policy→SMT, evidence, verify, replay, diff
├── plugins (subprocesses, gRPC):
│    ├── flowguard-witness   (Rust+Aya, eBPF, Linux only)
│    ├── flowguard-exec      (Go, in a microVM)
│    └── flowguard-prover    (wrapper over verus/dafny)
└── backends:
     ├── sandbox: firecracker | gvisor | none
     ├── witness: ebpf | pgaudit | log-replay
     └── prover:  verus | dafny | none
```

**Principle: without plugins, half of it works.** `audit` and `verify` require nothing but the binary. Plugins are invoked as subprocesses with a typed contract — which means a third-party witness or your own prover can be plugged in without forking the core.

`--sandbox none` — the "no KVM" mode: evidence is collected from logs and `pgaudit`, without a microVM. It is labeled honestly: `sandbox: none ⇒ dynamic guarantees unavailable`, and this field lands in the attestation.

---

## 7. GitHub life

| What | How it looks |
|---|---|
| `examples/hello-bank` | 500 lines, money flow, 3 vulnerabilities; `docker compose up` and everything works |
| `examples/multi-tenant-saas` | tenant policy, BOLA, show 4 policies |
| GitHub Action | `uses: flowguard/verify-action@v1` — verifies the bundle in a PR, fails on a hash mismatch |
| Action for dynamic | self-hosted KVM runner; the README explicitly says "hardware required" |
| Docs | `flowguard.dev`: Getting started (5 min), Attestation format (spec), 4 policies, FAQ about "how this is not a scanner" |
| Badge | `![flowguard](https://img.shields.io/.../Z-042/verified)` |

Three examples is the minimum: one shows the flow and the attacks, the second — the policy and the counterexample, the third — **verify of someone else's attestation** (so that it is visible that this is independent verification, not self-verification).

---

## 8. License and governance

- **Code:** Apache-2.0 (patent protection matters for infrastructure software).
- **Format spec:** CC-BY-4.0 — so that others, including competitors, can implement it. This is not a loss: the more independent implementations, the more valuable our signature.
- **Governance:** BDFL at the start, a public RFC process for format changes. A breaking format change is a new major version, old bundles are verified forever (the verifier supports all versions).
- **No "open core with poisoned hooks"**: if the README says "independently verifiable", then the verifier must not require our server. Otherwise the project's reputation will die within a week.

---

## 9. OSS roadmap

| Version | What | Why |
|---|---|---|
| **v0.1** (4 weeks) | `init/scan/plan/check` + `verify` + bundle format + hello-bank | already useful on a laptop: finds contradictions in the policy |
| **v0.2** (6 weeks) | mediator + `Permit` + PL/pgSQL trigger + `attack` (Linux) | physically blocks bypass |
| **v0.3** (4 weeks) | `prove` (Verus) + assumptions ledger | a proof appears |
| **v0.4** (3 weeks) | `attest`, `replay`, `diff`, `badge`, GitHub Action | turns into a standard |
| **v1.0** | 3 policies, 2 stacks, stable format | can be referenced in a contract |

**v0.1 is the most important.** If in four weeks a person on a Mac cannot find a contradiction in their policy in five minutes and verify someone else's attestation, the project will not take off, no matter how many microVMs are inside.

---

## 10. Honest risks of the OSS model

| Risk | What we do |
|---|---|
| A giant takes the format | that is the goal too: if GitHub/cloud implements our format, our signature becomes the standard |
| The OSS version devalues the sale | on the contrary: what is sold is liability and acceptance, not software. But the consulting margin remains — this has to be accepted |
| `dynamic` does not run for most | that is by design: `audit`+`verify` are free and viral, `dynamic` — on hardware or with us |
| The format changes and breaks bundles | an eternal verifier of all versions, RFC process, never remove support |
| "Yet another security scanner" in perception | positioning in the README, first line: **"it does not find bugs — it proves that the control cannot be bypassed"** |

---

## 11. In one line

**One static binary, four modes (audit / dynamic / attest / verify), two files (`flowguard.yml`, attestation bundle), twelve commands, a 500-line example, Apache-2.0, the format open, the signature commercial.** On a laptop, `audit` and `verify` work; on Linux with KVM — `dynamic` and `attest`; `verify` requires nothing and therefore can become a standard.

The main test of the design: **if a person cannot verify our guarantee without us, it is not a guarantee but marketing.** The OSS version exists precisely to make that possible.
