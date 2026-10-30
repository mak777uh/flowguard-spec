# The usefulness reports, surveyed — seven scores, four read in full, and a corrected estimate

Corpus: the `proof-of-usefulness` tag feed (54 posts), from which seven are scored project reports. **Read in
full**: Nullmail (76), GUN101 (77.6), phoenix2pytest (50), Quiet Cost (34). **Read from headline, score and tags
only**: Brainmate (43), PRODSEER (38.59), Spawnr (49) — saying so is cheaper than pretending.

| project | score | domain | what carried the score |
|---|---|---|---|
| GUN101 | **77.6** | PDF encryption library | a novel threat model and confident phrasing; **no** traction, no retention story, evidence question answered with a hypothetical |
| Nullmail | **76** | disposable email | ~10k inboxes/month, 500 organic clicks, **voluntary donations** on a free tracking-free service |
| phoenix2pytest | **50** | LLM trace → pytest | a working demo round-trip (51 labelled traces) and an explicit "we are pre-launch, 0 stars" |
| Spawnr | 49 | agentic economy | not read |
| Brainmate | 43 | AI shared memory / governance | not read |
| PRODSEER | 38.59 | production failure prediction | not read |
| Quiet Cost | **34** | revenue-leak diagnostics | completion behaviour and *critique from users*; a Lovable prototype shared privately |

## The correction that matters: 50 is the floor, not the middle

The phoenix2pytest interview states it plainly: **"50 is the baseline score for a public-but-pre-launch repo."**
That reframes everything I estimated yesterday. The scale is not 0–100 with 50 as average; it is:

- **below 50** — the thing is not publicly reachable, or not complete enough to try (34, 38.59, 43);
- **50** — public, runnable, zero users (phoenix2pytest, with 0 GitHub stars and an honest interview);
- **76–78** — top band, reached by **either** real usage (Nullmail) **or** a compelling narrative (GUN101).

My earlier note said FlowGuard would score "15–20". That was wrong arithmetic on my part: a public repository with
a working command and no users sits at **≈50**, and our engine strengths (innovation, completeness) do not lift it
above the baseline because the top band is decided by the 50% and above.

So the honest sentence is: **we are a 50-point project, and the distance to 76 is exactly one consumer's evidence.**

## Insight A — inside the top band, evidence and narrative are not separated

Nullmail 76, GUN101 77.6. One has a donation signal on a zero-tracking free service; the other has the phrase
"the whole world can use this simultaneously" and no number at all. The band does not distinguish them.

That is the gap our product fills, and it is now a measured statement rather than an opinion: the corpus produces
~300 narratives, and its own instrument ranks an unfalsifiable one above a documented one by 1.6 points.

## Insight B — Quiet Cost shows the evidence type we are missing: **critique**

Its strongest signal was not volume but behaviour: "when users engage enough to **critique what is missing** rather
than dismiss what's there, that's a strong early indicator". For a diagnostic tool that is exactly right, and it
maps onto us precisely:

> a consumer who reads a bundle and says "you missed the path through the nightly job" has used the artifact
> successfully — even though the artifact was wrong.

That is a usefulness signal that does **not** require our verdict to be right, only for the artifact to be specific
enough to be argued with. It is cheaper to obtain than a "decision changed" and it is measurable: count the
consumer's objections and whether they name a path.

## Insight C — specificity is the price of the top band

Quiet Cost's most consistent feedback: "you may have churn issues" is not useful; "users who don't reach value
within 48 hours are likely your biggest leak" changes how someone thinks. The tool lost perceived value **even when
its insight was correct**, purely because the output was general.

Our reports are already specific by construction — a verdict with `wp_017`, a role, a table, a coverage number. That
is a real advantage in this market and it costs nothing to lean on: the report should lead with the path, never with
the conclusion.

## Insight D — honesty is not punished, and it is not rewarded

phoenix2pytest answered "0 GitHub stars at submission", "no users yet", "50 is the baseline and it lines up with
where we are" — and received exactly the baseline. No penalty for candour, no bonus either. The candour that our
repository practises is therefore **safe** in this market; it simply is not a strategy for reaching the top band.

## What I would do with these four

1. **Ask one consumer the eleven questions** and add the twelfth we now know matters: *what did you think the
   report missed?* — Insight B says that answer is the cheapest real usefulness signal.
2. **Lead every report with the specific path**, not the verdict (Insight C).
3. **Say "50, and here is why"** if the score is ever quoted: honesty at the baseline is free (Insight D), and the
   distance to 76 being one consumer is a clean, honest sentence to publish.
4. **Do not chase the band with a narrative** (Insight A): the corpus proves it works, and it is the one move that
   would make our artifact indistinguishable from GUN101's.

## What this survey is not

- It is not all 54 posts: seven are scored reports, four were read in full, three only from metadata.
- It is not a score we were given: nobody scored this repository. The 50 is an inference from a stated baseline plus
  our own reading of the rubric.
- It is not a verdict on GUN101. Its mechanism may be implemented; the report simply contains no evidence either
  way, and that is the finding.
