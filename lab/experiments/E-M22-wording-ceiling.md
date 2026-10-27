---
id: E-M22
hypothesis: H-M22
status: completed
base_commit: "uncommitted tree"
started: "2026-10-28T00:10:00+03:00"
finished: "2026-10-28T00:22:00+03:00"
environment: "Windows, CPython 3.13.11"
command: "python lab/check-claims.py && bash lab/selftest-guards.sh"
threshold: "Pre-registered: (a) the wording ceiling is enforced mechanically, (b) a claim typed statistics or weaker cannot carry a reserved word anywhere in its wording column, with no negation exception, (c) the real registry passes after correction, not after weakening, (d) a planted violation is caught by a negative control."
result: "Enforced. The registry had one real violation (C-08 put a caveat about guarantees in the wording column) and one structural smell (a type cell carrying a promotion instruction). Both corrected: the caveat moved to the refutation column, the type is a bare judgment, and the promotion condition is stated where refutation lives. Negative control passes: a statistics claim using PROVEN is caught. Controls: 7 of 7."
verdict: supports
---

# E-M22 — the wording ceiling was stated in two places and enforced in none

## What was wrong

`lab/check-claims.py` opened with:

> A claim may not be worded more strongly than its evidence type permits.

and `docs/CLAIMS.md` had a table mapping each evidence type to the strongest wording it allows, with three
reserved words — `PROVEN`, `ENFORCED_TESTED`, `guarantee`. The linter checked types, duplicate ids, cited artifacts
and cross-references. It never compared the wording column to the type.

That is the seventh instance of one pattern in this repository: **the rule was declared, and nothing executed it.**
Six earlier instances were checkers counting prose, a readiness score counting a template, and a denominator kind
with no source.

VecDHT's note 2 asks for the same thing from a different angle: make the wording *derived* from the evidence type
rather than written freely. This card is that derivation.

## What is enforced now

For every claim, the wording column is checked against its type:

| type | reserved words allowed | additionally denied in the wording |
|---|---|---|
| `proof`, `test` | yes | — |
| `statistics`, `observation`, `judgment` | **no** | `guaranteed`, `always holds`, `never fails` |
| `withdrawn`, `not established`, `false as stated` | **no** | same |

**No negation exception.** "May not be stated as a guarantee" is a *comment about* the claim, and it belongs in the
refutation column; the wording column holds only the sentence the claim is allowed to say. This is stricter than it
first appears, and it is what surfaced the real defect.

## Run

```
before: RESULT: fail
  ERROR C-08: wording uses the reserved word 'guarantee' while typed 'judgment'
after:  RESULT: ok   (three warnings remain: artifacts not yet built, the to-do list)
controls passed: 7   failed: 0
```

## The two corrections, and why they were not weakening

- **C-08** carried "currently: … may not be stated as a guarantee until E-M9 exists" *inside* the wording cell. The
  caveat moved to the refutation column; the wording is now the bare permitted sentence. The claim itself is
  unchanged.
- **C-08's type cell** read ``judgment` → must become `test``, so the parser read a type that does not exist and the
  promotion instruction lived in the type field. The type is now a bare `judgment`, and the promotion condition sits
  with the refutation, which is where "what would change this" belongs.

Neither change relaxes the claim; both make it checkable.

## What this does not do

- It cannot tell whether the *wording column's* sentence is true — only whether it exceeds its evidence type.
- It does not police prose elsewhere. A report can still overstate; the check covers the registry, and `NC-09` says
  the registry is not the only surface.
- It does not decide the ceiling for new evidence types. A new type without an entry defaults to "reserved words
  forbidden", which fails closed.
