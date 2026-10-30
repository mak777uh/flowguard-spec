# What the usefulness corpus actually rewards — read from two reports and the rubric

Read at source: the [rubric](https://hackernoon.com/proof-of-usefulness-weight-distribution), the
[Nullmail report at 76](https://hackernoon.com/nullmail-earns-a-76-proof-of-usefulness-score-by-building-an-open-source-disposable-email-service),
and the [GUN101 report at 77.6](https://hackernoon.com/gun101-earns-a-776-proof-of-usefulness-score-by-building-a-5-layer-security-protocol).
Two reports is not a corpus; what follows is a hypothesis from two data points and the rubric, not a survey.

## Insight 1 — the highest-scoring security project in this sample has no evidence at all

GUN101 scored **77.6**, higher than a working service with real users. Its answers, verbatim:

| rubric question | GUN101's answer |
|---|---|
| traction to date | "since it's a python library, the whole world can use this simultaneously" |
| who's noticing | "traction is taking root in the open-source community" — no number |
| one data point, not vanity metrics | a **hypothetical**: "the pdf will still not open, no matter what they try, no matter which malware they run" |
| adoption versus tourists | "it doesn't matter who wants to adopt and who's just giving it a try" |
| the mechanism | "the secret key … is stored in TPM and a nanosecond based time challenge to make sure the person entering the password is actually the one who encrypted this pdf" |

By the rubric's own weights that should score near zero on traction (25%) and weakly on utility (25%) — the
answers are unfalsifiable. It scored 77.6.

## Insight 2 — the rubric measures narrative plausibility, not verification

Nullmail's 76 came from *evidence*: ~10k inboxes a month, 500 organic clicks, voluntary donations on a free
tracking-free service. GUN101's 77.6 came from *narrative*: a novel mechanism, a compelling threat model, and
confident phrasing. Both land in the same band.

So the score is a **pitch-quality instrument**, not an evidence instrument. The 50% weight on "utility + traction"
is real, but it is scored by how convincingly the interview answers those questions, not by whether the answers
survive a check.

## Insight 3 — which is exactly our product's opening, and exactly why we would score badly

Our discipline forbids the moves that earned 77.6. We publish `NC-01…NC-11`, we refuse a verdict above the
evidence, we ship a `not_claimed` list with every claim, and we have two refuted hypotheses of our own. Applied
honestly to the eleven questions, that produces lower scores: an unverifiable security claim is where the rubric
pays and where this repository refuses to go.

Two consequences, and they point in opposite directions:

1. **Do not optimise for this rubric.** Its top band rewards confidence about security, and buying that confidence
   would cost the only thing we have — the refusal vocabulary. A project that scores 77.6 while saying "the whole
   world can use this simultaneously" is the adversary our product exists to check.
2. **Position FlowGuard as the step after the pitch.** The corpus contains ~300 narratives; a buyer, an auditor or
   an underwriter reading one has no way to tell Nullmail's evidence from GUN101's story. Our artifact is the one
   thing that separates them: does the claim about a control point survive a re-run, and what does it refuse to
   say. That is a market the rubric creates and does not serve.

## What I would now do with this

- **A comparison page** (`docs/`): "two reports, same band, one with evidence, one with a hypothesis" — the clearest
  possible statement of the gap, and it costs a page.
- **Use it as the honest answer to Q9**: the reason we cannot score high is the same reason a buyer needs us.
- **Do not chase the 20% reach weight** with an article that oversells; the corpus shows overselling is free, and
  that is precisely why it is worthless to the buyer we want.

## What this study does not give

- A survey. Two reports, both from the final band, chosen for contrast, not sampled.
- A judgement of the authors. Nullmail's numbers are modest and honest; GUN101's mechanism may well be implemented
  — the report simply contains no evidence either way, which is the point.
- A reason to change our score. It is 15–20 on this rubric and that number is *correct*: the rubric is not built to
  reward what we do.
