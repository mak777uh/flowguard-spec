# 35 — Full-spec audit after the pivot

**Date:** 2026-10-27. **Scope:** every document as it stands after ADR-0001…ADR-0004.
**Verdict: not all consistent.** Ten findings, three structural. Two documents now describe a product that no
longer exists in the form they describe.

---

## Structural findings

### S1 — Two incompatible product shapes, never reconciled

`docs/01-VARIANTS.md` and `docs/02-GRID.md` describe the **remediation ladder**: for one finding, offer paths from a
minimal patch to migration onto a safe core. ADR-0003 describes the **growing core**: on one live service, absorb
flows into a strict core over time, publishing the perimeter.

They are not the same product and they are not obviously compatible:

| | ladder | growing core |
|---|---|---|
| unit | one finding or one flow, once | one flow, repeatedly, over months |
| output | a menu of fixes | a versioned map of what is strict now |
| buyer's question | "what do I do about this?" | "what has become strict since last year?" |
| failure mode | sells the same hole twice at different prices | accumulates rings while the perimeter grows |

**Fix required:** choose which is the product and which is a feature of it. My reading: the ladder is *how* a ring
is entered, the core is *what the product is over time*. That should be written into `01`/`02` as a header, not left
to the reader to infer. **This is a decision, not a question.**

### S2 — No format for the agent's analysis (the input side)

ADR-0004 makes the tool accept an analysis and compare it with a bundle. That analysis has **no schema**: no field
list, no refusal taxonomy, no definition of what "discovered paths" means when an agent produced them.

This is now the largest hole in the specification. The bundle is defined; the thing it must be checked *against* is
not. **Round 7, Q3 and Q5.**

### S3 — `SPEC-v0.1.md` is a stale format definition

It describes a single-verdict bundle. After ADR-0002 (three reserved fields), ADR-0003 (`outside[]`, per-flow
levels) and ADR-0004 (an analysis input), the bundle format differs materially.

**Fix:** keep `SPEC-v0.1` as the *first ring* — an escrow with one flow — and move the format definition to a
separate document that carries the current schema. Do not silently patch the old one; its value is that it was
written before the changes.

## Consistency findings

### C1 — The hackathon plan still puts the browser verifier first

`docs/97-HACKATHON-PLAN.md` A1 is "a verifier that runs in a browser tab (deployment URL)". That contradicts
ADR-0001 (test first) and ADR-0004 (an agent has no browser). **Fix:** reorder to the CLI verifier + substitution
test, keep the static page as a demo only.

### C2 — The commercial layer describes an abandoned product twice over

`70` and `80` are frozen, so this is not urgent — but they describe engagements, findings per engagement, assessor
minutes and per-finding economics. After ADR-0003 (flows, not findings) and ADR-0004 (agents, not assessors), they
are stale in two independent ways. **Fix:** the freeze notice should say *why* they are stale, not only that they
are frozen.

### C3 — Claims on the critical path are mixed with claims that no longer matter

Sixteen claims cite missing artifacts. Some are now off the critical path: E-M1 (detector recall), E-M2 (reviewer
minutes), E-M6 (pricing), E-M8 (consumer). They stay in the registry — deleting them is how a team forgets — but
the to-do list should distinguish **needed for the first ring** from **deferred by ADR**. **Fix:** a `path` column
or a "deferred" note per row.

### C4 — C-11 (reviewer minutes) has no marker for the agent branch

ADR-0004 keeps the human branch but nothing in the registry says so. **Fix:** one line in C-11.

### C5 — The witness/human sign-off boundary is undefined

ADR-0004 says an agent's `CONFIRMED` still deserves human sign-off in any liability-bearing context — but nothing
defines when. **Round 7, Q2.**

### C6 — `PACKET-ROUND6.md` describes the pre-pivot product

A reader who finds it first will learn about a browser verifier and a single verdict. **Fix:** a header note
pointing at the two ADRs. It stays as a record; it must not be mistaken for current.

## The absence finding

### A1 — The mission is not written down

The driver is not a buyer. It is: *attacks are becoming cheap, so defence must become cheap and copyable; the goal
is fewer broken systems and a network that survives, not revenue.* Nothing in the repository says this.

That absence explains the hollow feeling of the commercial documents: they were written for a buyer the owner does
not actually want to chase. **Fix:** a one-page statement of mission and of what success means (adoption and
reduction of broken systems), which the commercial layer will have to answer to when it is unfrozen.

---

## What is genuinely fine

- The verdict ladder and its arithmetic: unaffected by the pivot, still the honest core.
- The eliminations registry: 25 entries, still the most useful artifact.
- The kit and the interop channel: working, and the sibling repository caught three of our numbers.
- The guards and the negative controls: 4/4 controls pass; one real defect found by them.
- `E-M9` and `E-M10`: unaffected, still the first two cards.
- ADR-0002's reserved fields: still correct, and now clearly the envelope the agent world needs too.

## What goes to round 7

Five questions, all created by the pivot, none answerable by us internally — see
[`15-ROUND7-QUESTIONS.md`](15-ROUND7-QUESTIONS.md).
