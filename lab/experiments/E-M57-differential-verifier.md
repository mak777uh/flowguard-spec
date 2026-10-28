---
id: E-M57
hypothesis: H-M57
status: completed
base_commit: "a6437c2"
started: "2026-10-28T16:10:00+03:00"
finished: "2026-10-28T16:40:00+03:00"
environment: "Windows, CPython 3.13.11; two independent verifiers of the same written contract"
command: "python lab/e-m57-run.py"
threshold: "Pre-registered: our verifier and one written by a stranger from the format page alone must agree on every mutation of the sample bundle. Any disagreement is a defect in one of them, and which one is decided by the page, not by seniority."
result: "Ten mutations, one disagreement, and the disagreement was ours: a file added to objects/ that the manifest does not declare verified SIGNED_AND_CONSISTENT. The page forbids it, the stranger's verifier refused it, and none of our three adversarial rounds had ever tried it. Fixed: objects/ is now compared with the manifest in both directions - undeclared is REPORT_BUNDLE_INCONSISTENT, absent is MISSING_EVIDENCE. After the fix, ten of ten mutations agree: object flipped, role statement edited, accepted_scope rewritten, version bumped, signature deleted, role deleted, unsigned role appended, object truncated, undeclared object added, declared object deleted."
verdict: supports
---

# E-M57 — two implementations of one page, and the bug was ours

## What the differential is

`E-M56` produced something no round before it had: a **second implementation** of the same written contract,
written by an agent that never saw our code. Two implementations of one specification are a stricter test than
either alone, because they fail differently.

`lab/e-m57-run.py` mutates the sample bundle ten ways, runs both verifiers, and compares only one bit: would this
artifact be accepted?

## The disagreement

```
undeclared object added: ours=SIGNED_AND_CONSISTENT  theirs=REFUSED
```

A file dropped into `objects/` that `bundle.json` does not declare passed our verifier. The page says it must not,
the stranger's verifier refused it — and **three adversarial rounds and 40 cases had never tried it**, because every
attacker had been thinking about documents and fields, not about extra files.

Fixed in the verifier: `objects/` is compared with the manifest in both directions — an undeclared file is
`REPORT_BUNDLE_INCONSISTENT`, a declared file that is missing is `MISSING_EVIDENCE`.

## After the fix

Ten of ten mutations agree:

| mutation | ours | theirs |
|---|---|---|
| object byte flipped | refused | refused |
| role statement edited | refused | refused |
| accepted_scope rewritten | refused | refused |
| bundle_version bumped | refused | refused |
| signature deleted | refused | refused |
| role file deleted | refused | refused |
| unsigned role appended | refused | refused |
| object truncated | refused | refused |
| undeclared object added | refused | refused |
| declared object deleted | refused | refused |

## Why this belongs in the method

The three attack rounds tested *documents* a claimant writes. This tested *agreement between two readers of one
page* and found a hole in a place nobody had looked: the directory around the artifact. Two implementations disagree
where a specification is silent or one of them is wrong, and it takes ten minutes to find out which.

The stranger's verifier is now kept at `interop/verifiers/third-party-verifier.py`, with its own decision log beside
it, and the differential runs in the round ritual.

## What it does not establish

- That either verifier is complete. Two readers can share a blind spot; they share the page.
- That the ten mutations are the interesting ones. They were chosen by the author — the same hand that missed the
  undeclared object.
