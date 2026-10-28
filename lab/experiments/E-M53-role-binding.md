---
id: E-M53
hypothesis: H-M53
status: completed
base_commit: "20dde31"
started: "2026-10-28T13:45:00+03:00"
finished: "2026-10-28T14:20:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m53-run.py"
threshold: "Pre-registered: create a bundle carrying a risk acceptance, verify it, then edit one term of that acceptance and verify again. The first must be SIGNED_AND_CONSISTENT with binding \"role\"; the second must fail. If the second passes, the binding is decorative and ADR-0015 is false."
result: "PASS. Genuine acceptance verifies with signature_binding {demo: role, owner: role}; after changing the statement to 'this acceptance is withdrawn' the bundle is INVALID. The sample bundle was rebuilt with role-bound signatures in the same run (new address 27a4c397…, because the role digests now enter the signature and the old keys were ephemeral), and an acceptance whose signature covers only the address is now refused. Three defects were mine and were found by the test rather than by reading: signing before the role file existed, building the document twice so creation and verification disagreed on two bytes, and a harness case (E-M28 R5) that had been signing the address alone and calling that a correct split."
verdict: supports
---

# E-M53 — the binding, demonstrated by breaking it

## The rule, now in force

```
signature message = address || "\n" || "role:" || sha256( canonical( role without accepted_scope ) )
```

One function implements it (`role_message(address, role_doc)`), and creation and verification both pass a
parsed dictionary, so the two sides cannot canonicalise differently. `accepted_scope` is excluded because it
must equal the address; everything else is inside the digest.

## The test that makes it true

`lab/e-m53-run.py` builds a bundle with an acceptance by a second key, verifies it, then rewrites one field of
that acceptance — the same words the previous attacker used, "this acceptance is withdrawn":

```
genuine acceptance verifies:    True  (binding {'owner': 'role', 'verifier': 'role'})
tampered acceptance is refused: True  (INVALID)
```

Without the second line the first is decoration. This is the test `E-M52` said was missing.

## Three of my own defects, found by the test and not by reading

1. `create` signed before the role file existed, so the message covered the address alone and verification
   quietly fell back — the tampered acceptance passed. Fixed by building the document once.
2. The signing document was built twice, in two places, and canonicalised differently; creation and
   verification disagreed on two bytes and even the genuine bundle failed.
3. `E-M28` case R5 signed a `risk_acceptance` over the address alone and called the result "a correct split
   accepted" — the harness had been testing the weaker binding as if it were the strong one. It now signs the
   role-bound message.

## What changed for artifacts

The sample bundle was rebuilt with role-bound signatures: new address `27a4c397…`. The old keys were ephemeral,
so new keys were generated; the payload objects and the claim are unchanged. Two consequences are stated rather
than hidden:

- `M7` was performed on the previous artifact (`E-M39`, address `e3699948…`). The format changed after that
  rebuild, so the independent reproduction certifies the earlier envelope, not this one.
- An acceptance whose signature covers only the address is now **refused**; other roles keep the weaker binding
  and the verdict prints `signature_binding` so nobody has to guess which one was used.

## What this does NOT establish

- That the accepting party is who it claims. A key is a key (`NC-08`).
- That the risk is acceptable. The artifact records who accepted which words about which address.
- That a rebuilder can reproduce the envelope: the format description was updated, but `M7` has not been re-run
  against this address.
