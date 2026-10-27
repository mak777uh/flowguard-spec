# NOT-CLAIMED — the vocabulary of what an attestation refuses to assert

Round 7, review 2 and review 5 both flagged the same weakness: `not_claimed` is where a vendor writes "results may
vary" and calls it honesty. A free-text list cannot be checked, so it becomes boilerplate.

This file fixes the vocabulary. A claim carries **codes**, not sentences:

```json
"not_claimed": ["NC-01", "NC-02", "NC-04", "NC-05"]
```

`tools/fg_verify.py` reads this table, rejects unknown codes, and rejects a claim that omits the codes its declared
level requires. Adding a code is a deliberate act: it means a new kind of thing we refuse to assert.

## The codes

| code | refuses to assert | why it cannot be asserted |
|---|---|---|
| **NC-01** | that the inventory contains every relevant path | the inventory is a merge of sources, each with declared blind spots; completeness is unprovable |
| **NC-02** | that anything outside the verified scope is safe | nothing outside the scope was examined |
| **NC-03** | that an agent's reading of the code is correct | interpretation errors are the dominant agent failure mode and are not instrument-checked |
| **NC-04** | that the repository equals the deployed system | establishing that requires a runtime binding (extcodehash, build receipt), which is out of the offline path |
| **NC-05** | that evidence from one source is independent of another | two sources can share a blind spot; corroboration counts what was found twice, not what was missed twice |
| **NC-06** | that the policy matches business intent | we check conformance to a policy; whether the policy is the right one is not a technical question |
| **NC-07** | that risk weights are objective | weighting residual risk requires an agreed classification; until one exists, weights are a convention |
| **NC-08** | that the issuer of a trust anchor was authorised to issue it | a trusted key list is a file; who may sign it is a governance question |
| **NC-09** | that a third party can reproduce the analysis | only the bundle address is reproducible; the analysis is reproducible only after M7 |
| **NC-11** | that these numbers generalise beyond the schemas actually validated | a result on one corpus says nothing about an unmeasured population; generalisability is a property of the sample, not of the tool |
| **NC-10** | that observed runtime behaviour matches the static model | static paths and exercised paths are different sets; runtime evidence is a separate source |

## Required by level

| declared level | codes that must be present |
|---|---|
| `CONSISTENT_DECLARED` | NC-01, NC-02 |
| `SCOPED_ASSURANCE` | NC-01, NC-02, NC-04, NC-05, NC-11 |
| `PROVEN` | NC-01, NC-02, NC-03, NC-04, NC-05, NC-10, NC-11 |

A claim that declares a level without the codes it requires is refused, with the missing codes named.

## What this does not do

- It does not make the refusals complete. A code that nobody thought to add is absent from this table.
- It does not prevent a claim from *also* refusing more than required — that is always allowed.
- It does not check that the refusal is *true*. A claim that lists NC-01 while its prose says otherwise is a
  contradiction a human has to catch; the machine checks presence, not sincerity.
