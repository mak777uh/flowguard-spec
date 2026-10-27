---
id: E-M38
hypothesis: H-M38
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T04:35:00+03:00"
finished: "2026-10-28T04:55:00+03:00"
environment: "Windows, CPython 3.13.11; independent agent with no access to the implementation"
command: "spawn an agent with C:\\111\\_m7\\sample-bundle only; it may not read the repository"
threshold: "Pre-registered: an agent that has never seen the implementation reproduces the bundle address from the written description alone, verifies both signatures, and checks every object digest. Any ambiguity in the description counts against the description, not against the rebuilder."
result: "Address reproduced exactly (c3a2e79b…), both signatures verified, all four objects matched - BUT the description was not in the directory at all: a packaging error removed it. The rebuilder matched the address by fitting sixteen candidate canonicalisations, and said so plainly. It then produced thirteen concrete defects in the format, two of which were real bugs: inventory_digest matched nothing in the bundle, and three of four objects contained CRLF so their digests were not portable. The test as designed is invalid and must be repeated; the defects are real."
verdict: refutes
---

# E-M38 — the rebuild that found my documentation was missing

## What I intended

Hand an agent an isolated directory with a bundle and a one-page format description, forbid it from reading the
implementation, and see whether it reproduces the address. That is M7.

## What happened

**The description was not in the directory.** My packaging step copied the bundle with README.md deleted and then
tried to copy it to another name — the copy silently failed, and I did not check. The rebuilder opened the directory,
found no description, and said so instead of guessing quietly.

It then did something more useful than the test: it derived the rules **from the artifacts themselves** by fitting
sixteen candidate canonicalisations, reproduced the address exactly (c3a2e79b…), verified both Ed25519 signatures,
and confirmed all four object digests.

It also stated the limitation in one sentence, which is the most valuable thing in its report:

> my canonicalization rule was found by fitting 16 plausible variants and taking the one that matched. That is
> pattern-matching the answer, not predicting it.

So: **agreement, obtained by cheating with the answer available.** The test is invalid. The defects it listed are not.

## The thirteen defects, and which were real

Two were bugs in the artifact, confirmed by inspection:

1. **inventory_digest matched nothing** — not the canonical bytes, not any object, not any concatenation. A third of
   the bundle's trust story pointed at a document that was not in the bundle.
2. **Three of four objects contained CRLF.** Content-addressed files whose hash depends on the client's line-ending
   conversion: a text-mode copy on Linux produces different objects. Nothing declared normalisation.

The rest were documentation holes, all confirmed:

- the trailing newline rule was undeclared, and a single \n changes the address;
- the signed message type was undeclared (digest bytes? hex? canonical payload?);
- the two digest conventions (sha256: prefix present in two places, absent in four) were undeclared;
- nsure_ascii cannot be resolved from an all-ASCII bundle;
- float formatting, sort collation and role semantics are untested by this vector.

## What was fixed

g_bundle create now puts the inventory **inside** the bundle as an object and sets inventory_digest to its bare
hex; every digest is bare hex; the sample bundle was rebuilt with LF inputs so objects are portable; and the
description was rewritten stating every rule above, including the ones this bundle cannot demonstrate.

## What this means for M7

ebuild_result: differed would be wrong — the address agreed. greed would be worse — the agreement came from
fitting. The honest record is **refuted as a test**: the description was absent, so the experiment measured the wrong
thing. It is re-run with the description present, and that run is what M7 will be recorded from.

## Log

`lab/logs/e-m38-2026-10-28.log` — the rebuilder's report, verbatim.
