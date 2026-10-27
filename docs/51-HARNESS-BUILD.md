# 51. Harness: the concrete build (OS, languages, wiring, workflow)

> An answer to the question "what is this made of": which OSes, which languages for each component, how they are connected, how the images are built, what the working cycle looks like. No "you could use" — a choice with justification.

---

## 1. Operating systems: four different roles, do not confuse them

There are four kinds of machines in the system, and each has its own OS. Mixing them is the source of half the problems.

| Role | What it is | OS | Why |
|---|---|---|---|
| **Host** | the hardware the microVMs run on | **Debian 12 (bookworm) minimal**, kernel 6.1+ with BTF, KVM | no superfluous services, stable packages, eBPF with BTF out of the box. Ubuntu 24.04 is acceptable, but it pulls in snapd and more surface |
| **Guest (agent VM)** | where the agent and its tools live | **Debian 12 slim rootfs** built by `mkosi`, `vmlinux` kernel from Firecracker | <200 MB, no init-system ballast, start <150 ms |
| **Guest (target VM)** | where the **client's application** is deployed | **the same image the client runs in prod** (pinned digest) | otherwise the PoC will not reproduce — this is requirement I2 |
| **Witness** | collection of eBPF/DB/IdP evidence | **host, outside both VMs** | if the witness is inside the agent's VM, it is not a witness |

### Windows: target only, not a harness

**v1 — Linux-only targets.** Windows is supported neither as a host nor as a guest for the agent.

The reason is technical, not ideological: the entire witness layer is built on **eBPF** and `pgaudit`. On Windows the equivalent is **ETW + Windows Event Log + Sysmon**, a different format, a different collector, a different trust model (no BTF, no `bpf()` hooks, and "outside the agent's VM" cannot be guaranteed as cheaply). That is a separate witness engine and a separate product track.

Windows appears in v2 as a **target** (enterprise legacy: .NET, MSSQL, AD), while the harness stays on Linux and the Windows target is brought up on a **separate Windows host** with an ETW collector. Firecracker does not run Windows (there is no EFI/TPM path in any reasonable form) — so you need Hyper-V/WHPX or separate hardware. That changes the economics, which is why it is not in v1.

**Rule:** if the client is on Windows, in v1 we sell diagnostics only (`HYPOTHESIS`), we do not sell a guarantee. This goes into the public list of exclusions.

---

## 2. Languages: by component, with justification

| Component | Language | Why exactly this one |
|---|---|---|
| **`flowctl`** — the client's and the operator's CLI | **Rust** | a single static binary that runs on any client machine without dependencies; `clap` + `serde` |
| **`flow-orch`** — the orchestrator (control plane) | **Go** | the Temporal SDK is mature, concurrency on goroutines, static build into a scratch image |
| **`flow-exec`** — the tool server **inside** the agent VM | **Go** | a static binary without libc, fits into a minimal rootfs; a typed gRPC contract |
| **Planner** (LLM loop) | **Python 3.12** | the LLM-client ecosystem, fast iteration; it lives **outside** the VM and has no access to the target |
| **`flow-witness`** — eBPF collection | **Rust + Aya** | eBPF in Rust without the libbpf pain, safe ring-buffer handling, a single binary |
| **`flow-verify`** — verifier + verdict aggregator | **Rust** | determinism, cryptography (`ed25519-dalek`, `sha2`), no possibility of accidentally "interpreting" |
| **Mediator (reference, proof track)** | **Rust + Verus** | memory for free, provable contracts, industry acceptance; Verus runs on stable Rust |
| **Mediator (library for the client)** | **Java / TypeScript / Python** — per the client's stack | you cannot drag Rust into Spring Boot; here `Permit` = private constructor + linter + DB trigger |
| **DB trigger** | **PL/pgSQL** | the last line: rejects a write without a `Permit` signature; Ed25519 verification via `pgcrypto`+extension |
| **Policy DSL → SMT** | **Python + `z3-solver`** | z3py is the only mature path; the DSL is parsed into SMT-LIB, counterexamples are returned as text |
| **Proof** | **Verus** (Rust), **Dafny** (algorithms), **Lean 4** (policy invariants) | per task class; Verus for code, Lean for the model |
| **Gate UI** | **TypeScript + React** | four screens, a diff view; nothing exotic |
| **Stand eval harness** | **Python** (`pytest`) | tests that run the whole DAG over the corpus |

**Why not "everything in Python":** determinism and signing. The components whose outputs go into the act (`flow-verify`, the mediator, the witness) must be in a language with predictable semantics and no dynamic surprises. Python is kept where development speed matters, not guarantees.

**Why not "everything in Rust":** team speed. `flow-orch` in Go is written three times faster and does not need to be proved.

---

## 3. Monorepo structure

```
flowguarantee/
├── cmd/
│   ├── flowctl/            # Rust CLI
│   ├── flow-orch/          # Go
│   ├── flow-exec/          # Go (in VM)
│   ├── flow-witness/       # Rust + Aya (eBPF)
│   └── flow-verify/        # Rust
├── crates/
│   ├── permit/             # Ed25519 token: structure, signature, verification
│   ├── evidence/           # CAS, JCS canonicalization, hash-chain
│   └── oracle/             # oracle contract + 3 classes
├── mediator/
│   ├── reference/          # Rust + Verus, proven
│   └── adapters/           # java/ ts/ py/ — brownfield versions
├── policy/
│   ├── dsl/                # YAML parser
│   ├── smt/                # z3py bridge, counterexample generation
│   └── library/            # 5 typical policies
├── proof/
│   ├── verus/              # mediator contracts
│   ├── dafny/              # algorithms (limits, states)
│   └── lean/               # policy invariants
├── images/
│   ├── mkosi/              # guest rootfs (agent, target base)
│   └── host/               # ansible/cloud-init for bare-metal
├── attacks/                # 7 executable red-team scripts
├── evals/                  # eval harness, corpora, negative controls
├── examples/hello-bank/    # 500 lines: balance mutation (Day 1)
└── docs/spec/              # this spec
```

---

## 4. Images and reproducibility

| What | How | Why |
|---|---|---|
| Guest rootfs | **`mkosi`** → `.ext4` + `vmlinuz` | declarative, repeatable, no Docker daemon on the host |
| Target environment | **the client's image as is**, pinned digest | otherwise the PoC will not reproduce at the client's (I2) |
| Host | **Ansible + cloud-init** on bare metal | KVM, hugepages, `nftables`, `bpftrace` — everything explicit |
| Build toolchain | **Nix flake** (`rust-toolchain`, Go, Python, z3, Verus) | the compiler version is part of the proof hash |
| Artifacts | **cosign** + digest in the run manifest | image signing; without it the orchestrator does not start |

**Rule:** `digest(rootfs)` + `digest(toolchain)` + `digest(policy)` = part of the verdict's `signed_hash`. Without that, "reproducible" is just a word.

---

## 5. Runtime wiring: how the components talk to each other

```
flowctl ──gRPC──▶ flow-orch ──Temporal──▶ DAG steps
                     │
                     ├──▶ flow-exec (in agent-VM) ──tool RPC──▶ tools (semgrep, no-nmap, curl)
                     ├──▶ flow-witness (host, eBPF) ──signed batch──▶ evidence
                     ├──▶ flow-verify ──▶ verdict, signed
                     └──▶ z3py (policy check) ──▶ unsat/counterexample
```

| Connection | Mechanism | Why |
|---|---|---|
| Client ↔ orchestrator | **gRPC**, mTLS | typed contract, easy to version |
| Orchestrator ↔ steps | **Temporal** | durable, idempotency, retries without double effects |
| Orchestrator ↔ VM | **Firecracker API** (vsock) | no network between the control plane and the VM — only vsock |
| VM ↔ tools | **`flow-exec` + allowlist** | the agent has no shell; only declared tool-calls |
| Evidence | **S3 Object Lock (MinIO) + Rekor** | WORM + external timestamp |
| Metadata | **PostgreSQL** | runs, verdicts, registries, signatures |
| witness→evidence queue | **NATS JetStream** | lightweight, at-least-once, without Kafka ballast |

### Two different "policies" — do not confuse them

This is the classic mistake that breaks the architecture:

| | Harness policy | Client authz policy |
|---|---|---|
| What it decides | what the **agent** is allowed to do | what the **subject** is allowed to do with an object |
| By what | **OPA/Rego** or Cedar, at the tool-call level | its own DSL → **Z3**, compiled into the mediator |
| Where | `flow-exec` before the tool call | the mediator, in the client application's process |
| Is it proved | no, it is tested | yes, SMT + Verus |

They must not be mixed: Rego is not provable, and SMT cannot decide "may the agent run nmap".

### Network model

- An agent VM has **no** network interface by default; only vsock to `flow-exec`.
- Egress — through **Envoy** with an allowlist, a separate route to the target VM.
- The target VM is in an isolated netns; host `nftables` forbids everything except what is declared.
- **No cloud metadata endpoints** (169.254.169.254) — a separate drop rule.

---

## 6. Dev workflow: how this gets built

| Step | Tool | Gate |
|---|---|---|
| Build | `just build` on top of the Nix flake | compilation + `clippy -D warnings` + `gofmt -l` |
| Unit | `cargo test`, `go test`, `pytest` | coverage ≥70% on `permit`/`evidence`/`oracle` |
| Integration | `just vm-test` — brings up Firecracker, runs `flow-exec` | VM start <1 s, tool RPC works |
| E2E | `just e2e` — the whole DAG on `examples/hello-bank` | 7/7 attacks `BLOCKED`, 0 false `PROVEN` |
| Proof | `just verify` — Verus/Dafny in CI | 0 `sorry`, `assume` only from the whitelist |
| **Reproducibility** | `just attest-replay` | **yesterday's act rebuilds byte-for-byte** — the release gate |
| Release | `just release` | cosign, SBOM, digest into the manifest |

**The release is blocked by a single test:** `attest-replay`. If it is red, we ship nothing, because a non-deterministic stand cannot issue guarantees.

---

## 7. Runtime workflow: the life cycle of a run

```
IDLE ──compile──▶ PLANNED ──inventory──▶ DRAFT_Z ──G1──▶ Z_SIGNED
                                                          │
                                          policy ◀────────┘
                                            │
                                        DRAFT_P ──G2──▶ P_APPROVED
                                            │
                                        mediate ──▶ M_DEPLOYED
                                            │
                              witness ──▶ W_READY ──attack──▶ 7×BLOCKED
                                            │
                                         prove ──G3──▶ PROOF_ACCEPTED
                                            │
                                        declare ──G4──▶ ATTESTED
                                            │
                        ┌───────────────────┴───────────────────┐
                        ▼                                       ▼
                  RE_ATTEST (15 min)                      DEGRADED (boundary changed)
                        │                                       │
                        └──────────▶ ATTESTED ◀─── re-declare ──┘
```

The states are stored in Temporal; the transition to `DEGRADED` is automatic on any `Δ ≠ 0` in the inventory or in the M hash.

---

## 8. What actually has to be written for Day 1

Five binaries, not twelve. The rest is configuration and scripts.

| Binary | Lines (estimate) | Language | Can be simplified to |
|---|---|---|---|
| `flow-exec` | 800–1200 | Go | one tool: `http_call` with an allowlist |
| `flow-witness` | 600–1000 | Rust+Aya | tap only; the DB digest by an SQL script |
| `flow-verify` | 500–800 | Rust | signing + the C/T/N aggregator |
| `mediator/reference` | 300–500 | Rust+Verus | one policy: ownership |
| `flowctl` | 400–600 | Rust | `attest`, `replay`, `sign` |

Plus non-code: the `mkosi` image (1 day), 7 attack scripts (2 days), the PL/pgSQL trigger (half a day), the z3py bridge (1 day).

**A total of ~3000–4000 lines of code** before the first full run. That is two to three weeks for one strong engineer, not half a year.

---

## 9. Why exactly this way, if someone asks "could it be done differently"

| Alternative | Why not |
|---|---|
| Docker instead of Firecracker | a shared kernel with client code = no isolation; C5 violated |
| Kubernetes right away | for one machine and one client this is pure overhead; K8s is for when there are 10 clients |
| A single agent in the "chat with a shell" style | no allowlist, no determinism, no act |
| Python for the verifier | signing and hashing must be in a predictable runtime |
| Prove everything end to end | the proof is limited to the mediator (hundreds of lines); the rest is measured |
| Windows in v1 | a different witness layer (ETW), different economics; a separate track |
| Our own proof assistant | Verus/Dafny/Lean already exist and are cheaper |

---

## 10. In one line

**Host:** Debian 12 + KVM on bare metal. **Guest:** Debian 12 slim via `mkosi`, Firecracker. **Languages:** Rust for everything that goes into the signature (`verify`, the mediator, the witness, the CLI), Go for the orchestrator and the in-VM executor, Python for the LLM planner and the SMT bridge, PL/pgSQL for the last line in the DB. **Wiring:** gRPC between services, vsock to the VM, Temporal for the DAG, NATS for evidence, S3+Postgres for storage, Envoy for egress, OPA for the agent's rights and Z3 for the subject's rights. **Windows:** as a target only, v2 only. **Release gate:** yesterday's act rebuilds byte-for-byte.
