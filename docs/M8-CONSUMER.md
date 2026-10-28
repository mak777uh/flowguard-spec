# M8 — the consumer test

**Status: not filled.** This file exists so that the one question the whole product rests on has a shape a single
conversation can fill in twenty minutes. It is deliberately not free-form: the fields below are the minimum that
distinguishes a consumer from a compliment.

`tools/fg_readiness.py` awards the ten points for P2 **only** when every field carries a real value — a placeholder
like `<name>` scores zero, because a template that passes its own check is the failure mode this repository keeps
finding in its own instruments.

---

## The five-line form

```
person:            <a named human, not a role>
organisation:      <who they work for>
decision_before:   <the decision they make today about this flow>
decision_after:    <what they would do differently given a bundle>
what_they_lose:    <what goes wrong for them if the bundle is wrong>
date:              <YYYY-MM-DD of the conversation>
verbatim:          <one sentence in their words that supports the four lines above>
```

## Why each field is required

| field | what it excludes |
|---|---|
| `person` | "security teams" — a category cannot change a decision |
| `decision_before` | "they would find it useful" — usefulness is not a decision |
| `decision_after` | "they would feel better" — a feeling is not an action |
| `what_they_lose` | nothing — if a wrong bundle costs them nothing, their reliance is free and worthless |
| `verbatim` | our paraphrase — the sentence that survives translation into a contract |

## What counts, and what does not

**Counts:** an auditor who would change the scope of an engagement; an insurer who would change a premium or an
exclusion; a protocol team that would gate a release or a listing; a procurement team that would accept a vendor it
currently rejects.

**Does not count:** our own escrow (circular); a friendly "interesting" reply; a person who says the report is
useful but names no decision; a hypothetical buyer described in the third person.

## If ten conversations produce nothing

That is an answer, and it is worth recording in `docs/eliminations.md` as X-21: *"a verifiable attestation is
valuable because it can be checked" is eliminated — nobody's decision depended on it*. The product then narrows to
the open-source tool, which is a legitimate outcome and needs no apology.

## Filled version

When a conversation happens, fill the block above and delete the note lines that follow it. The readiness number
will move by itself; nothing else needs to be edited.
