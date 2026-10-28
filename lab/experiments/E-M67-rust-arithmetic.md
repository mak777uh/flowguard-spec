---
id: E-M67
hypothesis: H-M67
status: completed
base_commit: "3ebb6f4"
started: "2026-10-28T17:20:00+03:00"
finished: "2026-10-28T17:55:00+03:00"
environment: "Windows, rustc 1.99.1 + WinLibs UCRT, CPython 3.13.11"
command: "cd core-rs && cargo test --offline && cd .. && python lab/e-m67-run.py"
threshold: "Pre-registered: the claim arithmetic ported to Rust must hold the six cases other model families broke in Python - NaN density, sampled completeness, growth declared false with an unpublished delta, vanished as a string, an honest report, a lying report - as unit tests that fail if the rule regresses, and the Python core must still agree on the same six."
result: "Ported and green. core-rs/src/claim.rs carries the arithmetic: strict level parse, kind whitelist, duplicate path_id, finite density with a band, truncation from completeness_claim partial|sampled or truncated kept<total, growth from a delta that has a baseline, coverage over attributed non-vanished paths whose sources exist, report reconciliation with analysed_paths required above the floor level, floors keyed to the printed level, and the clamp to the claim. Nine new unit tests plus the existing six: 15 pass. lab/e-m67-run.py re-runs them and compares the Python core on the same six cases: 6 of 6 agree."
verdict: supports
---

# E-M67 — the arithmetic that every break landed in, now in Rust

## What was ported

`core-rs/src/claim.rs`, ~300 lines, no dependency beyond `serde_json`:

| rule | why it exists |
|---|---|
| the level is parsed, never carried as a string | `"PROVEN "` printed PROVEN with exit 0 (`E-M42` B1) |
| `path_id` must be unique and the floor counts identifiers | one row relabelled eight ways passed an eight-path floor (`E-M50`) |
| density must be finite and in `0..1` | `NaN` cleared the floor because `NaN < 0.15` is false (`E-M60`) |
| `completeness_claim` in `partial\|sampled` truncates the denominator | `sampled` passed as exhaustive (`E-M60`) |
| a delta with a baseline and unpublished growth blocks regardless of the flag | `perimeter_growth: false` cancelled a real delta (`E-M60`) |
| a delta with **no** baseline is not growth | a first inventory was punished for being first (`E-M61`) |
| `vanished` must be a boolean | the string `"false"` counted as coverage (`E-M60`) |
| the report needs `analysed_paths` above the floor level, and its coverage is compared with the inventory's | a report could skip the cross-check by omitting the list (`E-M62`) |
| the floor is keyed to the level being printed, then the verdict is clamped to the claim | asking for less must not buy more (`E-M42` B1/B2) |

**Fifteen unit tests pass**, nine of them new and each named after the attack it prevents. The Rust tests are the
machine-checked half: a regression fails `cargo test` before any harness runs.

## The comparison with Python

`lab/e-m67-run.py` re-runs the Rust tests and then puts the same six cases through the Python core. Six of six
agree — and the harness's first version taught something about testing rather than about code: the claim used in
those cases is capped by its own evidence tier, so "the report changed the verdict" was never the right
assertion. What the report changes is the **codes**, and the harness now asserts
`REPORT_BUNDLE_INCONSISTENT` for a lying report and no change for an honest one.

That is `E-M55`'s lesson for the fourth time: an assertion about a strong verdict is often really an assertion
about which refusal fired.

## What this does not do

- The Rust core is not yet wired to a CLI for claims; the arithmetic is exercised by tests and compared through
  the harness, which is honest but is not the same as the binary answering. The next step is `fg-core
  verify-claim --claim c.json --inventory i.json [--report r.json]`.
- It does not verify anything formally. `hax`/`Aeneas` are still a path, and "written in Rust" is a statement
  about affordances.
- It does not move the ceiling: the arithmetic is about a document, not about the system the document claims.
