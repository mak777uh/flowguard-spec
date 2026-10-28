# FlowGuard — product specification and external review rounds

> Russian mirror: [README.ru.md](README.ru.md). This file is canonical; where they disagree, this one wins.

**What this is.** Documents for one product: a service that does not claim "the system is secure", but
proves that **inside a declared closure no value can move past the single control point** — and issues a
statement that can be verified without trusting its issuer.

**What it is not.** A safety promise. Outside the declared closure the guarantee does not apply, and that
is written into the artifact itself, not into a footnote.

## Open-by-default policy

Everything is published openly by default — including economics, margin caps and internal schedule
estimates — because trust is verified, not declared. There is exactly one exception: **secrets**.

That is not a slogan but a mechanism: the repository carries a guard that blocks publication when it finds
tokens, keys, private keys or local paths — in files **and across the whole history**.

```bash
bash lab/check-secrets.sh    # tokens, keys, local paths: files + history
python lab/check-links.py    # every relative link between documents resolves
python lab/check-claims.py   # every claim typed; every cited artifact traceable
```

Both run automatically on every push and pull request (`.github/workflows/guards.yml`). If someone ever
commits a token, CI goes red instead of the reputation.

## Read first

| File | Role |
|---|---|
| [docs/FLOWGUARD-MASTER-v2.md](docs/FLOWGUARD-MASTER-v2.md) | **master document**: paste it whole into a model for external review |
| [docs/SPEC-v0.1.md](docs/SPEC-v0.1.md) (first ring) | on-chain detail: escrow, invariants, attacks, acceptance |
| [docs/SPEC-v0.2-LEGACY.md](docs/SPEC-v0.2-LEGACY.md) (superseded) | legacy detail: closure, mediator, trigger, witness, oracles |
| [docs/90-DEV-AND-NEXT-ROUND.md](docs/90-DEV-AND-NEXT-ROUND.md) (superseded) | development method, sober assessment, next round's questions |
| [docs/CLAIMS.md](docs/CLAIMS.md) | claim registry: evidence type and the strongest permitted wording |
| [docs/eliminations.md](docs/eliminations.md) | what five rounds ruled out, and what would revive it |
| [docs/M8-CONSUMER.md](docs/M8-CONSUMER.md) | the five-line form the product rests on: fillable in one conversation, worth zero until filled |
| [docs/READINESS.md](docs/READINESS.md) | **what works, who can use it, and the gate for showing it to others — computed, not asserted** |
| [docs/STATUS-v0.md](docs/STATUS-v0.md) | what exists, what does not, and what this repository does not claim |
| [docs/METRICS.md](docs/METRICS.md) | every number with its command and log digest — 59 rows, every one with the command that produced it |
| [docs/NOT-CLAIMED.md](docs/NOT-CLAIMED.md) | the vocabulary of what an attestation refuses to assert, with required codes per level |
| [docs/33-EBT-AND-LDD.md](docs/33-EBT-AND-LDD.md) | what we take from evidence-based testing and log-driven development, and what we refuse |
| [docs/95-CLOSED-LOOP.md](docs/95-CLOSED-LOOP.md) | the loop: product is the showcase, the approach is the factory |

## Repository map

| Group | Files |
|---|---|
| Spec | [master v2](docs/FLOWGUARD-MASTER-v2.md) · [v1 (superseded)](docs/FLOWGUARD-MASTER.md) · [v0.1](docs/SPEC-v0.1.md) (first ring) · [v0.2](docs/SPEC-v0.2-LEGACY.md) (superseded) · [claim registry](docs/SPEC-CRITIQUE.md) |
| Product and boundaries | [protected flow](docs/40-FLOW-GUARANTEE.md) · [variants](docs/01-VARIANTS.md) · [remediation ladder](docs/02-GRID.md) |
| Crypto | [in scope from day one](docs/61-CRYPTO-IN-SCOPE.md) · [crypto and auto-payout](docs/60-CRYPTO-AND-AUTOPAY.md) |
| Economics | [SKUs and services](docs/70-SERVICE-TIERS.md) · [pricing doctrine](docs/80-PRICING-DOCTRINE.md) |
| Decisions | lab/decisions/ — 14 ADRs, each stating its own limits |
| Provers | [Harmonic Aristotle: what it changes here](docs/24-ARISTOTLE.md) |
| Methods | [what to borrow from NVIDIA auto-ontology](docs/23-BORROWED-METHODS.md) |
| Formal | [formal-verification tooling worth adopting](docs/22-FORMAL-TOOLING.md) |
| Advisory | [five models answered the owner list; advice, not decisions](docs/ADVISOR-INPUT-2026-10-28.md) |
| Interop | [coordination channel with VecDHT](docs/interop/README.md) |
| Exchange | [review exchange protocol](interop/REVIEW-EXCHANGE.md) · [ledger](interop/reviews/LEDGER.md) |`n| Assessment | [what this repository reached, and what it did not](docs/21-FINAL-ASSESSMENT.md) |
| Audit | [whole-repository and method audit, 2026-10-28](docs/18-AUDIT-2026-10-28.md) · [how attacks are part of development](docs/19-ATTACK-PRACTICE.md) |
| Hand-off | **[DOSSIER.md](DOSSIER.md)** — one generated, self-contained file to paste into any model (Russian) |
| Validate | [how a schema owner confirms or denies a finding](docs/FOREIGN-VALIDATION.md) — the door to evidence tier 2 |
| Open | [questions for the owner](docs/QUESTIONS-FOR-OWNER.md) · [round 8 review pack](docs/16-ROUND8-QUESTIONS.md) · [round 8 disposition](docs/17-ROUND8-DISPOSITION.md) — only what cannot be decided here |
| Process | bash lab/round-check.sh · python tools/fg_audit.py · python tools/fg_readiness.py |
| Implementation | [enumerators](enumerators/grants-pg/README.md) (grant, call-graph, runtime, routes) · [verifier](tools/fg_verify.py) · [the stand](docs/50-IMPLEMENTATION-STAND.md) · [the harness](docs/51-HARNESS-BUILD.md) · [OSS product](docs/52-OSS-PRODUCT.md) |
| Development | [method and next round](docs/90-DEV-AND-NEXT-ROUND.md) (superseded) · [closed loop](docs/95-CLOSED-LOOP.md) · [hackathon plan](docs/97-HACKATHON-PLAN.md) (superseded) · [grants](docs/98-GRANTS.md) · [sources](docs/99-SOURCES.md) · [interop](docs/96-INTEROP.md) · [evals and roadmap](docs/03-EVAL-ROADMAP.md) |
| Review rounds | [synthesis 2](docs/00-SYNTHESIS.md) · [decisions](docs/20-ROUND2-DECISIONS.md) · [synthesis 3](docs/30-ROUND3-SYNTHESIS.md) · [synthesis 4](docs/31-ROUND4-SYNTHESIS.md) · [**synthesis 6 — plan change**](docs/32-ROUND6-SYNTHESIS.md) · [open questions](docs/34-OPEN-QUESTIONS.md) · [spec audit](docs/35-SPEC-AUDIT.md) · [round 7 pack](docs/15-ROUND7-QUESTIONS.md) · [**synthesis 7 — the name was wrong**](docs/36-ROUND7-SYNTHESIS.md) · [refusal codes](docs/37-REFUSAL-CODES.md) · [inventory design](docs/38-INVENTORY-DESIGN.md) |
| Question sets | [round 2](docs/10-ROUND2-QUESTIONS.md) · [3](docs/11-ROUND3-QUESTIONS.md) · [4](docs/12-ROUND4-QUESTIONS.md) · [5](docs/13-ROUND5-QUESTIONS.md) · [**6 — the method itself**](docs/14-ROUND6-QUESTIONS.md) |

## The one rule that is not up for debate

No number marked as a hypothesis enters commercial material before the corresponding measurement closes.
Evidence types and permitted wording live in [docs/CLAIMS.md](docs/CLAIMS.md): three words — `PROVEN`,
`ENFORCED_TESTED`, `guarantee` — are allowed only with evidence type `proof` or `test`.

## License

Documents — [CC BY 4.0](LICENSE). Code, when it appears, — Apache-2.0.
