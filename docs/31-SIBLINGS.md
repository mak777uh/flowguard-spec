# The pinned repositories, read one after another — and what each one solves that we do not

Six pinned repositories, one owner, one discipline applied to six different subjects. This is what each is for,
what it does better than this repository, and what I took from it. Nothing here is a comparison of quality: each
entry names a mechanism we can copy without copying the subject.

## The set

| repository | subject | its central mechanism |
|---|---|---|
| **flowguard-spec** (this one) | value flow through a database control point | scoped consistency verdict, refusal vocabulary, signed bundle |
| **VecDHT** (Rust) | a peer-to-peer vector index | canonical byte form as the contract between two implementations, 7-method kit, eliminations with revival conditions |
| **lexspec** | legal statements that software can check | anchor-or-refuse: an atom without an unambiguous span in a pinned revision is not a weak claim, it is a different product |
| **herness** | a harness that measures boundaries of truth | the instrument must **show its own error**; evidence types drive wording |
| **cases** | public record of verification work | one plain sentence per case, a generated registry, and "not confirmed" published as a result |
| **`-` (morphogenesis)** | emergent morphology in neural cellular automata | pre-registration, sensitivity arithmetic before launch, seed anchors, eliminations, retractions at n=20 |

## What morphogenesis does that this repository does not

Read its README once and the difference is uncomfortable. Four mechanisms, all of them cheap:

1. **Sensitivity arithmetic before launch.** Any A/B experiment must show the arithmetic that creates the
   difference *before* the run; two of their early series were insensitive by construction and are reported as
   "the test did not reach the effect", never as "there is no effect". My two paired evaluations (`E-M73`,
   `E-M75`) were exactly this defect: I measured a difference the design could not produce, twice, and only
   afterwards understood why.
2. **A registry of eliminated hypotheses with revival conditions.** `docs/eliminations.md` keeps every ruled-out
   hypothesis with its artifact and **what would revive it**. We have `refutes` cards but no registry, so a
   refuted idea can quietly return.
3. **Retractions are published with the same weight as results.** Their `§10cv` retracts a morning result at
   n=20: "the morning result of 7.14 vs 3.9–4.7 was 3–6-seed noise". We have two refutations of my own claims
   (`E-M73`, `E-M75`) and no single page that lists them.
4. **Seed anchors.** Every code change re-runs a pinned reference run and compares bit-for-bit; a probe that
   consumed the RNG once shifted the world and the anchor caught it in 90 seconds. Our analogue exists — the
   sample bundle's address — but we do not re-derive it on every change as a tripwire.

## What herness does that this repository does not

Its AGENTS.md states the rule in one line: **the instrument must show its own error.** Every guard here reports a
pass or a fail; none reports "what this guard would miss". The negative controls (`lab/selftest-guards.sh`) are the
closest thing, and they were added only after an external audit.

## What cases does that this repository does not

**One plain sentence per case**, and a generated registry that includes the case that ended "not confirmed". Our
`lab/experiments/INDEX.md` is generated and does list verdicts, which is the same mechanism; the difference is that
their sentence is written for a human who reads nothing else, and ours is the card's title.

## What VecDHT and lexspec already share with us

Both have the same three instruments we do — a kit of methods, a closed refusal vocabulary, and an
eliminations-with-revival document — and both arrived at them independently. That convergence is the strongest
signal in the family: it means the shape is not one author's habit.

## What I am taking, in order

1. **`docs/ELIMINATIONS.md`** — every refuted claim and every ruled-out mechanism, with the artifact that killed it
   and **what would revive it**. Generated skeleton from the cards whose verdict is `refutes`, hand-written revival
   conditions, and a guard that every `refutes` card appears in it. (This commit.)
2. **A sensitivity line in every experiment card** — before the threshold, an explicit "what difference can this
   design produce, and is it larger than noise?" with the number that shows it. `E-M73` and `E-M75` are the two
   cards that would have been refused by their own sensitivity line.
3. **The instrument's own error** — one line in `lab/selftest-guards.sh`: for each control, what the guard would
   miss even when it passes.

None of the three needs a decision from the owner: they are documentation and guard work inside the existing
formats.
