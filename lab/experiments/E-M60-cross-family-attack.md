---
id: E-M60
hypothesis: H-M60
status: completed
base_commit: "2899eab"
started: "2026-10-28T13:55:00+03:00"
finished: "2026-10-28T14:40:00+03:00"
environment: "Windows, CPython 3.13.11; five model families on the same provider, one attack prompt"
command: "workflow with agent(prompt, {model}) over claude-haiku-5-5, gpt-6-luna, mimo-v2.6-flash, qwen3.8-flash, glm-5.3-flash; then python lab/e-m60-run.py"
threshold: "Pre-registered: models from other families attack the gate with the same prompt the DeepSeek-family agents were given. Every finding is reproduced mechanically before it is accepted, and any break that reproduces is fixed and added to the suite. A finding that does not reproduce is recorded as not-reproduced, not quietly dropped."
result: "Five families, four answered with findings, six breaks reproduced and fixed. glm found a not-a-number density that passes the floor (NaN < 0.15 is False) and, better, that my report-versus-inventory check double-counted outside paths so the HONEST report was refused and a lying one accepted - a defect introduced by my own E-M48 fix. qwen found that completeness_claim 'sampled' passes as exhaustive and that an observed stmt:CALL is invisible to the verb list. mimo found that perimeter_growth:false cancels the delta that reports unpublished growth. haiku found that vanished:'false' as a string counts as coverage. gpt-6-luna returned nothing. All six fixed; e-m60 keeps the honest report as a must-pass control so the check cannot be inverted again. Regressions: E-M12 25/25, E-M42 0 breaking, E-M53, E-M28, differential 44/44, refusal coverage ok."
verdict: supports
---

# E-M60 — other model families found six things my own family did not

## Why this round exists

Every attacker so far was a DeepSeek-family agent, and that was the honest limit stated in `docs/STATUS-v0.md`
and in the `M7` record: an adversary from the author's own family can miss what the author misses. The owner
authorised running every model at or below `deepseek-v4.1-flash` pricing, so the same prompt went to five
families in one workflow: Claude Haiku, GPT-6 Luna, MiMo, Qwen and GLM.

## What each found

| family | break | why it matters |
|---|---|---|
| glm-5.3 | `db_logic_density: NaN` | `NaN < 0.15` is `False`, so a density that is literally not a number clears the floor — while an **absent** field is refused |
| glm-5.3 | report check inverted | my own `E-M48` fix computed `in_core / (paths + outside)`; `outside` is a subset of `paths`, so the denominator was inflated: the **honest** report was refused and a **lying** one accepted |
| qwen3.8 | `completeness_claim: "sampled"` | the schema's own value for "we kept part of what we found" passed as exhaustive |
| qwen3.8 | `stmt:CALL` invisible | the observed-verb list was DML only, so a procedure call seen at runtime explained nothing and blocked nothing |
| mimo-v2.6 | `perimeter_growth: false` + delta | a declared `false` cancelled a delta reporting three unpublished new paths |
| haiku-5.5 | `vanished: "false"` | the string passed `is not True`, so a non-boolean counted as coverage |
| gpt-6-luna | — | returned nothing; recorded, not hidden |

Six for six reproduced by `lab/e-m60-run.py` before any fix was written.

## The one that stings

The report/inventory check was **my repair** from `E-M48`, and it was wrong in the direction that matters: it
refused honest evidence and accepted a contradiction. That is the same failure shape as `E-M47` break 3 and
`E-M55`'s false equality — a fix that reads as correct and inverts the outcome. It was found by a model that
had no stake in my previous reasoning, which is exactly what cross-family attack is for.

## What changed

- non-finite numbers are refused everywhere a number is a floor or a density;
- the report is compared with the same ratio the verdict uses;
- `sampled` joins `partial` as a truncated denominator;
- a delta with unpublished growth blocks regardless of the flag;
- `vanished` must be a boolean;
- any observed verb the catalogue does not explain is unenumerable, not only DML verbs.

`e-m60-run.py` keeps the honest report as a **must-pass** control, because the previous version of this check
could only be caught by noticing that the correct answer was rejected.

## What this does not establish

- That these families are independent of each other. They are different training lineages on one provider, not
  different institutions.
- That six is the number waiting to be found. gpt-6-luna produced nothing, which may mean it found nothing or
  may mean it did not look.
- That the gate is now sound. The ceiling is unchanged: every check still reads a document the claimant writes.
