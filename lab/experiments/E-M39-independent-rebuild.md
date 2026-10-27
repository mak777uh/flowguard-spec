---
id: E-M39
hypothesis: H-M39
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T05:00:00+03:00"
finished: "2026-10-28T05:20:00+03:00"
environment: "Windows, CPython 3.13.11; independent agent, fresh context, forbidden from reading the implementation"
command: "spawn an agent with C:\\111\\_m7\\sample-bundle only (bundle + README.md); it may not read the repository"
threshold: "Pre-registered: a rebuilder with only the description reproduces the address, verifies both signatures, checks every object, uses no brute-force search for the answer, and reports every place the description was ambiguous or wrong. Every wrong statement in the description counts against the description."
rebuild_result: agreed by an independent agent on 2026-10-28 (description only, no source access; an AI agent, same model family, not a third-party human)
result: "Address matched on the first computation: e369994878f1b4cb…, canonical length 1388 bytes. Both signatures verified, and every predicted negative control failed (raw digest bytes, sha256: prefix, trailing LF/CRLF, uppercase, NUL). 5 of 5 objects matched, inventory_digest resolved to a real object. No brute force was used to find the answer; the variants were computed afterwards to test the page's own claims. The rebuilder found two factual errors in my description: the files shipped CRLF while the page said LF, and the page claimed sort order was untestable when the bundle in fact distinguishes code-point from locale collation."
verdict: supports
---

# E-M39 — the rebuild that agreed, and the two lies in my own description

## What was done differently from E-M38

`E-M38` failed as a test: the description was missing, and the rebuilder reproduced the address by fitting sixteen
variants — agreement bought with the answer in hand. This time the description was present, the agent was forbidden
from reading the implementation, and **the first computation matched**. No fitting.

## Result

| check | outcome |
|---|---|
| address | computed `e369994878f1b4cb…` = recorded. Canonical length 1388 bytes |
| signatures | 2 verified, 0 failed; the two keys are distinct |
| negative controls | 32 raw digest bytes, `sha256:` prefix, hex+`\n`, hex+`\r\n`, uppercase, hex+`\0` — all fail, as predicted |
| objects | 5 checked, 5 matching; `inventory_digest` resolves to `inventory.json` |
| brute force | none |

## The two things the description got wrong

**1. It said LF; the files shipped CRLF.** `manifest.sha256` was 66 bytes (hex + `\r\n`) and each `.sig` 90 bytes. An
implementer reading the page literally would read the value with a trailing `\r`, fail both signatures, and conclude
the artifact was forged. The rebuilder called this exactly right, and noted that the two signature failures would look
like a signing defect, not a documentation defect.

*Fixed:* the three text files are now LF-terminated and `fg_bundle create` writes bytes explicitly. The address is
unchanged, because the signature covers the address and the address is derived from `bundle.json` only.

**2. The page claimed sort order was untestable in this bundle. It is testable.** `claim_id` and `claimed_coverage`
sort differently under code-point order and under punctuation-ignoring collation — the rebuilder produced a different
address (`7af6136b…`) with the locale variant. My confident "this cannot be distinguished here" was simply false.

*Fixed:* the page now states that recursive code-point sorting is required and that this bundle distinguishes it.

## The most likely place a future rebuilder diverges

Not the traps the page advertises. The rebuilder's own answer:

> **Recursive vs top-level-only key sorting.** It is the only unstated choice that actually moves the address, the
> page never says the sort applies to nested objects, and unlike the "don't hash the file bytes" trap it gets no
> warning at all.

That is now stated explicitly, because a warning nobody writes is a trap.

## What this establishes, and what it does not

**Establishes:** the format description is sufficient for an implementation that has never seen the code to reproduce
the address, verify the signatures and check the objects — after this round's fixes. The description now states every
rule that moves the address.

**Does not establish:** that a **human stranger** can do it. The rebuilder is an AI agent from the same model family
as the author: it cannot independently confirm a shared misconception, and it was given a tidy directory rather than a
repository. `M7` is now `present in the weaker form`, and `docs/STATUS-v0.md` says so rather than claiming the
stronger one.

**Also does not establish:** that the claim is true. The rebuild checks the envelope, not the letter.

## Log

``lab/logs/e-m39-2026-10-28.log`` — the rebuilder's report, verbatim.
