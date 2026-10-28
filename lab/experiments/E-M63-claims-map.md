---
id: E-M63
hypothesis: H-M63
status: completed
base_commit: "d3fd521"
started: "2026-10-28T15:00:00+03:00"
finished: "2026-10-28T15:25:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/claims-map.py"
threshold: "Pre-registered: M3 is marked partial on our side because claims are tied to a wording ceiling but not to the kind of evidence behind them. The repair must DERIVE the type from the artifacts rather than let it be typed, and must fail when a claim's wording outruns its evidence."
result: "lab/claims-map.py derives four types - proof-like (a card with verdict supports AND a captured log), measured (a card with supports), refuted (a card with refutes), assertion (no card) - and checks the sentence against the ceiling each type allows. First run: 3 of 18 outrun their evidence, and all three were withdrawn claims whose sentence quotes the wording being retired; rather than loosen the rule, withdrawn claims are now a fifth type that is not a claim at all. 18 claims, 0 outrunning. Wired into the round ritual."
verdict: supports
---

# E-M63 — the M3 dimension, derived instead of typed

## Why it was `partial`

Our registry tied a claim to a wording ceiling, but the *type* of evidence came from nothing: a sentence could
say "guaranteed" because a human had written "guaranteed". The other side calls this the missing dimension, and
they are right — a ceiling that is not derived from an artifact is a preference.

## What is derived

| type | how it is decided | may say |
|---|---|---|
| proof-like | a card whose verdict is `supports` **and** which names a captured log | proven, verified, guaranteed, measured |
| measured | a card whose verdict is `supports` | measured, shown, demonstrated |
| refuted | a card whose verdict is `refutes` | refuted, failed, does not hold |
| assertion | no card at all | nothing strong |
| withdrawn | the registry marks it withdrawn | nothing: it is not a claim |

The word list is checked against the sentence, not the title, so "the trigger is a physical guarantee" is caught
wherever it appears.

## What the first run found

Three of eighteen outran their evidence — `C-09`, `C-13`, `C-18` — and all three were **withdrawn**: the sentence
quotes the wording being retired, which is the opposite of asserting it. The lazy fix would have been to add
"guarantee" to the allowed list for withdrawn claims, which would have let a real outrun pass later. Instead
`withdrawn` became a type that is not a claim at all, and the checker reports it without judging its sentence.

## What this does not do

- It does not check that the card's numbers are right; that is what the metrics digests and the differential are
  for.
- It does not decide whether a claim *should* exist. A claim backed by a weak card and worded weakly passes, which
  is correct: the map measures the distance between wording and evidence, not the value of the evidence.
