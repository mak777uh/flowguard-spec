---
id: E-M55
hypothesis: H-M55
status: completed
base_commit: "5f55be1"
started: "2026-10-28T14:55:00+03:00"
finished: "2026-10-28T15:25:00+03:00"
environment: "Windows, CPython 3.13.11; third independent rebuilder, description only"
command: "spawn a rebuilder with C:\\111\\_m7v3\\sample-bundle only; it may not read the repository"
threshold: "Pre-registered: a rebuilder given the rewritten page must reproduce the address, both role-bound signatures and five objects first-pass, and must be able to write a CONFORMING verifier - not merely verify this one bundle. The second half is the stricter test, and it is where the page failed."
result: "Artifact reproduced completely: address 27a4c397…, both signatures verified in the role-bound form, 5/5 objects, every bytes/name field consistent. But the page still could not support a conforming verifier, and the reason is a design fault rather than a wording one: it MANDATED a refusal code for every failure and then deferred the vocabulary to a repository the reader does not have. Five defects fixed: the false CRLF story (both .sig are 89 bytes, LF only; a strict decoder fails on the LF, which is the opposite of the stated cause), the digest input set defined as document-minus-one-key with unknown keys refused, absent-or-wrong accepted_scope resolved to RISK_ACCEPTANCE_INCOMPLETE against the recorded address, issuer-must-equal-stem, and a full refusal-code table with the payload shape and public-key identity rule. Float rendering restated as unspecified rather than untested."
verdict: supports
---

# E-M55 — the page mandated codes and withheld the vocabulary

## What reproduced

Address `27a4c3977982779d…` matched, canonical body 1384 bytes; the page's own warning check verified (pretty bytes
hash to `7358bb44…`, exactly the value it quotes). Both signatures verified in the role-bound form, with every negative
control rejected: address-only, `accepted_scope: null` instead of deleted, raw `.role` bytes hashed, `asserts` dropped,
digest uppercased. Five objects, all names and byte counts consistent. Collation is genuinely pinned: swapping
`claim_id`/`claimed_coverage` yields `b94d0112…`.

## The defect that mattered

> A refusal must name a code … the full set and its meanings live in the issuing repository.

The page required a coded refusal for every failure — `bundle_version` mismatch, address mismatch, object disagreement,
role-digest mismatch, `accepted_scope` mismatch, signature failure — and supplied five codes while sending the reader
elsewhere for the rest. **A stranger could verify this bundle and could not write a conforming verifier.** Worse, the
page also said the names are "stable", which forbids inventing one.

That is a different class of defect from the previous two rounds. `E-M39` and `E-M54` were errors of omission: a rule
was missing and the artifacts taught it silently. This one is an error of *delegation*: the page told the reader that
something was required, then made it unobtainable. A description that mandates an output it does not define is not
underspecified, it is unusable as a specification.

Fixed by putting the vocabulary in the artifact: a table of eight codes, each bound to the check that emits it, with
the refusal payload shape (code, subject, expected, observed, next action), the rule that a failed check must produce a
refusal rather than an omission, and the definition of public-key identity (the raw 32-byte Ed25519 key decoded from the
PEM, not its file name or formatting).

## The other four

**A false cause.** The page explained its whitespace tolerance with a CRLF story that the artifact refutes: both `.sig`
files are 88 base64 characters plus one LF, no `0x0D` anywhere. A strict decoder does fail — on the LF, which is the
opposite of the stated reason.

**An undecidable digest input.** Three sentences described the role digest three ways: whole document minus one key, a
whitelist of five fields, and "every field except `accepted_scope`". For a role carrying an extra key the three disagree.
Now: document-minus-one-key, and an unlisted key is a refusal.

**Guessed semantics.** Whether `accepted_scope` is compared to the computed or recorded address, whether `issuer` must
equal the file stem, and whether a `name`/`source` mismatch is a refusal — all now stated.

**A mislabelled limit.** Float rendering was called "under-tested", which is a coverage gap; it is an unspecified rule,
and this artifact cannot pin it. Saying "under-tested" implied that enough tests would settle it.

## The judgement this leaves

A stranger can now rebuild and verify this bundle, and can write a verifier that emits conforming refusals. They still
cannot know what `NC-01`…`NC-11` assert — the artifact carries identifiers whose vocabulary lives outside it — and the
page says so in section 9 rather than glossing it.

Three rebuilders, three different classes of defect: omission, contradiction, delegation. The method that found them is
the same one that found the gate breaks, applied to prose.
