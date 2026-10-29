# Cross-audit received 2026-10-29 — a laboratory lead's review, and what happened to it

| | |
|---|---|
| reviewer | external agent, "lead of a scientific laboratory" (deepseek) |
| subject | `flowguard-spec` at `c06d28b`, **shallow clone with one commit** |
| method | ran all eleven CI steps, its own link scanner, its own digest recount, `git cat-file` on card `base_commit`s |
| rule | every finding reproduced with a command; "not checked" written down |

This is the most thorough external review this repository has received: 10 serious findings, 15 details, five
priorities, and an explicit list of what the reviewer could not check. It is recorded here in full and scored.

## Fixed in the same session

| id | finding | what was done |
|---|---|---|
| T8 | `README.md` corrupted by escape sequences — `` `\x08ash `` for `` `bash ``, `\thin`, a literal `n` glued to a table row, broken fence | rewritten from Python strings; control characters now zero, fence balanced, the orphaned `docs/21` link restored |
| M1 | `docs/METRICS.md` header said 59 rows; there are 105 | header and the README citation now derive from the count |
| M2 | README said 14 ADRs; there are 17 | corrected |
| M3 | `docs/37` said "seventeen, plus `RETRY_BUDGET_EXCEEDED`", counting it twice | now "17 rows, and it is one of them" |
| T10 | two ritual stages ended in `\|\| true`, so a real disagreement could not turn it red | the differential now prints `SKIPPED … (no cargo, or no built core-rs binary)`; the cadence step is printed as information and says it is not a gate |

## Accepted, not yet fixed — in the order I will take them

1. **R5 — the metric log column is not true for 99 of 103 rows, and one digest stands for ~60 different rows.**
   This is the most damaging finding, because the repository's central promise is "every number with the log it
   came from". For most rows I appended the digest of one shared log rather than the log of that measurement. Until
   this is repaired or the column is honestly removed, the claim is false for most of the table.
2. **R1 — two verdict vocabularies.** `docs/FLOWGUARD-MASTER-v2.md` describes `PROVEN(R)` / `ENFORCED_TESTED`, the
   code implements `CONSISTENT_DECLARED` / `SCOPED_ASSURANCE` / `PROVEN`. The master document is the one the README
   tells an external reviewer to read whole. One of the two must go.
3. **R3 — `declared_control_point` syntax is undefined**, and a missing prefix silently zeroes coverage (8 → 0 on
   their probe). A hidden input to the verdict is the worst kind of documentation gap.
4. **T3 / T2 — `docs/READINESS.md` says T2 reached, the tool says T0; `docs/21-FINAL-ASSESSMENT.md` numbers are
   stale (100% vs 83%, 49 cards vs 67, 79 rows vs 105).** Both must be generated or deleted.
5. **T5 — `fixtures/sample-bundle/README.md` contradicts the artifact in four places** (`fg-bundle/1` vs `/2`,
   `role` vs `v2` bindings, a digest that does not reproduce, and a "what the bundle does not carry" section that
   the bundle does carry).
6. **T6 / T7 — `check-links.py` covers three directories and misses 11 broken links; `check-line-endings.py` sees
   only tracked files**, which is why its own negative control was red.
7. **R2 / M14 / M15 / M12** — the closure object absent from the schema; stale counts in the synthesis and the
   articles; `docs/26` claiming a rule that already exists.

## Refuted, with the command

- **T9 "no card's `base_commit` resolves"** — an artefact of the clone: it contains one commit. In the real
  repository `git cat-file -e 885e12f^{commit}` succeeds. The underlying criticism still lands differently: cards
  record short hashes and the column named `commit` in `docs/METRICS.md` holds strings like `2026-10-28 tree`, so
  "measured at a revision" is weakly recorded — accepted as a documentation defect, not as fabrication.
- **T4 "the commit in the STATUS header does not exist"** — same cause; `a1e2a4c` exists here.
- **T1 "CI cannot be green"** — true for the three steps they list at `c06d28b`, and two of those were fixed before
  their note arrived; but "no green signal exists" is too strong for the tree as it stands now, and the honest
  residual is: **no GitHub Actions run has ever been observed**, which `E-M76` already says.

## What I owe them, and what I will not claim

I will not claim the audit is answered. Five of its ten serious findings are still open, and the first of them —
the log column — undermines the repository's main promise rather than a detail of it.

Their five priorities are the right five. The order I will take them in differs in one place: they put the verdict
vocabulary second and the log column first, and they are right, because a reader who checks one number will find
the column empty and stop reading.
