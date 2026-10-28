---
id: E-M71
hypothesis: H-M71
status: completed
base_commit: "fbeefd5"
started: "2026-10-28T22:40:00+03:00"
finished: "2026-10-28T23:10:00+03:00"
environment: "Windows, CPython 3.13.11, Node 24.14.1, LexSpec @ 2c74648"
command: "python lab/xrepo-canonical.py && python lab/xrepo-floats.py"
threshold: "Pre-registered: two projects in one family both claim that the canonical byte form is the contract between implementations. Check it: the same document must produce identical bytes under our canonicaliser and theirs, and the address must not depend on which language serialised it. Any disagreement is a finding, not a note."
result: "Fourteen documents produce identical bytes under both canonicalisers - keys sorted at every depth, minimal separators, non-ASCII literal, arrays in order, astral plane and control characters included. One class disagrees: non-integer numbers. LexSpec refuses them (CanonError); FlowGuard accepts them, and the acceptance is language-dependent - of ten float values, six render differently in Python and in JavaScript ('1.0' vs '1', '1e-07' vs '1e-7', '-0.0' vs '0', 2^53 as '9007199254740992.0' vs '9007199254740992'). Our own shipped artifacts contain 0.0 and 0.9, so an address computed by a JavaScript verifier today would differ from ours. The fix changes canonical bytes and therefore invalidates existing addresses, so it is queued as Q7 rather than applied."
verdict: refutes
---

# E-M71 — the canonical form is the contract, except for the numbers

## What was checked

Two sibling projects, one claim: *the canonical byte form is the contract between implementations*. So run both
canonicalisers on the same documents and compare bytes.

**Fourteen of fourteen documents agree.** Keys sorted at every depth, `,`/`:` with no spaces, non-ASCII literal,
array order preserved, combining marks, astral-plane characters, U+0001, U+2028/2029, quotes and backslashes,
nested empty containers, `2^63-1`. That agreement is not a coincidence of two authors — it is what a written rule
produces, and it is the strongest thing the family shares.

## The class that does not agree

| value | Python bytes | JavaScript bytes | |
|---|---|---|---|
| `1.0` | `{"n":1.0}` | `{"n":1}` | differ |
| `1e-7` | `{"n":1e-07}` | `{"n":1e-7}` | differ |
| `-0.0` | `{"n":-0.0}` | `{"n":0}` | differ |
| `100.0` | `{"n":100.0}` | `{"n":100}` | differ |
| `2**53` | `{"n":9007199254740992.0}` | `{"n":9007199254740992}` | differ |
| `1234567890123456789.0` | `…e+18` | `1234567890123456800` | differ |
| `0.5`, `0.9`, `0.1`, `1e21` | same | same | agree |

LexSpec's rule is: **integers only**, and a float is a `CanonError`. Ours is "whatever `json.dumps` produces",
which is a Python-specific rendering, not a specification.

## Why this is not academic

Our own shipped fixtures contain non-integer numbers: `fixtures/attack/a7-claim.json` has `0.9`,
`fixtures/attack/a12-report.json`, `a4-policy.json`, `a6-inv.json` and `inbox/ironclaw-claim.json` have `0.0`.
`claimed_coverage: 0.0` is the *default* claim shape — every first artifact contains it.

So today: a verifier written in JavaScript, or a producer whose pipeline serialises through JavaScript, computes
a **different address for the same document**. The claim "an address is the contract between implementations"
is therefore false for the most common artifact we ship. It is invisible because both of my implementations are
Python and Rust, and `serde_json` happens to agree with `json.dumps` on `0.0` and `0.9`.

That is exactly the class of defect a second implementation is supposed to catch, and mine could not: the two
implementations share a serialisation habit. The sibling project and a third language caught it.

## Why it is queued instead of fixed

Every remedy changes canonical bytes:

1. **integers only** (the LexSpec rule): `0.0` becomes `0`, or the document is refused. Cleanest, invalidates
   every existing address that contains a float.
2. **normalise integral floats to integers** in the canonicaliser: keeps documents readable, still changes the
   address of anything containing `0.0`, and leaves `0.9` as an unrepresentable case to refuse.
3. **document the limit** and keep bytes as they are: cheapest, and leaves the cross-language trap in place for
   whoever writes the next verifier.

This is a format decision that invalidates artifacts, so it goes to `docs/QUESTIONS-FOR-OWNER.md` as **Q7** with
the three options and the measured consequences. I am not choosing it silently.

## What this changes in the cross-repo registry

`lab/xrepo-canonical.py` and `lab/xrepo-floats.py` become the first two entries: a styk between projects is
checked by running both sides on the same input, and "they agree" is a measurement with a number attached, not a
statement of family resemblance. The registry's rule, learned here: **agreement between two implementations of
the same author proves less than agreement between two authors** — and both prove less than agreement with a
third language.
