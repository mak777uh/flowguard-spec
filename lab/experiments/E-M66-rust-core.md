---
id: E-M66
hypothesis: H-M66
status: completed
base_commit: "d2108e6"
started: "2026-10-28T15:50:00+03:00"
finished: "2026-10-28T17:05:00+03:00"
environment: "Windows, rustc 1.99.1 (windows-gnu) + WinLibs UCRT 16.2.0, CPython 3.13.11"
command: "cargo test --offline && cargo build --offline in core-rs/ && python lab/e-m66-run.py"
threshold: "Pre-registered: the Rust core must build, pass its unit tests, reproduce the sample address 5336c02a… and both signatures, and then agree with the Python core on every mutation of the sample bundle. A disagreement is a defect in one of them and is fixed before the card is written."
result: "Built and adopted. The port: canonical JSON with recursive code-point ordering, the address, both message forms (v2 and the two v1 forms), Ed25519 verification, the level ladder as an enum, floors keyed to the printed level, and distinct-path counting over identifiers. Six unit tests pass, including the two that encode past defects: a level string with a trailing space is not a level, and one row relabelled eight times is one row. Against the sample: address 5336c02a… recomputed and matched, both signatures verified as v2. The differential found TWO REAL RUST BUGS on its first run - the port never hashed objects against their names, and it did not require a signature for every role - both closed. It also found a defect in the ARTIFACT: the sample was fg-bundle/2 while its acceptance was signed under the v1 message, so Python and Rust agreed on a reading that should never have been publishable. A rule now refuses a v1-bound acceptance inside a v2 artifact, and the sample was re-signed under v2."
verdict: supports
---

# E-M66 — the Rust core, and what the differential found on its first run

## What was installed

The Rust toolchain was present but unusable: the `windows-gnu` host could not link (`collect2.exe: error: ld
returned 1`), and cargo's own download path failed over schannel while the same URL worked from PowerShell.
`WinLibs UCRT 16.2.0` via winget fixed the linker; the 390 crates already cached made the offline build possible.

## What was written

`core-rs/`, ~600 lines, no dependency it does not use:

- **canonical JSON** with recursive code-point ordering, `,`/`:` separators, no trailing newline, UTF-8;
- **the address**, recomputed and compared with the manifest, which must be exactly 65 bytes;
- **two message forms** — v2 (`sha256("fg-bundle/2|" + address + "|" + role_digest + "|" + scope)`) and the
  two v1 forms — with the binding used reported, never substituted silently;
- **Ed25519** verification, PEM parsed by hand (SPKI's last 32 bytes) so the core has one fewer dependency;
- **the level ladder as an enum**, floors keyed to the printed level, and distinct paths counted by identifier.

Six unit tests pass, two of which encode past defects as assertions: `"PROVEN "` is not `PROVEN`, and one row
relabelled eight times is one row.

## The two Rust bugs the differential found immediately

```
object byte flipped      python=False  rust=True     ← the port never hashed objects against their names
a signature deleted      python=False  rust=True     ← a role with no signature was not refused
```

Both are exactly the class the port was supposed to eliminate, which is the honest lesson: a language makes some
defects unrepresentable, not all of them. Both closed before the card was written; ten of ten mutations agree.

## The artifact defect it found

The sample bundle is `fg-bundle/2`, and its acceptance was signed with the **v1** message — the one that excludes
`accepted_scope`. Python and Rust agreed on that reading, which is why neither had flagged it: the artifact was
internally inconsistent in a way both implementations were willing to accept.

Now: a `risk_acceptance` bound under a v1 form inside a `fg-bundle/2` artifact is refused, and the sample was
re-signed under v2. Both cores report `{"demo": "v2", "owner": "v2"}` and `SIGNED_AND_CONSISTENT`.

## What this does not do

- It does not make the Rust core the only one. Two implementations that disagree are the cheapest oracle we
  have; the Python core stays as the reference and the differential stays in the ritual.
- It does not prove anything. `hax`/`Aeneas` remain a path, not a deliverable: "the core is in Rust" is a
  statement about affordances, not about theorems.
- It does not move the ceiling. A faster verifier of a claimant's document is still a verifier of that document.
