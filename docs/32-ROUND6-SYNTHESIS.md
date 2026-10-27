# Round 6 synthesis — five independent reviews, one verdict

**Date:** 2026-10-27. **Material reviewed:** `PACKET-ROUND6.md` (self-contained, ~2,000 words).
**Reviews:** five, independent, none seeing the others.

Unlike rounds 1–5, this round did not produce a list of design objections. It produced a **plan change** and one
question that all five asked in different words. The convergence is the finding.

---

## 1. What all five said

| # | Finding | Reviews | Consequence |
|---|---|---|---|
| 1 | **Do not build the browser verifier first.** Its value is isolated-run convenience, not proof. | 5/5 (one cuts it entirely, four defer it) | Build order changes; browser becomes an optional front end |
| 2 | **Build the substitution test first**, as the executable contract of the bundle format | 4/5 | It becomes the first artifact, before the verifier |
| 3 | **The archive can wait.** It proves durability of text, not that a control works | 5/5 | Removed from the first stage |
| 4 | **No named buyer exists at recall 0.71.** Nearest analogue is SOC 2 Type II / pentest: a disclosed-scope report, not a guarantee | 5/5 | Positioning changes from guarantee to measured, disclosed-scope verification |
| 5 | **The residual hole is instrument correctness**, not claim wording. Eight columns cannot catch a wrong instrument | 5/5 | Next artifact is instrument verification (negative controls), not another registry |
| 6 | **The unasked question is the same in all five**: who is the specific person whose decision changes, and what does the publisher lose if the bundle is wrong | 5/5 | This is now the product's central open question — see §4 |

## 2. What the reviews corrected in our own text

**The substitution test as specified was near-tautological.** One reviewer put it precisely: swap the code, the
digest fails, the verifier rejects — that tests our own hash comparison. Two classes are needed:

- **D-1, tampering after signing**: a subject is replaced while the old signature stays. The verifier must reject
  because digests no longer match.
- **D-2, falsely attested pair**: a bundle is correctly signed by a trusted key but describes a *different*
  target than the one presented. Signature and digests are valid; the claim is false. This is mechanism T1, and
  D-1 does not touch it.

**"Offline" and "bound to the running version" conflict.** An offline verifier cannot learn what code sits at a
contract address; that needs `extcodehash` from a finalized checkpoint, i.e. the network or carried evidence. We
must state what is verified offline and put the rest in `not_claimed`. Otherwise the artifact claims a property
it cannot have.

**`PROVEN` was overstated as unreachable.** One reviewer objected, correctly: whether `PROVEN` is attainable
depends on the model's strictness, the object's boundary and the completeness of checked paths. It is unreachable
*for a whole application under our assumptions*, not in principle. The claim registry now says it that way.

**Recall needs an interval, not a point.** 0.71 on a corpus of 20 is roughly 14/20; the interval at that size is
about 0.5–0.9. Publishing the point estimate without the interval makes the number look more precise than it is —
and a buyer with an auditor will notice.

## 3. The numbers they gave us for stopping

| Review | Number | Reading |
|---|---|---|
| 1 | 14 days to a named consumer conversation, 30 days to a first measurement | 2026-11-10 and 2026-11-26 |
| 2 | 21 days to a checkable offline artifact | 2026-11-17 |
| 3 | 30 working days, with three binary external signals | ≈ 2026-12-08 |
| 4 | 90 days without an external party blocking a release | outlier — a different threshold (integration, not invention) |
| 5 | 30 days for a minimal artifact | 2026-11-26 |

**Adopted: two dates, both now in `STATUS-v0.md`.**

- **2026-11-10** — a named person, in a named role, has had a conversation with us about what evidence would
  change their decision. Not a buyer; a conversation.
- **2026-11-26** — one executable measurement exists: `E-M9` recorded, with its pre-registered thresholds, and
  the result published including failure.

If 2026-11-26 passes without an `E-` result, the method is not extended; the project narrows to the piece that
can be measured, per review 1's framing: *the next action must be able to fail.*

## 4. The question all five asked

They phrased it five ways; it is one question:

> **Who is the specific person whose decision changes when the first line says `coverage: 11/14` — and what does
> the publisher of the bundle lose if the bundle is wrong?**

Three of five added the second half unprompted: liability. A limitation-of-liability disclaimer and a
"known unknowns" list may read as diligence before an incident and as negligence after one, if they are not
backed by a contract that allocates the risk.

This is not a marketing question. It decides the artifact: if the consumer must be able to act, the bundle needs a
liability surface — who signed, on what authority, for what period, with what effect. That is a field we do not
have, and no amount of coverage arithmetic substitutes for it.

**Recorded as the product's central open question. It is not answered by any round of design review; it is
answered by one conversation with one person, which is what 2026-11-10 is for.**

## 5. What changes in the repository

| Change | Artifact |
|---|---|
| Build order: substitution test first, verifier second, browser optional | `lab/decisions/ADR-0001-build-order.md` |
| First experiment card, two substitution classes, thresholds fixed before the run | `lab/experiments/E-M9-substitution.md` |
| Evidence types no longer claim `PROVEN` is impossible in principle | `docs/CLAIMS.md` C-04 note |
| Three positions newly eliminated with revival conditions | `docs/eliminations.md` X-16…X-18 |
| Stop dates and the liability question | `docs/STATUS-v0.md` |

## 6. What we are not doing

- Not starting a seventh round. Four reviewers said so explicitly; the fifth implied it by asking for an
  artifact.
- Not building the archive before a consumer exists.
- Not adding an instrument-assessment registry before there is one instrument to assess. The cheap version comes
  first: **a negative control per guard** — a planted defect that the guard must catch, run in CI. Our three
  self-caught checker errors are the calibration basis.
