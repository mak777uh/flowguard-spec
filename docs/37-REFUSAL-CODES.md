# 37 — Refusal codes

The verifier's visible surface is refusal. Four of five round-7 reviewers converged on a small, stable,
machine-actionable taxonomy; this file is the merged result. It is designed so an agent can act on a refusal
without guessing, and so it cannot be talked into a weaker reading.

## The six codes

| code | meaning | what the agent can do | auto-fixable |
|---|---|---|---|
| `MISSING_EVIDENCE` | a required artifact, test or trace is absent, or a digest does not match | obtain or produce the named evidence | yes, if the source is reachable |
| `CLAIM_EXCEEDS_EVIDENCE` | the claimed level is stronger than the evidence supports | lower the claim, or supply the missing obligations | yes |
| `UNKNOWN_OR_UNBOUND_PATH` | a path is referenced that is absent from the obligation manifest, or its status is unset | investigate the path; it may **not** be excluded without evidence | partially |
| `REPORT_BUNDLE_INCONSISTENT` | report and bundle disagree on version, digest, boundary or level | regenerate the derived document from the source | yes, if the cause is mechanical |
| `POLICY_CEILING_EXCEEDED` | exclusions, outside-paths or residual risk exceed the policy ceiling | nothing autonomous — needs a scope change or a human decision | **no** |
| `E_NO_INDEPENDENT_CLOSURE` | there is no obligation manifest from a source outside the analysing agent | supply one, or accept the capped verdict | **no** |
| `SIGNATURE_ROLE_UNKNOWN` | a signature claims a role the policy does not define | use a defined role | **no** |
| `LIABILITY_NOT_A_ROLE` | a contract was declared as a signature role | record it as an external reference, not a signature | **no** |
| `RISK_ACCEPTANCE_INCOMPLETE` | an acceptance lacks scope, expiry or residual-risk codes | complete it or remove it | **no** |
| `SEPARATION_OF_DUTIES_VIOLATED` | one key signed both the verdict and the acceptance | use different keys for different acts | **no** |
| `EXCLUSION_REASON_CONTRADICTION` | an exclusion reason cannot hold for this path (e.g. `DATA_NOT_SENSITIVE` on a money path) | use a reason whose preconditions the path can satisfy | **no** |
| `EXCLUSION_REASON_UNKNOWN` | the reason code does not exist in the policy | use a known code | **no** |
| `AMBIGUOUS_ATTRIBUTION` | a call name matches more than one function, so the path cannot be placed in or out of the core | resolve by signature or oid, or leave the path outside | **no** |
| `UNENUMERABLE_PATH` | an action was observed that no enumerated path explains | extend the sources; the denominator is known to be incomplete | **no** |
| `POLICY_UNTRUSTED` | the policy, or the key that signed it, is not in the trusted set | obtain a trusted policy | **no** |

`MISSING_EVIDENCE` also carries `subject: coverage_basis` when every source in the manifest is a witness (runtime,
agent). Witnesses observe; they do not enumerate, so a ratio computed against them is not coverage.

Plus one loop-stopper, not a failure of the artifact:

| code | meaning |
|---|---|
| `RETRY_BUDGET_EXCEEDED` | the same fixable refusal was returned N times; further automatic retries are refused |

## Response shape

```json
{
  "verdict": "CONSISTENT_DECLARED",
  "errors": [
    {
      "code": "CLAIM_EXCEEDS_EVIDENCE",
      "subject": "flow/balance_transfer",
      "claimed_level": "PROVEN",
      "supported_level": "CONSISTENT_DECLARED",
      "expected": "coverage >= 1.0 with an independent obligation_manifest",
      "observed": "coverage = 0.6, obligation_manifest.generator = analysis_agent",
      "next_action": "lower the claim or supply an independent inventory",
      "retryable": true
    }
  ],
  "attempt_budget": { "used": 1, "max": 3 }
}
```

Rules that make it usable:

1. **At most three errors per response**, in the first blocking ring. A wall of forty refusals is a refusal to
   communicate.
2. **Every error names its subject** — a path, a claim, an evidence id. "Invalid bundle" is not a refusal, it is a
   shrug.
3. **`next_action` never grants permission to weaken the policy.** It names evidence to obtain or a claim to lower.
4. **The two non-fixable codes end the loop.** They are not retried with a reformulated report; they require the
   operator or a new inventory.
5. **The attempt budget is enforced by the verifier**, not by the agent's good manners.

## What is not yet known

Whether agents actually fix these autonomously is **unmeasured**. Four reviewers said so; one offered a criterion:
measure the share fixed on the first attempt, after a re-run, and the share where the agent tries to route around
the refusal instead. That is `E-M11`, and it is only meaningful after the verifier exists.

**Recorded as a hypothesis, not a property:** `UNKNOWN_OR_UNBOUND_PATH` is the code most likely to produce
work-arounds rather than fixes, because it asks the agent to admit a gap in its own analysis.
