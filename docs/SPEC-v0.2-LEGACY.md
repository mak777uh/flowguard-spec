# SPEC v0.2 — flowguard Legacy

**Status:** design specification for the legacy track. Companion document to `SPEC-v0.1.md` (on-chain).
**Tags:** `[PROVED]` machine-proved · `[MEASURED]` measured/reproduced · `[HYPOTHESIS]` hypothesis.
**What this is:** a complete summary of what has been understood about the legacy flow across all rounds: closure, mediator, evidence, oracles, the remediation ladder, the limits of applicability.
**What it does not promise:** the absence of vulnerabilities. Legacy attestation asserts: "within the declared closure nothing gets past the mediator" — and nothing more.

---

## 1. Framing

### 1.1. Why legacy comes second, not first

On-chain (v0.1) requires only EVM — it runs on a laptop. Legacy requires three expensive things:

| What is needed | Cost |
|---|---|
| MicroVM + host with KVM | bare-metal; nested virtualisation will not do |
| Dynamic witness | eBPF on the host + `pgaudit` + IdP interception = 12 person-days per target |
| Reproducible deployment of the client application | every adapter is engineering days; the main source of `DEPLOY_FAILED` |

Hence legacy is v0.2: first the mechanism is proved on a contract, where the witness is free, and only then is it carried over to infrastructure where the witness costs two weeks.

### 1.2. What is included in v0.2

| Included | Not included |
|---|---|
| `scan --runtime`: eBPF + `pgaudit` → the actual registry of writers | The six ports beyond Postgres |
| Mediator in two modes: `in_process` and `single_writer` | Multi-cloud deployments |
| `Permit` (Ed25519) + PL/pgSQL trigger | A key-management service for the client |
| Witness: tap + DB digest + identity; 2 acceptance tests | Windows targets (a separate track, ETW) |
| Oracles of 3 classes: SQLi, BOLA, path traversal | Oracles for business logic (outside the product) |
| 3 policies out of 5 (ownership, limit, tenant) | PII and the state machine (v0.4) |
| 7 attacks, the R0–R2 grid | R3–R5 (v0.3+) |
| An act of 8 fields, 4 signatures, the 3-day rule | Automatic payouts |

---

## 2. Legacy domain model

The same seven entities, instantiated differently:

| Entity | In legacy this is | Port |
|---|---|---|
| **Resource** | a ledger row, a balance, a table, an object by `object_id` | `StateProvider` → Postgres |
| **Subject** | `userId`/`tenantId` from a verified JWT/session | `StateProvider` + IdP |
| **Policy P** | the rules for "who may do what with an object" | DSL → Z3 |
| **Closure Z** | 12 elements (§8) | inventory |
| **EnforcementPoint M** | a function in the process **or** the single service-writer **+ DB trigger** | `EnforcementPoint` |
| **Witness** | eBPF tap, WAL/`pgaudit`, IdP log | `ObservationChannel` |
| **Attestation** | the act bundle with 4 signatures | `verify` |

### 2.1. The six ports — concrete implementations

| Port | v0.2 implementation | What can be replaced later |
|---|---|---|
| `StateProvider` | Postgres: `read(resource, version)`, `history(resource, range)` | another SQL, an object store |
| `EnforcementPoint` | `in_process` (library) + `postgres_trigger` | gateway, sidecar |
| `ObservationChannel` | `ebpf_tap`, `wal_digest`, `idp_log` | chain events (for v0.1 targets) |
| `Clock` | system clock + `(timestamp, height=txid)` | — |
| `Domain` | `tenant_id` + `app_id` in the `Permit` signature | `chain_id` for on-chain |
| `Prover` | Verus (Rust) | Dafny, Certora |

---

## 3. `flowguard.yml` — the extension for legacy (normative)

The same rules: unknown fields in `policy`/`closure`/`enforcement`/`evidence` → **MUST** reject.

```yaml
schema_version: "1.0"
flow:
  id: "payments.transfer"
  domain: legacy                     # MUST
  assets:
    - kind: money
      id: "ledger.balance"
      criticality: high

subject:
  kind: legacy.flow                  # MUST
  repo: "github.com/org/payments"    # MUST
  commit: "9f3a1c"                   # MUST for the signature
  build_cmd: "make build"            # MUST — the contract of validatability, §14
  run_cmd: "docker compose -f ci.yml up -d"   # MUST
  test_cmd: "make test"              # MUST or health_oracle
  health_oracle: null
  runtime: "node@22"                 # MUST
  db:
    engine: postgres                 # MUST
    migrations: "db/migrations"      # MUST
    write_principals: [svc_balance, job_settlement]   # MUST, registry §8.5

policy:
  id: "authz-v1"
  version: 3
  fail_closed: true
  rules_file: "policy/rules.yaml"    # MUST for legacy
  invariants:                        # MUST, ≥2 from §5.2
    - id: "I2"
    - id: "I4"

closure:
  elements:                          # MUST, from the 12 elements of §8
    - sync_entrypoints
    - batch_jobs
    - admin_console
    - backups
    - write_paths
    - db_principals
    - queues_retries
    - policy_config
    - cicd_secrets
    - observability
    - inbound_settlement
    - mediator_self
  excluded:
    - path: "ci_supply_chain"
      reason: "supply-chain integrity is not proved; CI holds no data credentials"
  unknown_behavior: INCONCLUSIVE

enforcement:
  mode: in_process                   # MUST: in_process | single_writer
  mediator:
    lang: rust                       # MUST: rust | java | ts | py
    artifact_hash: "0x…"             # MUST
    placement: library               # MUST: library | sidecar | gateway | service
  permit:
    algorithm: Ed25519               # DEFAULT
    max_ttl_seconds: 300             # DEFAULT 300 (shorter than on-chain)
    version_bound: true              # MUST, false is forbidden
    domain_bound: true               # MUST, false is forbidden
  database_trigger:                  # MUST when placement=library
    enabled: true                    # MUST, false is forbidden for the guarantee
    verify_signature: true           # MUST

evidence:
  observation_channels: [ebpf_tap, wal_digest, idp_log]   # MUST, ≥2; 3 = full witness
  human_review_coverage: 1.0         # MUST, printed in the report
  reorg_behavior: null               # not applicable
  prover_backend: [verus]

attestation:
  expires_after_seconds: 7776000     # DEFAULT 90 days
  signatures_required: 4
  signer_roles: [product_owner, infra_owner, security_lead, verifier]
  reissue_within_days: 3             # MUST, the reissue rule
  bundle_format: "fg-bundle/1"

limits:
  max_compute_seconds: 7200          # DEFAULT 2 h (build + tests)
  max_vm_seconds: 14400

# FORBIDDEN:
# - database_trigger.enabled: false when placement=library
# - excluded with reason = "we ran out of time"
# - human_review_coverage < 0.25
# - write_principals that do not match the discovered ones
```

---

## 4. The legacy bundle (normative)

```
bundle/
├── manifest.json
├── flowguard.yml
├── subject.json                 # repo, commit, build_cmd, run_cmd, runtime
├── closure/
│   ├── declaration.json         # 8 act fields + 12 elements + excluded
│   ├── writers.json             # registry of writers: service, credential, resource, type
│   ├── discovered_vs_declared.json   # diff — the key file
│   └── db_principals.json       # who holds INSERT/UPDATE on the ledger
├── policy/
│   ├── rules.yaml
│   ├── rules.smt2               # SMT-LIB
│   └── counterexamples/         # sat models from Z3
├── mediator/
│   ├── source/                  # mediator code
│   ├── artifact_hash
│   └── trigger.sql              # PL/pgSQL
├── witness/
│   ├── tap.jsonl.zst            # request/response + nonce
│   ├── db_digest.json           # state before/after, hash-chain
│   ├── identity.json            # token → principal
│   └── acceptance/
│       ├── replay_test.json     # test A: forgery/replay
│       └── independence_test.json  # test B: the agent cannot disable the channel
├── oracles/
│   ├── sqli.json
│   ├── bola.json
│   └── traversal.json
├── findings/
│   ├── proven.json              # C/T/N × K, verdicts
│   └── hypotheses.json          # Lane A, a separate artefact
├── attacks/
│   └── results.json             # 7 scenarios
├── proof/
│   ├── results.json             # Verus
│   └── assumptions.json
├── replay/
│   └── manifest.json
├── verdict.json
└── signatures/
```

| File | Required fields | Signatory |
|---|---|---|
| `closure/declaration.json` | the 8 fields of §9 | product_owner, infra_owner, security_lead, verifier |
| `closure/discovered_vs_declared.json` | `discovered[]`, `declared[]`, `diff[]`, `unknown_count` | security_lead |
| `closure/db_principals.json` | `principal`, `privilege`, `resource`, `discovered_by` | infra_owner |
| `policy/counterexamples/*` | `rule_id`, `model`, `impact` | security_lead |
| `mediator/trigger.sql` | `table`, `signature_check`, `version_check` | verifier |
| `witness/acceptance/*` | `test_id`, `setup`, `expected`, `observed` | verifier |
| `findings/proven.json` | `finding_id`, `class`, `c`, `t`, `n`, `k`, `oracle_id`, `verdict` | verifier |
| `attacks/results.json` | 7 × `attack_id`, `expected`, `observed`, `replay_cmd` | security_lead + verifier |
| `verdict.json` | `status`, `reason_code`, `human_review_coverage`, `expires_at` | verifier |

**Rule:** `findings/hypotheses.json` is **never** mixed with `proven.json`. These are two files, and the client sees only `proven` in the "findings" section.

---

## 5. Verdict and invariants

### 5.1. The rule

```
PROVEN(x) ⟺ attacks_all_blocked(x) ∧ invariants_discharged(x)
           ∧ closure_complete(x) ∧ witness_intact(x)
           ∧ build_reproducible(x) ∧ policy_matches(x)
```

Four values — as in v0.1: `PROVEN` / `NOT_PROVEN` / `INCONCLUSIVE` / `INVALID`. For legacy a mandatory field is added, `human_review_coverage` — the share of findings reviewed by a human before shipment. In v0.2 it is `1.0`; dropping below `0.25` is forbidden.

### 5.2. The eight invariants of the ledger flow

A summary from the fourth round, each with its verification mechanism:

| # | Invariant | How it is verified |
|---|---|---|
| **I1** | Full mediation: every ledger mutation passes through M | reconciling the `pgaudit` delta against the log of `Allow` events |
| **I2** | Capability enforcement: a write is accepted only with a valid `Permit` | the trigger rejects a write without a signature; an attempt without one → `BLOCKED` |
| **I3** | Atomicity: the check, the `Permit`, the event and the mutation are one transaction | fault injection at every step |
| **I4** | No ambient authority: `INSERT/UPDATE` on the ledger only for M | credential scanner: the set of principals = {M} |
| **I5** | Signed deployment: M, the policy and the migrations only when the hashes match | CI gate + hash check at M start-up |
| **I6** | Fail-closed audit: the log being unavailable → `Deny` | chaos test: kill the channel, expect a refusal |
| **I7** | Version-bound: a decision is valid only for the version of the object and of the policy | concurrent test: change the object between the `Permit` and the write |
| **I8** | The restore procedure | an acceptance test of 6 steps (§11.3) |

**The key distinction that must not be blurred:** I1, I6, I8 are **not a proof but a test**. For an arbitrary system they are unprovable, yet they are checkable on every run. In the act they are marked `[MEASURED]`, not `[PROVED]`.

**And the second invariant, without which the first is useless:**

```
I1' : ∀ mutation(ledger) ⟹ ∃ Permit ∧ ∃ signed Allow event
```

`∀ Permit ⟹ P` says "the mediator does not lie". `I1'` says "nothing got past the mediator". Without the second, a typical protection remains a library that can simply not be called.

---

## 6. The legacy CLI

| Command | What it does | Codes |
|---|---|---|
| `flowguard scan` | static: writers, IaC, OpenAPI, authorisation rules | 0 |
| `flowguard scan --runtime` | microVM + eBPF + `pgaudit` → the actual registry | 0 ok · 5 `DEPLOY_FAILED` |
| `flowguard mediate init --lang rust\|java\|ts\|py` | mediator skeleton + `Permit` + `trigger.sql` | 0 |
| `flowguard mediate check` | the trigger is enabled, the `Permit` is version-bound | 0 · 1 violation |
| `flowguard check` | rules → SMT; invariants I1–I8 | 0 · 1 violation |
| `flowguard attack` | 7 scenarios (a target is required) | 0 all blocked · 1 any passed |
| `flowguard witness test` | tests A (replay/forgery) and B (independence) | 0 · 1 |
| `flowguard prove` | Verus on the mediator | 0 · 2 timeout |
| `flowguard attest` | bundle + 4 signatures | 0 |
| `flowguard verify` / `replay` | as in v0.1 | 0 / 1 / 2 / 4 / 5 |

---

## 7. The mediator and the `Permit`

### 7.1. The mediator contract

```
authorize(subject: VerifiedSubject, action: Action, resource: ResourceRef,
          store: &dyn StateProvider) -> Result<Permit, Deny>
```

Six rules that all reviewers of the fourth round converged on:

1. `subject` comes **only** from a verified token/session; the owner field from the body is ignored.
2. The owner of the resource is read from trusted storage, not from the client.
3. `deny-beats-allow`, default deny, missing data → `Deny`.
4. Binding to the resource version; the check and the change are atomic (TOCTOU is forbidden).
5. The decision is logged **before** execution; a failure of the log → `Deny`.
6. `Deny` for a non-existent object is indistinguishable from `Deny` for someone else's — otherwise the mediator itself becomes an oracle for enumeration.

### 7.2. The `Permit` — a non-transferable token

```
Permit := Ed25519 {
  subject_id, resource_id, resource_version, action,
  policy_hash, nonce, exp, domain_id
}
```

The proof reduces to a single statement: `∀ Permit ⟹ P(subject, resource, action)` `[PROVED]` (Verus).

**How non-transferability is emulated per language:**

| Stack | Mechanism | Strength |
|---|---|---|
| Rust | a private type constructor, `Permit` is not `Clone` | compiler |
| Java / TS | a private constructor + a factory in the mediator | discipline + linter |
| Python | `__slots__` + a private module | discipline + linter |
| **all** | **PL/pgSQL trigger** | **physical** |

Only the fourth row is a guarantee. The first three are noise reduction.

### 7.3. The trigger — the last line

```sql
CREATE OR REPLACE FUNCTION guard_ledger_write() RETURNS trigger AS $$
DECLARE p jsonb; sig bytea; payload bytea;
BEGIN
  p := current_setting('app.permit', true)::jsonb;
  IF p IS NULL THEN
    RAISE EXCEPTION 'deny: missing permit';
  END IF;
  payload := canonical_json(p->'payload');
  sig := decode(p->>'sig', 'base64');
  IF NOT verify_ed25519(sig, payload, current_setting('app.verifier_pubkey')) THEN
    RAISE EXCEPTION 'deny: bad signature';
  END IF;
  IF (p->'payload'->>'resource_id') <> NEW.id
     OR (p->'payload'->>'resource_version')::int <> NEW.version THEN
    RAISE EXCEPTION 'deny: stale permit';
  END IF;
  IF (p->'payload'->>'exp')::bigint < extract(epoch FROM now()) THEN
    RAISE EXCEPTION 'deny: expired';
  END IF;
  NEW.version := NEW.version + 1;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER ledger_guard BEFORE UPDATE ON ledger
  FOR EACH ROW EXECUTE FUNCTION guard_ledger_write();
```

The application must execute `SET LOCAL app.permit = '<b64>'` within the same transaction. Without this the write physically does not go through.

### 7.4. Placement: a hybrid

| What | Where | Why |
|---|---|---|
| ownership, tenant, state transition | **in-process library** | one transaction together with the operation is required (TOCTOU); a small core is cheap to prove |
| the amount limit and money | **the single service-writer** | one write path; it is closed by revoking credentials |

"Single" is **logical**, not physical. In v0.2 we take not event sourcing but **DB-level enforcement**: there may be many writers, but the trigger will not let anything be written without a `Permit`.

---

## 8. Closure Z: 12 elements

Nine mandatory ones (agreed 4/4) + three structural ones.

| # | Element | "Otherwise false" |
|---|---|---|
| 1 | Synchronous entry points: API, web, mobile, partner, webhooks | a transfer without a check of P |
| 2 | Batch / cron / ETL of money operations | a background write past M |
| 3 | The admin console, support, break-glass | a privileged bypass |
| 4 | Backup, restore, replication, failover | a rollback or duplication of the balance |
| 5 | All write points, including stored procedures and migrations | a bypass through SQL |
| 6 | The registry of DB principals with write rights | a shared account writes past M |
| 7 | Queues, retries, idempotency | a repeat without a check of state |
| 8 | Policy configuration: limits, flags, overrides | the limit changes without reissuing P |
| 9 | CI/CD, secrets, deployment of M and of the migrations | unproved code goes to production |
| **10** | **The observable layer** (tap, DB digest, IdP, M events) | **a bypass cannot be told apart from a failure** |
| **11** | **External credits and the provider's reconciliation** | incoming money goes past M |
| **12** | **M itself, with a signed policy version** | substituting M outside Z makes the statement false |

### 8.1. The seven bypass paths and the decisions

| Path | Decision | Why |
|---|---|---|
| Batch / cron / ETL | mediate | it writes the balance → it is obliged to go as a client of M |
| Admin console / support | mediate + dual control | adjustments go through M with a subject class |
| Backup / restore | **forbid a direct restore**; only a signed snapshot + post-reconciliation + reissue of the act | the most dangerous operation: the return of an old state with balances |
| Partner / mobile API | mediate; disable old versions | a second ingress |
| Direct access to the DB | **forbid**; write credentials only held by M; break-glass with logging | it kills the closure |
| Logs / analytics | **forbid writing** into the money path; a copy of PII is a separate flow | otherwise the copy leaves Z |
| CI / supply chain | **forbid data credentials** + deployment hash check; supply-chain integrity is outside the guarantee | substitution of M |

**Bottom line: all seven are inside the product, zero "outside the guarantee" at the path level.** Exactly one thing remains outside the guarantee — compromise of the supply chain — and that is declared.

---

## 9. The act: 8 fields and 4 signatures

| Field | Content |
|---|---|
| `z_id`, version, hash | identification |
| Flow F | operations, data, owners, success criterion |
| Registry of paths: `resource \| path \| owner \| decision` | mediate / forbid / outside the guarantee |
| M hash: code, commit, toolchain, proof hash | what exactly was proved |
| Registry of DB principals as at the signing date | who could write past it |
| Method of building the registry | privilege audit + 14 days of `pgaudit` + 30 days of ingress logs `[HYPOTHESIS]` |
| The "outside the guarantee" list with a reason for each row | negative scope |
| Results of the 7 attacks with the date and the version of M | confirmation of the closure |

**Four signatures, each for one statement:**

| Signatory | For what |
|---|---|
| The client's product owner | completeness of the registry of **product** entry points |
| **The client's infra owner** | completeness of the **infrastructure** paths: batch, DB, CI, backup |
| The client's security lead | the registry of credentials and DB principals |
| Our lead verifier | the M hashes, the proof, the attack run |

Two owners at the client, not one, is the direct answer to "we forgot the night job".

**Contractual limitation:** the guarantee applies only to the paths in the act of version N. A new path is outside the guarantee until a reissue, **mandatory within 3 business days**. During the window the state is `DEGRADED`: new paths are `deny by default`, money paths a full deny.

---

## 10. Witness: three channels, two tests

### 10.1. Channels

| Channel | What it records | What it does not prove | Days `[HYPOTHESIS]` |
|---|---|---|---|
| **eBPF tap** on the host | the actual requests/responses, nonce, session identifiers | it does not prove who owns the object | 4.5 |
| **DB digest** (`pgaudit`/WAL) | the actual reads and writes, with the role | it does not prove that the response contained exactly this data | 3.5 |
| **Identity** (IdP) | token → principal → roles | it does not prove the absence of an error in granting rights | 3 |
| bundle assembly | one witness per E2E run | — | 1 |
| **Total** | | | **12** (wall-clock 5 days when run in parallel) |

**The residual boundary that must not be hidden:** the witness does not protect if the bench itself or the IdP is compromised. That goes into the negative scope.

### 10.2. Two acceptance tests (not one)

**Test A — integrity of the evidence.** The agent presents an old piece of evidence with a new nonce, substitutes the object, writes the nonce into its own log → `verify` returns `INVALID`. Failure: any forged/replayed witness obtained `PROVEN`.

**Test B — independence of the observer.** An agent with root inside the VM tries to disable/substitute the channel → the channel lives on the host, the change is recorded as an incident, the run → `INVALID`. Failure: the agent disabled the witness and still obtained `PROVEN`.

**A correction that must not be lost:** the nonce catches a replay but **does not prove independence**. That is why there are two tests.

---

## 11. Oracles, findings, attacks

### 11.1. Three classes and their predicates

| Class | Oracle predicate | What we lose |
|---|---|---|
| **SQLi** | the canary string in the DB digest changed as a result of the injection | blind/time-based, non-standard DBMS |
| **BOLA / IDOR** | subject A read/changed an object owned by B | complex RBAC/ABAC and multi-tenant policies |
| **Path traversal** | access to the marker file outside the permitted root | LFI/RFI, non-standard sinks |

**The classes we do not sell publicly in v0.2:** business logic without a deterministic oracle — Lane A only, free of charge, without promises. The public list of refusals is part of the product, not the fine print.

### 11.2. C/T/N and the adaptive K

```
PROVEN(finding) ⟺ C=false ∧ T=true ∧ N=false, on K fresh VMs
K: 3 by default → escalation to 10 only on ambiguity
```

`K` is printed in the bundle. A fixed `K=10 × 3 branches × N restarts` is the main source of the cost explosion `[HYPOTHESIS]`.

The verdict aggregator: three isolated judgements (one per control) → a dumb aggregator applies `!C ∧ T ∧ !N`. The oracle **never** issues the final `PROVEN` — only `PROVEN_CANDIDATE` for a single control.

### 11.3. The seven attacks

| # | Attack | Expectation | Failure |
|---|---|---|---|
| A1 | a direct write to the ledger under a service/admin credential | an exception from the trigger | a delta without an `Allow` event |
| A2 | a batch/refund job above the limit | refusal/limit | a write without M |
| A3 | restore of an old backup and replay | the hash-chain check fails | the restored state allows a repeated spend |
| A4 | an old version of the partner/mobile API | disabled | a transfer without M |
| A5 | a PR/deployment that changes the limit or bypasses M | CI gate + hash | a deployment with an unsigned hash |
| A6 | escalation through the admin console/support | dual control | a change without M |
| A7 | drain through a queue/retry (repeating the operation) | idempotency | a repeated debit |

### 11.4. The restore procedure (6 steps, acceptance test I8)

1. freeze of money mutations;
2. a signed snapshot with the state hash;
3. a check that the restore does not roll back external obligations already fulfilled;
4. restoration only from the signed snapshot;
5. post-restore reconciliation;
6. a mandatory reissue of act Z.

### 11.5. Break-glass

It cannot be mediated by definition — it is needed when the mediator is broken.

- a hardware key (HSM/YubiKey) held by the client's CISO, **not in the system**;
- the DBA signs the raw SQL with this key; the DB accepts it but sets `is_emergency = true`;
- the witness raises an alert immediately;
- **the guarantee is suspended automatically** until reconciliation and the signing of the incident act.

---

## 12. Policies and their cost

| Policy | SMT | Harness | Days `[HYPOTHESIS]` |
|---|---|---|---|
| Tenant isolation | yes | yes | 6 |
| Object ownership (BOLA) | yes | yes | 6 |
| Amount / rate limit (with overflow) | yes | yes | 8 |
| PII class × role | partially | yes | 10 |
| Permitted state transition | yes | yes | 5 |
| **All five** | | | **35 (maximum)** |
| **Those needed for v0.2 (ownership + limit + tenant)** | | | **20** |

---

## 13. The contract of validatability and refusal

### 13.1. What the client must have

1. A reproducible build.
2. Lock files and pinned versions.
3. A test command **or** a health oracle.
4. An isolated environment without secrets.
5. A record of the runtime version and of the configuration.

If even one is missing → Lane A only (hypotheses) or a refusal.

### 13.2. Five cases that break automation

| Case | Detector | Decision |
|---|---|---|
| Monorepo | >1 deployable manifest, a shared CI | manual mode, the client names the target service |
| Polyglot | >1 language with executable code on the flow | refusal for languages outside the set |
| No IaC | no Terraform/Helm/compose | manual mode; the guarantee is limited to the code |
| No tests | coverage 0 / no runner | a surcharge for acceptance tests, or a refusal |
| Generated code >30% LOC | codegen markers | we analyse the generator; no source → refusal |

---

## 14. Determinism and tool security

| Requirement | Measure |
|---|---|
| One input → one output | JCS, SHA-256, sorting, no time in the hash |
| Pinning | image digest, toolchain versions, `seed`, recorded network responses |
| No network during `verify` | `verify` makes no requests at all |
| Release gate | `attest` + `replay` produce a byte-for-byte identical bundle |
| Prompt injection from the target | target content is a tool-result only, `taint` tracking; in v0.2 the verdict is deterministic |
| Substitution of artefacts | a signature over the digest of the whole bundle + Rekor |
| Code leakage | the bundle stores hashes, not sources |

---

## 15. v0.2 acceptance criteria

1. `scan --runtime` on the reference application yields a registry of writers that matches the static one **and** `discovered_vs_declared`.
2. `db_principals` contains **exactly one** role with `INSERT/UPDATE` on the ledger after the migration.
3. A write attempt without a `Permit` raises a trigger exception, not a write.
4. `attack A1` (a direct write) — `BLOCKED`; with the trigger disabled — `PASSED` (a check that the test is not tautological).
5. `witness test` A and B — both green.
6. `C/T/N × K=3` on the reference vulnerability yields `PROVEN`; on the fixed one — `NOT_PROVEN`.
7. `consistent`: `findings/proven.json` and `findings/hypotheses.json` do not intersect.
8. `verify` on a bundle with a modified `manifest.sha256` → 4 (`INVALID`).
9. `replay` reproduces the bundle on a clean machine byte for byte.
10. A change of the boundary (a new writer) moves the state to `DEGRADED` and blocks `PROVEN`.

---

## 16. Legacy roadmap

| Version | Timeline `[HYPOTHESIS]` | Content |
|---|---|---|
| v0.2 | 8 weeks after v0.1 | microVM + eBPF + witness, mediator + trigger, 3 classes, 7 attacks, R0–R2 |
| v0.3 | +8 weeks | Verus proof of the mediator, R3, 5 policies |
| v0.4 | +6 weeks | R4–R5, PII and the state machine, a report-act with 4 signatures |
| v0.5 | +8 weeks | re-attestation with a single command, 15 minutes |

---

## 17. Known weaknesses of legacy

| # | Weakness | Mechanism | Horizon | Early sign |
|---|---|---|---|---|
| **L1** | Incompleteness of the registry of writers | an off-chain script, an operator's manual cron, an external service with a shared credential | the first 3–10 targets | an incident with a path outside `Z` |
| **L2** | Drift after a hotfix | a new endpoint/role outside the reissue window | 30–90 days | `code_hash` diverges, a path outside `declaration.json` |
| **L3** | Witness noise | an unstable tap, loss of `pgaudit` | the pilot | a rise in `INCONCLUSIVE` without violations |
| **L4** | The mediator is not always called | a developer bypasses the library; the trigger saves only the ledger | always | `A1` passes in the test with the trigger disabled |
| **L5** | The cost of review | 100% human review at 3–4 findings = $500–1000/finding | immediately | margin < 40% |
| **L6** | Reproducibility of deployment | `DEPLOY_FAILED` on monoliths | the pilot | >30% of targets do not come up |

**L1 is not cured completely.** What cures it is the rule `unknown ⇒ INCONCLUSIVE`, the public list of "what the analyser does not see", and the fact that the infrastructure owner signs, not only the product owner.

---

## Appendix A. Legacy glossary

| Term | Meaning |
|---|---|
| `writer` | a process/role able to change a protected resource |
| `Permit` | a signed token of authority bound to the object, the version, the policy and the domain |
| `DEGRADED` | the state between a change of the boundary and the reissue of the act: new paths are denied |
| `Lane A` | the hypothesis track: not billed, not mixed with findings |
| `human_review_coverage` | the share of findings reviewed by a human before shipment |
| `break-glass` | emergency access outside the mediator; it suspends the guarantee |

## Appendix B. Reviewer's checklist for a legacy bundle

1. Is `discovered_vs_declared.diff` empty?
2. `db_principals`: exactly one role with write on the ledger?
3. Is the trigger enabled, `verify_signature: true`?
4. Are both witness tests (A and B) green?
5. Are all 7 attacks `BLOCKED`?
6. Do `proven.json` and `hypotheses.json` not intersect?
7. `human_review_coverage` = 1.0 (or ≥0.25 with a justification)?
8. `assumptions.json`: does every assumption have `what_breaks_if_false`?
9. 4 signatures from 4 different keys, `infra_owner` separate from `product_owner`?
10. Is `expires_at` in the future, is `DEGRADED` not active?
