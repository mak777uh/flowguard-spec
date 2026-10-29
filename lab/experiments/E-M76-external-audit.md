---
id: E-M76
hypothesis: H-M76
status: completed
base_commit: "885e12f"
started: "2026-10-29T20:50:00+03:00"
finished: "2026-10-29T21:30:00+03:00"
environment: "Windows, CPython 3.13.11; an external model's audit of this repository"
command: "python lab/check-interop.py --repo . && bash lab/selftest-guards.sh && python lab/check-refusal-coverage.py"
threshold: "Pre-registered: every finding in the external audit is reproduced with its own command before anything is changed. Accepted findings are fixed with a test that would catch the regression; a finding that does not reproduce is recorded as refuted, with the command that fails to reproduce it."
result: "Five of six findings reproduced and are fixed; the sixth is refuted. (1) HIGH: docs/28 still said 'There is no fg_map.py' while tools/fg_map.py exists - the very contradiction the document's neighbours are meant to catch, and my own earlier edit had replaced a different sentence. (2) HIGH: the CI step 'published schemas accept the artifacts' ended in '|| true' against tools/_tmp/m13.json, which is gitignored and untracked - a step that could not fail. Now the step asserts a valid fixture is accepted AND that a malformed one is refused. (3) MEDIUM: docs/STATUS printed kit conformance 7/7 while no CI step ran lab/check-interop.py; the step now exists and recomputes it. (4) MEDIUM: three guards had no planted failure (line-endings, metric-digests, refusal-coverage); three controls added, and writing the third exposed a self-referential bug - the planted code literal sat inside lab/selftest-guards.sh, which is itself a carrier, so the guard counted its own planted code as exercised. It now generates the code at run time. Controls: 8 -> 11, all passing. (5) LOW: docs/28's staleness test named MAP_BASIS_STALE for a vanished path, while the tool answers MAP_PATH_UNKNOWN; the test is now split into its two forms and the two undocumented codes are listed. (6) REFUTED: the audit's LOW about ADR-0072 being a dangling reference - it is VecDHT's own ADR number quoted inside VecDHT's note, and no guard in this repository resolves ADR numbers at all (only round-check.sh counts the files), so there is no false finding to suppress."
verdict: supports
---

# E-M76 — an external audit, reproduced line by line

## What was found and what happened to it

| # | audit finding | reproduced | fixed |
|---|---|---|---|
| 1 | `docs/28` says there is no `fg_map.py` while it exists | yes | yes |
| 2 | CI step ends in `\|\| true` against a gitignored path | yes | yes |
| 3 | `7/7` published, no CI step computes it | yes | yes |
| 4 | three guards have no planted failure | yes | yes (and it found a worse bug) |
| 5 | `docs/28` names the wrong code for a vanished path | yes, by a different diff than the audit's | yes |
| 6 | `ADR-0072` is a dangling reference | **no** | recorded as refuted |

On the audit's commit id: `05a70d2` does not exist in this repository (`git cat-file -t` fails), so its exact
state could not be reproduced. Every finding nevertheless reproduced against the current tree, which is the only
thing that matters for a fix.

## The two that matter most

**The step that could not fail.** `python3 tools/fg_schema_check.py --inventory tools/_tmp/m13.json || true`
combines two ways of not checking: the file is gitignored (0 tracked paths under `tools/_tmp`), so CI never has
it, and `|| true` swallows the exit code anyway. It now asserts both directions — a valid fixture must be
accepted, a malformed one must be refused — and the malformed fixture is committed, so both directions are real.

**The guard that counted its own plant as evidence.** Writing control 10 exposed a self-reference: the refusal
coverage guard treats `lab/selftest-guards.sh` as a carrier, so a planted code written as a literal in that file
was "exercised" by the control that planted it, and the control failed. The fix is to build the code at run time:

```bash
PLANTED="SYNTHETIC_$(date +%s)_UNRAISED"
printf '\n| `%s` | planted by the selftest | n/a | no |\n' "$PLANTED" >> "$DOC"
```

This is the same class as `E-M45` (a test that measures the fixture) and `E-M67` (a test that measures the
ceiling), one level up: **a negative control must not be part of the evidence for the thing it controls.**

## What the audit got right about my own habits

Its MEDIUM 3 said the published number had no carrier, and pointed at `docs/36-ROUND7-SYNTHESIS.md:120`, which
is my own sentence: a number inflated by prose is worth nothing. That is the third time in two days an outside
reader found a place where I had written the rule and then broken it — the first two were the refusal-code count
in a heading and the unimplemented `SPEC §4`.

## What this does not do

- It does not make the audit's claims about the project true; it verifies six specific lines.
- It does not re-run the CI itself: no GitHub Actions run was observed, so "the step now fails when it should" is
  verified locally, not in their runner.
- It does not close the deeper point behind MEDIUM 3: `check-interop.py` is now in CI, but its `7/7` still
  measures my own tree, not an outsider's rebuild — `P1` is unchanged.
