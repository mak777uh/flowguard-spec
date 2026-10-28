# What NEAR AI's attestation stack says about our missing anchor

Source: [`docs.near.ai`](https://docs.near.ai/), particularly [Verification](https://docs.near.ai/cloud/verification)
and its children (gateway attestation, model attestations, TLS binding, response signatures, image provenance,
verification policy). Read from the docs; nothing was run against the service.

## What they attest, in their own words

> "All AI computations run privately and securely in Trusted Execution Environments (TEEs) … You can
> cryptographically verify that the TEE is genuine and model requests are processed in that secure environment."

The verification surface is five separate things, and the separation is the lesson:

| they verify | what it establishes |
|---|---|
| **gateway attestation** | the deployment is fresh — a quote, a nonce and a signer binding |
| **model attestations** | the model that ran matches the claimed measurement |
| **TLS connection binding** | the response came over the connection the attestation covers, not a different one |
| **response signatures** | this reply is the one that deployment produced |
| **image provenance** | the container image corresponds to a known source |
| **verification policy** | *the verifier chooses* which measurements and provenance it will accept |

## The three ideas worth taking

### 1. A nonce, so evidence is bound to a request rather than lying around

Their quote is bound to a nonce the caller supplies. Ours is not: a FlowGuard bundle can be produced today, for
no one, and presented next year as if it answered this week's question. The `risk_acceptance` role has
`valid_until`, which covers the acceptance; the **claim itself has no freshness binding and no challenge**.

This is the cheapest gap in the whole format and I did not see it until reading their page. Adding it changes
bytes, so it is a format decision rather than a repair, and it goes to `docs/QUESTIONS-FOR-OWNER.md` instead of
being done silently.

### 2. The verifier chooses the policy, and it is written down

Their "verification policy" is a document the relying party writes: which measurements, which provenance, which
checks. Ours is a command-line flag (`--trusted-keys`) plus rules scattered through a verifier. The difference
matters when two parties disagree about what a bundle proves: they cannot point at their policies and compare.

Our `docs/37-REFUSAL-CODES.md` is close to this — it is the list of reasons a bundle is refused — but it is
written by the producer side. A policy file that a consumer owns is a different artifact.

### 3. Provenance of the image is a first-class check

They verify that the container image corresponds to a known source. Our equivalent is weaker: an inventory
records `sources` and `independent_of_agent`, but not **which tool version produced it**. A consumer cannot say
"this analysis must have been produced by fg_verify 0.3.x from the published repository".

That is a smaller fix than the nonce — a `tool` object with name, version and digest — and it does not change
any existing field's meaning.

## The most useful sentence for our ceiling

The strongest attestation in this stack says: **this code ran, in this enclave, and this reply came from it.**
It says nothing about whether the answer is correct. NEAR AI is careful about this and never claims otherwise —
their vocabulary is privacy and provenance, not truth.

That is exactly the distinction this repository keeps drawing (`NC-01`, `ADR-0010`): hardware attestation and
signed consistency are the same kind of artifact — **evidence that a process happened**, not evidence that its
conclusion is true. The industry's best-funded attestation stack agrees by the way it words its own claims, which
is worth one sentence in the article and nothing in the readiness tiers.

## What this does not change

- No TEE makes an incomplete inventory complete, and their model attestations would not help with `NC-01`.
- `E_NO_INDEPENDENT_CLOSURE` is about **who produced the enumeration**, and a TEE could in principle attest that a
  named party's pinned code ran on a named database — that is the one place where this stack is a real candidate
  answer rather than an analogy. It would need a third party willing to run it, which is `P1` again.

## Proposal for the owner (format change, not applied)

Add to `claim`:

```json
"challenge": "<64 hex, supplied by the relying party>",
"tool": {"name": "flowguard", "version": "0.3.0", "digest": "<sha256 of the published tree>"}
```

Verifier: when a challenge is supplied (`--expect-challenge`), a claim without it — or with a different one — is
refused as `MISSING_EVIDENCE`; a `tool` whose digest is absent is reported, never assumed.

Both are additive, both invalidate existing artifacts' addresses only when a producer opts in, and both need the
owner's decision because they touch the format.
