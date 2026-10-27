# ELIMINATIONS — what has been ruled out, and what would revive it

Negative results are published on equal terms with positive ones. This file is the registry of
hypotheses that were eliminated across five review rounds and the reasoning that killed them. Each
entry records **what would revive it** — because an elimination is a claim about the state of evidence,
not a permanent truth.

Borrowed from [Project Morphogenesis](https://github.com/mak777uh/-) (`docs/eliminations.md`), where the
list of ruled-out ideas is a first-class document with artifact references and revival conditions.

Reading rule: an eliminated item may still be argued in a review, but the argument must address the
revival condition directly. Re-asserting the original position without new evidence is not a review
round, it is a repeat.

---

## Product premises

### X-01 — "We can prove the system is safe" — eliminated

Four review rounds converged: the provable object is a **mediator plus a closure**, never a system.
`PROVEN` about a whole application was abandoned in favour of `PROVEN(R)` relative to a detector with
measured recall, plus `ENFORCED_TESTED` for legacy.

**Revived if:** a system exists whose complete set of state-changing paths can be enumerated from an
authoritative source (grants and triggers in a database, not an analysis of code) *and* the enumeration
is confirmed complete against an independent manual pass with zero misses.

### X-02 — "An attestation is valuable because it is checkable" — eliminated

Checkability without a consumer is a property nobody buys. Stated bluntly by one reviewer: if no external
party changes a decision because the bundle exists, then offline verifiability solves a non-existent
problem, and pricing by value at risk has no basis. Our own escrow does not count as a consumer — that is
circular.

**Revived if:** E-M8 finds at least one consumer (insurer, auditor, bank, counterparty) who commits in
writing to changing a decision — premium, admission, limit or payout — on the strength of a bundle.

### X-03 — "Signature proves the claim" — eliminated

A signature proves integrity of what was signed, not the truth of the statement inside it, and not the
binding between bundle, real target and executed version. Treated as mechanism **T1** and mitigated, not
closed: published toolchain hashes, an independent verification replica, and a substitution test (E-M9).

**Revived if:** the binding is instrument-checked end-to-end for code, build, configuration and identity,
so that a substituted target is rejected with valid signatures intact.

---

## Technical positions

### X-04 — "`unknown_paths = ∅` means there is no bypass" — eliminated (5 of 5 reviewers)

It means only that the detector's own model contains no unknown path. A blind spot yields `PROVEN`
rather than `INCONCLUSIVE` — the rule worked backwards in the most dangerous case. Replaced by the
relative verdict `PROVEN(R)`, a mandatory coverage scalar, and a measured recall.

**Revived if:** a detector achieves measured recall 1.0 on a held-out blind corpus, twice, on an
unchanged tree.

### X-05 — "The database trigger is a physical guarantee" — eliminated (4 of 5)

The trigger is configuration of the same DBMS, not an independent boundary against an administrator. It
covered only `UPDATE`, and it is bypassed by `INSERT`/`DELETE`/`TRUNCATE`, `DISABLE TRIGGER`, DDL,
`session_replication_role`, logical replication, restore and superuser sessions. The word "physical" was
withdrawn; the guarantee is now conditioned on a declared privilege model with the DBA outside the threat
model.

**Revived if:** the trigger layer is shown to hold with the DBA inside the threat model — e.g. an
externally anchored witness plus an append-only log outside the customer's infrastructure.

### X-06 — "Reconciling `pgaudit` with `Allow` events proves complete mediation" — eliminated (4 of 5)

A bypass writer can write its own `Allow` event. Fixed by binding the event cryptographically to the
`Permit` (nonce, resource version, signature) and reconciling inside one transaction.

**Revived if:** an event-not-bound-to-permit case is found that nevertheless passes reconciliation.

### X-07 — "K = 3 runs are enough" — eliminated (4 of 5)

Three runs give no statistical guarantee against a flaky effect. K ≥ 5 by default, K = 10 when the flake
rate is unknown, escalation to `INCONCLUSIVE` on any discrepancy, and a published false-positive ceiling
per oracle.

**Revived if:** measured flake rate per oracle class is low enough that K = 3 achieves a stated
false-positive bound — the bound must be published, not assumed.

### X-08 — "INV-1 holds for tokens" — eliminated (4 of 5)

False for fee-on-transfer and rebasing tokens, and for tokens with pause, blacklist or upgrade authority —
which are themselves paths outside the closure. Replaced by a behavioural token preflight; non-standard
tokens return `INCONCLUSIVE` unless wrapped.

**Revived if:** a per-token-class model with measured invariants exists for those classes.

### X-09 — "One L2 finality rule covers all rollups" — eliminated (2 of 5)

Each rollup has its own finality mechanism and configuration. Replaced by per-chain adapters; block count
as a sole criterion is forbidden.

**Revived if:** a single predicate is shown to be sound and complete across at least three L2 families
with published proof.

---

## Economics

### X-10 — "Price per finding" — eliminated (first principles)

It rewards inflating findings and destroys the trust the product sells. Price is per scope, per change, or
per subscription — never per finding.

**Revived if:** never. This one is a values constraint, not an empirical claim.

### X-11 — "The cost of a validated finding is a measurable quantity" — eliminated

Spread across five independent estimates was 65×, because findings are lumpy and cost is nearly fixed per
engagement. Replaced by three metrics: engagement cost, assessor minutes per finding, findings per
engagement.

**Revived if:** a definition of "finding" emerges that is uniform enough across classes for cost to be
meaningfully averaged.

### X-12 — "15 minutes per review is a planning number" — eliminated (3 of 5)

Consensus estimate was 20–45 minutes, median about 35–38. Fifteen minutes remains a target, achievable
only marginally, for a repeat finding of a known class on an already onboarded target. Planning uses
35–40, and SKU-1 carries review cost as pass-through until E-M2 closes.

**Revived if:** E-M2 shows median ≤ 20 minutes on first findings with three independent reviewers.

### X-13 — "Margin above 45% on services is compatible with the price doctrine" — eliminated by the doctrine itself

The doctrine caps service margin and shares automation savings 50/50 with the customer. A plan that
requires margin expansion contradicts the stated doctrine; one of them has to go, and the doctrine wins.

**Revived if:** never as a plan. This is a constraint, and a plan conflicting with it is defective.

---

## Development method

### X-14 — "AI agents will write the code, so the code will be fast" — eliminated

Agents accelerate writing by a factor; verification and acceptance barely compress because a human and
instruments do them. Planning must use the right-hand column: 2–3 weeks writing plus 2–3 weeks
verification for the on-chain slice.

**Revived if:** measured acceptance throughput rises without dropping the gates — then the ratio changes,
not the principle.

### X-15 — "A passing test suite means the implementation matches the spec" — eliminated

An agent can write a test that passes without testing, or implement a plausible variant of the spec.
Mitigated by: tests written by a different agent that never sees the implementation; reserved paths
(`tests/`, `spec/`, `lab/`) read-only for the implementing agent; any `skip`/`xfail`/weakened assert in a
diff is an automatic reject.

**Revived if:** an instrument exists that derives tests mechanically from the spec and cannot be influenced
by the implementer.

---

## Round 6 additions

### X-16 — "The browser verifier is where the value is" — eliminated

Five of five reviewers rejected the browser as the first artifact. The substantive content of a verifier is not
hash comparison — `sha256sum` does that — it is **recomputing the denominator**: closure, coverage, excluded,
unknown, and refusing a bundle whose printed numbers do not derive from its objects. That is a command-line
program, and it is smaller than the front end.

The browser version adds isolated execution and convenience. Both are real; neither is proof.

**Revived if:** a consumer exists whose workflow requires verification inside a browser session and who will not
run a CLI — a concrete person, not a persona.

### X-17 — "Eight claim columns are sufficient" — eliminated

Five of five said the same thing, and one named the exact hole: a claim passes all eight columns when the
*instrument* is wrong or the corpus was chosen after seeing results. `snapshot` documents where a number was
taken; it cannot detect that the instrument lied.

**Revived if:** an instrument-assessment entity exists with a reference corpus, known positive and negative cases,
published false-positive and false-negative rates, and an independent re-measurement — and a linter can require
it.

Until then the cheap version applies: **a negative control per guard**, a planted defect that the guard must
catch, running in CI. Our own checker was wrong three times before it had one.

### X-18 — "The substitution test is one test" — eliminated

As first specified it was near-tautological: replace the code, the digest fails, the verifier rejects — that
tests our own hash comparison. What cannot be caught by a hash is a correctly signed bundle describing a
different target than the one presented.

Two classes are now pre-registered in `E-M9`: tampering after signing (D-1) and falsely attested pairs (D-2).

**Revived if:** never as a single class. Any future substitution test must name which of the two it addresses.

### X-19 — "Logs are evidence" — eliminated, narrowed

A log is read by people; evidence is a log that something replays and that can fail to match. An append-only
journal nobody replays is prose with timestamps.

**Revived as:** the narrow rule now in force — every number in `docs/METRICS.md` carries the command that
produced it and the sha256 of the log it came from. Adopted from the sibling repository, where 121 append-only log
files are counted, including a counter for duplicated hashes.

### X-20 — "Evidence-based testing means more tests" — eliminated

It means **measured** tests: a corpus with declared defect classes, a detection rate per class, and a
false-rejection rate on valid inputs. A larger suite with no per-class numbers is the coverage theatre that
`E-M10` exists to prevent.

**Revived if:** never as "more tests". Any test artifact added here states which class it measures and against
what corpus.
