---
id: E-M9
hypothesis: H-M9
status: completed
base_commit: "uncommitted tree; bundle and verifier digests are inside the artifacts"
started: "2026-10-27T21:45:00+03:00"
finished: "2026-10-27T22:05:00+03:00"
environment: "Windows, CPython 3.13.11, cryptography 50.0.2 (Ed25519)"
command: "python lab/e-m9-run.py --no-anchors"
threshold: "D-1: 4 of 4 subject substitutions rejected with a machine-readable reason. D-2: 2 of 2 falsely attested pairs must NOT receive a green verdict. Any green verdict on any of the six cases fails the experiment."
result: "3 of 6 caught. D-1a/b/c (code, build, config) rejected on digest mismatch. D-1d accepted: swapping the signer for another key still returned SIGNED_AND_CONSISTENT, because the bundle carries its own public key and any key that signs the bundle's own address verifies. D-2a/b accepted: a validly signed bundle re-pointed at another target and re-signed with the original key passed, because nothing outside the bundle says which target the caller is looking at."
verdict: refutes
---

# E-M9 — substitution test, run 1: no anchors

## Pre-registration (unchanged from the original card)

Six cases. D-1: four subject substitutions must be rejected with a machine-readable reason. D-2: two falsely
attested pairs must not receive a green verdict. **Any green verdict fails the experiment as a whole.**

## Run

```
D-1a code      INVALID              CAUGHT
D-1b build     INVALID              CAUGHT
D-1c config    INVALID              CAUGHT
D-1d identity  SIGNED_AND_CONSISTENT  ACCEPTED — FAIL
D-2a pair      SIGNED_AND_CONSISTENT  ACCEPTED — FAIL
D-2b pair      SIGNED_AND_CONSISTENT  ACCEPTED — FAIL

cases caught: 3/6   threshold: 6/6   RESULT: FAIL
```

## Result: refuted

The experiment failed, and the failure is the useful part.

**D-1d — identity.** The bundle carries `signatures/<name>.pub` beside the signature. A verifier that trusts it
verifies whatever key signed the address, including a key invented a second earlier. Self-signed provenance is not
provenance.

**D-2a/b — falsely attested pair.** Re-pointing the claim at another target and re-signing with the *original* key
produces a bundle that is internally perfect: address matches, objects hash correctly, signature valid. Nothing
inside the bundle can notice, because the bundle is the only thing being consulted.

Both failures have one cause: **the verifier had no anchor outside the bundle.** This is mechanism T1 from round 1,
finally measured rather than described.

## What follows

Two anchors are required, and they are not part of the bundle: a **trusted key list** and the **target the caller
is actually looking at**. Implemented and re-run as `E-M9b`.

This card stays as it is — a failed pre-registered experiment with its cause named. The fix does not get to
rewrite the failure.
