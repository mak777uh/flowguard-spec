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
| F-3-1 | 2026-10-28 r3 | flowguard → LexSpec | high | tools/lexcheck.py find_repo_root | the verdict depended on whether the tree sat inside a repository marker; with no marker the report said S2_HASH_MISMATCH, blaming the corpus | lab/lexspec-root.py (their copy of the tree, no .git, no docs/) | accepted → fixed in lexspec 40926d3: upward search from the statement, new code S2_CORPUS_NOT_FOUND, root_source in the report, regression test without --root |
| F-3-2 | 2026-10-28 r3 | flowguard → LexSpec | medium | docs/10 SPEC 9 + the verdict branch | the coverage threshold cannot decide any verdict: coverage < 1.0 implies a declared escape, and an escape already caps the verdict | read only, code inspection | accepted → fixed in lexspec ADR-0010: threshold removed from the verdict path and declared reporting-only |
| F-2-1 | 2026-10-28 r2 | flowguard (own) | medium | interop/verifiers/third-party-verifier.py | accepts a signer whose .pub cannot be parsed | python lab/e-m57-run.py (demo.pub truncated: theirs=SIGNED_AND_CONSISTENT, ours=INVALID) | accepted → open: their verifier is wrong, recorded rather than patched, because the divergence is evidence |
| F-4-1 | 2026-10-28 | LexSpec (external reader) | `docs/37-REFUSAL-CODES.md` heading said "six" above a table of seventeen codes | fixed; the heading is gone and the file credits the finder | accepted |
| F-3-1 | 2026-10-28 | flowguard (Lead) | LexSpec tools/lexcheck.py: verdict depends on whether the tree carries a repository marker; the refusal blames S2_HASH_MISMATCH and accuses the corpus | open - reported in interop/reviews/2026-10-28-flowguard-reviews-lexspec.md with lab/lexspec-root.py as the reproduction | sent |
