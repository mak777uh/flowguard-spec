---
id: E-M62
hypothesis: H-M62
status: completed
base_commit: "dca072d"
started: "2026-10-28T14:05:00+03:00"
finished: "2026-10-28T14:55:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m53-run.py && python lab/e-m57-run.py && python tools/fg_bundle.py verify --bundle fixtures/sample-bundle ..."
threshold: "Pre-registered: the owner accepted the earlier recommendations, so (a) the v2 envelope becomes the default and one signature must cover address, every role term including accepted_scope, and the scope; (b) the NC dictionary text must travel inside the bundle; (c) nothing already issued may be silently reinterpreted - a v1 artifact must still verify under its own rule and report which form was used; (d) every existing bundle test must stay green."
result: "Both adopted. fg-bundle/2 is the default envelope: signature = Ed25519(sha256('fg-bundle/2|' || address || '|' || role_digest || '|' || scope)), role_digest covering every term including accepted_scope, so the exception ADR-0015 carried is gone. nc_vocabulary now carries the dictionary text (3249 characters) and its digest, so a stranger can read what was accepted without a second document. The sample bundle was rebuilt at address 5336c02a…; a v1 artifact still verifies and reports signature_binding 'v1-role'. Three defects of mine surfaced on the way: the version check still demanded fg-bundle/1, the harness compared against a bundle whose inventory had no target_lock (so the third-party verifier correctly refused it), and two differential mutations touched a signer the test bundle does not carry and were counted as disagreements instead of being skipped."
verdict: supports
---

# E-M62 — the v2 envelope adopted, and the dictionary moved inside

## What changed

```
payload     = sha256( "fg-bundle/2|" || address_hex || "|" || role_digest || "|" || scope )
role_digest = sha256( canonical( role document ) )     # every term, accepted_scope included
signature   = Ed25519( payload as ASCII hex )
```

The `ADR-0015` exception — `accepted_scope` excluded from the digest and checked separately — is gone. Every
term of the role, the address and the scope are inside one signature; there is nothing left to check "on the
side".

`nc_vocabulary` now carries `{version, sha256, text_included: true, text}`: 3249 characters of the closed
vocabulary travel with the artifact. A stranger holding only the bundle can read what the accepting party
accepted, and the digest still detects drift.

## Compatibility, checked rather than promised

`fg-bundle/1` artifacts still verify under their own rule and the verdict reports `signature_binding:
"v1-role"`. The version check had to learn both strings — it still demanded `fg-bundle/1` and refused the new
bundle, which the round-trip test caught immediately.

Sample bundle rebuilt: address `5336c02a…`, `fg-bundle/2`, dictionary inside. Old address `27a4c397…` stays in
the cards as the last v1 artifact, because the third rebuild was performed against it.

## The differential had to be re-based

The third-party verifier implements v1 and, correctly, refuses an unknown version. The differential therefore
builds a v1 bundle for comparison and runs on it. Two of its mutations then disagreed — but not because of the
verifiers: they edited a signer the test bundle does not carry, so both sides accepted a no-op. The harness now
skips mutations that need an absent signer instead of counting them.

One genuine finding came out of the re-basing: the first v1 test inventory had no `target_lock`, and the
third-party verifier refused it — correctly, by the page's own rule that `claim.target_lock.commit` must equal
the inventory's `target_lock`. Ours had accepted it. That is a page rule I had not enforced in `create`; the
harness output made it visible.

## What this does not change

The ceiling. A signed claim still says "this party asserted these words about this address", not "the words are
true" (`NC-01`, `ADR-0010`). The dictionary inside the bundle makes the claim easier to read, not stronger.
