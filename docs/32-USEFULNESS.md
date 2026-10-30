# Proof of usefulness: the real rubric, the real report, and our honest score

Studied at source, not inferred: HackerNoon's proof-of-usefulness tag feed, the rubric article
["Proof of Usefulness Weight Distribution"](https://hackernoon.com/proof-of-usefulness-weight-distribution), and
one winning report at score 76 ([Nullmail](https://hackernoon.com/nullmail-earns-a-76-proof-of-usefulness-score-by-building-an-open-source-disposable-email-service)).
Scores seen across the corpus: 38.59, 43, 49, 50, 76, 77.6.

## The rubric, verbatim weights

| criterion | weight | the question it asks |
|---|---|---|
| Real-world utility | **25%** | does this solve a genuine problem, practically and immediately |
| Evidence of traction | **25%** | can you prove people are using this; which signals are independently verifiable |
| Audience reach & impact | **20%** | how many genuinely benefit; impact, not registered accounts |
| Technical innovation & stability | **15%** | novel *and* reliable enough to depend on |
| Market timing & relevance | 10% | is this a current need, in this competitive landscape |
| Functional completeness | 5% | does it work right now |

The article is explicit that the weights come from startup-failure research (CB Insights, BLS survival data), and
that **50% is utility + traction combined**: "nothing else compensates for weakness here". Functional completeness
is the lowest weight on purpose — "working software should be the baseline expectation, not a competitive
advantage".

## What the winning report actually is

An **interview with a fixed question set**, published as a story, scored by a machine, with the score page at
`proofofusefulness.com/report/<project>`. The questions, in order:

1. what do you do, and why is now the time for it to exist
2. traction to date, how many people does it reach
3. who does it serve
4. tech stack, and why those choices
5. traction around the web — who has noticed
6. you scored N — needs reassessment or just right
7. what excites you about its potential usefulness
8. **"your most concrete evidence of usefulness — not vanity metrics or projections — the one data point that
   proves people genuinely need what you've built"**
9. adoption versus "tourists": the retention story
10. if re-scored in 12 months, which criterion improves most, and what are you doing now
11. operations: monitoring, abuse, scaling

For Nullmail the answer to (8) was not analytics but **voluntary donations on a free, ad-free, tracking-free
service** — "when someone voluntarily pays for something they could keep using for free". Its reach numbers were
modest (≈10k inboxes a month, 500 organic clicks) and it still scored 76, because utility and traction were
demonstrable.

## Our honest score today

| criterion | us | why |
|---|---|---|
| real-world utility (25) | partial | the mechanism works and four enumerators run, but no named person has had a decision changed |
| evidence of traction (25) | **0** | zero users; the only "consumers" are sibling agents who audited the repository |
| reach & impact (20) | **0** | no distribution, no publication, no audience |
| innovation & stability (15) | strong | two implementations, 12 negative controls, third-party verifier, honest ceilings |
| timing (10) | arguable | agent-driven attacks are rising; that is a reason, not evidence |
| completeness (5) | yes | `fg_init` takes a dump to a verdict in one command |

So on this market's own arithmetic we are a **15–20 point project** — roughly a quarter of the 76 that Nullmail
earned — and the missing 50 points are exactly `P2` and `P4`. That is the same finding from the other direction:
the engine half is done, the evidence half does not exist.

## What to do with this, concretely

1. **Run the eleven questions on one consumer**, not a report about a consumer. The rubric's weight on traction
   means a single real user with a verifiable signal beats any amount of additional engine work.
2. **Prepare the honest answer to (8)** before asking. Candidate: "an auditor re-ran the bundle and found a path
   the team had missed" — which requires that it actually happen first.
3. **Do not optimise for the 15% and 5%** where we are already strong; that is the comfortable work and the
   rubric says it does not compensate.
4. **Publish the score we would get.** A page that says "15–20 by this rubric, here is why" is more credible than
   silence, and it matches this family's habit of publishing the uncomfortable number.

## What this study changed in my own documents

`docs/32` previously contained a template I derived from the announcement. That template was close, but it was a
guess; the real instrument is a weighted score plus a fixed interview, and the interview's eighth question is
sharper than anything I wrote: *one data point, not vanity metrics, that proves people need what you built*.

`Q9` keeps its meaning — the owner still has to name one person — but the ask is now the eleven questions, not a
five-line form.
