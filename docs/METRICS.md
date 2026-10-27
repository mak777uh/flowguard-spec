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
| 5 | `E-M13` attribution on legitimate callers / false attribution | **2 / 2** and **0 / 9** | pgcalls over the fixture; decoy `transfer_fast` not attributed | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
| 6 | `E-M13` coverage after attribution | **0.133** (2 of 15 paths), was 0.000 | grants + pgcalls merged, then `fg_verify` | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
| 7 | `E-M9` substitution, run 1 without anchors | **3 / 6** (refutes) | `python lab/e-m9-run.py --no-anchors` | `-` | 2026-10-27 tree | 2026-10-27 |
| 8 | `E-M9b` substitution with two external anchors | **6 / 6** | `python lab/e-m9-run.py` | `918b5cafed2f0ec66f03d3e638588a3f0f3d5cd4df319ef033904d36a1c59943` | 2026-10-27 tree | 2026-10-27 |
| 9 | `E-M10` D-1 detection on 68 generated mutants | **1.000** | `python lab/e-m10-run.py` | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
| 10 | `E-M10` D-2 detection on 34 generated mutants | **1.000** | same run | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
| 11 | `E-M10` false rejection on 30 valid bundles | **0.000** | same run | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
