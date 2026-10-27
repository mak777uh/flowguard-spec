# Hackathon plan: Decentralize AI

> **PARTLY SUPERSEDED (2026-10-27).** A1 below puts a browser verifier first. ADR-0001 puts the
> substitution test first, and ADR-0004 removes the browser entirely — the consumer of the tool is an agent.
> Read A1 as "a static demo page", not as the primary artifact. (HackerNoon × Nosana × Arweave × MEXC)

**Recorded:** 2026-10-27, before any code exists. **Owner's decision:** write it down now, build the code later.
**Purpose:** a plan that survives the week, so the next session does not re-derive strategy from a FAQ.

Sources: the hackathon FAQ ([decentralizeai.tech/faq](https://decentralizeai.tech/faq)) and HackerNoon's
writing guide ([help.hackernoon.com](https://help.hackernoon.com/your-complete-guide-to-writing-for-hacker-noon)).
Anything not sourced from those two pages is marked as our inference.

---

## 1. The pool, and where the money actually is

| Prize | Amount | Who gets it |
|---|---|---|
| Nosana GPU compute credits | **$70 each, up to 500 participants** | every eligible participant |
| Nosana bonus | **+$450** | round winners |
| Arweave storage credits | $2,500 | winning or qualifying projects built on permanent storage |
| AR cash | $2,500 | winners |
| MEXC MX tokens | $5,000 | winners |
| **Grand prize** | ownership of DecentralizeAI.tech — domain + codebase (a writing tool on Llama 3 / Mixtral / Stable Diffusion) | **one** overall winner |
| Total | $51,750+ | two rounds, June 2026 – February 2027 |

**The arithmetic that drives the plan:** 500 × $70 = **$35,000 of the $41,750 compute pool is payment for
eligibility, not for winning.** The floor is therefore a real prize, and it is won by being *eligible*, not
by being clever.

**Consequence:** optimise for (a) guaranteed eligibility in both rounds, (b) a credible shot at a round win,
and do not spend effort chasing the single grand prize. Expected value lives in the first two.

---

## 2. The eligibility gate — the only thing that matters

The FAQ states the four judging criteria verbatim:

1. **Technical depth** — is this a real implementation?
2. **Originality** — does it solve something unsolved?
3. **Impact** — does it meaningfully advance the decentralized AI stack?
4. **Verifiable evidence** — working code, a deployment URL, or reproducible metrics.

And then the sentence that decides our current fate:

> **"Mockups, prototypes without demos, and coming-soon projects are not eligible."**

**Our position against the gate, honestly:**

| Criterion | Status today |
|---|---|
| Technical depth | ✗ no code |
| Originality | ✓ the eliminations registry + reserved vocabulary + the loop with two brakes |
| Impact | ~ arguable; needs to be stated in their vocabulary (permanent provenance, verifiable systems) |
| Verifiable evidence | ✗ no deployment URL, no reproducible metric |

**Therefore: submitting the specification, or the article about it, fails criterion 4.** The article is
documentation of a project, not a project. This is the single most important correction in this file.

---

## 3. The three artifacts that close the gate

Each one is chosen because it maps to a specific criterion and to a specific sponsor's stack.

### A1 — a verifier that runs in a browser tab (deployment URL)

Implement `fg verify` for the `fg-bundle/1` format as a static page: drop a bundle in, the page recomputes
hashes locally in the tab, checks the signatures, and prints `PROVEN` / `ENFORCED_TESTED` / `INCONCLUSIVE` /
`INVALID` with the coverage scalar in the header.

- **Criterion served:** technical depth + deployment URL.
- **Why it is the strongest single move:** it continues the exact aesthetic of the article that already
  placed — *verify it yourself, in a tab, without trusting the author*.
- **Acceptance:** a stranger opens the URL, loads the sample bundle, and gets a verdict in under five
  seconds without any server round trip.
- **Cost:** one static page, no backend. The hard part is the crypto in the browser (Ed25519 + canonical
  JSON), not the UI.

### A2 — a real Arweave archive (transaction id in the repo)

Archive the specification, the claim registry and the eliminations registry to Arweave, and commit the
transaction id.

- **Criterion served:** the Arweave credit criterion, verbatim: "projects building on permanent,
  decentralized storage".
- **Why it matters beyond the prize:** it converts the article's thesis from a proposal into a fact. The
  thesis is "permanence without semantics is durable ambiguity" — so the artifact that must be permanent is
  the typed claim registry, not another README.
- **Acceptance:** the tx id resolves, the content hash matches the repo file byte-for-byte, and the repo
  links the id.
- **Cost:** a few dollars of AR; the credits being claimed are exactly for this.

### A3 — one reproducible metric: the substitution test (`E-M9`)

Swap code, build, configuration and identity while keeping valid signatures; report whether the offline
verifier rejects all four.

- **Criterion served:** "reproducible metrics" — one number, with the command that re-shoots it.
- **Why it is the honest choice:** if the verifier misses one, the claim in `CLAIMS.md` moves from
  `judgment` to `false as stated`, and we publish that. A negative result is still a reproducible metric,
  and the registry is built to record it.
- **Acceptance:** a table of four substitutions × accept/reject, plus `lab/experiments/E-M9.md`.
- **Cost:** three days.

---

## 4. Two rounds, two submissions, no repetition

| | Round 1 | Round 2 |
|---|---|---|
| Artifact | A1 + A2 + A3 | A1 extended: the typed-claim linter as a service over an API, plus the coverage report for a real target |
| Novelty vs previous | first working artifact | evolution, visibly built on round-1 results |
| Article | "Verifiable AI needs more than a hash" — already drafted, rewritten for the platform | follows from round-1 outcome, including any claim we had to withdraw |

Submitting to both rounds is explicitly allowed ("you can submit your project for consideration in each one
as your build progresses"). Two rounds also mean the second submission can cite the first round's public
result, which is the cheapest possible evidence of momentum.

---

## 5. Submission mechanics

| Step | Where | Notes |
|---|---|---|
| Claim Nosana credits | [decentralizeai.tech/claim/nosana](https://decentralizeai.tech/claim/nosana#claim) | every eligible participant, before or after building |
| Claim Arweave credits | linked from the same claim area | for projects on permanent storage |
| Publish the article | HackerNoon | first person, headline ≤80 chars in Title Case, at least one image, up to 8 tags |
| Submit the project | [decentralizeai.tech](https://decentralizeai.tech) | needs code/repo, deployment URL and metrics |

**HackerNoon rules that changed the draft** (from their guide, not our taste):

- first person "I", **not "we"** — "leave the pronoun 'we' at home";
- headline ≤80 characters, Title Case, accurate, not clickbait;
- **at least one image is mandatory**; original preferred, a diagram counts;
- 1–2 lines of who the author is;
- **up to 8 tags**, chosen as if winning an SEO competition;
- hyperlink naturally, never paste a bare URL next to the phrase.

---

## 6. Order of work, and what blocks what

```
1. browser pass on /prizes and /judges      → tells us which criterion the judges weight
2. claim Nosana (+ Arweave) credits          → free money, no dependency on code
3. A1 verifier in a browser tab              → unblocks the gate (technical depth + URL)
4. A3 substitution test                      → unblocks "reproducible metrics"
5. A2 Arweave archive                        → unblocks the Arweave credit criterion
6. rewrite + publish article                 → documentation of a working artifact
7. submit round 1, then repeat for round 2
```

Steps 1–2 cost nothing and can happen before any code. Steps 3–5 are the block. Step 6 must come **after**
step 3, otherwise the article advertises something that does not exist — and the rules exclude exactly that.

---

## 7. Decisions recorded here

- **D1.** The article is documentation, never the submission. Submitting prose alone fails criterion 4.
- **D2.** The floor ($70 × 2 rounds) is treated as a real prize, not a consolation.
- **D3.** No effort spent chasing the grand prize until a round is won.
- **D4.** Arweave is used for the claim registry, not for the repository: permanence belongs to the thing
  other people must be able to check later, and that is the registry.
- **D5.** If `E-M9` fails, we publish the failure and submit the negative result. The registry has a
  `false as stated` state exactly for this.

## 8. Open questions for the browser pass

1. Prize split per round: are AR/MX awarded per round or once overall?
2. Who are the judges, and what is their background — formal methods, Arweave, GPU infra?
3. Does a submission require a specific form with fixed fields (repo, deployment URL, video)?
4. Is there a deadline date for round 1, or is it rolling?
5. Does the platform's own article generator count for or against an entry?

---

## 9. Corrected mechanics — read from the live site, 2026-10-27

The site pages (PRIZES, JUDGES, the claim form) and the tag page were read directly through the shared
Chrome session. Five facts change the plan.

**9.1. Entry is a post, not a code submission.** PRIZES states it plainly: *"Your shot at $51,750+ starts
with one post. Publish your decentralized AI piece on HackerNoon with the right tags and you're in."*
The mandatory tag is **`#decentralize-ai-hackathon`** — the site's "Hackathon Entries" link resolves to
`hackernoon.com/tagged/decentralize-ai-hackathon`.

**9.2. The tag had 35 posts when checked, and one of them is already ours.** ModelProof, published
2026-10-27. So the entry exists; the remaining question is a second, stronger entry, not a first one.

**9.3. Winner slots are 15, not one.** "15 Winners × $450 Compute Credits". The grand prize is a single
winner on top. With ~35 entries in the tag, the count-odds on a winner slot are close to 2 in 5; the
quality-weighted odds are the ones we can move.

**9.4. The rubric is a writing rubric, and it is published.** Deep technical understanding · novel insights ·
real-world impact · **research and evidence ("data, papers, case studies")** · clear communication.
Plus a stated pro tip: *"Judges favor posts that cite specific projects, papers, and people."*
Our first draft cited only itself — that is a direct hit on criterion 04.

**9.5. The Nosana claim is a form, and it collects personal data.** Fields: project name, proposal
(≤5,000 chars), GitHub repo URL, model/workload details (≤2,000), deployment commitment, team members,
social links, email, phone, country, one-representative confirmation. Credits arrive by email after review.
**Requires the owner's data and explicit approval — not submittable by an agent on its own.**

### What the plan becomes

| Priority | Action | Why |
|---|---|---|
| 1 | Publish the citation-heavy second article with the hackathon tag | entry mechanism, doubles coverage, targets criterion 04 |
| 2 | Claim the $70 Nosana credits (owner's data, owner's OK) | free money, no dependency on code |
| 3 | Add one original image to the post | HackerNoon requirement, and the rubric rewards clarity |
| 4 | Build the browser verifier + substitution test | makes the *next* entry score 03/04 instead of claiming it |

### Decisions added

- **D6.** Citations are not decoration; they are criterion 04. Every claim about prior art gets a source.
- **D7.** A second entry in the same round is allowed and cheaper than waiting, provided it is a different
  artifact rather than a rehash of the first.
- **D8.** The claim form is submitted by the owner or with the owner's explicit approval, because it
  contains personal data (email, phone, country) and creates an obligation to deploy on Nosana.
