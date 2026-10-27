# ADR-0010 — two anchors outside the bundle, or the verdict is not evidence

**Date:** 2026-10-27 · **Status:** accepted · **Source:** `E-M9` run 1 (3/6, refutes) and `E-M9b` run 2 (6/6, supports)

## Context

`E-M9` was pre-registered as six substitution cases. Run 1 caught three. The two it missed are the interesting ones:

- a bundle whose **signer was swapped** still verified, because the bundle carries its own public key;
- a bundle **re-signed for another target** still verified, because nothing outside the bundle said which target
  the caller was looking at.

Both are mechanism T1, measured at last: a signature proves the integrity of what was signed, not that the signer
was trusted or that the target is the one in front of the reader.

## Decision

**A bundle verification is evidence only when two anchors are supplied from outside the bundle:**

1. `--trusted-keys <pem>…` — signature keys are accepted only from this set. A key shipped inside the bundle is
   provenance, never trust.
2. `--expect-target <commit>` — the claim's target must equal the target the caller is actually looking at, not the
   target the bundle chose for itself.

Without both, `fg_bundle verify` reports `SIGNED_AND_CONSISTENT`, and that phrase means exactly one thing: the
bundle is internally consistent. It is **not** an attestation and must not be presented as one.

## Consequences

- The verifier's output vocabulary separates "internally consistent" from "consistent with an externally supplied
  key and target". The first is cheap and nearly worthless; the second is the product.
- Whoever supplies the trusted key list decides what trust means. That is a policy artifact with an owner, not a
  cryptographic fact, and the bundle must record which policy digest was applied.
- `E-M9b` reproduces run 1 with `--no-anchors`, so the improvement is attributable to the fix rather than to a
  weakened test.

## What this decision does NOT do

- It does not make the claim true. An anchor says who signed and what was meant; it says nothing about whether the
  analysis was right, which is round 7's finding and remains in `not_claimed`.
- It does not define who may issue a trusted key list. That is the liability question, still open.
