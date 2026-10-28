---
id: E-M49
hypothesis: H-M49
status: completed
base_commit: "c4d5938"
started: "2026-10-28T11:10:00+03:00"
finished: "2026-10-28T11:30:00+03:00"
environment: "Windows, CPython 3.13.11, Git Bash"
command: "bash lab/selftest-guards.sh"
threshold: "Pre-registered: the second attacker's structural finding must be closed by a control, not by an edit. A test suite that cannot fail is a comment; the control must turn red when the suite is broken and green when it is not, demonstrated both ways."
result: "Added the eighth negative control: with FG_ATTACK_SELFTEST=1 the attack suite is given a deliberately wrong expected code and must report 'still breaking: 1'. Demonstrated both directions - with the suite's failure condition disabled the control goes red (7 passed, 1 failed), with it restored the control goes green (8 passed, 0 failed). This closes the finding that the suite accepted any error code per case, which is why break 7 stayed green through two rounds."
verdict: supports
---

# E-M49 — a test that tests the tests

## The finding this closes

The second adversarial round's sharpest structural observation was not a break in the tool:

> The regression suite cannot catch any of them because it accepts any error code for a case and any
> non-strong verdict, so unrelated defects keep it green. Break 7 is the proof.

It was right. `E-M42` added expected codes per case, but nothing proved the suite notices when an expected
code is missing — a suite that has quietly stopped checking anything looks exactly like a suite that passes.

## What was added

An eighth control in `lab/selftest-guards.sh`. The suite runs with `FG_ATTACK_SELFTEST=1`, which plants a
wrong expected code in one case, and the control requires the suite to report a failure.

## Demonstrated both ways

```
with the suite's failure condition disabled:  FAIL  the attack suite did not notice ...   7 passed, 1 failed
with it restored:                             controls passed: 8   failed: 0
```

A control that only ever passes is as suspect as a suite that only ever passes, so it was run against a
deliberately broken suite before being trusted.

## Why this belongs in the method

Three rounds of work produced a pattern worth naming: **every artifact that was never executed turned out to be
wrong** — the published schema, the report input, the policy merge, and now the test suite's own failure path.
The control is cheap and it is the only thing standing between "the tests pass" and "the tests run".
