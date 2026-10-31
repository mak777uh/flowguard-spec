# Status of the Rust core

`ADR-0017` decided that the verifying core is Rust; on 2026-10-31 the decision moved from `proposed` to
`accepted`, because the crate now builds somewhere that counts.

## What runs now

`.github/workflows/guards.yml`, on every push and pull request:

```
cd core-rs && cargo build --locked && cargo test --locked
python3 lab/e-m67-run.py    # the claim arithmetic, Rust against Python on the cross-family cases
python3 lab/e-m68-run.py    # the claim CLI against the Python verifier
python3 lab/e-m83-run.py    # two report generators, the same facts
```

A core that is never built is a folder of source, not a core. These four steps are what makes the path in
`lab/decisions/ADR-0017-rust-core.md` a description of the repository rather than an intention.

## The Windows machine this was written on

The toolchain is installed (`cargo 1.99.1`, `rustc 1.99.1`, target `x86_64-pc-windows-gnu`) and 390 crates are
cached, but linking fails for every build script:

```
error: linking with `x86_64-w64-mingw32-gcc` failed: exit code: 1
collect2.exe: error: ld returned 1 exit status
```

A fresh download is also blocked for cargo specifically (`SSL connect error (schannel ...)` from
`static.crates.io`, while the same URL answers from PowerShell). Both are environment defects, not code
defects, and neither is a reason to keep the port unbuilt — CI links, and CI is where the parity runs.

What would make the local build work, if it is worth the download:

1. **MSVC target** — Visual Studio Build Tools, `rustup target add x86_64-pc-windows-msvc`, then build with
   `--target x86_64-pc-windows-msvc`.
2. **Complete MinGW** — for example
   `winget install --id BrechtSanders.WinLibs.POSIX.UCRT`, then put its `mingw64\bin` on `PATH`.

`lab/e-m67-run.py` already globs the WinGet package directory, so the harness works without a manual export once
a linker exists.

## What has not changed

- The Python core (`tools/fg_verify.py`) still produces the verdicts the product ships today; the Rust core is
  held to it on every push, and a disagreement is a defect in one of them.
- The harnesses resolve the binary per platform (`fg-core.exe` on Windows, `fg-core` on Linux). Hardcoding the
  `.exe` was why these runners had never executed under CI: they looked for a file that only exists on the one
  platform that could not link.
- Coverage arithmetic and exclusion rules are still being ported; what is ported is canonicalisation, the
  address, the two signature message forms, the level ladder, the object/role checks and the report generator.
