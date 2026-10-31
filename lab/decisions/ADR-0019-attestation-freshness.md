# ADR-0019 — a bundle records the tool that produced it; a challenge is accepted only when a party issues one

**Status:** accepted, 2026-10-31. `tool` is required for new claims; `challenge` is optional and is a refusal
condition only when the relying party supplied one.

## What is missing today

A bundle says what was found and says nothing about **what produced it** or **who asked for it**.

- **What produced it.** Two bundles made by `fg-core 0.1.0` and by a patched build are indistinguishable. A
  reader who wants to reproduce a run has to guess the instrument.
- **Who asked for it.** A bundle can be produced for nobody and presented later, as if it were fresh, to a
  different party. Nothing in the signed bytes ties it to a request.

## The decision

**`tool` — required.** A claim carries `tool {name, version, digest}`. `name` is the artefact, `version` is the
release tag or commit, `digest` is the sha256 of the binary or of the source tree that ran. The verifier reports
its absence as `MISSING_EVIDENCE` for levels above `CONSISTENT_DECLARED` and never infers it.

Why required rather than optional: an optional provenance field is omitted exactly when the run is inconvenient,
which is the case that matters. The cost is one small object per claim.

**`challenge` — optional, and refuses only when expected.** The relying party may supply a hex value before the
run; the claim carries it inside the signed bytes. If the caller supplied a challenge and the claim carries a
different one, the verdict is `REFUSED` with `CHALLENGE_MISMATCH`. If the caller supplied none, the claim may
carry none, and the report says `no freshness binding` in `not_claimed` rather than pretending.

Why not required: on 2026-10-31 the owner decided the product is a tool and that nobody signs a reliance scope.
A nonce binds an artifact to a request, and a tool with no counterparty has no request to bind. Requiring it
would add ceremony that no one consumes and would make every honest local run refused.

## What this does not do

- It does not make a bundle fresh. A challenge prevents replay to a party who issued one; it does nothing about
  a database that changed after the run.
- It does not authenticate the tool. A digest identifies bytes; whether those bytes are trustworthy is the
  reader's policy, and `NC` codes keep saying so.
- It does not change the address rule beyond carrying two more fields through it.

## Cost and sequencing

Both fields change the canonical bytes of new claims, so this lands with the same re-signing step as `ADR-0018`:
schema `claim-0.2`, the two fields in `fg_bundle` and in `fg-core`, a fixture claim carrying both, and the
verifier's two new refusals. Old bundles remain valid under their own `fg-bundle/1` version; the version field
is what tells a reader which contract applies.
