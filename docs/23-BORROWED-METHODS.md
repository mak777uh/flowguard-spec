# What to borrow from NVIDIA auto-ontology, and what not to

Source: [`NVIDIA/auto-ontology`](https://github.com/NVIDIA/auto-ontology) and its evaluation set
[`NVIDIA/ontology-sql-eval`](https://github.com/NVIDIA/ontology-sql-eval). Read from the repository page and the
summary provided by the owner; the README body was not fully retrievable here, so claims about internals below
are marked as *reported* rather than verified.

## What it is

A framework that builds a **semantic layer over data**: it extracts schema metadata from Postgres, Databricks,
Snowflake or DuckDB, reconciles divergent definitions of the same metric, and stores the result as a graph in
Postgres with pgvector. An agent reaches it through MCP, a CLI or an API. Inference defaults to NVIDIA NIM
(Nemotron 3 Nano 30B for queries, an embedding model and a reranker), deployable with Helm or Docker Compose.
Corrections and successful queries are fed back into the ontology. **External pull requests are not accepted.**

## The one thing worth copying: the paired test

> the same question is answered by an agent with a bare schema and by an agent with the ontology, and both runs
> are scored by comparing the result … no separate model call is needed for the scoring.

That is an **ablation harness**, and it is exactly the measurement this repository has never made. Our product
claim is that the artifact changes a decision. We have measured the engine exhaustively — 25 acceptance
scenarios, 34 adversarial breaks closed, 44 differential mutations — and we have never measured whether a
consumer who reads the bundle answers better than a consumer who reads the raw schema.

The design transfers directly:

```
question set  N questions about one schema (fixed, written before any run)
arm A         agent receives the bare catalogue (tables, functions, triggers)
arm B         agent receives our inventory + verdict + NC vocabulary
scoring       both answers compared against a ground-truth list written from the catalogue,
              not from our tool (otherwise the tool grades itself)
metric        agreement on the set of write paths, and on which bypass the control point
```

Arm A versus arm B on the same model is the only honest way to say the report adds anything. If arm B does not
beat arm A, the product is a report generator and should be described as one.

## What is not worth copying

- **The stack.** pgvector, Next.js, FastAPI, Helm and NIM are four services to run a graph query. Our artifact is
  a directory of JSON and two hundred lines of Python; adopting their deployment shape would triple the surface
  for no measurable gain.
- **The contribution model.** No external PRs means the framework can be *read* but not *relied on* as
  infrastructure: a defect we find cannot be fixed by us. That is acceptable for an idea, not for a dependency.
- **The problem.** Auto-ontology verifies that **generated SQL matches the definitions**; we verify that **a
  declared control point actually covers the write paths**. Both are "consistency, not truth", but the objects
  are different. Merging them would let us claim query correctness we do not test — the exact over-claim this
  repository spends its time refusing.

## The narrower borrow: control points as a graph

Their graph carries lineage and inheritance between entities. We already enumerate paths between a control point
and a table; rendering that as a graph with inheritance (a view over a table, a partition of a table, a function
calling a function) is a **view of data we already have**, not a new engine. Worth doing when a consumer asks
to see the shape rather than a list — not before, because a graph nobody queries is a diagram.

## Next step if accepted

`lab/paired-eval.py` (not written yet): one question set on the fixture, two arms, one model, ground truth written from the
catalogue. Threshold pre-registered: arm B must find **strictly more** true paths than arm A, with no additional
false paths, or the artifact's product claim is not supported and readiness `P2` stays at zero for a reason we
can name.
