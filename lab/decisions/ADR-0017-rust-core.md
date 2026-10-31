# ADR-0017 — the verifying core is Rust; the enumerators stay Python

**Status:** accepted, 2026-10-31. Settled on merit on 2026-10-28 and kept `proposed` because the core could not
be linked on the author's machine — every build script failed with `collect2.exe: error: ld returned 1 exit
status` under the MinGW toolchain (see `core-rs/README.md`). The blocker was environmental, not architectural:
on Linux the crate links, and `.github/workflows/guards.yml` now builds it, runs its own tests, and diffs it
against the Python core on the cross-family cases (`E-M67`), the claim CLI cases (`E-M68`) and the report facts
(`E-M83`) on every push. The Python core stays as the differential partner — a second implementation is an
asset here, not a fallback nobody runs.

## The decision

Split the repository by what each half has to be good at:

| half | language | why |
|---|---|---|
| **verifying core** — canonicalisation, the address, signatures, the level ladder, the checks that decide a verdict | **Rust** | the only candidate that can be *verified itself*, and the only one whose type system makes half our defects unrepresentable |
| **enumerators and experiment harnesses** — SQL against Postgres, file writing, campaign scripts | **Python** (unchanged) | they shell out to `psql` and write JSON; a rewrite buys nothing and costs weeks |
| **artifact format** | JSON, unchanged | the split is behind the same bytes, so a consumer never learns which language answered |

The boundary is one direction only: a Rust binary consumes an inventory and a claim and prints a verdict. It
never enumerates, never connects to a database, and never writes into the repository.

## Why Rust, on merit rather than availability

**1. It can be verified itself.** The product's thesis is that a claim should be checkable rather than
trusted. A verifier written in a language with no verification path is a weak place to stand: `hax`
(Rust → F*/Coq/Lean), `Aeneas` (Rust → Lean), `Kani` (bounded model checking) and `Creosot`/`Prusti` all take
Rust as input and none take Python, Go or TypeScript. `docs/22-FORMAL-TOOLING.md` proposed formalising the verdict algebra;
Rust is the only candidate language where the code and the proof can be about the *same* artifact.

**2. Half of this repository's 34 adversarial breaks are unrepresentable in it.**
- `"PROVEN "` with a trailing space printed `PROVEN` — an enum parsed at the boundary makes a near-miss a
  parse error, not a comparison that silently misses (`E-M42` B1).
- `NaN` cleared a density floor because `NaN < 0.15` is false — `serde_json` will not produce a non-finite
  number, and a `checked` conversion refuses it explicitly (`E-M60`).
- `vanished: "false"` counted as coverage because a string is not `true` — a `bool` field cannot hold a string.
- A missing `analysed_paths` skipped a whole check — `Option<T>` forces the absence to be handled (`E-M62`).
- Duplicate `path_id` inflated a floor — a `HashMap`/`HashSet` makes identity counting the default.

That is not aesthetics. It is five named defects, each of which cost a card and a round.

**3. Deployment matches how the tool is used.** A single static binary in CI, no interpreter, no virtualenv,
no dependency on the host's Python patch level; and it can be embedded through FFI or compiled to WASM the
first time the gate has to run inside somebody else's process — the trigger `docs/22-FORMAL-TOOLING.md` named for revisiting the
language question at all.

## Why not the others

- **Go** is the closest second: fast to write, easy deployment. But it cannot express the level ladder as a sum
  type, has no verification toolchain, and its interfaces would push the same runtime-shape errors back to us.
- **TypeScript** is JSON-native and pleasant, but the types vanish at runtime — the exact plane on which our
  defects lived — and there is no formal path.
- **Python** is where the enumerators belong and where the defects were born. Keeping it for the verifying core
  would mean arguing that 34 breaks were about discipline rather than about the language's affordances, and the
  record does not support that.

## What this costs, and what it does not fix

- A second implementation to keep in step. That is a cost **and an asset**: `E-M57` showed a second
  implementation finds what three attack rounds miss, so the Python core stays as the differential partner
  rather than being deleted.
- The port is incremental. The first delivery is canonicalisation, the address, the two signature message
  forms, the level ladder and the object/role checks — enough to verify the sample bundle end to end. Coverage
  arithmetic and the exclusion rules follow.
- **It does not move the ceiling.** A verifier in Rust still reads a document the claimant wrote. `NC-01` and
  `ADR-0010` are unchanged by the language choice.

## What this decision does NOT do

- It does not make the Python core authoritative or the Rust core decorative; while both exist they are
  compared on every mutation, and a disagreement is a defect in one of them.
- It does not promise proofs. `hax` is a *path*, not a deliverable; claiming "verified core" before a proof
  exists would be the exact over-claim this repository refuses.
- It does not change the artifact format, the address rule, or any verdict semantics. A consumer sees the same
  bytes and the same verdicts, or the port is wrong.
