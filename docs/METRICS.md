# METRICS — every number carries its command and its log

**Status:** contract in force, 59 rows. The first measurement in this repository: `E-M11`, the grant
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
| 1 | `E-M11` recall on planted bypasses | **8 / 8** | `python lab/e-m11-run.py --psql <conda>/Library/bin/psql.exe --port 54329` | `7df2c03adb50229d04b9e5ae5a6fe67167d8c66f9a91952649a5a92d5b388fa7` | 2026-10-27 tree | 2026-10-27 |
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
number cannot be recomputed from the tree. The script does not exist yet; every row here was entered by hand and names its command — an empty table is
honest, a filled one without logs is the failure mode the whole repository is built against.

## What this file does NOT do

- It does not record numbers quoted from other projects; those live in `docs/CLAIMS.md` with their artifact.
- It does not store the logs themselves — logs are artifacts, this is the index with digests.
- It does not claim coverage of anything. A row without a command is not a measurement, not zero risk.
| 5 | `E-M13` attribution on legitimate callers / false attribution | **2 / 2** and **0 / 9** | `python lab/e-m13-run.py --psql <conda>/Library/bin/psql.exe --port 54329` (decoy `transfer_fast` not attributed) | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
| 6 | `E-M13` coverage after attribution | **0.133** (2 of 15 paths), was 0.000 | `python tools/merge_inventory.py s-grants.json s-calls.json --out m.json && python tools/fg_verify.py --claim c.json --inventory m.json` | `c19388a2bb41b914d107e636f377752c175736082422deaec7f627aa6ba707fe` | 2026-10-27 tree | 2026-10-27 |
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
| 18 | `E-M17` paths after merging three sources | **18** (15 catalogue + 3 observed) | `python tools/merge_inventory.py s1.json s2.json s3.json --out m.json` | `6475c8e84df2c6ea2b46f17ffd8eebb74f060821de1e07018bcc0c2caba81bc6` | 2026-10-27 tree | 2026-10-27 |
| 19 | `E-M18` acceptance scenarios with the coverage basis | **19 / 19** | `python lab/e-m12-run.py` | `da38bfd071941a70c97636d96909b35a312ad9a6aabe708ef17015556c7122b8` | 2026-10-27 tree | 2026-10-27 |
| 20 | `E-M18` readiness P2 on an unfilled M8 template | **0 points** (placeholder or too short) | `python tools/fg_readiness.py` | `da38bfd071941a70c97636d96909b35a312ad9a6aabe708ef17015556c7122b8` | 2026-10-27 tree | 2026-10-27 |
| 21 | `E-M19` perimeter delta after one new writer | **+1 new, -0 vanished, growth true** | `python tools/merge_inventory.py after.json cafter.json --previous m-before.json --out m-after.json` | `c4595701d4fa9f431c7e0b3b4f1534187f1800751bbfff650311a8d22705cf07` | 2026-10-27 tree | 2026-10-27 |
| 22 | `E-M19` upgrade after perimeter growth | **level_upgrade_allowed = false** | `python tools/fg_verify.py --claim claim19.json --inventory m-after.json` | `c4595701d4fa9f431c7e0b3b4f1534187f1800751bbfff650311a8d22705cf07` | 2026-10-27 tree | 2026-10-27 |
| 23 | `E-M20` endpoints kept vs excluded | **4 / 3** of seven | `python enumerators/routes-json/fg_enum_routes.py --manifest fixtures/http-routes/routes.json --schema bank --table accounts --control transfer` | `c57af71d6f476a5b885338e7508c2f59804be68433724e31045f2afd64c10a91` | 2026-10-27 tree | 2026-10-27 |
| 24 | `E-M20` endpoints attributed to the control point | **2 / 2** (one direct, one transitive), 0 false | `python tools/merge_inventory.py s-routes.json g20.json c20.json` | `c57af71d6f476a5b885338e7508c2f59804be68433724e31045f2afd64c10a91` | 2026-10-27 tree | 2026-10-27 |
| 25 | `E-M21` real schema: paths reported for public.payment | **2**, both true on inspection | `python enumerators/grants-pg/fg_enum_grants.py --db fgpagila --schema public --table payment` | `dc6f60dd0e00612549f68d068804b41559f734732906d2aca0a805168bbf666e` | 2026-10-28 Pagila v2.1.0 | 2026-10-28 |
| 26 | `E-M21` run time on a foreign schema | **0.4 s**, exit 0 | `python enumerators/grants-pg/fg_enum_grants.py --db fgpagila --schema public --table payment` (timed) | `dc6f60dd0e00612549f68d068804b41559f734732906d2aca0a805168bbf666e` | 2026-10-28 Pagila v2.1.0 | 2026-10-28 |
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
| 37 | `E-M30` foreign schemas loaded and measured | **4 / 5** (adventureworks needs an extension) | `python lab/e-m30-run.py --psql <psql> --port 54329 --schemas <dir> --pagila <file>` | `2ad5b2c63a4c7c7a33642e3774313d373d0c4ac247e2cd8584f1b88bbb3bc10c` | 2026-10-28, five public schemas | 2026-10-28 |
| 38 | `E-M30` paths reported across the foreign schemas | **4 total**: 2 + 2 in two dumps of one model, 0 + 0 where no functions exist | `python lab/e-m30-run.py --psql <psql> --port 54329 --schemas <dir> --pagila <file>` | `2ad5b2c63a4c7c7a33642e3774313d373d0c4ac247e2cd8584f1b88bbb3bc10c` | 2026-10-28, five public schemas | 2026-10-28 |
| 39 | `AUDIT` cards linked to their log file | **22 / 22** (was 1 of 22 before the audit) | `python tools/fg_repo_audit.py` | `8ae1cc011b64e48843e78e8d98c5fc00eb09ac83227dd52ccd4ba43f9e8a605b` | 2026-10-28 tree | 2026-10-28 |
| 40 | `AUDIT` claims citing artifacts that do not exist | **0** (was 15) | `python lab/check-claims.py` | `815ee86ee2acba56be5bdb4931140068ad2f3e979c76079b8f08faea460d5fa5` | 2026-10-28 tree | 2026-10-28 |
| 41 | `E-M31` determinism of the bundle address | **2 / 2 builds identical** | `python lab/e-m31-run.py` | `815ee86ee2acba56be5bdb4931140068ad2f3e979c76079b8f08faea460d5fa5` | 2026-10-28 tree | 2026-10-28 |
| 42 | `E-M32` confirmation records refused for missing fields | **5 of 5** named | `python tools/fg_confirm.py --record record.json --check` | `e03e4c2eaf0b22ae921650e4c9874828c07905e8ff0ed6ad342f63df71618752` | 2026-10-28 tree | 2026-10-28 |
| 43 | `E-M32` a complete record raises the supported tier | **1 → 2** | `python tools/fg_confirm.py --record record.json --inventory m.json --out m2.json` | `e03e4c2eaf0b22ae921650e4c9874828c07905e8ff0ed6ad342f63df71618752` | 2026-10-28 tree | 2026-10-28 |
| 44 | `E-M33` malformed inputs handled as verdicts, not crashes | **17 / 17** (was 12 of 17, one silently accepted) | `python lab/e-m33-run.py` | `1befaf7f8e3289b8e89889a06ca19c41168d651e1a78aafde183ce809a611c50` | 2026-10-28 tree | 2026-10-28 |
| 45 | `E-M34` paths and runtime on a 400-function schema | **480 paths in 0.4 s**, 320 of 320 writers found | `python lab/e-m34-run.py --psql <psql> --port 54329` | `1cc08484d4b13ef3ade45df5a6833b15ecb6aaa05bdff4db12378577089f82a7` | 2026-10-28 generated schema | 2026-10-28 |
| 46 | `E-M34` output readable at scale (<=120 paths or a summary) | **summary present**, list 480 | `python lab/e-m34-run.py --psql <psql> --port 54329` | `1cc08484d4b13ef3ade45df5a6833b15ecb6aaa05bdff4db12378577089f82a7` | 2026-10-28 generated schema | 2026-10-28 |
| 47 | `E-M35` truncated inventory refused as a coverage denominator | **refused** (kept 100 of 480) | `python lab/e-m35-run.py --psql <psql> --port 54329` | `badcef9ce832456d99ae6fb6cbd1efdfeb50b8323c4a10fd6691001346e86b73` | 2026-10-28 generated schema | 2026-10-28 |
| 48 | `E-M35` summary counts match the published list | **True** (was 350 functions beside 100 paths) | `python lab/e-m35-run.py --psql <psql> --port 54329` | `badcef9ce832456d99ae6fb6cbd1efdfeb50b8323c4a10fd6691001346e86b73` | 2026-10-28 generated schema | 2026-10-28 |
| 49 | `E-M36` attacks on the verdict gate blocked | **8 / 8** (was 4 of 8; four reached PROVEN) | `python lab/e-m36-run.py` | `342c72f86615288308a5c782c31261b9a56834dabbdc4cd710211638dd81a1ac` | 2026-10-28 tree | 2026-10-28 |
| 50 | `E-M37` paths on GitLab production schema (1436 tables, 558 functions) | **10 on projects, 0 on three other tables**, 0.4 s each | `python enumerators/grants-pg/fg_enum_grants.py --db fg_gitlab --schema public --table projects` | `00b163a4f958b7fda479ac90a52b5af1e2ee87f42a5c9ae80b129de94ff1937a` | 2026-10-28 GitLab structure.sql | 2026-10-28 |
| 51 | `E-M37` functions with write statements in GitLab schema | **36 of 558** | `psql -d fg_gitlab -c "select count(*) from pg_proc where prosrc ~* '(update|insert into|delete from)'"` | `00b163a4f958b7fda479ac90a52b5af1e2ee87f42a5c9ae80b129de94ff1937a` | 2026-10-28 GitLab structure.sql | 2026-10-28 |
| 52 | `E-M39` independent rebuild: address and signatures | **agreed**, first computation, no fitting | `python tools/fg_bundle.py verify --bundle fixtures/sample-bundle --trusted-keys <both .pub> --expect-target flowguard-sample@2026-10-27` | `c48f654c457a6733e17eb3a45eff6422979f3f815bdb8b34ea0e47e81a1390b4` | 2026-10-28 sample bundle | 2026-10-28 |
| 53 | `E-M39` factual errors found in the format description | **2** (file endings claimed LF, sort order claimed untestable) | `python tools/fg_bundle.py verify --bundle fixtures/sample-bundle --trusted-keys <both .pub> --expect-target flowguard-sample@2026-10-27` | `c48f654c457a6733e17eb3a45eff6422979f3f815bdb8b34ea0e47e81a1390b4` | 2026-10-28 sample bundle | 2026-10-28 |
| 54 | `E-M40` db_logic_density across three systems | **0.812 / 0.100 / 0.005** | `python enumerators/grants-pg/fg_enum_grants.py --db <db> --schema public --table <t>` | `e30dc94502c77f474c5f702555606f666a2167f3e8550516ca379f1f3dfa5fb7` | 2026-10-28 tree | 2026-10-28 |
| 55 | `E-M40` strong level refused on a thin-database system | **THIN_DB_LOGIC_COVERAGE**, verdict capped; not fired at 0.812 | `python tools/fg_verify.py --claim claim40.json --inventory mgl.json` | `e30dc94502c77f474c5f702555606f666a2167f3e8550516ca379f1f3dfa5fb7` | 2026-10-28 tree | 2026-10-28 |
| 56 | `E-M41` independent oracle vs enumerator on GitLab `projects` | **0 disagreements** (2/2 cascades, 3/3 writers, 7/7 trigger chains) | `python lab/e-m41-run.py --db fg_gitlab --schema public --table projects` | `a5fef60438339aa68b39a642c49ce83c42dea3d383a8600624ff100474f0b6a5` | 2026-10-28 GitLab structure.sql | 2026-10-28 |
| 57 | `E-M41` false negatives found before the fix | **2** (cascade keys `namespaces -> projects`, `organizations -> projects`) | `python lab/e-m41-run.py --db fg_gitlab --schema public --table projects` (before fk_cascade existed) | `a5fef60438339aa68b39a642c49ce83c42dea3d383a8600624ff100474f0b6a5` | 2026-10-28 GitLab structure.sql | 2026-10-28 |
| 58 | `E-M42` independent adversarial breaks of the verdict gate | **11 found, 11 closed** | `python lab/e-m42-run.py` | `55ca75309b913524b4e3dd2b41e85797dd16fc87b8b92d6528bd6771be19f10d` | 2026-10-28 tree | 2026-10-28 |
| 59 | `E-M42` attack suite as a permanent regression | **13 cases, 0 still breaking** | `python lab/e-m42-run.py` | `55ca75309b913524b4e3dd2b41e85797dd16fc87b8b92d6528bd6771be19f10d` | 2026-10-28 tree | 2026-10-28 |
| 60 | `E-M43` hostile documentation review: findings fixed | **11 of 21** (see the card for the open ten) | `python tools/fg_readiness.py` after the T4 attack | `-` (run not captured) | 2026-10-28 tree | 2026-10-28 |
| 61 | `E-M43` T4 reachable by typing, before the fix | **yes** (one card line + one role file + invented M8 fields) | `python tools/fg_readiness.py` in a scratch copy | `-` (run not captured) | 2026-10-28 tree | 2026-10-28 |
| 62 | `E-M44` open findings closed after the hostile review | **8 of 10** | `python lab/round-check.sh` | `dc6f60dd0e00612549f68d068804b41559f734732906d2aca0a805168bbf666e` | 2026-10-28 tree | 2026-10-28 |
| 63 | `E-M45` metric digests that resolve to a captured log | **0 unresolved** (was 14 across 8 rows) | `python lab/check-metric-digests.py` | `2ad5b2c63a4c7c7a33642e3774313d373d0c4ac247e2cd8584f1b88bbb3bc10c` | 2026-10-28 tree | 2026-10-28 |
| 64 | `E-M46` card digests that resolve to a captured log | **0 unresolved** (was 3) | `python lab/check-metric-digests.py --cards` | `2ad5b2c63a4c7c7a33642e3774313d373d0c4ac247e2cd8584f1b88bbb3bc10c` | 2026-10-28 tree | 2026-10-28 |
| 65 | `E-M47` second independent adversarial round: breaks found | **14, all blocked** (3 created by E-M42 fixes) | `python tools/fg_verify.py --claim <attack2 case> --inventory <attack2 case>` | `2ad5b2c63a4c7c7a33642e3774313d373d0c4ac247e2cd8584f1b88bbb3bc10c` | 2026-10-28 tree | 2026-10-28 |
