---
id: E-M64
hypothesis: H-M64
status: completed
base_commit: "c97932e"
started: "2026-10-28T15:15:00+03:00"
finished: "2026-10-28T15:45:00+03:00"
environment: "Windows, CPython 3.13.11, PostgreSQL 17.2"
command: "python tools/fg_init.py --psql <psql> --port 54329 --db fg_try --dump <pagila-style schema> --schema bank --table accounts --control function:bank.transfer"
threshold: "Pre-registered: a stranger with a schema dump, a psql binary and Python must reach a verdict in one command, without reading any other document. The run must create the database if absent, print the density band BEFORE any claim, enumerate, merge, write a claim that asserts nothing it has not earned, and verify. Any manual step in the middle is a failure of the procedure."
result: "One command, seven labelled steps, end to end on a real dump: database created, dump loaded, scope printed as '3 tables, 10 functions, 8 writing (density 0.8, band dense)', grants enumerated (14 paths), callers enumerated (2 functions reach the control point), merged into 16 paths, a CONSISTENT_DECLARED claim written with claimed_coverage 0 and five NC codes, and the verifier confirmed CONSISTENT_DECLARED with no refusals. The procedure found and fixed the class of defect the reviewer named: the tier claimed 'an outsider can install' while the harnesses assumed a running database, a loaded schema and a hand-written claim."
verdict: supports
---

# E-M64 — one command from a dump to a verdict

## Why this was the right next step

The hostile review (`E-M43`) put it plainly: **T2 says "a stranger can install, run and reproduce", and no
stranger has, because there is no install step**. Every harness this repository owns assumes a database that
already exists, a schema already loaded, and a claim somebody wrote by hand. That is not an installation, it is
a working environment that happens to be mine.

## What the command does

```
[1/7 database]   fg_try created
[2/7 dump loaded] _fgtry.sql, 9292 bytes
[3/7 scope]      3 tables, 10 functions, 8 writing (density 0.8, band dense)
[4/7 enumerated] 14 paths, 1 control point
[5/7 callers]    2 functions reach the control point
[6/7 inventory]  16 paths
[7/7 verdict]    CONSISTENT_DECLARED
```

Three decisions inside it are worth naming:

**The band is printed before the claim.** A thin database cannot carry a strong verdict, and the user should
learn that before reading a number that would mislead them — not after the verifier refuses.

**The claim asserts nothing.** `CONSISTENT_DECLARED`, coverage 0, five `NC` codes, evidence tier 0. The tool
starts by claiming the minimum; raising the claim is a separate act with its own evidence.

**It stops at the first failure and says which step.** A stranger needs to know whether the dump was wrong, the
database was unreachable, or the enumerator crashed, and "something failed" is not that.

## What it does not do

- It does not install PostgreSQL. The client tools and a reachable server are prerequisites, and the README now
  says so plainly instead of implying the tool brings its own.
- It does not write a strong claim, a bundle, or a signature. Those are separate steps with separate evidence,
  and bundling them would turn "it ran" into "it attested".
- It does not verify itself: the verdict comes from `fg_verify`, which is the same code the adversarial rounds
  attack.

## What this changes in readiness

`P1`–`P4` stay at zero, because no third party has used it. But the sentence "an outsider can install and
reproduce" is now a procedure instead of an assumption, and `T2`'s definition in `docs/READINESS.md` matches
what the repository can actually demonstrate.
