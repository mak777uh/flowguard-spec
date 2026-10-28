# ADR-0015 — an acceptance is bound to what it accepts

**Status:** proposed, 2026-10-28 — **not implemented**. The reasoning below is settled; the code is not written (see E-M52 for the failed attempt and what it exposed). Supersedes the implicit rule in `fg-bundle/1` that a role is covered by
the address.

## The problem

`fg-bundle/1` requires `risk_acceptance` to carry `accepted_scope` equal to the bundle address, and it requires the
acceptance to be a different key from the verdict. Both are enforced (`E-M28`).

But the role file lives in `signatures/` and its bytes are not part of `bundle.json`, so the address does not cover
them. The consequence, found by the third adversarial round (`E-M50` B2):

- a full acceptance can be **appended** with no signature at all — closed by refusing unsigned roles (`E-M51`);
- the terms of a **signed** acceptance can still be edited after signing: `valid_until` moved to 1999,
  `residual_risk` replaced, the statement changed to "this acceptance is withdrawn" — and the bundle still verifies,
  with a byte-identical address.

Putting the role bytes into `bundle.json` does not work: the acceptance must name the address, so the address would
cover a document containing the address.

## Decision

**The signature over a role is made over a message that binds both the address and the role's own bytes.**

```
message = address || "\n" || "role:" || sha256( canonical( role_document without accepted_scope ) )
```

`accepted_scope` is excluded from the digest because it must equal the address (already checked separately); every
other field — `issuer`, `residual_risk`, `valid_until`, `statement`, `policy_digest` — is inside it.

Consequences:

- editing any term breaks that party's signature, and the verification says so;
- the address stays computable before any acceptance exists, so the circularity is gone;
- an acceptance is still a separate act by a separate key, as `E-M28` requires.

## Compatibility

Bundles produced before this ADR carry signatures over the address alone. Verification tries the role-bound message
first and falls back to the address-only message, then reports which binding was used:

```
"signature_binding": "role" | "address"
```

A `risk_acceptance` bound only to the address is **refused** from this version on: its terms are not covered, which
was the whole defect. Other roles keep working under the old binding, with the weaker binding stated in the output
rather than hidden.

## Consequences to accept

- A party that wants to accept risk must sign twice in practice: once for the bundle (if it also holds a verdict role)
  or once, over the role-bound message (if it only accepts). The tool handles both.
- The message format is now load-bearing documentation: a rebuilder must implement it, and the format description
  must state it in the same precision as the address rules (`E-M39` taught what happens otherwise).
- `fg-bundle/1` is not renamed. The address rules are unchanged; only what a role signature covers has changed, and
  that is versioned by the `signature_binding` field rather than by a new bundle version.

## Alternatives rejected

1. **Role digests inside `bundle.json`** — circular with `accepted_scope`.
2. **Acceptances outside the bundle entirely** — loses the single-artifact property that makes the bundle useful to
   someone who was not in the room.
3. **A second address per acceptance** — correct in principle, but two addresses for one artifact is a new class of
   confusion, and `E-M9` already showed how much a rebound address costs to explain.
