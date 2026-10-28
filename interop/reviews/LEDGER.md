# Ledger — every finding from either side

One row per finding. A finding stays here after it is fixed, because a deleted finding teaches nothing.
Format and rules: [REVIEW-EXCHANGE.md](../REVIEW-EXCHANGE.md).

| id | round | from | severity | where | what | reproduction | disposition |
|---|---|---|---|---|---|---|---|
| F-1-1 | 2026-10-28 r1 | flowguard → VecDHT | medium | `lab/` listing | no adversarial harness against the gate is listed in `lab/` (eleven `check-*` files, no attack suite) | read only — directory listing at `2ec31ec` | open, awaiting their answer |
| F-1-2 | 2026-10-28 r1 | flowguard → VecDHT | medium | `lab/claims.tsv` | the wording column must appear verbatim in the carrier; what happens when the carrier is edited in a way that keeps the wording but changes its meaning? | read only | open |
| F-1-3 | 2026-10-28 r1 | flowguard → VecDHT | low | `docs/AUTONOMY.md` | green-zone list authorises "записи `lab/` (append-only)" and spec edits "отдельным коммитом после замера" — who checks that the measurement came before the edit? | read only | open |
| F-1-4 | 2026-10-28 r1 | flowguard (own) | critical | `tools/fg_readiness.py` | T4 reachable by typing four lines | fixed — `E-M43` | accepted → fixed in `E-M43` |
| F-1-5 | 2026-10-28 r1 | flowguard (own) | high | `docs/STATUS-v0.md` | claims no verifier exists; contradicts its own kit table | read only | accepted → open (must be generated, not edited) |
| F-1-6 | 2026-10-28 r1 | flowguard (own) | high | `lab/check-secrets.sh` | history scan covers token shapes only; local-path rule four extensions | `grep -aEI "$LOCALPATH"` over history by hand | accepted → open |

## How to add a row

```
| F-<round>-<n> | <date> r<n> | <from> | <severity> | <file:line> | <what> | <command + output, or "read only"> | <accepted → fixed (card) / accepted → open / rejected / not reproduced> |
```
