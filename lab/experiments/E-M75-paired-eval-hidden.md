---
id: E-M75
hypothesis: H-M75
status: completed
base_commit: "e9dee93"
started: "2026-10-29T01:05:00+03:00"
finished: "2026-10-29T01:30:00+03:00"
environment: "Windows, qwen3.8-flash, hidden-bypass fixture, five questions, two arms"
command: "python lab/paired-eval.py --dry-run; both arms through the session on fixtures/hidden-bypass"
threshold: "Pre-registered: on a schema where the bypass is NOT listed but must be combined from facts (a grant on a view whose INSTEAD OF trigger writes the table, plus a SECURITY DEFINER function), arm B must name strictly more true bypasses than arm A, with no more false ones."
result: "REFUTED AGAIN, and this time the schema was built to make the difference appear. Arm A, given only the catalogue, reasoned correctly to BOTH bypasses: the view grant -> INSTEAD OF trigger -> table write, and the SECURITY DEFINER function granting a caller a write it has no privilege for. It named them explicitly and correctly, without path ids. Arm B named the same two, and additionally cited wp_mig ids, the trigger chain and coverage 0.0. One arm-A call of five returned empty again. So the honest count over two experiments is 0 for the recall hypothesis and 2 observations of the same pattern: the inventory does not find what a competent reader cannot find; it produces an artifact a reader can check, and it does so without requiring that reader to be competent in SQL semantics."
verdict: refutes
---

# E-M75 — the fixture built to make the difference appear, and the difference did not appear

## Why this experiment was different

`E-M73` was inconclusive by construction: its schema listed every path in the catalogue, so both arms had the same
information. `E-M74` then produced a schema where the bypass is **not listed** — a grant on a view whose `INSTEAD
OF` trigger writes the table, and a `SECURITY DEFINER` function that writes a table the caller has no privilege
for. If the inventory were going to show a recall gain, it would be here.

## What happened

**Arm A found both bypasses.** Its answer to `q1`, unprompted:

> app_rw -> UPDATE on sample2.accounts_v -> accounts_v_write INSTEAD OF UPDATE trigger ->
> sample2.accounts_v_update() -> UPDATE sample2.accounts …
> app_rw -> SELECT sample2.set_balance(p_id, p_amount) -> SECURITY DEFINER body executes UPDATE …

That is correct, complete, and derived from the catalogue alone. **Arm B found the same two**, and added
`wp_mig_*` identifiers, the trigger chain, `coverage 0.0`, and `NC-01`/`NC-02`.

So the pre-registered threshold — arm B strictly more — **fails**. One arm-A call of five returned empty again,
which is the third time this harness has dropped a call; that is a harness defect to fix, not evidence either way.

## What two experiments now say together

| experiment | fixture | recall difference |
|---|---|---|
| `E-M73` | every path listed | none — arm A found the same three |
| `E-M75` | bypass hidden in a combination | none — arm A found the same two |

Two negatives on schemas of a few hundred tokens. The honest reading:

> The inventory does not find what a competent SQL reader cannot find. It produces a **checkable artifact**, and
> it does so without requiring the reader to be competent in SQL semantics — which is what makes it usable by an
> auditor, an underwriter, or a lawyer, and what makes two answers comparable.

That is a weaker product claim than "better answers", and it is the one the evidence supports. It also aligns with
what the ceiling has said all along: consistency, not truth.

## What this does not rule out, and the experiment that would test it

- **Scale.** These schemas have one table and five paths. At 1400 tables a reader cannot hold the graph in mind;
  whether the artifact helps there is untested and is the only version of the recall claim still plausible.
- **Non-expert readers.** Both arms were the same model. A reader who does not know that an `INSTEAD OF` trigger
  makes a view writable is exactly the case the artifact serves, and that reader was never in the experiment.

The next experiment, if it is run, is therefore: one large real schema, and a *deliberately weakened* arm A — a
model told to answer from the catalogue without reasoning about Postgres semantics — to see whether the artifact
substitutes for knowledge. That is a different hypothesis from the two that failed, and it should be pre-registered
as such.

## What changes in the product story

`docs/21-FINAL-ASSESSMENT.md` must not claim that a consumer answers better. It should claim that a consumer can
**check**, and that the checking does not require Postgres expertise. Anything stronger is now contradicted by two
experiments of my own.
