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
| 23 | `E-M20` endpoints kept vs excluded | **4 / 3** of seven | `python enumerators/routes-json/fg_enum_routes.py --manifest fixtures/http-routes/routes.json --schema bank --table accounts --control transfer` | `66088d24ab5cb0bbe60b6e931c0fa70cda70e19932de73779c47562cfc5c62f6` | 2026-10-27 tree | 2026-10-27 |
| 24 | `E-M20` endpoints attributed to the control point | **2 / 2** (one direct, one transitive), 0 false | `python tools/merge_inventory.py s-routes.json g20.json c20.json` | `66088d24ab5cb0bbe60b6e931c0fa70cda70e19932de73779c47562cfc5c62f6` | 2026-10-27 tree | 2026-10-27 |
| 25 | `E-M21` real schema: paths reported for public.payment | **2**, both true on inspection | `python enumerators/grants-pg/fg_enum_grants.py --db fgpagila --schema public --table payment` | `d0293d7b7ab568279cc33d7ba731de3ab34e198e8a39cb289eb24f0542b2e6a2` | 2026-10-28 Pagila v2.1.0 | 2026-10-28 |
| 26 | `E-M21` run time on a foreign schema | **0.4 s**, exit 0 | `python enumerators/grants-pg/fg_enum_grants.py --db fgpagila --schema public --table payment` (timed) | `d0293d7b7ab568279cc33d7ba731de3ab34e198e8a39cb289eb24f0542b2e6a2` | 2026-10-28 Pagila v2.1.0 | 2026-10-28 |
| 27 | `E-M22` claim rows whose wording is checked against their evidence type | **18 / 18** | `python lab/check-claims.py` | `89b42bab0e5cfa5f2e585d40649ce7789578505869c312874b7003c4bdadd7cd` | 2026-10-28 tree | 2026-10-28 |
| 28 | `E-M22` negative controls for every guard | **7 / 7** | `bash lab/selftest-guards.sh` | `89b42bab0e5cfa5f2e585d40649ce7789578505869c312874b7003c4bdadd7cd` | 2026-10-28 tree | 2026-10-28 |
| 29 | `E-M23` acceptance scenarios with three-state coverage | **21 / 21** | `python lab/e-m12-run.py` | `300c88a52863270876825f4bd6c60e2457a151e3ef831ebda2a90bbc977dabeb` | 2026-10-28 tree | 2026-10-28 |
| 30 | `E-M23` observed-but-not-enumerated verbs on the fixture | **1** (DELETE), upgrade blocked | `python tools/fg_verify.py --claim claim23.json --inventory m23.json` | `300c88a52863270876825f4bd6c60e2457a151e3ef831ebda2a90bbc977dabeb` | 2026-10-28 tree | 2026-10-28 |
| 31 | `E-M25` ambiguity detection on an overloaded control point | **1 / 1**, attribution withdrawn | `python lab/e-m25-run.py --psql <psql> --port 54329` | `1889c75a949bc817e6c0b36f0e98f5b505495abdcb461cae8c7e789c1185cd09` | 2026-10-28 tree | 2026-10-28 |
| 32 | `E-M25` upgrade after an ambiguous attribution | **blocked** | `python lab/e-m25-run.py --psql <psql> --port 54329` | `1889c75a949bc817e6c0b36f0e98f5b505495abdcb461cae8c7e789c1185cd09` | 2026-10-28 tree | 2026-10-28 |
| 33 | `E-M26` delta classification: add then remove a writer | **additive 1 / subtractive 1**, growth only on the addition | `python lab/e-m26-run.py --psql <psql> --port 54329` | `9ab2d7753c7554736f402593e0af771c9322f37e111655b2650ce46c0aa88daa` | 2026-10-28 tree | 2026-10-28 |
| 34 | `E-M27` acceptance scenarios with typed exclusion reasons | **23 / 23** | `python lab/e-m12-run.py` | `b323be8b120b99e41edc13716805e2ca8287ee90a577c228e597d9f30db343ba` | 2026-10-28 tree | 2026-10-28 |
| 35 | `E-M28` signature role cases (unknown, incomplete, SoD, contract-as-role, valid) | **5 / 5** | `python lab/e-m28-run.py` | `506bc4f090ca0e01f4c498c8d9a76abcbbdc8e62f944908970ea9691b806c6d0` | 2026-10-28 tree | 2026-10-28 |
| 36 | `E-M29` acceptance scenarios with the evidence tier | **25 / 25** | `python lab/e-m12-run.py` | `ba021051fc9fcb7a814442552d8c8f0a911d3cfa3154a7b06d94eb21284ded9e` | 2026-10-28 tree | 2026-10-28 |
| 37 | `E-M30` foreign schemas loaded and measured | **4 / 5** (adventureworks needs an extension) | `python lab/e-m30-run.py --psql <psql> --port 54329 --schemas <dir> --pagila <file>` | `f8041dc77b546aa7cda481efff4184c376b2a79f149ddf220b6c43b06bfc779e` | 2026-10-28, five public schemas | 2026-10-28 |
| 38 | `E-M30` paths reported across the foreign schemas | **4 total**: 2 + 2 in two dumps of one model, 0 + 0 where no functions exist | `python lab/e-m30-run.py --psql <psql> --port 54329 --schemas <dir> --pagila <file>` | `f8041dc77b546aa7cda481efff4184c376b2a79f149ddf220b6c43b06bfc779e` | 2026-10-28, five public schemas | 2026-10-28 |
| 39 | `AUDIT` cards linked to their log file | **22 / 22** (was 1 of 22 before the audit) | `python tools/fg_repo_audit.py` | `4462d7977460f1d74b1720a1f6754badba41572371ad03858b2d579d6c5fed02` | 2026-10-28 tree | 2026-10-28 |
| 40 | `AUDIT` claims citing artifacts that do not exist | **0** (was 15) | `python lab/check-claims.py` | `815ee86ee2acba56be5bdb4931140068ad2f3e979c76079b8f08faea460d5fa5` | 2026-10-28 tree | 2026-10-28 |
| 41 | `E-M31` determinism of the bundle address | **2 / 2 builds identical** | `python lab/e-m31-run.py` | `815ee86ee2acba56be5bdb4931140068ad2f3e979c76079b8f08faea460d5fa5` | 2026-10-28 tree | 2026-10-28 |
| 42 | `E-M32` confirmation records refused for missing fields | **5 of 5** named | `python tools/fg_confirm.py --record record.json --check` | `e03e4c2eaf0b22ae921650e4c9874828c07905e8ff0ed6ad342f63df71618752` | 2026-10-28 tree | 2026-10-28 |
| 43 | `E-M32` a complete record raises the supported tier | **1 → 2** | `python tools/fg_confirm.py --record record.json --inventory m.json --out m2.json` | `e03e4c2eaf0b22ae921650e4c9874828c07905e8ff0ed6ad342f63df71618752` | 2026-10-28 tree | 2026-10-28 |
| 44 | `E-M33` malformed inputs handled as verdicts, not crashes | **17 / 17** (was 12 of 17, one silently accepted) | `python lab/e-m33-run.py` | `1befaf7f8e3289b8e89889a06ca19c41168d651e1a78aafde183ce809a611c50` | 2026-10-28 tree | 2026-10-28 |
| 45 | `E-M34` paths and runtime on a 400-function schema | **480 paths in 0.4 s**, 320 of 320 writers found | `python lab/e-m34-run.py --psql <psql> --port 54329` | `1cc08484d4b13ef3ade45df5a6833b15ecb6aaa05bdff4db12378577089f82a7` | 2026-10-28 generated schema | 2026-10-28 |
| 46 | `E-M34` output readable at scale (<=120 paths or a summary) | **summary present**, list 480 | `python lab/e-m34-run.py --psql <psql> --port 54329` | `1cc08484d4b13ef3ade45df5a6833b15ecb6aaa05bdff4db12378577089f82a7` | 2026-10-28 generated schema | 2026-10-28 |
| 47 | `E-M35` truncated inventory refused as a coverage denominator | **refused** (kept 100 of 480) | `python lab/e-m35-run.py --psql <psql> --port 54329` | `badcef9ce832456d99ae6fb6cbd1efdfeb50b8323c4a10fd6691001346e86b73` | 2026-10-28 generated schema | 2026-10-28 |
| 48 | `E-M35` summary counts match the published list | **True** (was 350 functions beside 100 paths) | `python lab/e-m35-run.py --psql <psql> --port 54329` | `badcef9ce832456d99ae6fb6cbd1efdfeb50b8323c4a10fd6691001346e86b73` | 2026-10-28 generated schema | 2026-10-28 |
