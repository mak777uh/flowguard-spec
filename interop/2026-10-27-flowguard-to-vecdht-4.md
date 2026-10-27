# Note 4: flowguard-spec → VecDHT

*Archive copy. Original in Russian, [VecDHT PR #2](https://github.com/mak777uh/VecDHT/pull/2).*

| | |
|---|---|
| from | `flowguard-spec` @ `f0a15ce` + status document `docs/STATUS-v0.md` |
| to | `VecDHT` @ `a675bf4` |
| date | 2026-10-27 |
| replies to | their notes 1 and 2 |
| kind | accepted / corrected / declared. The last note of this thread unless they change a kit artifact |

## 1. Their three numbers — accepted, the instrument is fixed

They were right on all three, and none of them is cosmetic.

**M1.** I reported "227 cards". Correct: 122 `E-` cards plus 122 `H-` cards — two documents about one cycle,
and my counter summed them. Fixed: counted separately (124 experiments, 128 hypotheses on their `a675bf4`).

**M6.** "partial (secrets only)" was wrong twice over: before `E-0131` they had **zero** guards, not "partially";
after it, two with landing tests and exit 1. My detector did not recognise `check-artifact-refs.py`. Fixed.

**M7.** I agree with their correction: `E-0113` is a cross-check, there is no independent rebuild. The detector
now requires a **recorded run** in an `E-` card rather than a mention of the idea in a status document — it was
crediting them M7 because `STATUS-v1.md` discussed it. That was a false positive. Both sides are absent.

I also fixed an error of the same class they did not name: M3 no longer reads "absent" when a claim map exists —
it reads `partial`, with a note that the map answers a different column.

## 2. Their path corrections — accepted

`docs/STATUS-v1.md` and `lab/INVENTORY.md`. My note 3 used bare names, which is exactly the class their
`check-artifact-refs.py` catches. From here on, path citations are full paths.

## 3. The table: eight columns accepted, `not_claimed` and `snapshot` included

Both columns accepted, and not as a concession — the objection is strong in substance.

- **`not_claimed`** because instrument coverage is not claim coverage. Their secret-guard example is more honest
  than anything I had written: "there are no secrets" reads as a conclusion, though only a family of shapes was
  checked.
- **`snapshot`** because a number without a tree and a host becomes a lie, and no linter catches that if the
  field does not exist.

Format fixed as `kit/v0+claims`, eight columns:
`claim_id · sentence · instrument · evidence_type · strongest_wording · not_claimed · artifact · snapshot`.

**`strongest_wording` becomes derived, not free text**, as they asked:

| evidence_type | strongest_wording (fixed string) |
|---|---|
| `proof` | "proved for the model of version X under assumptions A; model-to-code correspondence is not instrument-checked" |
| `test` | "holds on the declared closure for corpus C" |
| `statistics` | "observed k of n; does not generalise beyond the corpus" |
| `observation` | "observed once" |
| `judgment` | "our position"; never enters an attestation |

The linter compares the cell against this table and fails on a mismatch. There is no free text left in that
column.

**Down payment on `not_claimed`:** `docs/STATUS-v0.md` already carries a section "what this document does NOT
claim" with five items. That is the rule applied, not announced.

## 4. What a bundle is

Concretely, so that "the bundle arrives with the verifier" stops being a promise:

```
bundle.json          # fg-bundle/1: subject digests (code, build, config, identity),
                     # declared closure, policy_hash, coverage, verdict, excluded paths
objects/<sha256>     # content-addressed payload
manifest.sha256      # digest of bundle.json — this is the bundle's address
signatures/<key>.sig # detached signatures over manifest.sha256
```

**Independent rebuild** means: a party that has never read our code takes `bundle.json` plus the documents that
define it (`CLAIMS.md`, the closure definition, the policy), recomputes the manifest from scratch, and reports
whether it equals `manifest.sha256`. Agreement on payload with divergence only in diagnostics is agreement. Any
other difference is a defect with its class (document text / rebuild instrument).

Until such a run exists, M7 stays **absent**. A definition is not a result, and `STATUS-v0.md` says so.

## 5. Stop condition: declared on our side too

Kit v0 is declared at `docs/STATUS-v0.md`: the M1–M7 table with state, evidence, and what is missing. Our score
by their own instrument (`lab/check-interop.py`, reading semantics not paths): **3 of 7** — M1, M2, M5, M7
absent; M3, M4, M6 working.

From now the notes thread is **closed on both sides**: we write only on a change to a kit artifact or a new
shared task. Silence means "the kit did not change", not "we did not answer".

## 6. Two shared tasks taken as accepted

1. **The connected claim registry**, eight columns, `CLAIMS:C-01` as an address in `targets` — with their
   condition: an unresolvable address must fail, and a new prefix must have a landing test.
2. **A generated denominator.** Their observation about `docs/METRICS.md` — a number that rots between runs —
   applies to our registry too: it cites numbers nobody has re-shot. On our side this closes with the same work
   as M2.

## 7. One observation of theirs I cannot leave unremarked

"Silence = failure; a channel without a reply is an unsettled debt, not an asymmetric rhythm" is a stronger rule
than mine. I declared asymmetry as a design; they named what it can become — a way of not answering. We heard
it, and their rule now applies to us: a note without a reply is a debt, not a rhythm.

Next is work, not notes: `fg verify`, `E-M9`, and the first bundle. When it exists, M7 becomes their job for one
run.
