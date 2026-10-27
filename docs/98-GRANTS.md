# Grants: where the money actually is (checked 2026-10-27)

Sources: organiser pages read directly where possible, plus the [DevGrants Daily](https://devgrantsdaily.com)
aggregator for discovery. Every row marked `verified` was confirmed on the funder's own page; `agg` means
it comes from the aggregator and must be re-checked before writing anything.

---

## 1. The one that fits

### NLnet open call — €5,000–€50,000, deadline **3 November 2026, 12:00 CET**

Verified at [nlnet.nl/propose](https://nlnet.nl/propose/). The form has a fund selector:
**Restack Fund / CodeSupply Fund / Other / open call**.

- **CodeSupply** is the EU-funded sub-fund (€400k pool, Horizon Europe project 101298846) aimed at
  **software supply chain security**: development, research, audits, **formal proofs**, documentation,
  standards. It is almost a description of this repository.
- **But**: EU-supported funds require a "European dimension", which in practice means Horizon
  Europe-eligible countries. Russia is not one. The form does have an escape clause — "clarify how your
  project might satisfy the 'European dimension' requirement (e.g. European citizenship)" — which is worth
  using only if it is true.
- **The honest play**: apply to **Other / open call** (NLnet's own money, no EU dimension requirement,
  applicants worldwide) and mention CodeSupply's topic as alignment, not as the fund.

**Two constraints that matter, both from their own page:**

1. *"We are not interested in AI-generated projects or proposals."* There is an AI-disclosure field that asks
   for prompts and interactions. A repository developed by AI agents is fine; a **proposal written by AI and
   passed off as one's own is not**. Write it in your own words, in plain text, and disclose honestly.
2. Grants are for **technical development**, not for specs. The application must lead with what gets built:
   the verifier, the claim linter, the bundle format, the replay harness. The specification is evidence of
   thinking, not the deliverable.

### Draft answer structure for the five long fields

| Field | What to write (own words, short) |
|---|---|
| summary, 1000 chars | build `fg-verify`: an offline checker for attestation bundles, plus `fg-claim`: a linter that rejects a claim worded more strongly than its evidence type. Outcome: a third party can check a software supplier's security statement without trusting the supplier. |
| effort, 4000 chars | tasks with hours: bundle format + canonical JSON (40h), verifier with Ed25519 + hash chain (80h), substitution test harness, 4 attack classes (40h), claim registry + linter (40h), browser-only verifier (60h), docs and licensing (20h). Rate: state a daily rate and that it is below market. No expenses. |
| comparison, 4000 chars | SLSA provenance (build identity, not claim semantics), Sigstore/Rekor (transparency, not wording), seL4 (proofs about a model), Certora/Halmos (invariants for one class). What is new: **the evidence type attached to each sentence, enforced by a linter**, and an abandonment ledger with revival conditions. Consider contributing to Sigstore's attestation vocabulary rather than replacing it. |
| challenges, 4000 chars | model-to-code correspondence cannot be instrument-checked; token classes that break conservation (fee-on-transfer, rebasing); detector recall is measurable but not provable; the payer chooses the boundary and can narrow it. Each has a named countermeasure and a stopping rule. |
| ecosystem, 2000 chars | depends on: OpenSSF attestation formats, Sigstore, SLSA, in-toto, JSON Canonicalization RFC 8785. Users: auditors, insurers, procurement teams, OSS maintainers who must answer security questionnaires. |
| background, 2000 chars | independent researcher; published verification work with reproducible artifacts (`mak777uh/cases`, `mak777uh/audits`); VecDHT (Rust spec + implementation); the morphogenesis bench with a machine-checked claims registry; an open pull request with tests against a real project. Link the two HackerNoon articles. |
| other funding, 1000 chars | none to date; state it plainly. |

---

## 2. Ranked shortlist

`fit` is my judgement for this specific project, not the fund's prestige.

| # | Program | Amount | Deadline | Eligibility for an individual outside EU/US | Fit |
|---|---|---|---|---|---|
| 1 | **NLnet open call** (verified) | €5–50k | **3 Nov 2026** | yes — worldwide, individuals and collectives without a legal entity | ★★★★★ |
| 2 | **NLnet CodeSupply** (verified) | €5–50k | 3 Nov 2026 | EU dimension required — not for RU | ★★★★★ topic, ✗ eligibility |
| 3 | **Alpha-Omega** OSS security (agg) | $50–100k | 31 Oct 2026, then quarterly | yes, but wants **widely used** OSS — a new repo is weak | ★★☆ now, ★★★★ later |
| 4 | **TheDAO Security Fund** (agg) | $20–600k | round 2 until Jan 2027 | yes, crypto-native | ★★★★ |
| 5 | **EF ESP** + **Proximity Prize** (agg) | varies | rolling | yes; Proximity Prize is literally *Lean proofs for SNARK soundness* | ★★★★ for the formal branch |
| 6 | **FLOSS/fund** by Zerodha (agg) | up to $100k/yr | rolling, quarterly | yes — "anywhere" | ★★★★ |
| 7 | **OTF Internet Freedom Fund** (agg) | $10k–900k | rolling | yes | ★★★ |
| 8 | **Mozilla Foundation Fellowship 2027** (agg) | up to $125k | LoI **17 Dec 2026** | yes | ★★★★ (public interest framing) |
| 9 | **ARIA Scaling Trust** (verified via agg) | £100k–3M | 31 Oct 2026 | UK focus; non-UK only if it increases UK impact | ★★ (topic ★★★★★) |
| 10 | **Sovereign Tech Fund** (agg) | from €50k | rolling | funds base technologies; usually needs an entity | ★★★ |
| 11 | **GitHub Secure Open Source Fund** (agg) | $10k | rolling | yes | ★★ |
| 12 | **OpenSats** Q4 general (agg) | varies | 30 Nov 2026 | yes | ★★ (Bitcoin/nostr) |
| 13 | **Claude for OSS / Codex for OSS** (agg) | free compute | rolling | yes, trivial | ★★★ as tooling budget |
| 14 | **Amazon Research Awards — Automated Reasoning / Security** (agg) | ≤$80k + credits | 4 Nov 2026 | usually requires academic PI — check | ★★ |
| 15 | **Prototype Fund** (agg) | €95k | 30 Nov 2026 | Germany residency required | ✗ |
| 16 | **NSF PESOSE / NSF AI** (agg) | up to $1.5M | Mar 2027 | US institutions only | ✗ |

Geography is the hard filter, not quality: EU-funded calls (CodeSupply, Horizon Europe, EIC), US federal
(NSF), and Germany-residency programmes (Prototype Fund) are closed regardless of merit. Payment rail
matters too — crypto-native funds are the practical route when banking is the obstacle.

---

## 3. Hackathons and bounties running right now

| Program | Amount | Deadline | Note |
|---|---|---|---|
| Decentralize AI (HackerNoon) | $70 credits ×2 rounds + prizes | two rounds to Feb 2027 | entry = a tagged HackerNoon post; ModelProof already in |
| GitLab Life After Code | $45,000 pool | 27 Oct 2026 | AI agents that automate review and security |
| huntr Blind Trust AI | $15,000 pool | 30 Oct 2026 | prompt-injection style attacks on assistants |
| ZeroDay.Cloud (Wiz) | $6.5M pool | 1 Dec 2026 | RCE in open source cloud software |
| Google Patch Rewards | $100–15,000 per patch | rolling | security patches in OSS |
| Google OSS VRP | up to $31,337 | rolling | supply chain compromises |

---

## 4. What to do, in order

1. **Today–3 Nov: NLnet.** One application, own words, `Other / open call`, lead with the verifier.
   This is the only deadline that matches the fit.
2. **This week: TheDAO Security Fund** — same text, re-framed for the on-chain branch (escrow invariants,
   verified payouts). Rolling into January, so no panic.
3. **This week: FLOSS/fund and OTF** — short forms, worldwide, quarterly review.
4. **By 17 Dec: Mozilla Fellowship LoI** — if the public-interest framing ("verifiable claims for critical
   software") reads naturally, this is the largest single cheque with the longest runway.
5. **Only after the verifier exists:** Alpha-Omega. They fund projects that others depend on; a working
   offline verifier with users is a different application from a spec.

## 5. Honest cautions

- A proposal that promises "a formally verified safe core" will be read as fantasy by any reviewer who knows
  the field. Promise what the repository can demonstrate: an offline verifier, a claim linter, a substitution
  test with published results, including failures.
- Do not let AI write the proposal. NLnet asks for prompt logs and has stated it is not interested in
  AI-generated proposals. Drafts by an assistant are a disclosure question, not a shortcut.
- Do not apply to EU-funded calls without the European dimension. A rejection on eligibility is wasted time.
