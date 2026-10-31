# ADR-0018 — numbers are serialised by RFC 8785, and the switch waits for a re-signed bundle

**Status:** accepted, 2026-10-31. Implementation of the rule is in `tools/fg_canonical.py` and passes the
published number cases; the switch inside `tools/fg_bundle.py` is **not made yet**, and the reason is a key,
not a doubt.

## The problem, measured

Our canonical form was `json.dumps(..., sort_keys=True)` with a docstring calling itself "RFC 8785-shaped".
For numbers it was not. `lab/check-canonical-vectors.py` feeds the published cases through the bundler's own
`canon()`: **6 of 12 diverge**.

| input | we emit | the rule |
|---|---|---|
| `0.0` | `0.0` | `0` |
| `-0.0` | `-0.0` | `0` |
| `1.0` | `1.0` | `1` |
| `0.000001` | `1e-06` | `0.000001` |
| `1e-7` | `1e-07` | `1e-7` |
| `1e20` | `1e+20` | `100000000000000000000` |

`E-M71` had already measured the consequence from the other side: 6 of 10 floats serialise differently in Python
and in JavaScript. A canonical form whose two honest implementations disagree is not a contract, it is a habit.

## The decision

Numbers follow ECMAScript `Number::toString`, which is what RFC 8785 §3.2.2.3 mandates: shortest round-trip
digits, plain decimal while `-7 < k ≤ 21`, exponential otherwise with an explicit sign and no zero padding,
negative zero as `0`. `tools/fg_canonical.py` implements it; `tests/test_canonical.py` asserts all twelve
published cases, and `--strict` on the probe becomes the gate the day the switch is made.

Alternatives rejected: **integers only** (refuses `0.9`, which the density and coverage numbers need),
**normalise integral floats only** (leaves `1e-06` and `1e20` wrong, and those are exactly the cases that split
implementations), **document the limit** (the trap stays for whoever writes the next verifier, which is the
definition of leaving a defect in place).

## Why the switch is not made in this commit

A bundle carries Ed25519 signatures over its canonical bytes. `fixtures/sample-bundle/` is signed, and the
private keys are deliberately not in the repository. Changing the bytes without re-signing turns `E6`
("bundle verifies under both anchors") red permanently — not a red that means "fix the code", a red that means
"the fixture is now invalid and only the key holder can restore it".

So the order is: the owner re-signs the sample bundle with the new canonical form (or authorises a new fixture
key pair committed under `fixtures/` with its own `demo` role), then `fg_bundle.canon` is switched to
`fg_canonical.canonical_bytes` in the same commit, and the probe runs `--strict` in CI.

**Update, 2026-10-31:** the owner authorised the second option — a new demonstration key pair under
`fixtures/sample-bundle/signatures/` with the `demo` role, the sample bundle re-signed with it, and the
`owner` anchor left as it is. The private half is not committed: it is generated, used to sign, and discarded,
which keeps the repository free of secrets and means the fixture can only be rebuilt by whoever regenerates a
demo key deliberately — the same property the current fixture already has.

## What this does not change

Structure, key order, string escaping and the address algorithm are unchanged. Only the text of a number
changes, and only where it disagreed with the rule.
