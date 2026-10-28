---
id: E-M52
hypothesis: H-M52
status: completed
base_commit: "aa7b3e9"
started: "2026-10-28T13:00:00+03:00"
finished: "2026-10-28T13:35:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python tools/fg_bundle.py create ... && python tools/fg_bundle.py verify ..."
threshold: "Pre-registered: a role's terms must be covered by that party's signature, demonstrated by tampering with a signed acceptance and watching verification fail. If the demonstration does not fail for the right reason, the change is not shipped."
result: "FAILED AND REVERTED. The design is written down (ADR-0015, message = address + the role's canonical digest, with accepted_scope excluded because it must equal the address). Implementation was attempted twice and both attempts were wrong in the same way: the create path signs before the role file exists, so the message covered the address alone while verification fell back to the address-only message - and a tampered acceptance still verified green. The second attempt signed a document built inline, and verification then disagreed with creation on the two bytes, so even the genuine bundle failed. I reverted the code rather than ship a binding that cannot be demonstrated. The unsigned-role refusal from E-M51 remains in force and is tested."
verdict: refutes
---

# E-M52 — the binding I could not demonstrate

## Why this is recorded as a refutation

`ADR-0015` settles how a role's terms should be bound: the signature covers `address + "\nrole:" + digest(role without
accepted_scope)`. The reasoning is sound and the circularity is real, so the ADR stays as `proposed`.

The code does not exist, and two attempts to write it were wrong in instructive ways:

**Attempt one.** `create` signs at line 182 and writes the role file at line 184 — the signature was taken before the
role existed, so `role_message` received empty bytes and signed the address alone. Verification tried the role-bound
message, failed, fell back to the address-only message, and returned green. The tamper test — edit the statement to
"this acceptance is withdrawn" — **passed verification**. A binding that silently degrades to no binding is worse than
none, because the output says `SIGNED_AND_CONSISTENT`.

**Attempt two.** The signing document was built inline from the same fields, canonicalised differently from the file
that gets written, so creation and verification disagreed about two bytes and even the genuine bundle failed.

I reverted rather than ship either. The unsigned-role refusal from `E-M51` is unaffected and remains tested.

## What the two failures teach

1. **A fallback that turns a strong check into a weak one must be visible in the output.** The first attempt's silent
   fallback is exactly the pattern that produced `E-M50` B3 and `E-M47` B2: an honest case refused, a dishonest one
   passed.
2. **Two implementations of one message format will disagree unless they share the function.** Creation and
   verification each built the role bytes their own way; the fix is a single `role_message()` used by both, plus a
   test that creates and verifies in one run.

## What is needed before this can be implemented

- the role document written and signed through one function, so creation and verification cannot drift;
- a test that creates a bundle with an acceptance, edits one field, and requires verification to fail;
- a decision on what to print when a bundle predates the rule: `signature_binding: "address"` with the weaker binding
  stated, not hidden.

That is the next step, and `ADR-0015` says what it should look like.
