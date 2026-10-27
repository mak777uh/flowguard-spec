# 80. Pricing Doctrine: cut the price and raise the quality at the same time

> **FROZEN (2026-10-27, ADR-0002):** commercial work is deferred until the first executable measurement
> (`E-M9`). Nothing below is a live offer. Prices, margins and SKUs are doctrine, not quotes, and are not
> maintained while the product has no artifact. See `lab/decisions/ADR-0002-commercial-freeze.md`.


> Stance: do not milk clients. The goal is for the economics not to fall apart, and for the money for upgrades to be there.
> Problem: "we will cut the price and raise the quality" is a promise, and promises in security are worth nothing. What is needed is a **mechanism** that forces this to happen, and a **condition** under which the promise is honestly withdrawn.
> All numbers are `[HYPOTHESIS]` unless marked otherwise.

---

## 1. What "not milking" means operationally

Six rules. Each is verifiable from outside rather than declared.

| # | Rule | How it is verified from outside |
|---|---|---|
| **P1** | **Never a price per finding.** The price is for scope, change or subscription | public price list; the contract has no "per finding" line |
| **P2** | **Gross margin ceiling**: services ≤45%, subscription ≤70%. The excess above the ceiling goes to cutting the price in the next cycle or into a public fund | published margin reporting once a year |
| **P3** | **Automation dividend**: when person-minutes per finding fall, the savings are split 50/50 — half into the price, half into R&D | the published metric `assessor_minutes_per_finding` and its trend |
| **P4** | **The price falls on a schedule, not by goodwill**: the same scope costs no more than a year ago minus 10% | a public price index with history |
| **P5** | **No premium for fear**: the price of the guarantee does not rise on news of incidents in the industry | a comparison of the price list before and after an incident |
| **P6** | **Critical infrastructure at cost or free of charge** (hospitals, utilities, small OSS projects), funded from the margin ceiling and grants | a public list of recipients and the volume |

Rule **P2** is the main one. As long as the margin is not capped, any "we will not milk" remains words, because the incentive points the other way.

---

## 2. Where exactly the milking risk lives

Three kinds of revenue, and the risk is in only one.

| Revenue | What it is | Price dynamics | Milking risk |
|---|---|---|---|
| **Commodity** — "find problems" | scanning, inventory, report | **tends to zero**, and rightly so: the OSS core deliberately makes this free | none — here we drive the price to zero ourselves |
| **Assurance** — signature, liability, proof | an act, a guarantee, acceptance by an auditor | grows with trust, but **is capped** | **here** — if you take a % of the value at risk, an incentive appears to overstate the risk |
| **Infrastructure** — test bench, re-attestation | subscription | falls with automation | moderate |

Hence the principle: **in assurance one must not earn from fear.** That means a ceiling, regression and a ban on an incident premium (`P5`).

---

## 3. The mechanism for cutting the price: the automation dividend

The only physical way to cut the price and raise the quality at the same time is **for cost to fall faster than coverage grows**. In our cost base the human dominates (§10.2 of the compendium), so there is one mechanism:

```
savings = (minutes_old − minutes_new) × hourly_rate × findings_per_engagement

price_cut   = 0.5 × savings
rnd_budget  = 0.5 × savings
```

Example `[HYPOTHESIS]`: review 6 h → 15 min per finding, 4 findings, $120/h.
`savings = (6 − 0.25) × 120 × 4 = $2 760` per engagement.
Of that, $1 380 → into the price (from $12k to $10.6k), $1 380 → into R&D.

**This is the answer to "money for upgrades is needed"**: upgrades are funded **out of saved person-hours**, not out of a price increase. The logic is closed: the better the automation, the cheaper the product and the more money there is for the next automation.

---

## 4. The condition under which the promise is honestly withdrawn

This is the most important thing in the document.

The whole doctrine rests **on a single number**: `assessor_minutes_per_finding`. If the review does not compress to 15 minutes, the cost base does not fall, and P3/P4 become a lie.

Therefore the commitment is formulated **conditionally and publicly**:

> We cut the price by 10% a year for the same scope **provided that `assessor_minutes_per_finding` falls**. We publish this number every quarter. If it does not fall for two quarters in a row, we publish that and **suspend the price promise**, rather than quietly breaking it.

This is how "not milking" turns from a slogan into a verifiable commitment with an honest exit. A slogan without an exit is broken silently; a commitment with an exit is not.

---

## 5. Assurance: ad valorem with a ceiling and regression

The price of the guarantee is tied to the amount at risk (otherwise the product is meaningless for large clients), but with three limits:

```
price_guarantee = clamp(
    value_at_risk × k(v),
    floor = $12k,
    ceiling = $250k
)

k(v) = 0.60% for v ≤ $10M
       0.30% for $10M < v ≤ $100M
       0.15% for v > $100M
```

| Property | Why |
|---|---|
| **Regression of k** | a large client pays a smaller percentage — the market is not punished for size |
| **$250k ceiling** | above that we cannot provide the coverage, and selling dearer means promising more than we can |
| **$12k floor** | below that we do not cover the cost base and start economising on quality |
| **Definition of `value_at_risk`** | **MUST** be in the contract: the daily unmitigated flow, not "capitalisation" — otherwise the metric inflates |

**Rule P5 in action:** after a major incident in the industry our price list **does not change**. Otherwise we would be earning from someone else's catastrophe, and that is exactly the milking we do not want.

---

## 6. Four sources of money for upgrades (and only one from the price)

| Source | Share `[HYPOTHESIS]` | Condition |
|---|---|---|
| Automation dividend (§3) | 50% of the person-hour savings | grows together with quality |
| A fixed share of revenue for R&D | **≥30%, fixed in the charter** | not up for discussion during planning |
| Grants and public funding | external | the mission is partly a public good: DARPA/ARPA-H funded AIxCC, foundations fund OSS security |
| Prepayment for 2–3 years | external | stable cash flow **without raising the price** |

The key point: **not one of the four requires raising the price.** That is why the doctrine does not sacrifice development — it changes its source.

---

## 7. Why this is commercially stronger, not merely more ethical

Three reasons, each verifiable:

1. **The buyer has a free alternative** (OSS core + their own team). Pricing power is therefore physically limited, and a public commitment to cut the price is a weapon against competitors rather than altruism.
2. **In security, trust is destroyed asymmetrically**: one wrong report or one dispute about money costs more than all the profit from an inflated price.
3. **A public price list and a margin ceiling are the same artefact of trust as the negative scope.** We already sell "check it, do not take our word for it"; it would be strange not to apply the same discipline to money.

---

## 8. Claims for criticism

| ID | Claim | Tag | What breaks it |
|---|---|---|---|
| **P-1** | The 45%/70% margin ceiling holds under the current cost structure | `[HYPOTHESIS]` | R3/R4 give 35–40%; if the review does not compress, the ceiling is unreachable |
| **P-2** | The 50/50 automation dividend is real | `[HYPOTHESIS]` | the savings will go into compensating for manual exceptions |
| **P-3** | `assessor_minutes_per_finding` is measurable and controllable | `[HYPOTHESIS]` | the metric will turn out to be noisy and will start being counted differently |
| **P-4** | The regression of k (0.6/0.3/0.15) does not kill the economics of large deals | `[HYPOTHESIS]` | at v > $100M the price will fall below the cost base |
| **P-5** | `value_at_risk` can be defined so that the client does not argue | `[HYPOTHESIS]` | the client will demand "capitalisation" — the metric will inflate |
| **P-6** | Refusing the fear premium is feasible when demand rises after an incident | `[HYPOTHESIS]` | the market will raise the price itself — will we hold |
| **P-7** | Critical infrastructure at cost is fundable from the margin | `[HYPOTHESIS]` | the volume of such clients will eat the margin |
| **P-8** | 30% of revenue for R&D can be fixed in the charter | `[MEASURED]` | the jurisdiction/investors will not allow it |
| **P-9** | A public price index will not let competitors use our prices against us | `[HYPOTHESIS]` | competitors will dump prices in a targeted way |
| **P-10** | Grant funding is applicable to a commercial company | `[HYPOTHESIS]` | the structure will not allow it (a non-profit arm is needed) |

---

## 9. What this breaks in the spec already adopted

| Was | Now |
|---|---|
| SKU C = $48k + $12k/year (fixed) | **ad valorem** with a ceiling and regression: `clamp(v×k, 12k, 250k)` |
| The price is a hypothesis, tested by interviews | the price is a **formula**, tested by willingness to pay at three levels of `v` |
| Margin is a calculation | margin is a **ceiling**, and is published |
| Re-attestation is included in the subscription | it stays, but the subscription **gets cheaper** as automation advances |
| "We will not milk" is an intention | **P1–P6 + the conditional commitment of §4** |

---

## 10. In one sentence

**Not "we are kind", but: a price per finding is forbidden, the margin is capped, the price falls on a schedule, the saving from automation is split 50/50 with the client, there is no premium for fear — and all of it is conditional on one measurable number that we publish and, in its absence, we honestly withdraw the promise.** Upgrades are funded out of saved person-hours, not out of a price increase.