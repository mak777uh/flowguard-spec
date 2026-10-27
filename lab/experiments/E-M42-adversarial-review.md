---
id: E-M42
hypothesis: H-M42
status: completed
base_commit: "215520a"
started: "2026-10-28T06:15:00+03:00"
finished: "2026-10-28T07:05:00+03:00"
environment: "Windows, CPython 3.13.11; an independent adversarial agent with repository read access and no brief"
command: "python lab/e-m42-run.py"
threshold: "Pre-registered: an independent agent instructed to obtain SCOPED_ASSURANCE or PROVEN without the evidence for it may break the gate. Every break it reports must be reproduced, fixed, and then re-run as a permanent regression. Its fifteen negative controls must keep passing, so the fixes do not simply refuse everything."
result: "Eleven breaks, all reproducible, all closed. The worst three needed no fabrication at all: declaring a WEAKER level deleted the denominator floor and let coverage manufacture PROVEN from a single path; eight copies of one path satisfied the floor; and a report asserting 'the core is empty' changed nothing. Also closed: truncation gated on a self-reported label, a refuted confirmation raising the tier, attribution satisfied by [null], declared perimeter growth not blocking, an empty commit disabling target binding, a deleted density field deleting the check, prose descriptions of an observed write evading detection, and a caller policy zeroing every floor. The suite is now fixtures/attack + lab/e-m42-run.py; 13 cases, 0 still breaking; the agent's 15 negative controls still refuse correctly and E-M12 25/25, E-M36 8/8, E-M11, E-M13, E-M25, E-M41 unchanged."
verdict: supports
---

# E-M42 — an independent attacker found eleven ways through the gate

## How this differed from E-M36

E-M36 was my own eight attacks against my own gate — it tested what I could think of. This was an independent agent,
given the repository and one instruction: obtain a strong verdict without the evidence. It found eleven breaks, each
with inputs, command and output, and reported fifteen negative controls it could not break, which is what makes the
result trustworthy rather than a list of anything.

## The three that needed no fabrication

**B1 — asking for less bought more.** min_paths_for_level was looked up under the *claimed* level while the verdict
was computed from coverage. A claim declaring CONSISTENT_DECLARED with coverage 1.0 over a **single path** printed
PROVEN: the floor keyed to PROVEN was never consulted, because the claim never asked for it.

**B2 — a report that contradicted the verdict changed nothing.** Three paths plus a report stating "none of the
analysed paths passes through the control point; coverage is 0.0" still produced PROVEN. The report was read only
for its control_point field.

**B3 — the floor counted rows, not paths.** The same path dict eight times satisfied an eight-path floor. No
uniqueness check existed on path_id or on (entry, kind).

None of these required inventing a field: the tool manufactured the strongest label out of a denominator that was
empty in substance.

## The eight that needed a plausible lie

| break | mechanism |
|---|---|
| B4 | truncation refused only if the source *labelled itself* partial; 	runcated: {kept: 3, total: 4127} was ignored when the label said "exhaustive" |
| B5 | the tier-2 gate accepted {"owner_confirmed": true} with **no owner**, no statement, and erdict: "refuted" — a record g_confirm.py refuses |
| B6 | ttribution.sources: [null] satisfied "attributed by a named source" |
| B7 | perimeter_growth: true printed alongside PROVEN; the field was echoed, never gating |
| B8 | "commit": "" disabled target binding entirely; the refusal and the mismatch check were both skipped |
| B9 | deleting db_logic_density from the source deleted the thin-coverage refusal |
| B10 | the same observed DELETE written as prose instead of stmt:DELETE escaped UNENUMERABLE_PATH |
| B11 | a caller-supplied policy with zeroed floors and an absent 	rusted key yielded PROVEN for one path |

Plus four uncaught tracebacks in fields alidate_shapes did not inspect — the class E-M33 claimed was closed.

## What was changed

- the printed level is clamped to the claim, and the floor is looked up under **the level being printed**, over
  **distinct** (entry, kind) pairs;
- truncation is refused from the numbers, not from the label;
- a confirmation must pass the same checks g_confirm.py applies, and a efuted record does not raise a tier;
- an attribution must name sources that exist as strings in the inventory;
- declared perimeter growth blocks; an empty commit is a refusal;
- a catalogue source that does not report its density cannot support a strong level;
- an observed_write whose entry does not match stmt:<VERB>  is a shape error, not an observation;
- a caller policy may only tighten: floors are max(default, caller), thresholds min, and 	rusted must be 	rue;
- alidate_shapes now covers vidence_tier, ttribution, oreign_validation and xcluded.

## Result

`
breaks re-run: 13 cases, 0 still breaking
E-M12 25/25 · E-M36 8/8 · E-M11 · E-M13 · E-M25 · E-M41 · E-M33 all unchanged
`

The attacker's own words on the class: *"those share one defect — a gate satisfied by a field the analysed party
writes."* That is correct, and it is the honest boundary: every one of these checks reads a document the claimant
produced. The fixes make lying harder and more visible; none of them make lying impossible, and NC-01…NC-11 say
so in every verdict.

## What this establishes

An independent agent with the repository read access and one sentence of instruction found eleven ways through a gate
I had attacked eight times myself. The gate is measurably stronger now, and the attack suite is a permanent harness, so
the next refactor cannot quietly reopen one.

## What this does not establish

- That no other break exists. Thirteen cases now pass; that is a floor, not a proof.
- That the attacker was independent in the way that matters. It is an AI agent from the same model family as the
  author, with access to the same repository: shared blind spots are possible (NC-05).
- That a determined liar is stopped. The gate can only read what it is given.

## Log

`lab/logs/e-m42-2026-10-28.log` — sha256 `55ca75309b913524b4e3dd2b41e85797dd16fc87b8b92d6528bd6771be19f10d`.
