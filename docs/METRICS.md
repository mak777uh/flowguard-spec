# METRICS — every number carries its command and its log

**Status:** contract in force, **two rows**. The first measurement in this repository: `E-M11`, the grant
enumerator against eight planted bypasses. Both rows were produced by a command and carry the log digest; neither
was typed from memory.

## The rule

> A number enters this file only with three things: the command that produced it, the sha256 of the log it was
> extracted from, and the commit it was measured at. A number without a log is not published.

Why so strict: a number in a document rots on every cycle. One sibling repository learned this the hard way — its
metrics document still described a run from twelve cards ago, because the number was typed and the runs were not.
The fix there was the same: make the header generated from the carrier, not written by a person.

## Table

| # | metric | value | command | log sha256 | commit | measured |
|---|---|---|---|---|---|---|
| 1 | `E-M11` recall on planted bypasses | **8 / 8** | `python lab/e-m11-run.py --psql <conda>/Library/bin/psql.exe --port 54329` | `21a30af4b4aed7cb052e7593b731935da61dd59860237f52aed8e7e840972375` | 2026-10-27 tree | 2026-10-27 |
| 2 | `E-M11` row precision (true writers / rows) | **11 / 12** | same run; false positive is a function whose string literal contains the table name | `21a30af4…` | 2026-10-27 tree | 2026-10-27 |
| 3 | `E-M12` acceptance scenarios passed | **10 / 10** | `python lab/e-m12-run.py` | `eda90a18973a8639a902632d6fe498ec69a8baf7b7ead40cf3a7dedad0128f6d` | 2026-10-27 tree | 2026-10-27 |
| 4 | `E-M12` end-to-end: claimed vs recomputed coverage | **0.9 claimed / 0.0 recomputed -> lowered** | fixture DB + enumerator + merge + verify | `eda90a18973a8639a902632d6fe498ec69a8baf7b7ead40cf3a7dedad0128f6d` | 2026-10-27 tree | 2026-10-27 |

## What will fill it

| source card | metrics it will produce |
|---|---|
| `E-M9` | 6 substitutions: rejected / accepted, and the reason string for each |
| `E-M10` | detection per mutation class, false-rejection on valid bundles, corpus sha256 |
| first real pilot | assessor minutes per finding, findings per engagement, reproducible share |

## The generator, when it exists

The intended shape, so that the contract is not retrofitted after the first hand-typed number:

```
lab/metrics.py --card E-M10 --log lab/logs/e-m10-<timestamp>.log --write docs/METRICS.md
```

It reads the log, extracts counts, verifies the log's sha256 against the recorded one, and fails if a printed
number cannot be recomputed from the tree. Until that script exists, this file stays empty — an empty table is
honest, a filled one without logs is the failure mode the whole repository is built against.

## What this file does NOT do

- It does not record numbers quoted from other projects; those live in `docs/CLAIMS.md` with their artifact.
- It does not store the logs themselves — logs are artifacts, this is the index with digests.
- It does not claim coverage of anything. Zero rows means zero measurements, not zero risk.
