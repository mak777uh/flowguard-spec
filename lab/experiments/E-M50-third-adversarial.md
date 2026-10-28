---
id: E-M50
hypothesis: H-M50
status: completed
base_commit: "e25a3b5"
started: "2026-10-28T11:40:00+03:00"
finished: "2026-10-28T12:20:00+03:00"
environment: "Windows, CPython 3.13.11; third independent agent, told which surface was already closed"
command: "python tools/fg_verify.py --claim <attack3 case> --inventory <attack3 case>"
threshold: "Pre-registered: a third attacker that is told the closed surface must not produce a strong verdict from what is left. A break in the harness itself counts double, because a harness that passes on a failure hides every other break."
result: "Nine breaks. Two were reopened from earlier rounds: the path floor counted (entry, kind) so one row with eight legal kind labels reached PROVEN, and the report was reconciled against the SQL-verb ratio instead of the path coverage the tool prints, which made the honest report fail and the contradictory one pass. Three were harness defects: the suite counted a SKIPPED case as not-breaking, _valid_confirmation_tier3 was defined and never called, and e-m48-run printed 'crashes remaining: 0' while five inputs still tracebacked. Also closed: growth gated on the delta being a dict, db_logic_density:true accepted as a perfect density, the calls-exemption reachable by a source that contributed table paths. Fixed: duplicate path_id is now a shape error; the floor counts path_id; report coverage compares with path coverage; growth blocks unconditionally; tier 3 requires ground_truth; SKIP is a failure."
verdict: supports
---

# E-M50 — the third round, and the harness's own lies

## The two that mattered

**One row, eight labels, PROVEN.** `distinct_paths` was a set of `(entry, kind)`. The closed kind list of `E-M47`
made each label *legal* without making it *distinct*: one path, one `path_id`, one entry, eight different kinds —
`PROVEN`, exit 0, no errors. It matters more than before, because `PROVEN` requires coverage 1.0, i.e. every
enumerated path inside the core — so the claimant's best move is to enumerate one row and relabel it.

Now the floor counts `path_id`, and a repeated `path_id` is a shape error: one finding written eight times is one
finding.

**The report was reconciled against the wrong number.** `E-M48` compared `report.coverage` with the SQL-verb ratio
from `fg_coverage`, while the verdict and `computed_coverage` are path ratios. The result: an honest report saying
1.0 was refused, and a report saying 0.0 — the one that contradicts the verdict — passed. The fix compares like with
like.

## The harness defects, which count double

- **A SKIPPED case was not a failure.** Deleting one fixture left "still breaking: 0" and exit 0, and the self-test
  control still passed. Twelve of thirteen cases could stop running silently. `SKIP` now counts as a break.
- **`_valid_confirmation_tier3` was defined and never called**, so tier 3 passed without ground truth while
  `fg_confirm` refused the same record.
- **`e-m48-run.py` printed "crashes remaining: 0"** while five inputs still tracebacked — the harness tested three
  policy shapes and reported on all of them.

A harness that passes on a failure is worse than no harness: it converts an open question into a closed one.

## What the attacker says the design cannot do

> everything the tool "recomputes" is recomputed from the claimant's document … the honest ceiling of this design
> is not "a liar cannot pass" but "a liar's document contradicts itself".

That is correct and it is now the honest boundary in `docs/CLAIMS.md`. The one change it proposes — making every
assertion by a third party carry that party's key, and resolving `finding.path_id` against the inventory — is the
largest step available inside that ceiling, and is not done.

## Still open

- **Bundle roles are not signed**: an acceptance `.role` file with no `.sig` and no `.pub` verifies green, its terms
  are editable after signing, and separation of duties is satisfied by an unsigned file. This survived its own
  regression because the regression verified a single-signer bundle and called it "correct split accepted".
- `finding.path_id` is not resolved against the inventory.
- Tracebacks remain in `sources[].db_logic_density` as a string, `delta.new_paths` as a string, and `--report` pointing
  at a list.
