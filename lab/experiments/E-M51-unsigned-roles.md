---
id: E-M51
hypothesis: H-M51
status: completed
base_commit: "16ea006"
started: "2026-10-28T12:25:00+03:00"
finished: "2026-10-28T12:55:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python tools/fg_bundle.py verify --bundle <copy with an unsigned .role> --trusted-keys ..."
threshold: "Pre-registered: the third attacker's B2 must be reduced or closed, and the reduction demonstrated by reproducing the exact attack. A partial fix that is not measured is not a fix."
result: "PARTLY CLOSED. An unsigned role is now refused: a .role without that party's .sig and .pub produces INVALID/SIGNATURE_ROLE_UNKNOWN, and the attacker's exact reproduction now fails. The terms are still not covered by the address: bundle.json does not carry the role digests, so an already-signed party's acceptance can still be edited after signing. I attempted the full binding and reverted it, because the acceptance must name the address (accepted_scope == address) while the address would cover the acceptance, which is circular; breaking the cycle needs a format revision, not a patch at the end of a session. Recorded as open with the design constraint written down."
verdict: supports
---

# E-M51 — half of B2, and why the other half is a format question

## What is closed

The attacker's reproduction: create a bundle, append `signatures/acme-ciso.role` with a full risk acceptance, no
signature, no key. Before: `SIGNED_AND_CONSISTENT`, exit 0, address byte-identical. Now:

```
"verdict": "INVALID", "code": "SIGNATURE_ROLE_UNKNOWN",
"observed": "unsigned role: nobody signed this assertion"
```

A role without the party's signature is a claim about a party written by whoever holds the directory. That much is
refused today, and the sample bundle plus `E-M28` still pass.

## What is not closed, and why a patch did not fix it

The terms of a **signed** role are still editable after signing, because `bundle.json` does not carry the role bytes
and the signature covers only the address. The obvious fix — put `role_digests` into `bundle.json` so the address
covers them — collides with a rule already in the format:

- `risk_acceptance` must carry `accepted_scope` **equal to the bundle address**;
- the address would then cover a document whose content includes the address.

That is circular. Breaking it needs one of three decisions, and each is a format revision with consequences for every
artifact already issued:

1. acceptance signed **after** the address and stored outside it, with a second signature over `address + role`;
2. `accepted_scope` replaced by a reference (`target: <address>` in a separate endorsement file);
3. a two-level structure: the address covers everything except acceptances, and acceptances carry their own address.

I attempted (1) as a patch, hit the recursion, and reverted rather than ship a half-built format at the end of a
session. The attempt is recorded here because a failed attempt that is written down is cheaper than a silent one.

## What this means for the bundle today

`fg-bundle/1` states in its README that acceptance and verdict must be different keys; it does not state that an
acceptance's terms are outside the address. That sentence is now owed, and the format needs `ADR-0015` before the
product can claim that an acceptance is bound to what it accepts.
