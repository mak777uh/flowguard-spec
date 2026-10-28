# Sample bundle — the format description, written for someone who will not read our code

Address of this bundle: `27a4c3977982779d…` (full value in `manifest.sha256`).

This description was rewritten after an independent rebuild (`E-M38`) found that the previous version was missing the
details that actually decide the address. Every rule below is stated because a rebuilder got it wrong or had to guess.

## Layout

```
bundle.json          the manifest (pretty-printed; this file is NOT hashed as bytes)
objects/<sha256>     payloads, named by the SHA-256 of their exact bytes
manifest.sha256      the address: 64 lowercase hex characters, then a single LF, nothing else (65 bytes)
signatures/<id>.sig  base64 of the 64 raw Ed25519 signature bytes, then a single LF (89 bytes)
signatures/<id>.pub  Ed25519 public key, PEM, SubjectPublicKeyInfo
signatures/<id>.role JSON: which assertion this signature makes (no trailing newline)
```

## The address — exactly this, nothing else

1. Take `bundle.json`, parse it as JSON, and re-serialise it:
   - keys sorted ascending by Unicode code point, **recursively at every level** (`sort_keys=True`) — a top-level-only sort produces a different address;
   - separators `(",", ":")` — no spaces anywhere;
   - `ensure_ascii=False` — non-ASCII characters are written as UTF-8, not `\uXXXX` escapes;
   - no trailing newline. **A single `\n` at the end changes the address.**
2. Encode as UTF-8.
3. SHA-256 those bytes. Lowercase hex, 64 characters.

**The pretty-printed file on disk hashes to something else.** It is there for humans; the address is over the
canonical form only. A rebuilder that hashes the file bytes will get a different answer, and that is the most common
way to fail this test.

## Signatures

There are two message forms, and which one applies is decided by whether the signer publishes a role:

- **a signature with a `.role` file** covers the *role-bound* message defined in "Roles" below. Every
  signature in this bundle is of this kind.
- **a signature without a `.role` file** covers the address alone: 64 lowercase hex characters, ASCII, no
  `sha256:` prefix, no newline, no NUL terminator.

The address-only form is the older, weaker binding; a verifier that accepts it must say so. An earlier
version of this page stated only the address form and then contradicted itself two sections later — a
rebuilder lost time on it (`E-M54`).

Everything else fails, and it is checked: signing the raw 32 digest bytes fails; signing `"sha256:" + hex` fails;
hex with `\n` or `\r\n` or a space fails; uppercase hex fails.

Signatures are Ed25519 over that message; `.sig` files are base64 of exactly 64 bytes.

## Objects

Each file under `objects/` is named by the SHA-256 of its own bytes, lowercase hex. No normalisation of any kind: line
endings, trailing newlines and encoding are part of the content. A text-mode copy that converts CRLF to LF produces a
different hash and is a different object.

Five objects here: four subjects (`code`, `build`, `config`, `identity`) and the inventory.

## Digests: one convention

**Every digest in this bundle is bare lowercase hex.** There is no `sha256:` prefix anywhere — earlier versions had
two conventions in one file, which is a trap, and it is gone.

- `subjects.<name>.sha256` — the payload's digest, and that digest is a key in `objects`;
- `objects` maps digest → `{bytes, name}`;
- `inventory_digest` — the digest of the inventory object, which is present in `objects`;
- `role.policy_digest` — the digest of the risk policy file the verdict used. It is **not** in this bundle: the policy
  is an input of the verifier, not of the artifact, and a rebuilder cannot check it. Treat it as a reference to an
  external document.

## Roles

A role signature is **not** over the address alone. From `ADR-0015` it covers:

```
message = address_hex || "\n" || "role:" || sha256( canonical( role document without accepted_scope ) )
```

- `canonical` is **exactly** the rule used for the address: recursive key sort by code point, separators
  `(",", ":")`, `ensure_ascii=False`, UTF-8, no trailing newline.
- "without `accepted_scope`" means **the key is deleted**. Setting it to `null` or `""` produces a different
  digest and the signature fails.
- `sha256` output is 64 lowercase hex characters, ASCII.
- `owner.sig` is the file that distinguishes these choices: `owner.role` is not in sorted key order, so an
  implementation that hashes the file's own order fails on `owner` and passes on `demo`. Test the one that
  disagrees with you.

`accepted_scope` is excluded because it must equal the address; every other term — `issuer`,
`residual_risk`, `valid_until`, `statement`, `policy_digest` — is inside the digest. Editing any of them
breaks that party's signature, which is the point: before this rule an acceptance could be rewritten
after signing and the bundle would still verify. A role bound only to the address is refused for
`risk_acceptance`, and reported as the weaker binding for other roles.


`signatures/<id>.role` carries `asserts` (the role) and `issuer`. The table below is the normative definition
for this bundle; `policies/signature-roles.json` lives in the issuing repository and does **not** travel inside the
artifact, so a verifier must not depend on reading it:

| role | must carry |
|---|---|
| `analysis_provenance` | issuer |
| `process_attestation` | issuer |
| `consistency_verdict` | issuer, policy_digest |
| `risk_acceptance` | issuer, accepted_scope (= the bundle address), residual_risk, valid_until, statement |

`risk_acceptance` and `consistency_verdict` must be different keys. `liability_agreement` is not a role: a contract
cannot be created by a JSON field.

## What this bundle does not establish

- That the claim is true. It binds a claim to a target and a policy; it does not check the analysis behind it.
- That the signers are trusted. A key shipped inside the bundle is provenance, never trust — verification is evidence
  only with a key list and an expected target supplied from outside (`ADR-0010`).
- That the inventory is complete. `NC-01` says otherwise, in the claim itself.

## Known limits of this description

- **Number formatting is under-tested.** `claimed_coverage` is `0.133`; a value of `1.0`, `1e-7` or a negative would
  exercise float rendering, and no such value exists in this bundle.
- **`ensure_ascii` cannot be confirmed from this bundle.** Every string is ASCII, so both settings produce identical
  bytes. The rule above says `False`; this artifact cannot prove it. `E-M38` recorded that.
- **Sort order IS tested here, contrary to what this page said before.** `claim_id` and `claimed_coverage` sort differently under code-point order and under punctuation-ignoring collation, so a locale-aware implementation produces a different address. That was found by the second rebuilder.

If you hit something this page does not answer, that is a defect in the page — report it, and it becomes a card.

## What a role signature covers

Not the address alone. From `ADR-0015`:

```
message = address_hex || "\n" || "role:" || sha256( canonical( role document without accepted_scope ) )
```

- `canonical` is **exactly** the rule used for the address: recursive key sort by code point, separators
  `(",", ":")`, `ensure_ascii=False`, UTF-8, no trailing newline.
- "without `accepted_scope`" means **the key is deleted**. Setting it to `null` or `""` produces a different
  digest and the signature fails.
- `sha256` output is 64 lowercase hex characters, ASCII.
- `owner.sig` is the file that distinguishes these choices: `owner.role` is not in sorted key order, so an
  implementation that hashes the file's own order fails on `owner` and passes on `demo`. Test the one that
  disagrees with you.

`accepted_scope` is excluded because it must equal the address. Every other term — `issuer`,
`residual_risk`, `valid_until`, `statement`, `policy_digest` — is inside the digest, so editing any of
them breaks that party's signature. Before this rule an acceptance could be rewritten after signing and
the bundle still verified (`E-M50` B2). A role bound only to the address is refused for
`risk_acceptance` and reported as the weaker binding for everything else:

```
"signature_binding": { "demo": "role", "owner": "role" }
```


## What the signature does NOT cover

`accepted_scope` is excluded from the role digest, because it must equal the address and the address cannot
contain its own digest. The consequence has to be stated plainly:

- the signature covers `issuer`, `residual_risk`, `valid_until`, `statement` and `policy_digest`;
- it does **not** cover `accepted_scope`. A verifier must check `accepted_scope == address` itself; a
  rebuilder who only checks signatures will find that a rewritten `accepted_scope` still verifies. That is
  not a break of the scheme, but it is a step the description previously never asked for (`E-M54`).
