---
id: E-M56
hypothesis: H-M56
status: completed
base_commit: "4370b04"
started: "2026-10-28T15:30:00+03:00"
finished: "2026-10-28T16:05:00+03:00"
environment: "Windows, CPython 3.13.11; fourth independent agent, asked to WRITE A VERIFIER, not to reproduce values"
command: "spawn an agent with the bundle and its description; it must implement a standalone verifier and catch five tamperings it makes itself"
threshold: "Pre-registered: a stranger must be able to write a conforming verifier from the page alone - passing the valid bundle and catching an object edit, a role-term edit, an accepted_scope rewrite, a signature over the wrong message, and a version change - and must report every place where it had to guess. More than two guesses means the page is not yet a specification."
result: "PASS with four defects found. The verifier passed the valid bundle, caught all five required tamperings AND twelve more (17 cases, 0 mismatches), exercising all eight refusal codes. It did so in a language-independent stdlib-only implementation with its own Ed25519, first run, no second example artifact. Four defects remained in the page: (1) a LITERALLY FALSE equality - it said claim.target_lock equals the inventory's target_lock, but the claim carries an object and the inventory a bare string, so a literal comparison rejects the valid bundle; (2) three checks the page mandates had no refusal code, so the implementer had to reuse codes and say so; (3) nothing said a bundle must carry at least one signature, so an empty signatures/ directory could yield a false success; (4) an address-only signature cannot assert a role at all, which the page implied it could. All four fixed."
verdict: supports
---

# E-M56 — the page that mandated a false equality

## The test that mattered

Three rebuilders had reproduced values. This one was asked to **build a tool**: implement a verifier from the page,
then break the artifact five ways and catch each break.

| case | caught by the stranger's verifier | code |
|---|---|---|
| one object's bytes changed, same length | yes | REPORT_BUNDLE_INCONSISTENT |
| a role's `statement` edited | yes | MISSING_EVIDENCE |
| `accepted_scope` rewritten to zeros | yes | RISK_ACCEPTANCE_INCOMPLETE |
| a **valid** signature over the **wrong** message | yes | MISSING_EVIDENCE |
| `bundle_version` changed | yes | REPORT_BUNDLE_INCONSISTENT |

Seventeen cases, zero mismatches, all eight codes of the table exercised — from a page and one artifact, no source, no
second example. The fourth case is the one that proves the message rule is real: the implementer generated a keypair,
signed a message that hashed the whole role document, shipped the matching public key, and confirmed with an independent
crypto library that it verifies over the wrong message and fails over the prescribed one.

## The defect that mattered

> `bundle.claim.target_lock` equals the inventory's `target_lock`

False on the artifact the page calls valid: the claim carries `{"commit": "…"}` and the inventory carries the bare
string. A literal comparison **rejects the correct bundle**. The implementer guessed the intent, wrote down that it
guessed, and passed.

That is the most dangerous class found so far: not a missing rule, not withheld vocabulary, but a rule that is
affirmatively wrong and looks authoritative. A reader who trusts it concludes the artifact is broken.

## The other three

**Three mandated checks carried no code** — target-lock agreement, `issuer` versus file stem, `residual_risk` versus
`not_claimed` — while the page forbade inventing codes. Now each has one.

**A bundle with no signatures at all** could yield a false success, because nothing required any. Now: at least one
signature, and a claim above `CONSISTENT_DECLARED` needs a `consistency_verdict` holder.

**An address-only signature cannot assert a role at all**, because role identity lives in the `.role` file. The page
implied it could be the weaker binding of a role; it cannot be a role at all, only provenance.

## The standing judgement

A stranger can now implement a conforming verifier from the page, catch tampering, and knows which refusals to emit —
including that multiple failures produce multiple refusals rather than the first one. What remains outside the artifact
is what `NC-01`…`NC-11` assert, and the page says so.
