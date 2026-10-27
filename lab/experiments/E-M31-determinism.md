---
id: E-M31
hypothesis: H-M31
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T02:20:00+03:00"
finished: "2026-10-28T02:24:00+03:00"
environment: "Windows, CPython 3.13.11, cryptography 50.0.2"
command: "python lab/e-m31-run.py"
threshold: "Pre-registered: two independent builds of the same subject, claim and inventory, with the same key, produce byte-identical addresses."
result: "Identical. Both builds returned 7fd84271…, so a bundle address is a function of the inputs and not of the time, the order of files, or the signature. The claim C-02 that used to point at a planned replay harness now points at this card."
verdict: supports
---

# E-M31 — the address is a function of the input

## Why

Claim C-02 said "two runs of the same input produce a byte-identical bundle" and cited lab/e2e/replay, which never
existed — one of the 15 phantom citations the audit found. Rather than withdraw a claim that is easy to check, it was
checked.

## Run

`
build 1: 7fd842713096c6ee…
build 2: 7fd842713096c6ee…
identical addresses: True
`

## What it establishes

The bundle address depends on the claim, the inventory, the subject bytes and the payload names — not on wall-clock
time, file order, or the signature. Ed25519 signatures are deterministic, and the canonical JSON sorts keys, so the
same inputs produce the same address.

## What it does not establish

- That the **content** of an address means the same thing twice. Two builds of a changed system produce different
  addresses, which is the point.
- That the signature is reproducible across **implementations**. A different Ed25519 library should produce the same
  bytes, but that is what M7 would test, and M7 has not happened.

## Log

`lab/logs/e-m31-2026-10-28.log` — sha256 `815ee86ee2acba56be5bdb4931140068ad2f3e979c76079b8f08faea460d5fa5`.
