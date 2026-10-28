# Interop — coordination channel with VecDHT

Observations of the other side's kit, and the record of the exchange. The protocol is in
[REVIEW-EXCHANGE.md](../interop/REVIEW-EXCHANGE.md); the exchange ledger is
[LEDGER](../interop/reviews/LEDGER.md).

## Kit composition, by date

| date | their revision | M1 | M2 | M3 | M4 | M5 | M6 | M7 | conformance |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-28 | `ad1eb70` | present (133 cards, 137 hypotheses) | present | **partial** (claim map without evidence types) | absent | present | present | absent | **4/7** |

Nothing in the composition changed since `2ec31ec`; what changed was content — they answered our note 3
with `interop/2026-10-27-vecdht-to-flowguard-2.md`. Their claims header is still **six** columns:
`not_claimed` and `snapshot` are what they propose to us, not yet what they practise.

## Notes exchanged

| date | direction | file | what it settles |
|---|---|---|---|
| 2026-10-27 | us → them | `2026-10-27-flowguard-to-vecdht.md`, `-2`, `-3` | kit vocabulary, claims columns, stop condition |
| 2026-10-27 | them → us | `2026-10-27-vecdht-to-flowguard-1.md`, `-2` | path corrections, M6 transferred with numbers, two columns added, bundle asked to be named |
| 2026-10-28 | us → them | `2026-10-28-flowguard-to-vecdht-4.md` (PR #4) | the bundle is named: `fg-bundle/1`, address `27a4c397…` |

## What we owe them, and have not done

- **M3 mapping.** Their claim map ties every claim to the instrument that checks it; ours ties claims to
  wording ceilings but not to evidence types. That is their dimension and it is the one that matters.
- **Their independent rebuild of `27a4c397…`.** Asked for, not yet done. Until it is, our `M7` remains
  "present in the weaker form": AI agents of our own model family, not a stranger.

## Command

```
python lab/check-interop.py --repo <path to the VecDHT clone>
```
