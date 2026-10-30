# What the PutnamBench harness gives a verifier of documents — the code-level list

Source: [`nearai/putnambench-deepseek`](https://github.com/nearai/putnambench-deepseek), read at file level:
`harness/pb.py` (the verifier and the work queue), `README.md`. `[docs/26](26-PUTNAM-AGENT.md) recorded the four *ideas*; this records
what is in the code, what I took, and what I deliberately did not.

## Taken, and now in this repository

| their code | ours | what changed |
|---|---|---|
| work queue: one TSV, `flock` on a sidecar, atomic temp+replace, claim by PID, `reap` by liveness, explicit `requeue` | `lab/queue.py` | implemented; used to drive the cross-audit campaign |
| "a claim records the owning PID; liveness is decided by the PID, never by elapsed time" | same | they learned it from an orphaned solver; a Lean run takes days, a reaped live worker throws away real work |
| `claim` takes only `todo`, so retry is an explicit act | same | pass@1 vs pass@2 is a human decision, not a scheduler accident |
| selftest with **adversarial** cases, including "the frozen signature hidden in a comment" | `lab/selftest-guards.sh` (12 controls) | their case list is better than mine: every case names the message it expects |

## Not taken, and why

- **`prepare` / `stage` / `verify` for Lean.** No Lean in this product; the analogue of "verify" is `fg_verify`.
- **`costs.tsv`.** Their per-run cost ledger is right in principle. Mine has no per-run token accounting yet,
  because the model calls happen through the harness and are not instrumented. Recorded as a gap, not copied:
  a ledger with invented numbers is worse than none.
- **The 672-problem corpus.** Not a corpus of Postgres schemas.

## The one thing I should take but have not implemented

**The shadowing guard.** `pb.py` compares the statement textually — a frozen signature must appear verbatim — and
then adds a *semantic* check, because the text can be identical while a name it uses means something else:

```python
def shadowing(text, sig, thm, provided):
    """Names `text` redefines that also occur free in the frozen statement."""
    allowed = set(provided) | {thm}
    bound = sig_binders(sig)          # binders are not globals, or every helper is a false positive
    sig_idents = {t.split(".")[-1] for t in IDENT_RE.findall(sig)}
    return sorted(n for n in defined_names(text)
                  if n in sig_idents and n not in bound and n not in allowed
                  and not n.endswith("_solution"))
```

The comment above it is the reason it exists:

> the signature check is TEXTUAL, so it cannot see a proof that leaves the statement byte-identical while
> redefining what a name in it MEANS … `IsLeast s a` also requires `a` to be a lower bound, so dropping that
> conjunct throws away the whole problem — and the file still elaborates, has no `sorry`, and depends on no extra
> axioms.

**Our exact analogue, with the same shape and the same danger.** `declared_control_point` is matched by string
against `attribution.to` in the inventory. A claim can name `function:bank.audit_write`, and the inventory can
attribute paths to a *different* function that happens to render as the same string — a shadow in another schema,
a case difference, or a name that a later `CREATE OR REPLACE` repointed. The words match; the meaning does not.

The check to add (design, not code):

1. **Identity, not name.** A control point is `(schema, name, oid_or_signature)`. Two paths whose control point
   renders identically but differs in any component are `CONTROL_POINT_SHADOWED`, a refusal.
2. **Binder analogue.** Names that are local to a path (a function's own parameters) must not be treated as
   control points, or every function taking a `control` argument is a false positive.
3. **Provided set.** Anything the inventory's own source files already declared is part of the target, not a
   shadow — exact analogue of their `provided` set.
4. **Selftest case with the message it expects:** an inventory where `attribution.to` is `function:bank.audit_write`
   and a second function `bank.audit_write` exists in another schema, differing only by qualification.

Until that exists, the gate compares strings, and the PutnamBench comment explains precisely why that is not
enough.

## The sentence worth keeping

> A statement whose words are unchanged can still have been emptied.

That is also the honest summary of my own ceiling: an inventory whose paths are unchanged can still have been
emptied, and the only defence is a checker that compares meanings rather than strings.
