---
id: E-M58
hypothesis: H-M58
status: completed
base_commit: "50c9f6e"
started: "2026-10-28T16:45:00+03:00"
finished: "2026-10-28T17:20:00+03:00"
environment: "Windows, CPython 3.13.11; two independent verifiers, 44 systematic mutations"
command: "python lab/e-m57-run.py"
threshold: "Pre-registered: with 44 mutations - every claim field, every signature file broken four ways, every role field, formatting changes that must be harmless, structural damage - the two implementations must agree, except where one of them is demonstrably wrong and the divergence is written down with its reason."
result: "44 cases, 1 remaining divergence, and it is the third-party verifier that is wrong: it accepts a signer whose .pub cannot be parsed, so a signature is counted as evidence against a key that was never loaded. Ours refuses. Recorded as F-2-1 in the interop ledger rather than patched, because a divergence that is written down is evidence and a divergence that is quietly matched is a lost bug. Three real defects were fixed on our side first: the manifest address was read with strip(), so a truncated or CRLF manifest verified while a verifier built from the page refused it - it is now exactly 65 bytes, 64 hex and one LF; and two harness defects of mine, a missing '+' marker that turned a must-pass case into an expected failure."
verdict: supports
---

# E-M58 — 44 mutations, one honest divergence

## What was run

Every claim field changed; `manifest.sha256` uppercased, truncated, given CRLF, stripped of its LF; four ways of
breaking `owner.sig`; `owner.pub` replaced and truncated; the role document edited field by field, given an extra key,
stripped of `accepted_scope`, set to `null`, reformatted; objects renamed, truncated, added, deleted, renamed to a wrong
digest; directories emptied; the same key holding both roles; and three formatting changes that **must not** change the
verdict.

## Ours, fixed

**The manifest was read with `.strip()`.** A `manifest.sha256` that was truncated, or written with CRLF, verified — while
a verifier built from the page refused it, because the page fixes the file at 65 bytes. Ours was more tolerant than the
contract. Now: exactly 64 hex characters and one LF, or `REPORT_BUNDLE_INCONSISTENT`.

## Theirs, wrong

```
demo.pub truncated:  ours=INVALID   theirs=SIGNED_AND_CONSISTENT
```

A signer whose public key cannot be parsed is counted as evidence by the third-party verifier — a signature checked
against a key that was never loaded. Ours refuses.

Recorded as **F-2-1** in `interop/reviews/LEDGER.md` and in the harness's `KNOWN_DIVERGENCES` with the reason. Not
patched around: a divergence that is written down teaches something, and a divergence quietly matched loses the bug.

## Two of my own, found by the same run

The must-pass marker (`+`) was missing on a reformatting case, so the harness expected a refusal where the artifact
must stay valid; and a patch applied twice left a duplicated block, which the verifier's own baseline caught immediately
because the valid bundle stopped parsing.

## What it establishes

Two independent implementations of one page, agreeing on 44 mutations except where one of them is provably wrong. That
is the strongest evidence available without a third party: not "our tests pass", but "someone else's tests agree, and
where they do not, the disagreement is diagnosable".
