# METRICS — every number carries its command and its log

**Status:** contract in force, **zero rows**. There is no measurement in this repository yet, and this file exists
so that the first one cannot be typed by hand.

## The rule

> A number enters this file only with three things: the command that produced it, the sha256 of the log it was
> extracted from, and the commit it was measured at. A number without a log is not published.

Why so strict: a number in a document rots on every cycle. One sibling repository learned this the hard way — its
metrics document still described a run from twelve cards ago, because the number was typed and the runs were not.
The fix there was the same: make the header generated from the carrier, not written by a person.

## Table

| # | metric | value | command | log sha256 | commit | measured |
|---|---|---|---|---|---|---|
| — | *(none yet)* | — | — | — | — | — |

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
