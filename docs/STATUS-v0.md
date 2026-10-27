# STATUS v0 — what exists, what does not

**Snapshot:** 2026-10-27, `main` @ `f0a15ce`, Windows host, no build artifacts committed.
**How to falsify this file:** every "works" claim below names an artifact you can open. If one is missing or
does something else, this document is wrong — say so, and it gets fixed rather than argued.

Method: [`docs/95-CLOSED-LOOP.md`](95-CLOSED-LOOP.md) · kit: [`docs/96-INTEROP.md`](96-INTEROP.md) ·
claims: [`docs/CLAIMS.md`](CLAIMS.md) · eliminated: [`docs/eliminations.md`](eliminations.md)

---

## Kit v0 declaration

The shared kit with [VecDHT](https://github.com/mak777uh/VecDHT) — seven items, each side keeping its own copy.
This is our declaration, as agreed; theirs is in `VecDHT docs/STATUS-v1.md`.

| item | ours | evidence | what is missing |
|---|---|---|---|
| **M1** experiment cards | **absent** | — | `lab/experiments/` does not exist. First card is `E-M9`, the substitution test |
| **M2** metrics with a command | **absent** | — | every number in this repository is a citation, not a measurement |
| **M3** evidence types | **works** | [`docs/CLAIMS.md`](CLAIMS.md): 18 claims, 7 evidence types, enforced by [`lab/check-claims.py`](../lab/check-claims.py) | one column to add: `instrument` (VecDHT's claim map fills it) |
| **M4** eliminations with revival | **works** | [`docs/eliminations.md`](eliminations.md): 19 entries, 17 revival conditions | — |
| **M5** status document | **works** | this file | it is v0 and will be wrong within a week unless regenerated |
| **M6** guards | **works** | [`lab/check-secrets.sh`](../lab/check-secrets.sh) (files + full history), [`lab/check-links.py`](../lab/check-links.py) (84 links, 0 broken), [`lab/check-claims.py`](../lab/check-claims.py), wired into `.github/workflows/guards.yml` | — |
| **M7** independent rebuild | **absent** | — | no bundle that anyone has rebuilt; see the definition below |

Kit conformance measured by [`lab/check-interop.py`](../lab/check-interop.py): **3 / 7**.

## What works

- **A claim registry with a wording ceiling.** 18 claims, each carrying an evidence type; three words
  (`PROVEN`, `ENFORCED_TESTED`, `guarantee`) are reserved for `proof` and `test`. The linter fails on an
  unknown type, a duplicate id, a dangling claim reference, or a cited artifact that does not exist.
- **An elimination ledger.** 19 positions we gave up, each with the evidence that killed it and what would
  revive it.
- **Three guards in CI**, including a secret scan over files *and* the whole commit history.
- **A closed loop with two brakes** (external node, stop path) and a compatibility kit with a sibling
  repository, both written as checks rather than intentions.

## What is partial

- **Review cycles.** Six cycles, four to five independent reviews each. They produced objections and
  eliminations; they did not produce code.
- **The claim registry format.** It has six of the eight agreed columns. `not_claimed` and `snapshot` are
  adopted in principle and being added; until then a row says how strongly a claim may be worded but not what
  it does not claim.

## What is a stub

- **Everything executable.** There is no `fg verify`, no bundle, no invariant, no attack harness. The
  specification describes them; nothing implements them.

## Bundle definition (M7), so that "bundle" is not a promise

A bundle is a directory, addressed by the sha256 of its manifest:

```
bundle.json          # version fg-bundle/1, subject digests (code, build, config, identity),
                     # declared closure, policy_hash, coverage, verdict, excluded paths
objects/<sha256>     # content-addressed payloads referenced by the manifest
manifest.sha256      # digest of bundle.json, the bundle's address
signatures/<key>.sig # detached signatures over manifest.sha256
```

**Independent rebuild** means: a party that has never read our code takes `bundle.json` plus the documents that
define it (`CLAIMS.md`, the closure definition, the policy), recomputes the manifest from scratch, and reports
whether the recomputed bytes equal `manifest.sha256`. Agreement on the payload, disagreement only in diagnostics
= agreement. Any other difference is a defect, recorded with its class (document text / rebuild instrument).

Until such a run exists and is recorded in an `E-` card, M7 stays absent — a definition is not a result.


**Three reserved fields (ADR-0002).** `issuer`, `valid_until`, `reliance_scope` are defined in the format and may
stay unused. They reserve the shape of a liability surface — the thing a buyer would need before relying on a
bundle — without claiming semantics we cannot yet define. Adding them later would invalidate every bundle and
every verifier written before, so the envelope is cut now; the meaning waits for a counterparty.
## What this document does not claim

- That the specification is correct, complete, or safe to implement against.
- That any security guarantee holds for any system. No verifier exists, therefore no verdict has ever been
  produced by this repository.
- That the kit is settled. It is v0 and will change; changes are recorded as ADRs.
- That the review rounds made the design right. They made it less wrong, which is a different claim.
- That `3/7` means anything on its own. It is our own instrument measuring our own kit, and it has been
  corrected twice already for false positives — see the interop reports.

---

## Review points (round 6)

Five independent reviews of the round-6 packet converged on a plan change and one open question. Two dates are
recorded here because a stop condition that is not dated is a wish.

| date | what must exist | if it does not |
|---|---|---|
| **2026-11-10** | a conversation with a named person, in a named role, about what evidence would change their decision | the product question moves ahead of all engineering; no further design work until it is answered |
| **2026-11-26** | one executable measurement: `E-M9` recorded with its pre-registered thresholds, result published including failure | the method is not extended; the project narrows to the piece that can be measured |

The second date is the binding one. Five reviewers gave 21–30 days; the median is 26 November. One gave 90 days,
but that was a threshold for external integration, not for producing a first measurement.

### The open question, recorded as central

> **Who is the specific person whose decision changes when the first line says `coverage: 11/14` — and what does
> the publisher of the bundle lose if the bundle is wrong?**

All five reviews arrived at this independently, and three added the liability half unprompted. It decides the
artifact: a consumer who must act needs a liability surface — who signed, on what authority, for what period,
with what effect. No amount of coverage arithmetic substitutes for it.

**This is not answerable by design review.** It is answerable by one conversation, which is what 2026-11-10 is
for.

### Kit status after this change

M1 experiment cards: **present** (`lab/experiments/E-M9-substitution.md`, thresholds fixed before the run).
M2 metrics with commands: absent. M7 independent rebuild: absent. Conformance recomputed by
`lab/check-interop.py`.

---

## Capability ceiling after round 7 (ADR-0005)

Five independent reviews established what this artifact does and does not do. Recorded here because a status
document that omits its own ceiling is a brochure.

**What a positive verdict will mean, and what it will not.**

| verdict | means | does not mean |
|---|---|---|
| `CONSISTENT_DECLARED(R)` | report, policy and bundle agree at the declared coverage; **no independent inventory** | that the declared scope is complete |
| `SCOPED_ASSURANCE(R, level)` | as above, plus an independent obligation manifest and per-flow evidence | that anything outside the scope is safe |
| `PROVEN(R)` | one flow, independent inventory, all obligations discharged | anything about the surrounding system |

**Three mandatory inputs** (a bundle without them is invalid): `target_lock`, `obligation_manifest`,
`previous_bundle`. If the manifest's generator is the analysing agent or its harness, the verifier returns
`E_NO_INDEPENDENT_CLOSURE` and the verdict is capped at `CONSISTENT_DECLARED`. There is no override.

**Not claimed, permanently:** complete discovery of all relevant paths; absence of vulnerabilities outside the
verified scope; correctness of unvalidated agent interpretations; equivalence between the repository and the
deployed system; independence of evidence that shares common assumptions.

The fifth cannot be engineered away. It is the reason the artifact is called a scoped consistency attestation and
not an attestation of security.
