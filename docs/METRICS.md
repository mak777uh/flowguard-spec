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
| 2 | `E-M11` row precision (true writers / rows) | **11 / 12** | `python lab/e-m11-run.py --psql <conda>/Library/bin/psql.exe --port 54329` (same invocation; the false positive is a function whose string literal contains the table name) | `21a30af4…` | 2026-10-27 tree | 2026-10-27 |
| 3 | `E-M12` acceptance scenarios passed | **10 / 10** | `python lab/e-m12-run.py` | `eda90a18973a8639a902632d6fe498ec69a8baf7b7ead40cf3a7dedad0128f6d` | 2026-10-27 tree | 2026-10-27 |
| 4 | `E-M12` end-to-end: claimed vs recomputed coverage | **0.9 claimed / 0.0 recomputed -> lowered** | `python enumerators/grants-pg/fg_enum_grants.py ... && python tools/merge_inventory.py ... && python tools/fg_verify.py --claim ... --inventory ...` | `eda90a18973a8639a902632d6fe498ec69a8baf7b7ead40cf3a7dedad0128f6d` | 2026-10-27 tree | 2026-10-27 |

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
| 5 | `E-M13` attribution on legitimate callers / false attribution | **2 / 2** and **0 / 9** | `python lab/e-m13-run.py --psql <conda>/Library/bin/psql.exe --port 54329` (decoy `transfer_fast` not attributed) | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
| 6 | `E-M13` coverage after attribution | **0.133** (2 of 15 paths), was 0.000 | `python tools/merge_inventory.py s-grants.json s-calls.json && python tools/fg_verify.py ...` | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
| 7 | `E-M9` substitution, run 1 without anchors | **3 / 6** (refutes) | `python lab/e-m9-run.py --no-anchors` | `-` | 2026-10-27 tree | 2026-10-27 |
| 8 | `E-M9b` substitution with two external anchors | **6 / 6** | `python lab/e-m9-run.py` | `918b5cafed2f0ec66f03d3e638588a3f0f3d5cd4df319ef033904d36a1c59943` | 2026-10-27 tree | 2026-10-27 |
| 9 | `E-M10` D-1 detection on 68 generated mutants | **1.000** | `python lab/e-m10-run.py` | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
| 10 | `E-M10` D-2 detection on 34 generated mutants | **1.000** | `python lab/e-m10-run.py` | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
| 11 | `E-M10` false rejection on 30 valid bundles | **0.000** | `python lab/e-m10-run.py` | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-27 tree | 2026-10-27 |
| 12 | `E-M14` acceptance scenarios after exclusion binding | **12 / 12** | `python lab/e-m12-run.py` | `06b7bbceb1c767bd2847c8c9a7010d1560c64e5d7c973eb5d854e773b94dce06` | 2026-10-27 tree | 2026-10-27 |
| 13 | `E-M14` claims that passed before binding and must not | **2** (invented exclusion, core path excluded) | `python lab/e-m12-run.py` (T11 and T12) | `06b7bbceb1c767bd2847c8c9a7010d1560c64e5d7c973eb5d854e773b94dce06` | 2026-10-27 tree | 2026-10-27 |
| 14 | `E-M15` acceptance scenarios with the not_claimed vocabulary | **14 / 14** | `python lab/e-m12-run.py` | `6af1f48e20bf399f7a1165380f6fb9ddfd718492afd1789aaa64486afade415a` | 2026-10-27 tree | 2026-10-27 |
| 15 | `E-M16` acceptance scenarios with weighted perimeter | **17 / 17** | `python lab/e-m12-run.py` | `edfe264ee531c5b92a4319c51fc3c7a94edbba1ebb9f474d0607327a13929d8b` | 2026-10-27 tree | 2026-10-27 |
| 16 | `E-M16` outside weighted risk on the fixture | **1.000** (67/67 weights) | `python tools/fg_perimeter.py --inventory tools/_tmp/m3.json` | `edfe264ee531c5b92a4319c51fc3c7a94edbba1ebb9f474d0607327a13929d8b` | 2026-10-27 tree | 2026-10-27 |
| 17 | `E-M17` runtime source: direct writes observed vs function-mediated | **3 / 3** and **0 / 2** (declared under-count) | `python enumerators/runtime-pg/fg_enum_runtime.py ... --workload fixtures/pg-bypass/02-workload.sql` | `6475c8e84df2c6ea2b46f17ffd8eebb74f060821de1e07018bcc0c2caba81bc6` | 2026-10-27 tree | 2026-10-27 |
| 18 | `E-M17` paths after merging three sources | **18** (15 catalogue + 3 observed) | `python tools/merge_inventory.py s1.json s2.json s3.json` | `6475c8e84df2c6ea2b46f17ffd8eebb74f060821de1e07018bcc0c2caba81bc6` | 2026-10-27 tree | 2026-10-27 |
| 19 | `E-M18` acceptance scenarios with the coverage basis | **19 / 19** | `python lab/e-m12-run.py` | `da38bfd071941a70c97636d96909b35a312ad9a6aabe708ef17015556c7122b8` | 2026-10-27 tree | 2026-10-27 |
| 20 | `E-M18` readiness P2 on an unfilled M8 template | **0 points** (placeholder or too short) | `python tools/fg_readiness.py` | `da38bfd071941a70c97636d96909b35a312ad9a6aabe708ef17015556c7122b8` | 2026-10-27 tree | 2026-10-27 |
| 21 | `E-M19` perimeter delta after one new writer | **+1 new, -0 vanished, growth true** | `python tools/merge_inventory.py after.json cafter.json --previous m-before.json` | `0bbf14eefcdf84d528eb86e24e8eea1b178ed56649509ee77da16b7486954e90` | 2026-10-27 tree | 2026-10-27 |
| 22 | `E-M19` upgrade after perimeter growth | **level_upgrade_allowed = false** | `python tools/fg_verify.py --claim claim19.json --inventory m-after.json` | `0bbf14eefcdf84d528eb86e24e8eea1b178ed56649509ee77da16b7486954e90` | 2026-10-27 tree | 2026-10-27 |
