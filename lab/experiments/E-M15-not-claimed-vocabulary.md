---
id: E-M15
hypothesis: H-M15
status: completed
base_commit: "uncommitted tree; the verifier digest is in the run log"
started: "2026-10-27T22:30:00+03:00"
finished: "2026-10-27T22:40:00+03:00"
environment: "Windows, CPython 3.13.11; PostgreSQL not required for this card"
command: "python lab/e-m12-run.py"
threshold: "Pre-registered: an unknown not_claimed code is refused, a declared level that omits its required codes is refused, and the twelve earlier acceptance scenarios do not regress. All of it, in one suite, 14/14."
result: "14/14. T13 (not_claimed given as prose) refused with REPORT_BUNDLE_INCONSISTENT; T14 (PROVEN declared with only NC-01/NC-02) refused with MISSING_EVIDENCE naming the four absent codes. The twelve earlier scenarios pass unchanged. The sample bundle was regenerated with the vocabulary and verifies on a clean clone."
verdict: supports
---

# E-M15 — `not_claimed` becomes a checkable vocabulary

## The problem this closes

Round 7, review 2: *"not_claimed легко заполняется шаблонной фразой, линтер этого не отличит."* Correct. A free-text
field labelled "what we do not claim" is the most comfortable place in any attestation for boilerplate, and it
absorbs exactly the criticism it was meant to invite.

## What was built

**A vocabulary.** `docs/NOT-CLAIMED.md` defines NC-01…NC-10. Each code names something the attestation refuses to
assert **and why it cannot be asserted** — not "results may vary" but "the inventory is a merge of sources with
declared blind spots, so completeness is unprovable".

**A required set per level:**

| level | codes that must be present |
|---|---|
| `CONSISTENT_DECLARED` | NC-01, NC-02 |
| `SCOPED_ASSURANCE` | + NC-04, NC-05 |
| `PROVEN` | + NC-03, NC-10 |

**Enforcement** lives in the verifier and reads the registry from the document, so the table is the single source of
truth: a new code is added by editing the document, and no code change is needed.

## Run

```
T1-T12  PASS  (unchanged)
T13     PASS  not_claimed is prose instead of vocabulary -> REPORT_BUNDLE_INCONSISTENT
T14     PASS  PROVEN declared with only NC-01/NC-02 -> MISSING_EVIDENCE, four codes named

scenarios passed: 14/14
```

## Second artefact touched

The sample bundle's claim now carries `["NC-01", "NC-02"]` instead of two prose sentences. That changed the address,
so the bundle was regenerated and the README updated; the demo signing key stays outside the repository. Verified
again on a clean clone after regeneration, because the earlier EOL defect makes "it verifies here" an insufficient
claim.

## What this does not do

- It does not check that a refusal is **sincere**. A claim listing NC-01 while its prose asserts completeness is a
  contradiction a human must catch; the machine checks presence, not truth.
- It does not make the list **complete**. A thing nobody thought to refuse is absent from the table — which is the
  same limitation as an inventory with a blind spot, and gets the same treatment: it is declared, not denied.
- It does not replace the level's other requirements. Codes are a floor on honesty, not a substitute for coverage.

## Log

`lab/logs/e-m15-2026-10-27.log` — sha256 `6af1f48e20bf399f7a1165380f6fb9ddfd718492afd1789aaa64486afade415a`.
