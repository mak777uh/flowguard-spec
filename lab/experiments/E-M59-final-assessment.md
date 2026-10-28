---
id: E-M59
hypothesis: H-M59
status: completed
base_commit: "45f3eb8"
started: "2026-10-28T17:25:00+03:00"
finished: "2026-10-28T17:45:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python tools/fg_audit.py && python tools/fg_readiness.py && python lab/check-interop.py"
threshold: "Pre-registered: the closing assessment must answer the four numbered objectives with a command beside each claim, state the product half as measured rather than as hoped, and name what is unfinished without softening it. A closing document that only lists successes is a press release."
result: "The four objectives are done and measurable: call-graph attribution (2/2 attributed, 0/9 false, depth 8), the bundle format with E-M9 published as a refutation and repaired to 6/6, 102 instrument mutants, and three independent rebuilds - the last of which produced a conforming verifier written from the page. Engine readiness 100%, product 0%, kit 7/7, audit 12/12, 8 guard controls, 49 cards (46 supports, 3 refutes), 79 metric rows, 25/25 scenarios, 34 adversarial breaks closed, 44 differential mutations with one known divergence. Four things keep the product half at zero and none of them is code: no third-party rebuild by a human, no owner confirmation, no acceptance outside fixtures, no named consumer. Three decisions are queued for the owner."
verdict: supports
---

# E-M59 — the closing assessment

`docs/21-FINAL-ASSESSMENT.md` is the document; this card records that it was produced against a stated threshold and
what it refused to soften.

## The four objectives

1. **Attribution.** `enumerators/pgcalls/` resolves callers to depth 8; on the fixture 2 of 2 control-point callers
   attributed, 0 false attributions out of 9 decoys, coverage 0.111 of 18 paths where it was previously zero.
2. **Bundle and E-M9.** The substitution test published as a refutation at 3 of 6, repaired by moving the anchors
   outside the bundle, re-run at 6 of 6. The format has since changed twice under pressure from four rebuilders.
3. **E-M10.** 102 generated mutants, all named, all caught by their declared checks.
4. **M7.** Three independent rebuilds by agents without source access; the fourth wrote a *conforming verifier* from
   the page and caught five tamperings it made itself. Recorded in the weaker form, because the rebuilders are AI
   agents of the same model family, not human strangers.

## What the assessment refuses to claim

- That the product is usable by someone else. Product readiness is **0%**, and the four reasons are things no amount
  of code produces: a third-party rebuild by a human, an owner's confirmation, an acceptance outside `fixtures/`, a
  named consumer whose decision changes.
- That the gate cannot be beaten. Thirty-four breaks across three rounds, all closed, and the design ceiling is stated
  in the third attacker's words: *a liar's document contradicts itself*, not *a liar cannot pass*.
- That the repository is finished. Four unfinished items are named, including the reserved-word claims over three
  older documents and a report check that skips when `analysed_paths` is omitted.

## The number that matters

`product: 0%` beside `engine: 100%`. Everything in this repository was built to move the right-hand number, and it
stayed zero for the whole session on purpose — because the checks that would move it cannot be satisfied from inside.
