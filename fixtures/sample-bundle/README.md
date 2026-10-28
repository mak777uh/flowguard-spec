# Sample bundle — the format, written for someone who will not read our code

Address: `27a4c3977982779d…` (full value in `manifest.sha256`).

This is a **format description**, not a specification of security. Two independent implementers reproduced this
bundle end to end from this page alone; everything they had to guess is now written down.

Scope: `fg-bundle/1`. A verifier given another `bundle_version` must refuse rather than guess.

---

## 1. Layout

```
bundle.json          the manifest. Hashed in canonical form, NOT as bytes.
objects/<sha256>     payloads, named by the SHA-256 of their exact bytes.
manifest.sha256      64 lowercase hex characters, then one LF. 65 bytes.
signatures/<id>.sig  base64 of 64 raw Ed25519 bytes, then one LF. 89 bytes.
signatures/<id>.pub  Ed25519 public key, PEM, SubjectPublicKeyInfo.
signatures/<id>.role JSON: which assertion this signature makes.
```

The raw bytes of a `.role` file are **never hashed**. It is parsed and re-canonicalised (§4), so its formatting, key
order and trailing newline carry no meaning. Do not build a size or line-ending check on them; build one on the
canonical form.

`.sig` files are base64 — **decode tolerantly**: strip surrounding whitespace first. A strict decoder that rejects a
trailing `\r\n` fails on a well-formed bundle, because one signature here was written by a tool that used the platform
line ending.

## 2. The address

1. Parse `bundle.json`.
2. Re-serialise: keys sorted ascending by Unicode code point **recursively at every level**; separators `(",", ":")`,
   no spaces; `ensure_ascii=False`; **no trailing newline**.
3. Encode UTF-8, SHA-256, lowercase hex.

Hashing the pretty-printed file bytes gives a different value (`7358bb44…` here) and is the most common way to fail
this test.

Sort order is genuinely tested by this artifact: `claim_id` and `claimed_coverage` order differently under code-point
collation and under punctuation-ignoring collation, so a locale-aware implementation produces a different address.

## 3. Signatures — two forms

Which form applies is decided by whether a `.role` file exists for that signer:

- **with** `signatures/<id>.role` → the role-bound message of §4. Every signature in this bundle is of this kind.
- **without** a `.role` file → the address alone: 64 hex characters, ASCII, no prefix, no newline, no NUL.

The address-only form is the weaker binding. A verifier must report it (§6) and must refuse it for `risk_acceptance`.

## 4. The role-bound message

```
message = address_hex || "\n" || "role:" || sha256( canonical( role document without accepted_scope ) )
```

- `canonical` is **exactly** the rule of §2: recursive code-point sort, separators `(",", ":")`, `ensure_ascii=False`,
  UTF-8, no trailing newline.
- The digest is 64 lowercase hex characters, ASCII.
- "without `accepted_scope`" means **the key is deleted**. Setting it to `null` or `""` changes the digest and the
  signature fails.
- The fields **inside** the digest are exactly: `asserts`, `issuer`, and whichever of `policy_digest`, `residual_risk`,
  `valid_until`, `statement` the role carries (§8 says which). `asserts` is inside it — dropping it breaks both
  signatures.
- `accepted_scope` is the only field outside the digest, because it must equal the address (§7).

`owner.role` is not in sorted key order and `demo.role` is. An implementation that hashes the file's own key order
passes on `demo` and fails on `owner`: test the file that disagrees with you.

## 5. Objects

Each file under `objects/` is named by the SHA-256 of its own bytes, lowercase hex. No normalisation: line endings,
trailing newlines and encoding are part of the content.

- `objects` maps digest → `{bytes, name}`. `bytes` **must equal the file's length**; `name` is informational.
- No object may be declared but absent, or present but undeclared.
- `subjects.<name>.sha256` and `inventory_digest` must both be keys in `objects`.
- If the map, the directory and a subject disagree, the artifact is refused; nothing here says which one wins, because
  a disagreement is not resolvable by preference.

Five objects here: four subjects (`code`, `build`, `config`, `identity`) and the inventory.

## 6. What a verifier produces

One of: `SIGNED_AND_CONSISTENT`, or a refusal naming a code and the subject it applies to. It must never print a
success it cannot support, and a failed check must produce a refusal with a code — never an omission.

It reports the binding it used:

```json
"signature_binding": { "demo": "role", "owner": "role" }
```

`"role"` means the §4 message verified; `"address"` means only the weaker §3 form did. A `risk_acceptance` bound as
`"address"` is a refusal, not a warning.

Codes a rebuilder will meet: `SIGNATURE_ROLE_UNKNOWN`, `MISSING_EVIDENCE`, `RISK_ACCEPTANCE_INCOMPLETE`,
`SEPARATION_OF_DUTIES_VIOLATED`, `LIABILITY_NOT_A_ROLE`. The full set and its meanings live in the issuing repository;
the names are stable, the long descriptions are not carried here.

## 7. What the signature does NOT cover

The signature covers every role field except `accepted_scope`. Therefore:

- it proves the accepting party signed **these words about this address**;
- it does **not** bind `accepted_scope` — a verifier must compare it to the address itself, and refuse on mismatch;
- a verifier who checks only signatures finds that a rewritten `accepted_scope` still verifies. That is not a break of
  the scheme; it is a step this page asks for and an earlier version did not.

Separation of duties is the same kind of check: `risk_acceptance` and `consistency_verdict` must be different keys,
compared by public-key bytes, not by file name.

## 8. Roles

This table is normative for the artifact. `policies/signature-roles.json` exists in the issuing repository and does
**not** travel inside a bundle; a verifier must not depend on reading it.

| role | requires | inside the role digest |
|---|---|---|
| `analysis_provenance` | `issuer` | `asserts`, `issuer` |
| `process_attestation` | `issuer` | `asserts`, `issuer` |
| `consistency_verdict` | `issuer`, `policy_digest` | `asserts`, `issuer`, `policy_digest` |
| `risk_acceptance` | `issuer`, `accepted_scope` (= address), `residual_risk`, `valid_until`, `statement` | `asserts`, `issuer`, `residual_risk`, `valid_until`, `statement` |

`liability_agreement` is not a role: a contract cannot be created by a JSON field.

`policy_digest` names the risk policy the verdict used. That file is **not** in this bundle — it is an input of the
verifier, not an artifact — so a rebuilder cannot check it. Treat it as a reference to an external document.

## 9. What this bundle does not establish

- That the claim is true. It binds a claim to a target and a policy; it does not check the analysis behind it.
- That the signers are trusted. A key shipped inside the bundle is provenance, never trust — verification is evidence
  only with a key list and an expected target supplied from outside (`ADR-0010`).
- That the inventory is complete. `NC-01` says otherwise, in the claim.
- **What `NC-01`…`NC-11` mean.** The artifact carries only the identifiers; the closed vocabulary is defined in the
  issuing repository. A stranger who wants to know what the accepting party accepted must read it there. That is a
  real limit of the artifact, stated rather than hidden.

## 10. Known limits of this description

- **`ensure_ascii` is untestable here.** Every string is ASCII, so both settings give the same bytes. The rule says
  `False`; this artifact cannot prove it.
- **Float rendering is under-tested.** `claimed_coverage` is `0.133`; `1.0`, `1e-7` and negatives would exercise it.
- **This page was wrong twice.** A rebuilder found a flat contradiction and an undefined canonicalisation in an earlier
  version; another found that `asserts` was inside the digest without being listed. All are fixed. The history is in
  the experiment cards, because a description with no record of its defects is one nobody has read.
