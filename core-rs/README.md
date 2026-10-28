# Status of the Rust core — blocked by the toolchain on this machine

`ADR-0017` decided that the verifying core should be Rust. The reasoning stands; the build does not work here.

## What is installed

```
cargo 1.99.1 (5f94df478 2026-08-27)
rustc 1.99.1 (58cf8f9c6 2026-10-13)
```

Target: `x86_64-pc-windows-gnu`. 390 crates are already cached locally, including `sha2`, `serde_json`,
`ed25519-dalek`, `curve25519-dalek` and `base64` — so the dependency set is not the problem.

## What fails

```
error: linking with `x86_64-w64-mingw32-gcc` failed: exit code: 1
collect2.exe: error: ld returned 1 exit status
```

Every build script fails to link, including `generic-array` and `serde_json`. The GNU linker of the MinGW
toolchain is not usable in this environment, and the network path for a fresh download is also broken for
cargo specifically (`SSL connect error (schannel ...)` from `static.crates.io`, while the same URL is
reachable from PowerShell). So the toolchain is present but cannot produce a binary.

## Why this stops the port rather than slowing it

Writing Rust that has never been compiled would violate the rule this repository is built on: no artifact
counts as evidence until a run produces it, and a port that cannot be built cannot be tested, differentialled,
or claimed. Shipping unbuilt source as "the new core" would be exactly the kind of statement the readiness
tiers exist to refuse.

## What would unblock it

Either of these, both of which are an environment change rather than a code change:

1. **MSVC target** — install the Visual Studio Build Tools and
   `rustup target add x86_64-pc-windows-msvc`, then build with `--target x86_64-pc-windows-msvc`.
2. **Working MinGW** — install a complete `mingw-w64` toolchain and point `RUSTFLAGS`/PATH at it, so
   `x86_64-w64-mingw32-gcc` links.

Both need a download measured in hundreds of megabytes and, for the MSVC route, possibly administrator rights.

## How to build it here

```powershell
winget install --id BrechtSanders.WinLibs.POSIX.UCRT --accept-package-agreements --accept-source-agreements
# then add the WinGet package's mingw64\bin to PATH, or let the harness do it:
cd core-rs; cargo test --offline; cargo build --offline
```

`lab/e-m67-run.py` finds that toolchain by globbing the WinGet package directory, so the harness works without
a manual export; a bare `cargo build` in a shell that lacks MinGW will fail to link, which is the state recorded
below.

## Meanwhile

- The Python core remains the reference implementation and the only one that produces verdicts.
- The TypeScript scaffold that was started and then abandoned is deleted, not left half-built: a third
  implementation with no tests is worse than two.
- The decision is recorded as `proposed`, not `accepted`, and `docs/STATUS-v0.md` continues to describe what
  actually runs.
