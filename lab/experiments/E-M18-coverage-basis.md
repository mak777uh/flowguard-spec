---
id: E-M18
hypothesis: H-M18
status: completed
base_commit: "uncommitted tree"
started: "2026-10-27T23:24:00+03:00"
finished: "2026-10-27T23:34:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/e-m12-run.py && python tools/fg_readiness.py"
threshold: "Pre-registered: (a) a manifest whose sources are witnesses only (runtime, agent) cannot produce a coverage number — refused with MISSING_EVIDENCE on subject coverage_basis, (b) a witness plus a catalogue source is accepted and the verdict names the denominator kinds, (c) the M8 template scores zero for P2 because a template is not a consumer."
result: "19 of 19 acceptance scenarios pass, including T18 (witnesses only refused) and T19 (grants+runtime accepted, coverage_basis_kinds = [grants]). Readiness: P2 = 0 with the reason 'placeholder or too short', so the template cannot buy the nine points it is meant to earn by being filled."
verdict: supports
---

# E-M18 — the denominator has a kind, and a template is not a consumer

## Problem 1 — the coverage denominator could rest on a witness

`E-M17` measured that a runtime source **under-counts**: a write performed inside a stored procedure never appears in
the log as its own statement, so the log sees the bypasses and misses the legitimate path. The same is true, for
different reasons, of an agent source: it reports what it read, not how many paths exist.

Counting a denominator from either of them produces a number that looks like coverage and is not: the ratio would be
computed against a set that is known to be incomplete **by construction**.

## Fix

Sources are declared with a `kind`. The verifier now separates:

- **denominator kinds** — `grants`, `static`, `routes`, `manual`: these enumerate;
- **witness kinds** — `runtime`, `agent`: these observe or interpret.

A manifest whose sources are witnesses only is refused with `MISSING_EVIDENCE` on subject `coverage_basis`, and the
verdict is capped. A mixed manifest is accepted and the verdict publishes `coverage_basis_kinds`, so a reader can see
what the number stands on.

## Problem 2 — a template would have earned readiness points

`docs/M8-CONSUMER.md` did not exist, so P2 scored zero. Creating the file as a **template** would have scored ten
points for a document containing `<name>` and `<date>`, which is precisely the "text about a thing is not the thing"
failure this repository has already recorded five times in its own instruments.

## Fix

`ok_consumer()` requires seven fields — person, organisation, decision before, decision after, what they lose, date,
verbatim — each non-empty, none starting with `<`, each at least eight characters. The template scores **zero** with
the reason `placeholder or too short: person, organisation, decision_before, …`.

## Run

```
T18  witnesses only -> refused (coverage_basis)     PASS
T19  grants + runtime -> accepted, basis [grants]   PASS
T1-T17 unchanged                                    PASS
scenarios passed: 19/19

readiness: P2 = 0  «placeholder or too short»
```

## What this does not do

- It does not make a catalogue source complete. Three sources can still share a blind spot; `NC-05` says so in every
  claim.
- It does not decide which kinds may be denominator kinds forever. `routes` is included speculatively, before such a
  source exists; if it turns out to under-count like the runtime source, it moves.
- It does not make the M8 form sufficient. A filled form is one observation; whether the decision *actually* changed
  is only knowable afterwards, and that is why the form asks what they lose, not what they think.
