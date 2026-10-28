# ADR-0016 — one signature that binds the address, the role and the scope

**Status:** accepted, 2026-10-28. Supersedes `ADR-0015` (role-bound message that excluded `accepted_scope`).

## Why the previous design was weaker than it looked

`ADR-0015` bound a role's terms to the address by signing `address || "\nrole:" || sha256(role minus
accepted_scope)`. The exclusion was forced: the role's `accepted_scope` must equal the address, and if the
role digest entered the address the artifact would contain its own digest.

The forced exclusion created a permanent exception to "the signature covers everything": the accepting
party's scope was outside the signature, checked separately by an equality test. A separate check is not a
signature, and the owner's directive is that one signature must cover the semantic context rather than two
signatures layered on top.

## Decision

The addressed artifact no longer carries role digests at all, so the circularity disappears. The signature
message binds everything directly:

```
role_digest = sha256( canonical_json( role document ) )        # includes accepted_scope
payload     = sha256( "fg-bundle/2|" + address_hex + "|" + role_digest_hex + "|" + scope_hex )
signature   = Ed25519( payload as ASCII hex )
```

where `scope_hex` is `accepted_scope` for a `risk_acceptance` and the empty string otherwise. `canonical_json`
is the address rule: recursive code-point key sort, separators `(",",":")`, `ensure_ascii=False`, UTF-8, no
trailing newline.

Consequences:

- every term of the role **including the scope** is inside the signature;
- a role cannot be transplanted onto another address: the address is in the payload;
- a signature cannot be replayed as another role: the role digest is in the payload;
- one verification step, no exception, nothing checked "separately".

## Versioning and migration

`bundle_version` becomes `fg-bundle/2`. A verifier **must** refuse an unknown version rather than guess, so
`fg-bundle/1` artifacts are still accepted by this repository's verifier under their own rule, and the
verdict reports which message form verified:

```json
"signature_binding": { "demo": "v2", "owner": "v2" }        // or "v1-role" / "v1-address"
```

No artifact with `fg-bundle/1` is silently reinterpreted. The sample bundle is rebuilt as `fg-bundle/2`; its
previous address (`27a4c397…`) stays recorded in the experiment cards as the last `v1` artifact, because
`M7` was performed against it.

## What this does NOT do

- **It does not make the claim true.** The signature binds a party to words about an address; whether those
  words are accurate is not a property of a signature (`NC-01`, `ADR-0010`).
- **It does not identify the party.** A key is a key; who holds it is outside the artifact (`NC-08`).
- **It does not remove the need to check roles.** Required fields, separation of duties and the liability
  prohibition are still separate checks; the signature only guarantees that whatever fields are present were
  signed together with the address.
- **It invalidates `fg-bundle/1` for reliance.** Old artifacts remain verifiable under v1 rules, but a v1
  acceptance has its scope outside the signature and must not be offered as a reliance artifact.
