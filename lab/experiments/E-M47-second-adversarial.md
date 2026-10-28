---
id: E-M47
hypothesis: H-M47
status: completed
base_commit: "8a996dc"
started: "2026-10-28T09:45:00+03:00"
finished: "2026-10-28T10:35:00+03:00"
environment: "Windows, CPython 3.13.11; a second independent agent, told not to repeat the first round's eleven"
command: "python tools/fg_verify.py --claim <attack2 case> --inventory <attack2 case>"
threshold: "Pre-registered: a fresh attacker told which eleven breaks are closed must not produce a strong verdict from the fourteen candidates it may find. Every break it reports is reproduced before it is accepted. Nothing is fixed by weakening the claim; a fix that creates a new break counts as a defect."
result: "14 breaks, none of the previous eleven, and THREE OF THEM CREATED BY MY OWN FIXES: an unvalidated level string echoed back as the verdict ('PROVEN ' with a trailing space printed PROVEN with exit 0); a path-kind label the claimant types, so one path relabelled eight ways satisfied an eight-path floor; and a policy merge that LOWERED the density floor it was supposed to raise. Also closed: the tier-2 record was weaker than fg_confirm, density was required only for kind=='grants', growth blocked only on literal true, truncated-as-string slipped through, GRANT/CREATE/DROP were invisible to the three-state check, free text in detail fabricated a catalogue verb, a witness-only source satisfied the denominator, vanished paths counted as coverage. All 14 blocked; E-M12 25/25, E-M36 8/8, E-M42 13 cases, E-M11, E-M13, E-M25, E-M33, E-M41 unchanged. Still open and named: the report is still read only for control_point (break 7, unclosed from round one), seven tracebacks in policy/sources/target_lock/report, and schemas/inventory-0.1.json is not valid JSON."
verdict: supports
---

# E-M47 — the fixes created three new holes

## The most important sentence in the report

> the fixes added three new instances of a sharper kind: a level string that is never validated and is
> then echoed as the verdict; a check keyed to a label the claimant types; a policy merge that loosens a
> floor it was supposed to tighten.

All three were mine, introduced by `E-M42`.

## The breaks, and what each one was

**1. The verdict was the caller's string.** `declared_level: "PROVEN "` — one trailing space — printed
`"verdict": "PROVEN "` with **exit 0 and no errors**. The exact string `"PROVEN"` was refused with three codes.
A one-byte difference between a refusal and a strong verdict.

**2. The floor counted `(entry, kind)` and `kind` was free text.** One path, relabelled `privilege`, `catalog`,
`runtime`… eight ways, satisfied an eight-path floor. The distinct evidence was the one-byte entry `"e"`.

**3. The tier-2 record was weaker than the tool it claims to mirror.** `fg_confirm.py` refuses a record without
`schema`, `finding.path_id` and `finding.claim`; `fg_verify.py` accepted it and printed `PROVEN`.

**4. A "trusted" policy lowered the density floor** — `min()` where the key is a floor. It switched
`THIN_DB_LOGIC_COVERAGE` off.

**5–6.** Density was required only for `kind == "grants"`; growth blocked only on the literal `true` — `"true"` and
`1` both printed `PROVEN` beside `level_upgrade_allowed: false` in the same document.

**8–9.** `GRANT`, `CREATE`, `DROP` were invisible to the three-state check (its verb list was DML only), and typing a
verb into the free-text `detail` field silenced `UNENUMERABLE_PATH` — the one check that exists in order not to be
silenced.

**10–12.** A witness-only source satisfied the denominator; `vanished: true` paths counted as coverage; truncation
written as a string, or as `{"kept": 3}`, or labelled `"sampled"`, passed.

## What was changed

The level is a closed vocabulary — anything else is `INVALID`. Path kinds are a closed list. A confirmation is
validated by the same fields `fg_confirm` requires. Density is a floor: `max()`, not `min()`, and every source that
enumerates tables must report it (a source that enumerates *calls* is exempt by a structured field). Growth is
truthy for any spelling, and only meaningful against a previous inventory. Verb detection reads structured entries,
not free text, and covers DDL and privileges. `vanished` paths are excluded from coverage, and core paths must be
attributable to a catalogue.

## What this says about the method

Two independent attackers produced 11 + 14 breaks. The second round's value was not that it found more, but that it
found **what the first round's fixes broke**. A fix is a change, and a change needs the same attack it needed the
first time. The practice document says this; the evidence now does too.

## Still open

- **The report is read only for `control_point`** (round-one break 7). A report asserting "the core is empty,
  coverage 0.0" still does not move the verdict.
- **Seven tracebacks** remain in `policy`, `sources`, `target_lock` and `report`; exit 1 means both "crash" and
  "claim lowered".
- **`schemas/inventory-0.1.json` is not valid JSON**, and `claim-0.1.json` forbids `evidence_tier`, so every strong
  claim violates the published schema. `fg_schema_check.py` is not in CI.
