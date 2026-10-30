# A result you can only state after seeing it is a story. Pre-registration turns it into evidence.

---
id: E-MNN
hypothesis: H-MNN
status: planned | running | completed
base_commit: "<short sha of the tree the run started from>"
started: "<ISO datetime>"
finished: "<ISO datetime or '—'>"
environment: "<OS, interpreter, database, toolchain - whatever a re-run must reproduce>"
command: "<the exact command that produced the result>"

# --- pre-registration: written BEFORE the run, never edited afterwards -------------------------
sensitivity: |
  What difference can this design produce, and is it larger than the noise it will meet?
  A number, not a sentence. If two arms are compared: the smallest effect the design can detect,
  and the variance observed in a pilot. If one instrument is checked: how many cases it must
  catch, and how many it could miss without the result changing.
  (Two cards in this repository, E-M73 and E-M75, would have been refused by this line: they
  measured a difference the design could not produce.)
branches: |
  confirm:   <the outcome that would support the hypothesis, stated as a number>
  refute:    <the outcome that would kill it, stated as a number>
  inconclusive: <the outcome that would mean the test did not reach the effect - which is NOT "no effect">
stop_rule: |
  When to stop early, and when to stop without a result. "Run until it passes" is not a stop rule.
analysis_plan: |
  Which figure is computed from which artifact, and by which command.
  No number may enter the card that a command does not print.

# --- result ----------------------------------------------------------------------------------
threshold: "Pre-registered above; repeated here so the card can be read alone."
result: "<what happened, including 'the design did not reach the effect'>"
verdict: supports | refutes | inconclusive
---

# E-MNN — <the question in one line>

## What was asked

## What was done

## What was found

## What would revive a refuted hypothesis

(Required when `verdict: refutes` — the elimination registry links here.)

## What this does not do
