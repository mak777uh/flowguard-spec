# Sample bundle — for M7, the independent rebuild

This directory is a real `fg-bundle/1` bundle, small enough to read in a few minutes. It exists for one purpose:
**so somebody who has never read our code can rebuild it from this description and say whether they get the same
address.**

Address of this bundle: `929c2824dc5a123b…` (full value in `manifest.sha256`).

## Layout

```
bundle.json          # the manifest
objects/<sha256>     # four payloads, named by their own digest
manifest.sha256      # sha256 of the canonical form of bundle.json — the bundle's address
signatures/demo.sig  # Ed25519 signature over the address (base64)
signatures/demo.pub  # the public key that verifies it
signatures/demo.role # which assertion this signature makes
```

`bundle.json`:

| key | meaning |
|---|---|
| `bundle_version` | `fg-bundle/1` |
| `subjects` | for each of `code`, `build`, `config`, `identity`: the sha256 of the payload and its source name |
| `objects` | digest → `{bytes, name}`; every digest here must exist as a file under `objects/` |
| `claim` | the attestation: flow, target lock, declared control point, level, coverage, exclusions, `not_claimed` |
| `not_claimed` | codes from `docs/NOT-CLAIMED.md` (`NC-01`, `NC-02` here), not prose; the verifier refuses unknown codes and refuses a level that omits its required codes |
| `inventory_digest` | sha256 of the inventory manifest this claim was checked against |
| `plaintext_notified` | a flag for the human-facing report path; carries no security meaning |

## Canonical form

`manifest.sha256` is the sha256 of the canonical JSON of `bundle.json`:

- object keys sorted lexicographically;
- no whitespace between tokens (`separators (",", ":")`);
- UTF-8, `ensure_ascii=False`.

That is a subset of RFC 8785 (JCS); it is enough because the payload contains only strings, integers, booleans,
lists and objects with no floats.

## What an independent rebuild means

1. Read this file and `bundle.json`. Do not read `tools/` or `tools/fg_bundle.py`.
2. Recompute the canonical JSON of `bundle.json` from scratch and hash it.
3. Compare with `manifest.sha256`.
4. Verify `signatures/demo.sig` over the address using `signatures/demo.pub` (Ed25519, base64-decoded).
5. Check that every digest under `objects/` is the sha256 of the file with that name.
6. Report: agreement or the first differing byte/field, and whether your implementation disagreed with ours
   because of the format description (a documentation defect) or because of your own code (a rebuild defect).

**Agreement on the address and the signature, with differences only in diagnostics, counts as agreement.**

## What this does not prove

- That the claim is true. The claim says the analysis was checked against a policy; it does not say the system is
  safe. See `docs/31-…` and `docs/36-ROUND7-SYNTHESIS.md`.
- That the demo key means anything. It was generated for this fixture and is not trusted by anyone. Verifying with
  it proves the signature is well-formed, not that the signer is trusted.

## Known gaps of the description

Written down deliberately, because a rebuild that trips over them is doing its job:

- `objects` and `subjects` overlap: the same digest appears in both. A rebuild may reasonably ask which is
  authoritative.
- `signatures/demo.role` is not covered by the signature. A rebuild may reasonably call that a defect.
- There is no field for the verifier's version, so a rebuild cannot check which program produced the verdict.

If you hit one of these, that is a finding: report it and it becomes a card.
## A resolved hazard, kept in the record

On the first attempt this repository shipped the bundle through `.gitattributes` with `* text=auto eol=lf`.
A fresh clone rewrote the object files, their digests stopped matching their names, and the bundle verified as
`INVALID` — on a clean checkout, with nobody having touched it.

Object file names **are** their sha256, so any EOL normalisation is corruption. Fixed with
`fixtures/** -text -eol` and `fixtures/sample-bundle/** binary`. The check is now part of shipping: clone the
repository into a temporary directory and verify the sample bundle there; if it is not
`SIGNED_AND_CONSISTENT`, the repository is corrupting its own artifact.