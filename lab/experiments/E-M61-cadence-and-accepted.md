---
id: E-M61
hypothesis: H-M61
status: completed
base_commit: "3b126a3"
started: "2026-10-28T14:45:00+03:00"
finished: "2026-10-28T15:10:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/cross-family-due.py && python lab/e-m60-run.py"
threshold: "Pre-registered: (a) external-model attacks must run on change, not on a clock, and the licence to spend tokens must be a file a reader can inspect; (b) the three accepted recommendations that need no owner decision - analysed_paths, density bands, a reserved attestation field - must be implemented with their tests still green."
result: "Cadence implemented: lab/cross-family-due.py hashes the six files that decide verdicts and reports whether an attack is due, so a run costs tokens only after a change to the gate. Recorded run #1 at digest a4bce7a2. Also implemented: a report without analysed_paths cannot carry a level above CONSISTENT_DECLARED (the hole E-M60 found still open after E-M48); db_logic_density now publishes a band (thin < 0.15, mixed < 0.40, dense) beside the number, because 0.15 was a number nobody calibrated; inventory_attestation is reserved in the schema for a future third-party anchor. One regression appeared while wiring the band - a leftover reference to the old variable name - and was caught by E-M42 before commit."
verdict: supports
---

# E-M61 — token budget as a rule, and three accepted changes

## The cadence

Cross-family attacks cost money per run, so they run **on change**. `lab/cross-family-due.py` hashes the six
files that decide verdicts — `fg_verify`, `fg_coverage`, `fg_bundle`, both schemas, the grants SQL — and
answers one question:

```
gate digest now a4bce7a2…, last attack at never (0 run(s))
cross-family attack is DUE: the files that decide verdicts changed
```

After a run, `--record` stores the digest. The check sits in the round ritual and **never blocks**: it is a
reminder with state, not a gate. Deterministic suites (`e-m60`, `e-m42`, `e-m12`, the differential) run every
round for free; only the models cost.

## The three changes

**`analysed_paths` is required** for any level above `CONSISTENT_DECLARED`. `E-M60` found the report check
still skippable by omitting the field it was written to compare — now the omission is a refusal
(`MISSING_EVIDENCE`), not a bypass.

**Density is published as a band** beside the number: `thin` below 0.15, `mixed` below 0.40, `dense` above. The
threshold stays where it was, because moving it without data would be the same guess in a new costume, but the
verdict now says which band the target is in, and only `thin` forbids a strong level.

**`inventory_attestation` is reserved** in `schemas/inventory-0.1.json` — an object with `issuer`,
`public_key_pem`, `signature_base64` and `covers` — with the description saying no tool here produces it and a
verifier must ignore it until an anchor exists. Reserving the field now means adopting external attestation later
is not a format change.

## A regression caught by habit

Wiring the band left one reference to the old variable name, and `E-M42` went red on the next run before any
commit. That is the ritual doing what it exists for: the same class of defect — a rename that leaves a stale
name — has been caught three times this session by a suite, and zero times by reading.
