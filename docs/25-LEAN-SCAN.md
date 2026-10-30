# Lean ecosystem scan, 2026-10-28 — what is useful, and two constraints it imposes

Scanned the public Zulip archive (83 streams, the whole index; the chat itself is login-gated, the archive is
not). Filtered for streams that could matter to a verifier of JSON artifacts and SQL write paths: **Program
verification** (116 topics), **CSLib** (137), **CSLib: Code Reasoning**, **Machine Learning for Theorem
Proving** (482), **batteries**, **lean4**, **Is there code for X?**, **job postings**.

## The finds that matter

### 1. `mvcgen` — monadic program logic, and the hole in it

A Lean 4 tool for verifying `do`-notation and imperative code against specifications, discussed heavily in the
stream ("Monadic program logic: Request for feedback", 105 messages; "Proving Option monad programs with
Std.Do"; "Does `mvcgen` support recursive functions?"). It is the closest thing to a working program logic in
Lean today.

**The constraint:** `while` loops in Lean core are marked `partial`, so nothing can be proved about them. From
[the thread of 2025-11-19](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/Verifying.20while.20loops.20\(with.20mvcgen\).html),
Lean FRO developers say a `while … decreasing` form with extrinsic termination is "on our radar" and "Q2 next
year seems realistic".

**Consequence for us:** the formal model of the verifier must be **structural recursion over lists** — folds,
not loops. That is already how `fg_verify.py` is written (comprehensions and folds over `paths`), so the model
is a transcription rather than a redesign. It is worth stating as a rule: **no `while` in the Lean model, ever**,
because a `while` would make the whole theorem vacuous until the FRO ships termination proofs.

### 2. `Float` is opaque — you cannot prove even transitivity

From [“We can't prove anything about Float right?”](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/We.20can.E2.80.99t.20prove.20anything.20about.20Float.20right.3F.html):
`theorem float_lt_transitive (a b c : Float) : a < b → b < c → a < c` **cannot be proved in Lean**, because
`Float` is opaque; one would need something like Flocq ported from Rocq. A partial Flocq port exists
(`mkaratarakis/HopfieldNet/.../Flocqv2.lean`) and is early.

**Consequence for us, and it is a design requirement:** the formal model must express coverage, density and the
floors in **`Nat` and `Rat`**, never in `Float`; floats appear only at the JSON boundary, where they are an
**assumption**, not a theorem. This matches what the artifact already says in its own limits section: number
rendering is unspecified beyond shortest round-trip. Now there is a reason to say it in the formal document: the
alternative is unprovable by construction.

It also explains a real defect: `NaN` cleared a density floor (`E-M60`). In a model over ℚ, `NaN` cannot exist.

### 3. Rust → Lean is real, and there are two routes

- [hax into lean](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/hax.20into.20lean.html) (3 messages, Sep 2025)
- [Lean version of Aeneas library](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/Lean.20version.20of.20Aeneas.20library.html) (Sep 2025)
- [What is the connection between Aeneas and Hax?](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/What.20is.20the.20connection.20between.20Aeneas.20and.20Hax.3F.html) (21 messages)

This is the evidence behind `ADR-0017`: the Rust core was chosen partly because these paths exist and take
Rust, not Python. The Rust build is still blocked by the linker here (`E-M65`).

### 4. CSLib, and code reasoning as a library

`CSLib` (137 topics) and `CSLib: Code Reasoning` (4) are Lean libraries for reasoning about code — worth
watching as an alternative to hand-rolling `mvcgen` specs if our model grows.

### 5. The trusted-computing-base caveat, from the community itself

[To what extent is Lean4 itself verified?](https://leanprover-community.github.io/archive/stream/236449-Program-verification/topic/To.20what.20extent.20is.20Lean4.20itself.20verified.3F.html)
(14 messages) — the answer is "partly, and not in the way a buyer assumes". Any "formally verified" sentence we
write must carry this, exactly as we carry `NC-01`.

### 6. Neighbours worth knowing

- **Tamarin ↔ Lean / security protocol verification** (25 messages) — if the trust and anchor model is ever
  formalised, this is the tool family for it.
- **Lean's equivalence of TLA+'s CONSTANT** — a TLA+ → Lean path exists; model checking is an alternative to
  proofs for the state machine of bundle verification.
- **Model checking** (26 messages) and **Iris Lean** — the separation-logic community is porting to Lean.

## What this changes in the plan

[docs/22](22-FORMAL-TOOLING.md) proposed formalising the verdict algebra in Lean. This scan narrows it into something executable:

```lean
-- the shape of the model, decided by the two constraints above
structure Inventory where
  paths : List Path            -- structural recursion only
  density : Option Rat         -- ℚ, never Float
  ...

def distinctPaths (inv : Inventory) : Nat := (inv.paths.map (·.id)).dedup.length
def levelOf (n : Nat) : Level := ...
theorem clamp_le_claim (c claimed : Level) : minLevel c claimed ≤ claimed
theorem floor_monotone {a b : Nat} (h : a ≤ b) : levelOf a ≤ levelOf b
theorem no_nan (x : Option Rat) : ...        -- vacuous by construction, and that is the point
```

with one honest assumption node — `floatRendering : Assumption` — because the JSON boundary cannot be proved.

## What none of this changes

The ceiling. Lean proves things about a model; the model is about a document the claimant wrote (`NC-01`,
`ADR-0010`). A verified verifier is a verifier you can trust more; it is not a witness you can trust at all.

## How to use this archive when we start proving

The Zulip is the highest-value reference for Lean 4 proofs, and its value is concentrated: a handful of streams
carry almost everything, and the archive is searchable without an account. This section is the reading plan for
the day the verdict algebra is actually formalised (`docs/22`, `docs/24`).

### Where the answers live

| stream | why it matters to us |
|---|---|
| **Program verification** | `mvcgen`, `Std.Do`, `do`-notation semantics, termination, havex/Aeneas threads — the toolchain for "prove things about code" |
| **CSLib** and **CSLib: Code Reasoning** | a library for reasoning about code; the alternative if `mvcgen` is too young for our shape |
| **Is there code for X?** | where "has anyone formalised JSON / rationals / decimals" is asked and answered |
| **metaprogramming / tactics** | when `omega`/`linarith` do not close an arithmetic goal and a custom tactic is cheaper than a proof |
| **batteries**, **lean4**, **mathlib4** | what is in the standard library versus what must be built |
| **Machine Learning for Theorem Proving** | if an AI prover is used, this is where the state of the art is honest about its limits |

### The three constraints already extracted (do not re-derive them)

1. **`while` loops are `partial`** in core Lean, so nothing can be proved about them; `while … decreasing` with
   extrinsic termination was "Q2 next year" as of 2025-11-19. The model must be **structural recursion over
   lists** — which is how `fg_verify.py` is already written.
2. **`Float` is opaque**: `a < b → b < c → a < c` is not provable. Coverage, density and floors must be `Nat`/`Rat`
   in the model, with floats existing only at the JSON boundary and declared as an assumption.
3. **The trusted computing base is partly unverified** — "to what extent is Lean 4 itself verified" has a careful
   answer, and any "formally verified" sentence we write must carry it, exactly as it carries `NC-01`.

### The queries to start with

```
mvcgen                        # the current program logic
Spec monad do                 # how a function is specified
termination partial           # why a loop cannot be proved yet
Rat decimal JSON canonical    # if a canonical numeric form is ever proved
hax / Aeneas                  # Rust to Lean, if the core is ever written in Rust
```

### What this archive cannot give

An answer about **our** model. Every thread is about Lean's semantics, not about what "coverage" means for a
database control point. The proof is ours to state; the archive tells us whether the statement is expressible.
