---
id: E-M83
hypothesis: H-M83
status: completed
base_commit: "8fb089d"
started: "2026-10-31T02:50:00+03:00"
finished: "2026-10-31T03:15:00+03:00"
environment: "Windows, rustc 1.99.1 + WinLibs UCRT, CPython 3.13.11"
command: "cd core-rs && cargo build --offline && cd .. && python lab/e-m83-run.py"
sensitivity: |
  The comparison is over eight discrete facts extracted from two generated pages (verdict present, NC-01,
  NC-02, the phrase "paths enumerated", the coverage number, "no refusals", no <script>, no http link). A
  generator that omits a fact or changes the coverage number by any amount is detected; a generator that
  differs only in whitespace is deliberately not. Detection floor: 1 fact out of 8, or 0.01 on coverage.
branches: |
  confirm:    all 8 facts equal, and the pages are self-contained (no script, no network).
  refute:     any fact differs while the bundle is unchanged - one of the two generators is wrong.
  inconclusive: a generator fails to run at all (counted as a failure to compare, not as agreement).
stop_rule: |
  Stop after the eight facts and the two self-containment checks. Do not add facts during the run: an
  assertion about a ninth fact written after seeing the output is not pre-registered.
analysis_plan: |
  Every figure printed comes from `python lab/e-m83-run.py`, which generates both pages into a temp directory
  and extracts the facts with a tag-stripping regex. No number in this card was typed by hand.
threshold: "Pre-registered: all eight facts equal; both pages free of <script> and of any http link."
result: "Eight of eight facts equal, both pages self-contained. The pages are not byte-identical (2662 vs 2598 bytes) - whitespace and one signature-binding line differ - which is why the comparison is over facts and not over bytes: HTML whitespace is not a claim."
verdict: supports
---

# E-M83 — the report generator moves to Rust, and the Python one becomes the differential

## What was built

`fg-core report --bundle <dir> --out <file.html>`: the same self-contained page as `tools/fg_report_html.py`, now
in the language the product is written in (`ADR-0017`). No dependencies beyond what the core already uses;
`serde_json`, the address, the signature forms and the claim arithmetic are the ones already in the binary.

The page keeps the property that matters: no `<script`, no external link, no build step, so a stranger reads the
artifact offline and re-generating it from the same bundle gives the same facts.

## The differential, and why it is over facts rather than bytes

The two generators produce different byte lengths (2662 vs 2598 here) because whitespace differs and the Rust page
prints the signature binding per signer. Byte equality would be a false target: HTML whitespace is not a claim, and
pinning it would make every cosmetic change look like a defect.

So `lab/e-m83-run.py` extracts eight facts from each page and requires them all to agree:

```
ok   verdict      rust=True python=True
ok   nc01/nc02    rust=True python=True
ok   coverage     rust='0.50' python='0.50'
ok   refusals     rust=True python=True
ok   no_script / no_network   rust=True python=True
facts compared: 8, differing: 0
```

## What this says about the port as a whole

The Rust core now covers the address, both signature forms, the claim arithmetic and the report. What is still
Python: the database enumerators (they shell out to `psql`), the migrations enumerator (text parsing, the next
candidate), `fg_bundle create`, and the experiment harnesses. That is a coherent split rather than a half-finished
one — every fact a consumer reads is now produced by the Rust binary, and the Python side produces inventories.

## What this does not do

- It does not make the Rust binary the only generator in the ritual: the Python one stays, because a differential
  needs two.
- It does not port the migrations enumerator. That is the next piece of text-only work, and it is the one that
  would let `--recount` run without Python.
- It does not change the ceiling. A page about a document is still about that document.
