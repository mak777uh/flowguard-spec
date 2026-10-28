---
id: E-M43
hypothesis: H-M43
status: completed
base_commit: "fbc9107"
started: "2026-10-28T07:10:00+03:00"
finished: "2026-10-28T08:05:00+03:00"
environment: "Windows, CPython 3.13.11; a second independent agent, hostile documentation review"
command: "python tools/fg_readiness.py (in a scratch copy) ; python lab/round-check.sh"
threshold: "Pre-registered: an independent reader may find places where the text claims more than the artifacts. Every finding must be reproduced before it is accepted; a reproduction that does not hold is reported as not reproduced. Fixes go in; unfixed items are listed with their severity, not dropped."
result: "21 findings, 20 reproduced. The worst was real and severe: the top readiness tier (T4, product 100%) was reachable by typing four lines - a rebuild marker, an external-corpus marker, a three-field role file and invented M8 fields - because P1, P3 and P4 were marker checks and P2 is a shape check. Fixed: all three product checks now require validated records, and the typing attack no longer reaches above product 0%. Also fixed: the reserved-word scan pointed at a non-existent reports/ directory; the README table was joined by literal backtick-n; stale STATUS sections claiming no verifier exists; stale METRICS prose describing an empty file with 59 rows; eight card texts that disagreed with their own logs; the E-M19 log was regenerated against the inputs its card describes. Ten findings remain open and are listed below."
verdict: supports
---

# E-M43 — the hostile review that forced the top tier open

## What was tested

An independent agent was given the repository and the instruction to find text that claims more than the artifacts
support. It produced 21 findings with file:line, a reproduction and an honest sentence for each. Twenty reproduced.

## The one that mattered

**T4 — "a guarantee someone may rely on" — was reachable by typing.** The reviewer copied the repo and added:
one card line `rebuild_result: agreed by third party`, one line `external_corpus: ...`, one role file
`{"asserts":"risk_acceptance","issuer":"nobody-in-particular","valid_until":"2099-01-01"}`, and invented values in the
seven M8-CONSUMER fields. Result: **core 100%, product 100%, overall 100%, tier T4.**

That falsified the first sentence of `docs/READINESS.md`: "It cannot be argued upward." It could be typed upward.

## Fixed

| finding | fix |
|---|---|
| P1/P3/P4 were marker checks | P1 now needs a rebuild line **and** a foreign-validation record that passes the same checks `fg_confirm.py` applies; P3 requires the five fields `policies/signature-roles.json` demands; P4 requires a record with `ground_truth` + `blind_evaluation` |
| records were scanned from the whole tree, including `tools/_tmp` and `fixtures/` | scan limited to `docs/`, `interop/`, `lab/experiments/`, `reports/` — a demonstration is not an act |
| the reserved-word rule scanned a `reports/` directory that does not exist | the scan now covers `docs/` and `README.md` |
| README table rows were joined by literal `` `n ``; the round-check command read `ash`; the ADR count said 11 | repaired; 14 ADRs |
| STATUS said "no verifier exists, therefore no verdict has ever been produced" | corrected in place with the date it became false, rather than deleted |
| METRICS called itself "two rows" and "empty" | says 59 rows and that they are hand-entered |
| READINESS defined T2 by an event that never happened ("a stranger can install and run") | redefined: no outsider has done it; the harnesses assume a running PostgreSQL |
| eight card texts disagreed with their own logs (E-M30 times, E-M31 independence claim, E-M32 5↔6, E-M36 4↔7, E-M38 13↔7, E-M25 "both candidates", E-M42 case count, E-M10 wrong claim id) | corrected to the logged numbers |
| the E-M19 log was from a different run than its card | regenerated against the inputs the card describes: 15→16 paths, 2 sources, delta +1, growth true |

## Still open, with severity

- **high** — `check-secrets.sh` scans history for token shapes only, and the local-path rule covers four extensions;
  three committed logs contain the author's home path. The front page promises more than the guard does.
- **high** — `lab/check-claims.py` still treats a missing artifact as a warning rather than a failure in CI (the rule
  says "fails the linter"). With zero missing artifacts today this is a latent, not an active, lie.
- **high** — `STATUS-v0.md` still contradicts itself in several rows (M1 absent vs present; 84 links vs 122; "three
  guards" vs six CI steps; 7/7 beside a table that says 5/7). It should be **generated**, not edited.
- **medium** — four METRICS rows carry digests that match no file in `lab/logs/` (E-M21 and three others). The numbers
  reproduce; the digests were never computed from a captured run.
- **medium** — the same GitLab dump is counted as 1436 and 1102 tables in two logs, and Pagila as 20 and 15; no counting
  query is published, and `db_logic_density` depends on it.
- **medium** — E-M21's 0.4 s has no artifact and the only logged run of the same command says 1.5 s.
- **medium** — `fg_readiness.py` prints hard-coded result strings ("E-M11 recall 8/8") whenever a harness exits 0, which
  is a claim inside the tool that measures claims.
- **medium** — The harness named in E-M19's command field does not exist (the card now points at the merge and verify commands instead).
- **low** — DOSSIER truncates quoted results mid-word (`result[:300]`).
- **low** — four METRICS merge commands omit `--out` and cannot run as written.

## What this establishes

The repository's own instruments did not catch their own top tier being typeable; an outside reader did. The pattern
from `E-M36`/`E-M42` repeated at the level of documentation: **a check satisfied by text is not a check.** The fix
pattern is the same one that worked for the gate — bind each claim to a machine-validated record and keep the attack
that broke it.

## What this does not establish

- That the remaining ten are all of it. The reviewer read for about an hour; this is one pass.
- That the redefinition of T2 is now true. It is now honest, which is different.
- That the product half is reachable honestly. It is not: there is still no third party, no confirmed finding, no
  external corpus, and product remains 0%.
