# What a "proof of usefulness" is, and what our version would have to contain

Source: HackerNoon's Proof of Usefulness hackathon, final round announcement (2026): ~300 stories published, five
sponsor categories, $118,000 in the final round — **$12,000 cash and $106,000 in software credits**. Read as an
artifact format, not as a prize list.

## Four things the format says, read cold

1. **The judged artifact is the report, not the software.** Winners are announced with a link to "their report of
   proof of usefulness". Nobody's repository was read by a judge; ~300 reports were. The lesson for us is
   uncomfortable and exact: a bundle that nobody writes a report about has not demonstrated usefulness, however
   correct its verdict.
2. **Usefulness is about a change in someone's work, not about correctness.** The announcement's own framing:
   software that "helped answer a pressing question, do a task more efficiently, decide faster, or solve a problem
   existing tools complicated without need". Correctness is not in that list. Our ceiling says the same thing in
   another vocabulary: consistency is not truth, and truth is not usefulness.
3. **One artifact, several framings.** Siiqo took two categories, Cofoundr three, FoxPlug two, Visual MCP Gateway
   two. The same work, described for different buyers. We have exactly one framing — the security engineer's — and
   two other plausible ones (an auditor's, an underwriter's) that we have never written down.
4. **The prize economy is infrastructure.** $106k of $118k is credits from the sponsors whose products the
   category rewards. Money is the smaller half. For us this matches what we already found with the Nosana credits:
   the currency of this market is compute, not cash.

## The template our reports must follow

A usefulness report that cannot be falsified is a demo. Ours has to state, in this order, and refuse to omit any
line:

| field | what it must contain | why |
|---|---|---|
| the question | one sentence, written by the **consumer**, not by us | we cannot invent the question we answer |
| who asked | a named person or role, with the date they asked | `P1` refuses to credit a model rebuild; a report about a model is a demo |
| what they would have done instead | the previous workflow, named | without it, no change can be attributed |
| what the artifact said | the verdict, the coverage, and the `not_claimed` list **verbatim** | a verdict quoted without its boundary is a different claim |
| what changed | a decision, a code change, a sign-off — something that exists after | this is the only part that counts as usefulness |
| what did **not** change | at least one thing the consumer kept doing the old way, and why | a report with no such line is marketing |
| what remains unknown | `NC-01`-type limits, and whether the inventory was independent | the ceiling travels with the report |

Two rules on top of the table:

- **No named human, no report.** Not "a customer", not "a team", not a model. A role and a date.
- **A report may end in "we could not show it helped".** That is a result, and the family publishes those: `cases`
  has a case that ended "not confirmed", and this repository has two refuted hypotheses of its own.

## Why this is the honest shape of `P2` and `P4`

Our readiness tiers require an acceptance outside `fixtures/` and a consumer who says the artifact changed a
decision. That is exactly this template, applied once, by one person. The hackathon's economics suggest the same
thing from the other side: judges reward reports of a change in someone's work, and a report cannot be written
before the change happens.

So the next step is not more code. It is to hand one bundle to one person with the table above and ask them to fill
in five lines. If they cannot, the product claim is unsupported, and we will have learned that cheaply.

## What this document is not

- It is not a plan to enter a hackathon. The dates have passed and the categories are sponsor-shaped.
- It is not evidence that anyone has used this. It is a template for the first time somebody does.
- It does not make the verdict stronger. It makes the claim about the verdict checkable by the person who lived
  through the change.
