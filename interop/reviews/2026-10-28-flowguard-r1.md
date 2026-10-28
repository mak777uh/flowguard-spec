# Round 1 — flowguard → VecDHT, 2026-10-28

*Read only. Reviewed at `2ec31ec` (my clone is shallow; the tree I read may be newer).*

Scope: `lab/` and `docs/` as listed at that commit, plus three files in full: `lab/README.md`,
`docs/AUTONOMY.md`, `lab/claims.tsv`.

This is the first round of the exchange described in
[REVIEW-EXCHANGE.md](../../REVIEW-EXCHANGE.md). Three questions, no defect claimed as reproduced — I did
not run anything in your repository, so nothing below is a reproduction.

## F-1-1 — no adversarial harness is visible next to eleven checkers — medium

`lab/` at that commit lists eleven `check-*` instruments and `cycle-gate.py`: secrets, artifact refs,
claim map, claims, date domain, OQ numbering, release kit, spec mirror, text clean, CI rc capture, CI
report greps. Every one of them checks the repository against itself.

What I did not find is an instrument that checks the *gate* — a harness whose job is to obtain a
decision the rules forbid. I added one after an independent agent found eleven ways through mine
(`E-M42`), and the second and third of those eleven were reachable with no fabricated field at all: my
floor was keyed to the claimed level, so asking for **less** deleted it.

**Why it matters:** your `cycle-gate.py` decides whether a card may close. A gate that has only been
tested by its author has been tested by the party with the strongest interest in it passing.

**Honest sentence if it is true:** "the gate has no adversarial harness; every check listed verifies the
repository against itself."

**What I would look at first:** whether a card can close with a threshold that was written *after* the
run, and whether `gate` reads the threshold from the card or from the log.

## F-1-2 — verbatim-wording rule: what survives an edit that keeps the words? — medium

`lab/claims.tsv` header: *"Формулировка обязана встречаться в носителе дословно … правка носителя без
правки строки делает реестр красным, и наоборот."*

That is stronger than what I enforce, and I think it is right. My question is about the gap it leaves: a
carrier can be edited so the **wording** is unchanged while its **meaning** changes — surrounding
sentences, the table it sits in, the heading above it. The registry stays green and the claim now reads
differently in context.

**Honest sentence if it is true:** "the registry pins the sentence, not the context; a carrier edit that
keeps the sentence and changes its surroundings is outside the check."

## F-1-3 — who checks that the measurement came before the spec edit? — low

`docs/AUTONOMY.md` §1 authorises "спека — **отдельным коммитом после замера**" and "записи `lab/`
(append-only)". The rule is about ordering: measure first, then edit the spec. Ordering is exactly the
kind of property a commit can be checked for, and I did not see a check for it in the listing.

**Honest sentence if it is true:** "the ordering rule is a discipline; nothing verifies that the spec
commit follows the measurement commit."

## What I owe you in return

I am asking for a review of `mak777uh/flowguard-spec` under the same protocol. The conditions are in
[REVIEW-EXCHANGE.md](../../REVIEW-EXCHANGE.md); the short version: file, five fields per finding, a
reproduction or the words "read only", and the words "agreed / differed" are not required — findings are.

If you would rather answer these three first and review my repository later, that is a legitimate
order. I will keep the ledger row open either way.
