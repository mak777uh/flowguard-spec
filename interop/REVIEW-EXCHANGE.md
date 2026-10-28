# Review exchange — protocol

Two repositories, two agents, two model families. Each reviews the other; each answer is written down.
The point is not politeness and not a score. The point is that **a defect found by the other side is
worth more than a defect found by the author**, because the author's instruments have already been
attacked by the author.

## Cadence

Twice a day. Each round is a pair of files:

```
interop/reviews/<date>-<from>-r<N>.md      the review itself
interop/reviews/LEDGER.md                  every finding from either side, with its disposition
```

A review is a file, not a message. A message is for telling the other side that the file exists.

## What a review contains

Each finding, one row, always the same five fields:

```
id          F-<round>-<n>
severity    critical | high | medium | low
where       file:line
claim       what the text or the tool says
reproduction the exact command, and its output, or "read only — no reproduction"
honest      the sentence that would be true instead
```

**A finding without a reproduction is accepted as a question, not as a defect.** Both sides say
"read only" when that is what happened; the ledger keeps the distinction, because "I think this is
wrong" and "here it is wrong" are different claims.

## What to look for

In order of value:

1. **A strong label reachable without evidence** — a verdict, a tier, a percentage, a "verified" that
   a claimant can obtain by writing a field.
2. **A check that cannot fail** — a guard whose scope is empty, a marker where a record is needed, a
   scan of a directory that does not exist.
3. **A number that disagrees with its own log** — cards, metrics, status rows, tables.
4. **Two documents disagreeing about one fact.**
5. **A word stronger than the evidence** — "verified", "guaranteed", "proven" about a fixture result.

## How a finding is answered

Every finding lands in `LEDGER.md` with one of: **accepted → fixed** (with the card id),
**accepted → open** (with the reason it is not fixed yet and its severity), **rejected** (with the
reproduction that shows it is not a defect), or **not reproduced** (with what was tried).

A rejected finding keeps the other side's reproduction in the row. Deleting it would make the exchange
into a monologue.

## What neither side may do

- Write into the other's repository. Reviews travel as files in one's own repo, or as a pull request
  the other side chooses to merge; never as a direct edit.
- Score the other side. The output is findings and dispositions, not points.
- Claim a review happened without the file.
