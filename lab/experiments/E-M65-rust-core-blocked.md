---
id: E-M65
hypothesis: H-M65
status: completed
base_commit: "1ad26bc"
started: "2026-10-28T15:50:00+03:00"
finished: "2026-10-28T16:20:00+03:00"
environment: "Windows, cargo 1.99.1 (x86_64-pc-windows-gnu), rustc 1.99.1"
command: "cargo build --offline (and with network), in core-rs/"
threshold: "Pre-registered: choose the language for the verifying core on merit, not on what happens to be installed, and adopt it only if a build produces a binary that reproduces the sample address 5336c02a… and both V2 signatures. A port that cannot be compiled is not a port."
result: "DECISION MADE, EXECUTION BLOCKED. Rust is the right language for the verifying core and the ADR records why: it is the only candidate with a credible path to being verified itself (hax, Aeneas, Kani), and five of the 34 adversarial breaks are unrepresentable in it by type (a level string that is nearly right, NaN clearing a comparison, a string where a boolean belongs, an absent field skipping a check, duplicate identifiers inflating a floor). But the build cannot run here: the toolchain is the windows-gnu target and every build script fails to link (collect2.exe: ld returned 1), while cargo's own download path is broken over schannel even though the same URL is reachable from PowerShell. Writing uncompiled Rust would violate the rule that no artifact counts before a run, so core-rs/ carries the project skeleton and a README stating the blocker, ADR-0017 is marked proposed-blocked, and the Python core remains the only implementation that produces verdicts."
verdict: refutes
---

# E-M65 — the language decision, and the build that would not run

## The decision

`ADR-0017`: **Rust for the verifying core**, Python unchanged for the enumerators and experiment harnesses, the
artifact format untouched. The argument is not taste:

1. **It can be verified itself.** `hax` (Rust → F*/Coq/Lean), `Aeneas` (Rust → Lean), `Kani` (bounded model
   checking) all take Rust and none take Python, Go or TypeScript. [docs/22](../docs/22-FORMAL-TOOLING.md) proposed formalising the verdict
   algebra; Rust is the only candidate where the code and the proof can be about the same artifact.
2. **Five of our 34 breaks are unrepresentable in it by type** — the level string that was nearly right
   (`E-M42` B1), `NaN` clearing a density floor (`E-M60`), `vanished: "false"` counted as coverage, a missing
   `analysed_paths` skipping a check (`E-M62`), and duplicate `path_id` inflating a floor (`E-M50`).
3. **Deployment and embedding.** One static binary in CI, and an FFI/WASM path the first time the gate has to
   run inside somebody else's process.

TypeScript was started first and deleted: JSON-native, but its types vanish at runtime, which is the plane our
defects lived on. Go is the closest second and has no verification toolchain.

## Why it is recorded as a refutation

```
cargo 1.99.1 · rustc 1.99.1 · target x86_64-pc-windows-gnu · 390 crates cached locally
cargo build --offline
  error: linking with `x86_64-w64-mingw32-gcc` failed: exit code: 1
  collect2.exe: error: ld returned 1 exit status     (generic-array, serde_json, every build script)
cargo build (online)
  error: failed to download ... SSL connect error (schannel) from static.crates.io
```

The crates are cached and the same URL works from PowerShell, so neither dependencies nor the network as such
are the obstacle: the **linker** is. The GNU target cannot link in this environment.

The pre-registered threshold said the port counts only when a build produces a binary that reproduces the
sample address and both V2 signatures. It does not, so the port is not implemented — and writing Rust that has
never been compiled would be exactly the claim-without-a-run this repository exists to refuse.

## What is in the tree

- `core-rs/` — the cargo project skeleton and a README that states the blocker, what is installed, what fails,
  and the two ways to unblock it (MSVC build tools, or a complete mingw-w64).
- `ADR-0017` — proposed, blocked, with the merits argued and the execution gap named.
- No half-built third implementation: the TypeScript scaffold was deleted rather than left as a second
  unverified core.

## What unblocks it

An environment change, not a code change: `rustup target add x86_64-pc-windows-msvc` with the Visual Studio
Build Tools, or a working `mingw-w64`. Both are downloads in the hundreds of megabytes, and the MSVC route may
need administrator rights. Until then the Python core answers, and the differential with the third-party
verifier keeps the two-implementation check alive.
