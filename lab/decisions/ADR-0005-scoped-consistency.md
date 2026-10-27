# ADR-0005 — the artifact is a scoped consistency attestation, and the verdict is capped without an independent anchor

**Date:** 2026-10-27 · **Status:** accepted · **Supersedes:** the naming and verdict ceiling implied by ADR-0004
· **Source:** `docs/36-ROUND7-SYNTHESIS.md` (five independent reviews, 5/5 on finding 1 and 2)

## Context

Round 7 asked whether an agent can be both the client and the adversary, and five reviewers answered a different,
more important question: **what is the artifact actually?**

Their answer, independently: a tool that checks a report against a bundle verifies *internal consistency between two
documents*, both of which may be produced from the same wrong reading of the same system. One reviewer supplied the
sharpest formulation: the party that did the work never certifies the work. Another named what happens when it
does: verifiers accepted a warped output 90 of 90 times until they were given the missing facts.

Our own words made it worse. ADR-0004 said "the agent has eyes, the tool has a conscience". A conscience can audit
what it is shown; ours was described as if it could audit what it was never shown.

## Decision

### 1. The name

The artifact is a **`scoped consistency attestation`**:

> The report of an analysis was checked against a policy, and every obligation the policy requires is either
> satisfied by evidence or explicitly listed as outside the declared scope.

It is **not** an attestation of security, not a certification, not a proof that a flow cannot be bypassed. Those
words are removed from the specification and from any material derived from it. The string `attestation of security`
must not appear in a bundle, a report or a sales artefact.

### 2. The ceiling

A flow may reach `PROVEN` **only if its path inventory came from a source the analysing agent did not control**.
Otherwise the strongest verdict is:

```
CONSISTENT_DECLARED(R)
```

which means: documents agree at the declared coverage, an independent inventory is **absent**, and that absence is
printed in the verdict line itself, not in a footnote.

### 3. Three mandatory inputs

The bundle gains three fields, and a bundle without them is invalid, not merely weaker:

```
target_lock          # commit, SBOM digest, entrypoints, and the identity that signed the lock
obligation_manifest  # the path inventory: who generated it, with what tool, what its known blind spots are
previous_bundle      # digest of the previous attestation, for the perimeter delta
```

If `obligation_manifest.generator` is the analysing agent itself or its harness, the verifier returns
`E_NO_INDEPENDENT_CLOSURE` and the verdict is capped at `CONSISTENT_DECLARED`. There is no override flag. That is the
whole point: an override would be a way to buy the unearned verdict.

### 4. `not_claimed`, verbatim

Every bundle carries these five, machine-readably:

```
complete_discovery_of_all_relevant_paths
absence_of_vulnerabilities_outside_verified_scope
correctness_of_unvalidated_agent_interpretations
equivalence_between_source_repository_and_deployed_system
independence_of_evidence_sharing_common_assumptions
```

The fifth is the one that cannot be engineered away: two documents from one source are one document twice.

### 5. The semantics of `pass`

A positive verdict means **exactly one** of the following, and the verdict string says which:

| verdict | means | does not mean |
|---|---|---|
| `CONSISTENT_DECLARED(R)` | report, policy and bundle agree; coverage as declared | that the declared scope is complete |
| `SCOPED_ASSURANCE(R, level)` | as above, with an independent inventory and per-flow evidence | that anything outside the scope is safe |
| `PROVEN(R)` | a single flow, independent inventory, all obligations discharged | anything about the system it lives in |

## Consequences

- The product's first honest sentence is "we check that a report follows its policy and we account for the
  perimeter", not "we prove your flow is safe".
- The engineering priority changes: the missing piece is now an **independent path inventory**, not a nicer
  verifier. Two options exist and the owner chooses: build an enumerator (call graph, route registry, grant
  inventory), or define the interface and let the customer's own tooling supply the manifest.
- `E-M9` survives unchanged as the substitution contract; it does not test a path the agent never mentioned, and
  the reviews were right to separate those.

## What this decision does NOT do

- It does not make the consistency check worthless. Narrow and true beats broad and unsupported: a reader can
  believe "these documents agree and here is what is outside" in a way they cannot believe "your flow is safe".
- It does not remove common-mode failure. It names it.
- It does not make `PROVEN` reachable. It makes reachable only what we can support.
