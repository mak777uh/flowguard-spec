# The research chat, read as a market instrument — 7 022 messages, two years

Source: a Telegram supergroup export, `result.json` (4.9 MB), chat "ресечим/делаем (c) AI", 2024-10-16 →
2026-10-30. 7 022 messages, ~680 000 characters, one dominant author (3 569 messages) sharing links with short
Russian commentary: **1 527 arXiv links (1 494 unique) and 1 029 GitHub links (826 unique)**.

Read as a dataset, not as conversation. What follows is what the corpus says about the field's attention, which is
the only thing a link feed can honestly tell us.

## The finding that matters: our niche is absent

A keyword sweep over the whole corpus for the vocabulary of our product returned:

| topic | messages |
|---|---|
| reasoning / RL | 663 |
| agents | 339 |
| evaluation / benchmarks | 117 |
| security / vulnerabilities | 25 |
| formal verification / proof assistants | 20 |
| data / SQL / databases | 18 |
| **supply chain / SBOM / provenance / attestation / Sigstore / in-toto** | **0** |

Two years of an AI research community, 1 494 unique papers, and **not one mention** of supply-chain provenance or
attestation. That is the most useful number in the file. Two readings, and both matter:

1. **The problem is not felt here.** This population does not experience "who produced this artifact, and what does
   it refuse to claim" as a pain. Our market is not researchers.
2. **The adjacent things they do feel** are narrower and more concrete: *verifiable environments for agents*,
   *program verifiers for agents*, *leak detection*, *guardrails*. Those are the doorways into this community, and
   they are stated in their vocabulary, not ours.

A side observation with a little irony: the chat mentions the owner's own morphogenesis repository (2026-10-20) as
"проверка идей Майкла Левина про жизнь в цифровом субстрате" — so the portfolio is known here, but by its
research bench, not by its verification discipline.

## The shortlist worth reading, in the order I would read it

| date | item | why it is close to us |
|---|---|---|
| 2026-07-06 | **Dockerless: Environment-Free Program Verifier for Coding Agents**, arXiv 2606.28436 | a verifier for agent output without an environment — the same shape as our gate: it decides about a program without running the world |
| 2026-02-03 | **SWE-Universe: Scale Real-World Verifiable Environments to Millions**, arXiv 2602.02361 | "verifiable environments" at scale; if environments become cheap, the denominator of any verification becomes the scarce good — which is our thesis |
| 2026-02-17 | **Vending-Bench: long-term coherence of autonomous agents**, arXiv 2502.15840 | measures whether an agent stays the same agent over time; the analogue of our freshness problem (`Q5`, `challenge`) |
| 2026-08-21 | **CanaryArchiver** — a copy that leaks tells you whose it was | provenance by watermarking, an entirely different mechanism from our signed claim, and worth knowing as the competing answer |
| 2026-03-20 | **NVIDIA NeMo Guardrails** | the guardrails layer people actually adopt; useful as the thing we are *not* — we do not filter, we attest |
| 2026-10-21 | `DDSirota/reservoir-neural-bench` | a benchmark built by a member; shows how this community measures, from the inside |
| 2026-02-22 | `aisa-group/PostTrainBench` | same, for post-training: the local habit is "build a bench", not "sign an artifact" |

## What the corpus says about how this community argues

- **Links, not reviews.** The median message is a URL plus one line. There is no habit of a written verdict with a
  reproducible command — the thing every project in our own family requires.
- **Benchmarks are the currency.** Where our family signs artifacts, this one builds benches. Both are claims about
  evidence; only one of them is checkable by a stranger without running anything.
- **Russian, short, in-group.** The vocabulary is local ("можно", "надо", "пока"), and the audience is implied.

That is a real opportunity and a real warning: this population will not read a `not_claimed` list, but it will
click a benchmark. If FlowGuard is ever addressed to them, the entry point is "a bench for write-path coverage",
not "an attestation format".

## What I did not do

- I did not read 680 000 characters. I read the structure, the link inventory, a keyword sweep, and eighteen
  messages that combine a link with a verification or evaluation word.
- I did not judge whether any of the shortlisted papers are good. They are chosen by adjacency, and the next step
  for each is a read, not a citation.
- I did not treat the corpus as representative of the field: it is one curated feed with one dominant author.

## The one-line result

**In two years and 1 494 papers, this community never once discussed provenance — and the closest thing it did
discuss is verifiable environments for agents.** That tells us where the door is, and that our current room has no
door to it at all.
