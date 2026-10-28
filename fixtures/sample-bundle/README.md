# Sample bundle — the format, written for someone who will not read our code

Address: `5336c02a397cdf96…` (full value in `manifest.sha256`).

This is a **format description**, not a specification of security. Two independent implementers reproduced this
bundle end to end from this page alone; everything they had to guess is now written down.

Scope: `fg-bundle/2`. A verifier given another `bundle_version` must refuse rather than guess. `fg-bundle/1`
artifacts remain verifiable under their own, weaker rule and must be reported as such.

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

`.sig` files are base64 — **decode tolerantly**: strip surrounding whitespace first. The trailing LF is not part of
the base64, and a strict decoder (`b64decode(validate=True)`) fails on both files here because of it, not because of a
line-ending defect: both are exactly 88 base64 characters plus one LF. Interior whitespace is not expected and should
be refused.

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

An address-only signature **cannot assert a role at all**: role identity lives in the `.role` file (§8), and without it
there is no `asserts` to say what the signer meant. Such a signature is provenance only, and is never sufficient for
`consistency_verdict` or `risk_acceptance`.

`nc_vocabulary` travels with the artifact: `{version, sha256, text_included, text}`. The text is inside the
bundle so a stranger can read what was accepted without fetching a second document; the digest stays so drift
is detectable.

A bundle must carry at least one signature; a bundle with none is refused, not accepted as consistent. A claim that
declares `PROVEN` or `SCOPED_ASSURANCE` must be signed by a `consistency_verdict` holder. A `risk_acceptance` is
optional — but if the verdict is relied upon, the reader should ask why there is none, and this page does not pretend
that the artifact answers it.

## 4. The role-bound message

```
profile     = "fg-bundle/2|" || address_hex || "|" || role_digest || "|" || scope
role_digest = sha256( canonical( role document ) )   # every term, accepted_scope included
signature   = Ed25519( sha256(profile) as 64 ASCII hex )
```

- `canonical` is **exactly** the rule of §2: recursive code-point sort, separators `(",", ":")`, `ensure_ascii=False`,
  UTF-8, no trailing newline.
- The digest is 64 lowercase hex characters, ASCII.
- `accepted_scope` is **inside** the digest in `fg-bundle/2`. The old `fg-bundle/1` message deleted it and checked it
  separately; that exception is gone, which is the point of the change.
- The input to the digest is **the whole role document minus the `accepted_scope` key** — not a whitelist. The
  fields that appear in it here are `asserts`, `issuer`, and whichever of `policy_digest`, `residual_risk`,
  `valid_until`, `statement` the role carries (§8 says which). `asserts` is inside it — dropping it breaks both
  signatures.
- A role document carrying a key that §8 does not list for its role is **refused**, not silently included: the digest
  would otherwise cover text nobody has a rule for.
- The deletion is top-level only: no nested key is touched.
- `accepted_scope` is the only field outside the digest, because it must equal the address (§7).

`owner.role` is not in sorted key order and `demo.role` is. An implementation that hashes the file's own key order
passes on `demo` and fails on `owner`: test the file that disagrees with you.

## 5. Objects

Each file under `objects/` is named by the SHA-256 of its own bytes, lowercase hex. No normalisation: line endings,
trailing newlines and encoding are part of the content.

- `objects` maps digest → `{bytes, name}`. `bytes` **must equal the file's length**; `name` is informational.
- Within `objects/`, nothing may be declared but absent, or present but undeclared. An absent declared object is
  `MISSING_EVIDENCE`; a present object whose digest does not match its name is `REPORT_BUNDLE_INCONSISTENT`. `bundle.json`,
  `manifest.sha256` and `signatures/` are of course present and are not objects.
- `subjects.<name>.sha256` and `inventory_digest` must both be keys in `objects`.
- If the map, the directory and a subject disagree, the artifact is refused; nothing here says which one wins, because
  a disagreement is not resolvable by preference.

Five objects here: four subjects (`code`, `build`, `config`, `identity`) and the inventory.

## 6. What a verifier produces

A malformed document is a refusal, not a crash: an unparseable `bundle.json`, an unparseable `manifest.sha256` (not
64 hex characters plus LF), a `.sig` that is not base64 of exactly 64 bytes, or a `.pub` that is not a PEM
SubjectPublicKeyInfo are all `REPORT_BUNDLE_INCONSISTENT` with the document named as the subject.

One of: `SIGNED_AND_CONSISTENT`, or a refusal naming a code and the subject it applies to. It must never print a
success it cannot support, and a failed check must produce a refusal with a code — never an omission.

A refusal names a code, the subject it applies to (a signer id, an object digest, a path id, or `artifact` for the
bundle as a whole), what was expected, what was observed, and what to do next (§6b).

It reports the binding it used:

```json
"signature_binding": { "demo": "role", "owner": "role" }
```

`"role"` means the §4 message verified; `"address"` means only the weaker §3 form did. A `risk_acceptance` bound as
`"address"` is a refusal, not a warning.

Codes a rebuilder will meet: `SIGNATURE_ROLE_UNKNOWN`, `MISSING_EVIDENCE`, `RISK_ACCEPTANCE_INCOMPLETE`,
`SEPARATION_OF_DUTIES_VIOLATED`, `LIABILITY_NOT_A_ROLE`. The full set and its meanings live in the issuing repository;
the names are stable, the long descriptions are not carried here.

## 6b. Refusal codes

Every failure below is a refusal with this code. A verifier that invents a code is not conforming; a verifier that
skips one of these checks is not verifying.

| code | emitted when |
|---|---|
| `REPORT_BUNDLE_INCONSISTENT` | `bundle_version` is not `fg-bundle/1`; the address recomputed from `bundle.json` differs from `manifest.sha256`; a role document carries a key its role does not allow; the objects map, the directory and a subject disagree |
| `MISSING_EVIDENCE` | a declared object is absent; a signature does not verify over the message form that applies; the manifest lacks a required field |
| `SIGNATURE_ROLE_UNKNOWN` | a `.role` file exists without a `.sig` or a `.pub` from the same party; `asserts` is not one of §8's roles |
| `LIABILITY_NOT_A_ROLE` | `asserts` is `liability_agreement` or another key in `not_a_role` |
| `RISK_ACCEPTANCE_INCOMPLETE` | a `risk_acceptance` role is missing `accepted_scope`, `residual_risk`, `valid_until` or `statement`, or `accepted_scope` is not a string |
| `SEPARATION_OF_DUTIES_VIOLATED` | `risk_acceptance` and `consistency_verdict` are held by the same public key |
| `TARGET_MISMATCH` | the claim's `target_lock` does not equal the expected target supplied by the verifier |
| `POLICY_UNTRUSTED` | a signing key is not in the trusted set supplied out of band |
| `TARGET_MISMATCH` (also) | `claim.target_lock.commit` differs from the inventory's `target_lock` |
| `SIGNATURE_ROLE_UNKNOWN` (also) | a role's `issuer` differs from its signer id (the file stem) |
| `RISK_ACCEPTANCE_INCOMPLETE` (also) | a `risk_acceptance`'s `residual_risk` is not equal, as a set, to the claim's `not_claimed` |

`accepted_scope` that is present but not equal to the **recorded** address is `RISK_ACCEPTANCE_INCOMPLETE`, not
`TARGET_MISMATCH`: the scope is part of the acceptance, and the address is the thing it names.

Public-key identity means the **raw 32-byte Ed25519 public key** decoded from the PEM: two PEM files that decode to the
same 32 bytes are the same party, whatever their file names or byte formatting.

## 7. What the signature does NOT cover

The signature covers every role field except `accepted_scope`. Therefore:

- it proves the accepting party signed **these words about this address**;
- it does **not** bind `accepted_scope` — a verifier must compare it to the address itself, and refuse on mismatch;
- a verifier who checks only signatures finds that a rewritten `accepted_scope` still verifies. That is not a break of
  the scheme; it is a step this page asks for and an earlier version did not.

Separation of duties is the same kind of check: `risk_acceptance` and `consistency_verdict` must be different keys,
compared by public-key bytes, not by file name.

## 8. Roles

`issuer` must equal the signer id (the file stem): the stem names the party everywhere else, and a document whose
`issuer` disagrees with its own file name is ambiguous about who asserted it.

This table is normative for the artifact. `policies/signature-roles.json` exists in the issuing repository and does
**not** travel inside a bundle; a verifier must not depend on reading it.

| role | requires | inside the role digest |
|---|---|---|
| `analysis_provenance` | `issuer` | `asserts`, `issuer` |
| `process_attestation` | `issuer` | `asserts`, `issuer` |
| `consistency_verdict` | `issuer`, `policy_digest` | `asserts`, `issuer`, `policy_digest` |
| `risk_acceptance` | `issuer`, `accepted_scope` (= address), `residual_risk`, `valid_until`, `statement` | `asserts`, `issuer`, `residual_risk`, `valid_until`, `statement` |

`liability_agreement` is not a role: a contract cannot be created by a JSON field. The `not_a_role` set contains
exactly that name in this version; a verifier that meets another name it does not recognise treats it as
`SIGNATURE_ROLE_UNKNOWN`, not as a liability role.

A conforming verifier emits **at least one** refusal when several checks fail; it does not have to choose between them,
and must not report the first and drop the rest.

`policy_digest` names the risk policy the verdict used. That file is **not** in this bundle — it is an input of the
verifier, not an artifact — so a rebuilder cannot check it. Treat it as a reference to an external document.

## 8b. Cross-file equalities

Checked, and a mismatch is a refusal:

- `bundle.claim.target_lock.commit` equals the inventory's `target_lock`. The claim carries an object and the
  inventory carries a bare string; **they are never compared as whole values**. An earlier version of this page said
  `claim.target_lock` equals the inventory's field, which is false on this very artifact and made a conforming
  verifier reject a valid bundle;
- `accepted_scope` in a `risk_acceptance` equals the recorded address;
- `residual_risk` equals the claim's `not_claimed` set, as sets.

Not checked, and therefore not claimed: `plaintext_notified`, `declared_level`, `claimed_coverage`, `excluded`, and
every field inside the inventory other than its `target_lock`. The inventory's own arithmetic (`paths_total` versus the
number of path entries) is the inventory's business: this bundle records 15 total with 2 attributed to the core, and a
verifier may report the difference but must not treat it as a contradiction, because "total" counts what was
enumerated, not only what is listed.

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
- **Float rendering is unspecified, not merely untested.** This bundle contains one float (`0.133`), which renders
  identically in every language that uses shortest-round-trip formatting, so the artifact cannot pin the rule and this
  page does not supply one. An implementer must assume shortest round-trip (Python `repr`, JS `toString`, Go `%v`) and
  know that `1.0`, `1e-7` and `-0.0` are unresolvable from this artifact. That is a limit of the format, not of the
  description.
- **A `.role` trailing newline is untested here**: neither file has one, and the page says the bytes do not matter. The
  claim is true by construction, not by evidence; a verifier may ignore the bytes and must not rely on this artifact to
  prove it.
- **This page has been wrong repeatedly**, and every defect was found by a rebuilder rather than by its author: an
  address-only-versus-role contradiction, an undefined canonical form, an unlisted `asserts`, a false CRLF story, and a
  mandated refusal vocabulary withheld from the reader. All five are fixed.
- **Earlier wording, kept honest.** A rebuilder found a flat contradiction and an undefined canonicalisation in an earlier
  version; another found that `asserts` was inside the digest without being listed. All are fixed. The history is in
  the experiment cards, because a description with no record of its defects is one nobody has read.
