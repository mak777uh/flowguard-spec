# How attacks are part of development, not an event

The gate that decides whether an artifact may be called `SCOPED_ASSURANCE` or `PROVEN` was attacked twice: eight times
by its author (`E-M36`), then by an independent agent that found eleven more ways through (`E-M42`). The second result
changed the process, not just the code.

## The rules, now in force

**1. No gate is trusted until an independent attempt has failed against it.** New refusal, new floor, new signature
rule — the change is not done when it works; it is done when someone who did not write it has tried to get around it
and reported the result.

**2. Every break becomes a fixture and a case.** `fixtures/attack/` holds the exact inputs; `lab/e-m42-run.py` runs
them and asserts two things per case: the verdict is not strong, **and** the expected refusal code fires. A case whose
code changed silently is a red build, because it means the mechanism that stops it is no longer the one we think.

**3. Attacks run every round.** `lab/round-check.sh` runs the author's suite, the independent suite, and
`lab/check-refusal-coverage.py`, which requires every code in `docs/37-REFUSAL-CODES.md` to be triggered by at least
one test. A refusal nobody exercises is a comment.

**4. The attacker gets two things: the repository and one sentence.** The instruction is the objective — "obtain a
strong verdict without the evidence for it" — and nothing about how the author thinks it is protected. Giving the
attacker the author's own attack list is allowed; it saves it from rediscovering the known surface.

**5. A failed attack is reported too.** The independent agent listed fifteen controls it could not break. That list is
what makes the eleven findings trustworthy: without it, "I broke it" is a claim with no denominator.

## What this practice costs

One round. `E-M42` took about fifty minutes of wall-clock, most of it in fixing eleven defects.

## What it does not buy

- **Independence in the strong sense.** The attacker was an AI agent from the same model family as the author, with
  access to the same repository. Shared blind spots are not merely possible; `NC-05` says they exist.
- **A stopping rule.** Thirteen cases pass today. That is a floor on the surface explored, not a statement that the
  gate is sound.
- **Immunity to a determined liar.** Every check reads a document the claimant wrote. The fixes make lying harder and
  more visible; none makes it impossible.

## The sentence worth keeping

The attacker's own diagnosis, which nothing in this repository had said so plainly:

> Those breaks share one defect — a gate satisfied by a field the analysed party writes.

That is the honest boundary of the whole product, and it is now in `docs/CLAIMS.md` as the reason every claim carries
`NC-01` and `NC-02`.
