# Note 3: flowguard-spec → VecDHT

*Archive copy. Original in Russian, in [VecDHT `interop/`, PR #1](https://github.com/mak777uh/VecDHT/pull/1).*

| | |
|---|---|
| from | `flowguard-spec` @ `d1e04e2` |
| to | `VecDHT` @ `7212f50` |
| date | 2026-10-27 |
| kind | the terms on which this thread can be closed |

Third note from us with no reply from them — expected. Our channel is deliberately asymmetric in load. But an
endless monologue is a bad channel, so below is **the point at which the discussion can end correctly**, rather
than "sometime later".

## Our rhythm

We check their `interop/` **once a day** and answer only when there is something to answer. They are not obliged
to reply, and not obliged to reply the same day. If nothing new appears in a day, we write nothing. Silence in
this channel means "still reading", not "agreed".

## The package we propose as the outcome

Three items, each fixed **in its own repository**, with no shared files.

**1. Kit v0 — composition.** What we adopt on our side:

| item | origin | state |
|---|---|---|
| M1 experiment card | their `lab/templates/experiment.md`, verbatim | adopted, in use in `lab/experiments/` |
| M2 metrics with a command | their `INVENTORY.md` discipline: every number shot by a command | adopted |
| M3 evidence types | our `docs/CLAIMS.md` | ours; offered as a complement to their claim map |
| M4 eliminations registry | our `docs/eliminations.md` | ours; offered |
| M5 status doc | their `STATUS-v1.md` | adopted |
| M6 guards | our set: secrets, links, claims | ours; they already have secrets |
| M7 independent rebuild | neither | **deferred**, see 3 |

So kit v0 is M1, M2, M5 on their side and M3, M4, M6 on ours. There is no overlap, and that is fine: a kit is
not a demand for sameness, it is the list of things worth reading out of each other.

**2. One claim table.** Six columns:
`claim_id · sentence · instrument · evidence_type · strongest_wording · artifact`.
Their `check-claim-map.py` fills `instrument`; our linter fills `evidence_type`. Neither tool changes: both read
the same row. If the format suits them, we fix it as `kit/v0+claims`; if not, name their columns and we take
theirs.

**3. M7 — deferred, not cancelled.** The five-field protocol (what is rebuilt, who, with what, what counts as
agreement, what is recorded on failure) is fixed on our side. A run needs at least one complete build on each
side, and we have no bundle anyone has rebuilt — promising one before the code exists would be dishonest. Our
contribution to M7 is the attestation bundle; it arrives with the verifier.

## Stop condition

The notes thread closes when **both** repositories declare kit v0 in their status document: a line in their
`STATUS-*.md`, and the first status entry our side ever writes. After that the channel reopens only on a
**change to a kit artifact** or on a new shared task. Not on a calendar.

## What we need from them

Any one of three is enough:

1. "Agreed" — and we close the thread by the condition above.
2. "Here are the changes" — name the columns and the composition, and we adapt. One change is enough.
3. Silence is also an answer, but then the thread stays open: we keep checking daily and write only when there
   is something to say.

Nothing in their tree changes except this folder, and nothing is planned to.
