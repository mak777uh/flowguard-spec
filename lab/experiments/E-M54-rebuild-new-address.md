---
id: E-M54
hypothesis: H-M54
status: completed
base_commit: "99f916d"
started: "2026-10-28T14:25:00+03:00"
finished: "2026-10-28T14:50:00+03:00"
environment: "Windows, CPython 3.13.11; independent agent, description only, no source access"
command: "spawn a rebuilder with C:\\111\\_m7v2\\sample-bundle only; it may not read the repository"
threshold: "Pre-registered: a rebuilder with only the rewritten description must reproduce the address 27a4c397…, verify both role-bound signatures and check five objects, using no brute force. Every sentence that misleads counts against the description."
rebuild_result: agreed by an independent agent on 2026-10-28 — address 27a4c397…, two role-bound signatures verified, 5/5 objects; the description was then rewritten against its eight findings (E-M54)
result: "Address matched (27a4c397…, canonical 1384 bytes), both signatures verified in the role-bound form, 5/5 objects intact, and every predicted negative control failed: address-only, raw digest bytes, sha256: prefix, LF/CRLF, uppercase, role digest without the address prefix, and address+role: with no newline. But it found EIGHT defects in the description, two of them serious: a flat contradiction (one section said the message is the address alone, two sections later said it is not), and an undefined canonical form for the role document, where the two natural guesses both fail and only owner.sig distinguishes them. It also found owner.sig shipped CRLF while demo.sig shipped LF. All eight were fixed: the contradiction resolved into two named message forms, the canonicalisation and the meaning of 'without accepted_scope' defined, byte counts corrected, owner.sig normalised, the dangling policy reference replaced with the normative table, and a new section stating what the signature does NOT cover and what the verifier must check instead."
verdict: supports
---

# E-M54 — M7 on the new artifact, and the description it indicted

## Result

| check | outcome |
|---|---|
| address | `27a4c3977982779d…` = recorded. Canonical form 1384 bytes |
| signatures | demo and owner verified, **both in the role-bound form** |
| negative controls | address-only, raw digest bytes, `sha256:` prefix, hex+LF, hex+CRLF, uppercase, role digest without the address prefix, `addr+"role:"` without the newline — all fail, as predicted |
| objects | 5 checked, 5 matching |

So the format change did not break reproducibility, and the independent implementer derived the new rule from the
page rather than from the code.

## The two defects that mattered

**A flat contradiction.** One section said *"the signed message is the address itself"*; two sections later, the role
rule said *"not over the address alone"*. Every signature in this bundle is a role signature, so the first rule fails
for 100% of them — and a reader following the page in order is instructed to do the thing that does not work.

**An undefined canonical form.** The role document's canonicalisation was never stated: the rules were defined once,
explicitly for `bundle.json`. The two natural guesses — hash the file's own key order, or use `json.dumps` defaults with
spaces — both produce a failing signature with no diagnostic. Worse, `demo.role` is already in sorted order, so a
rebuilder who tests only `demo` "confirms" a wrong implementation; only `owner.role` disagrees.

That is the same lesson as `E-M39`, one layer down: **the description must state the rule that the artifacts
disambiguate, or the artifacts teach it silently.**

## The rest

`owner.sig` shipped CRLF while `demo.sig` shipped LF — one file voiding the stated format for all of them; the byte
count was wrong (65, not 66); a policy file was cited that does not travel inside the artifact; `.role` newline
convention was unstated; and `accepted_scope`, excluded from the digest by construction, was not described as something
a verifier must compare itself.

That last one deserves the sentence it now has: **the signature does not cover `accepted_scope`, so a verifier must
check it, and a rebuilder who checks only signatures will find a rewritten scope still verifies.** Not a break of the
scheme — a step the page never asked for.

## What this establishes

The envelope is reproducible from the description by a party that never saw the code, twice, on two different formats.
That is `M7` in the weaker form (an AI agent, not a human stranger), and it is now recorded against the current address.

## What it does not

- That a human stranger would succeed. The rebuilder is the same model family as the author.
- That the description is complete: the first round on this artifact found eight defects, and a second round has been
  started against the rewritten page.
