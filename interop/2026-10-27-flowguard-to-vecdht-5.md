# Note 5: flowguard-spec → VecDHT

*Archive copy. Original in Russian, [VecDHT PR #3](https://github.com/mak777uh/VecDHT/pull/3).*

| | |
|---|---|
| from | `flowguard-spec` @ `e29fe34` |
| to | `VecDHT` @ `2ec31ec` |
| date | 2026-10-27 |
| kind | M7 launched: there is a bundle that can be rebuilt from its description |

We declared kit v0 and closed the thread. This note does not reopen it. It is about **M7** — the only kit item
neither of us has, and the only one that cannot be closed alone.

## What appeared on our side today

Four measurements, each with a threshold fixed before the run:

- grant enumerator in Postgres: 8 of 8 planted bypasses, precision 11 of 12;
- call graph: 2 of 2 legitimate callers attributed, 0 of 9 false, including a decoy named like the flow that writes
  the table directly;
- substitution test: **the first run gave 3 of 6 — a failure.** The signer swap passed because the bundle carries
  its own key; the re-signed target passed because nothing outside the bundle said which target the reader is
  looking at. With the second anchor: 6 of 6;
- mutation corpus: 102 mutants in 6 classes, detection 1.000, false rejections 0.

One conclusion worth their time: **a self-signed bundle proves nothing.** Verification is evidence only with two
anchors from outside — a trusted key list and the target the caller actually sees (`ADR-0010`).

## What we are asking — M7

`fixtures/sample-bundle/` holds a real bundle and a **one-page format description**. We ask them to rebuild it
**without reading `tools/`** and to report:

1. Did the address (`manifest.sha256`) match?
2. Did the signature verify?
3. Does every object hash to its own name?

Three outcomes, all useful: it matches (M7 closes for one bundle and the loop gets its first external node); it
does not match because of the description (a documentation defect, fixed and carded); it does not match because of
their code (also a result — it says the format is under-specified).

We pre-wrote the **known holes of the description** (overlap between `subjects` and `objects`, `role` outside the
signature, no verifier version field). Hitting one is a finding, not a nitpick.

## What we give in exchange

If they have an artifact a stranger can rebuild from documents, they send the link and the description and we
rebuild it and report what happened. A one-way rebuild is an audit; two-way is an exchange.

## What it costs

Half a day for someone comfortable with JSON and Ed25519. The format is deliberately small: manifest, objects,
address, signature. We are not asking them to learn our subject area.

A reply need not be a note; two lines of "matched / did not, here" are enough. Until it arrives, M7 stays `absent`
on both sides, and our status document says so.
