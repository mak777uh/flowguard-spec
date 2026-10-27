# INTEROP — compatibility with the sibling repositories

Two repositories, one owner, one method: this one (`flowguard-spec`, the product) and
[VecDHT](https://github.com/mak777uh/VecDHT) (the network prototype), with
[`-`](https://github.com/mak777uh/-) (the research bench) as the third. They were built by the same person
under the same constraints, and they are now being read against each other.

That creates two risks and one opportunity.

- **Risk — drift.** The same idea gets invented twice in two formats (an experiment card that differs in eight
  fields; a claim registry with two incompatible schemas). Then nothing can be compared and both lose credibility.
- **Risk — coupling.** Sharing a module layout means their refactor breaks our CI, and our deadlines shape their
  architecture.
- **Opportunity.** A *thin* shared substrate: formats and guards, which are domain-agnostic and cheap to keep
  aligned, while every product-specific decision stays private.

This file defines the substrate, the boundary, and the recurring cycle. It is deliberately short, because a
compatibility doctrine that itself needs maintenance is not worth having.

---

## 1. What is shared, and what never is

**Shared (the method kit).** Formats, files and checks that mean the same thing in all three repositories:

| # | Artifact | Canonical shape | Why shared |
|---|---|---|---|
| M1 | experiment card | `id`, `hypothesis`, `threshold` (fixed before the run), `status`, `result`, `adr` | so a result from one repo is readable in the other |
| M2 | metrics doc | every number carries the command that produces it | so a number can be re-shot by a stranger |
| M3 | claim registry | `id · claim · evidence type · strongest permitted wording · artifact` | so a claim is worded the same way everywhere |
| M4 | eliminations registry | each entry carries the evidence that killed it **and** what would revive it | so a review round costs something in both repos |
| M5 | status doc | works / partial / stub, written to be falsified | so "done" means the same thing |
| M6 | guards | secrets over files **and history**, broken links, claim lint | one standard of hygiene, not three |
| M7 | independent-rebuild test | recorded as a result, with the defects it caught | the external node both projects need |

**Never shared.** Module layout, crate/package names, domain models, threat models, invariants, ADRs that
change a spec, pricing, and anything that would make one repository's refactor a dependency of the other.

**The test for "is this shared?"** — *would a stranger need it to read our results?* If yes, it belongs to the
kit. If it only helps us build, it stays private.

## 2. The cycle

A compatibility pass runs **quarterly** and **after any change to a kit artifact in either repository**. It is
not a conversation; it produces a file.

1. Run `python lab/check-interop.py` here, and `python lab/check-interop.py --repo <sibling>` against the other
   repository.
2. Each run prints, per kit item: `present` / `partial` / `absent`, plus a short reason.
3. Diff the two reports into `docs/interop/<date>.md`: what matches, what drifted, what is missing.
4. One ADR per drift that requires a change on our side. No ADR, no drift — prose is not a fix.
5. Log the pass in the loop ledger as edge **(5) interop**, with the number of matched items as the delta.

**The pass never fails a build.** Structural churn is expected — the sibling is being restructured right now.
The report describes gaps; a gap is information, not an error. What *is* an error is claiming compatibility
without having run the check.

## 3. Development assumes compatibility, in this order

Any new artifact we invent is created in two layers:

1. **Kit-compatible first.** If it can be expressed in M1–M7, it is, and it goes into the kit proposal. If the
   canonical shape is insufficient, the extension is named (`kit/v0 + extension fg:coverage`) rather than
   silently forked into a different schema.
2. **Product-specific second.** Everything that only this product needs lives in its own file, references the
   kit artifact, and is allowed to be ugly — nothing downstream should ever read it.

Concretely, when a task arrives the answer must state which of the seven kit items it touches, if any. A task
that touches none is product work. A task that touches one is a kit change and needs the sibling considered.

## 4. Reading the sibling's restructuring

The rule that makes this survivable: **depend on semantics, not on paths.** Our checker looks for *what a file
means* (a table with an evidence-type column), not for `docs/CLAIMS.md` specifically, and reports where it found
it. When their tree moves, the report shows `present (moved)`, and our development does not need to know.

The second rule: **their improvisation is data.** When VecDHT solves a MIG-*item differently and better, that is
a kit proposal, not an incompatibility. When it solves something differently and worse, that is their call, and
we say nothing in the repository — a shared format is not a mandate to redesign someone's project.

## 5. What compatibility is not

- Not a shared dependency. If one repository cannot be built without the other, the boundary has failed.
- Not a monorepo. Three repos, one kit.
- Not an obligation to be identical. Two repositories may implement the same kit item at different levels of
  rigour; the report says which level, and says it without editing anyone's work.
