---
id: E-M28
hypothesis: H-M28
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T01:12:00+03:00"
finished: "2026-10-28T01:26:00+03:00"
environment: "Windows, CPython 3.13.11, cryptography 50.0.2"
command: "python lab/e-m28-run.py"
threshold: "Pre-registered: (a) an unknown signature role is refused, (b) a risk acceptance without an expiry or without a scope bound to the bundle address is refused, (c) the same key signing both the consistency verdict and the risk acceptance is refused, (d) a liability agreement declared as a role is refused because a JSON field cannot create a contract, (e) a correct split is accepted."
result: "5 of 5. R1 SIGNATURE_ROLE_UNKNOWN, R2 RISK_ACCEPTANCE_INCOMPLETE, R3 SEPARATION_OF_DUTIES_VIOLATED, R4 LIABILITY_NOT_A_ROLE, R5 accepted. One defect found in my own check: holder identity was compared by file name, so the same key under two names passed the separation test - the same 'name is not an identity' error as E-M25, one layer up."
verdict: supports
---

# E-M28 — three acts, three signatures, and who may hold which

## What was wrong

The bundle carried one role field that said whatever it liked. Round-8 review, all three models: a signature under a
verification result, an acceptance of residual risk and a contractual liability are different acts with different
subjects, and one field cannot carry all three. A single field is worse than none, because it implies the three are
interchangeable.

## What is enforced

`policies/signature-roles.json` defines four roles, each with required fields:

| role | asserts | requires |
|---|---|---|
| `analysis_provenance` | produced by this agent from these inputs | issuer |
| `process_attestation` | produced by this harness, unmodified | issuer |
| `consistency_verdict` | the claim does not exceed the evidence | issuer, policy_digest |
| `risk_acceptance` | a named party accepts residual risk for a period | issuer, accepted_scope (= bundle address), residual_risk, valid_until, statement |

And two prohibitions:

- **`liability_agreement` is not a role.** A contract cannot be created by a JSON field, so declaring it is refused
  rather than accepted as paperwork.
- **Separation of duties.** `consistency_verdict` and `risk_acceptance` may not be held by the same key: the party
  that checks the claim cannot also accept what the check could not establish.

## Run

```
R1 unknown role                    PASS  SIGNATURE_ROLE_UNKNOWN
R2 acceptance without expiry       PASS  RISK_ACCEPTANCE_INCOMPLETE
R3 same key signs both             PASS  SEPARATION_OF_DUTIES_VIOLATED
R4 liability as a role             PASS  LIABILITY_NOT_A_ROLE
R5 correct split                   PASS  SIGNED_AND_CONSISTENT
cases passed: 5/5
```

## The defect inside the check

The first version compared holder identity by **file name**, so a key copied under another name passed the
separation test. That is the same error as `E-M25` one layer up: a name is not an identity. Holders are now compared
by public key bytes.

## Sample bundle, rebuilt

`fixtures/sample-bundle` now carries two signatures — `demo` as `consistency_verdict` with a policy digest, `owner`
as `risk_acceptance` with a scope bound to the bundle address, residual risk codes and an expiry. It verifies as
`SIGNED_AND_CONSISTENT` with both keys trusted, and the address changed accordingly.

## What this does not do

- **It does not make the acceptance true.** A named party and a date are structure; whether that party had the
  authority, the information and the standing to accept is outside the file, and `NC-08` still says so.
- **It does not create liability.** The bundle can record that a contract exists; it cannot be one.
- **It cannot detect one human holding two keys.** Separation of duties is checked at the key level; two keys held by
  one person pass.
