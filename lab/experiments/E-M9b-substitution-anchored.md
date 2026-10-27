---
id: E-M9b
hypothesis: H-M9
status: completed
base_commit: "uncommitted tree; bundle and verifier digests are inside the artifacts"
started: "2026-10-27T22:00:00+03:00"
finished: "2026-10-27T22:08:00+03:00"
environment: "Windows, CPython 3.13.11, cryptography 50.0.2 (Ed25519)"
command: "python lab/e-m9-run.py"
threshold: "Same six cases, same pre-registered threshold as E-M9: 6/6, any green verdict fails."
result: "6 of 6 caught. D-1a/b/c rejected on digest mismatch, D-1d rejected because the swapped key is not in the trusted set (POLICY_UNTRUSTED), D-2a/b rejected because the claim's target differs from the target supplied by the caller (TARGET_MISMATCH). Reproducing run 1 with --no-anchors still yields 3/6, so the improvement is attributable to the anchors and not to a changed test."
verdict: supports
---

# E-M9b — substitution test with two external anchors

## What changed between the runs

Exactly two things, both outside the bundle:

1. `verify --trusted-keys <pem>…` — a signature counts only if its key is byte-identical to a key supplied
   out-of-band. This closes D-1d.
2. `verify --expect-target <commit>` — the claim's `target_lock` must equal the target the caller is actually
   looking at. This closes D-2.

The test itself did not change: `--no-anchors` reproduces run 1 and still catches 3/6, so the difference is
attributable to the fix.

## Run

```
D-1a code      INVALID                  CAUGHT
D-1b build     INVALID                  CAUGHT
D-1c config    INVALID                  CAUGHT
D-1d identity  INVALID                  CAUGHT   (POLICY_UNTRUSTED)
D-2a pair      not SIGNED_AND_CONSISTENT CAUGHT   (TARGET_MISMATCH)
D-2b pair      not SIGNED_AND_CONSISTENT CAUGHT   (TARGET_MISMATCH)

cases caught: 6/6   threshold: 6/6   RESULT: PASS
```

## Result: supported

The verifier now rejects all six. The two codes that carry the weight are `POLICY_UNTRUSTED` and `TARGET_MISMATCH`,
and both are refusals about **the world outside the bundle**, which is the only kind that can catch a correctly
signed false claim.

## What this does not establish

- **That the bundle is honest.** An anchor says who signed and what target is meant; it says nothing about whether
  the analysis behind the claim was right. That is round 7's finding, unchanged.
- **That the anchors are trustworthy themselves.** A trusted key list is a file; whoever supplies it decides what
  is trusted. That is a policy question (ADR-0010), not a cryptographic one.
- **D-2b as specified.** The two pair cases currently differ only in the re-signing path, not in the strength of
  the lie; a stronger D-2 (manifest numbers consistent under the wrong target) needs a bundle whose inventory was
  produced for the other target, which requires the inventory to carry its own target lock — it does, so this is
  testable next round.

## Consequence

`fg_bundle verify` without `--trusted-keys` and `--expect-target` is documented as **not evidence**: it answers
"the bundle is internally consistent", which is precisely the round-7 trap. ADR-0010 records this.

## Log

`lab/logs/e-m9b-2026-10-27.log` — sha256 `918b5cafed2f0ec66f03d3e638588a3f0f3d5cd4df319ef033904d36a1c59943`.
