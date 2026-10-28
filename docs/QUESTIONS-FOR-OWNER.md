# Questions for the owner — the short list

Everything else is being decided and built by the agent. This file holds only what **cannot** be decided here, with
what is blocked, what happens while waiting, and what it costs. Reviewed every round; answers land as edits here.

Last updated: 2026-10-28, after the coordination check with VecDHT.

---

## Q1 — a real schema to measure on (blocks the first non-synthetic evidence)

**What I need:** permission to point the tool at one real Postgres database, or the name of one.

Every measurement so far is on a fixture **I wrote**. That is the strongest criticism available against this
repository, and it is correct: eight planted bypasses in a schema I designed prove the mechanism, not the utility.

**What I have done alone:** four public schemas loaded and measured (Pagila, Sakila, Chinook, Northwind), plus
GitLab's production structure.sql — 1436 tables, 558 functions. On GitLab only 36 functions contain a write
statement, which is why db_logic_density now refuses a strong verdict on such a system. Q1 is therefore half
answered: public evidence exists, your schema or a client's does not.

**What I cannot do alone:** anything of yours, or a client's, which is where the real test is.

**Cost of waiting:** the evidence stays synthetic; readiness cannot exceed T2 on synthetic evidence alone.

## Q2 — one consumer conversation (blocks T3, the product half)

**What I need:** one introduction — an auditor, an insurer, a protocol team, or a procurement person — and twenty
minutes. The form is [M8-CONSUMER.md](M8-CONSUMER.md); five lines fill it.

**What is blocked:** the product half of readiness is 0% and cannot move without a named human. `P2` in
[READINESS.md](READINESS.md).

**Cost of waiting:** ten conversations that produce nothing would justify eliminating the product thesis
(`X-21`). Without any conversation, we do not even learn that.

## Q3 — who signs risk acceptance, and with what liability (money decision)

**What I need:** a decision, not information. Three options, in ascending commitment:

1. **No signature.** The bundle carries analysis provenance only; nobody accepts risk; nobody can rely on it. Free,
   and the product is a tool.
2. **Signature with a reliance scope.** A human signs "this may be relied upon for this flow, up to this date, for
   these decisions". This is the reserved field `risk_acceptance` and it is the thing a client would buy.
3. **Signature with an indemnity.** Money at risk. Requires a legal entity, insurance, and a cap.

**What is blocked:** option 2 is designed and unimplemented; option 3 is not designed at all.

**Cost of waiting:** the artifact cannot be sold to anyone who needs recourse, which is most buyers.

## Q4 — publish Part 2 of the hackathon article?

Ready since before the pivot, marked as drafted-not-published. You declined once; the offer stands until the
hackathon closes.

## Q5 — the $70 Nosana credits

Requires your account data to claim. Low value; ignored unless you want it.

---

## Standing decisions I am making while these wait

- **No product claims** in any public surface until Q2 or Q3 resolves. `NC-01`…`NC-10` enforce this mechanically.
- **No pricing, no buyer outreach** — your call, unchanged since round 6.
- **Public schema next** (Q1, alone): Pagila or equivalent, then the same four sources, same thresholds.
- **M7 stays `absent`** until a stranger rebuilds a bundle. Asked of VecDHT (PR #3); no answer yet.

## Вопросы, накопившиеся за последние круги

1. **Принятие риска связано с адресом, но не покрыто им полностью.** С ADR-0015 подпись роли покрывает все её
   поля, кроме ccepted_scope (он обязан равняться адресу, и адрес не может содержать собственный дайджест).
   Верификатор сверяет его отдельно. Вопрос владельцу: достаточно ли этого, или принятие должно быть
   криптографически привязано к адресу иначе — например, второй подписью поверх адрес + дайджест роли?
   Решение меняет формат и инвалидирует выданные артефакты, поэтому это вопрос к вам, не ко мне.

2. **NC-01…NC-11 живут вне артефакта.** Бандл несёт только идентификаторы; что именно приняла сторона,
   из артефакта не узнать. Нужно ли вшивать текст словаря в бандл (дороже по размеру, но самодостаточно)
   или оставить ссылку?

3. **Цена ложного сильного вердикта.** Гейт выдерживает три раунда атак (11 + 14 + 9 прорывов, все закрыты),
   но каждая проверка читает документ, который пишет заявитель. Потолок конструкции: «документ лжеца
   противоречит сам себе», а не «лжец не пройдёт». Вопрос: нужна ли внешняя привязка (подпись третьей
   стороны над инвентарём), или этот потолок приемлем для первого продукта?

## Q5 — does a bundle need a freshness binding (challenge) and tool provenance?

A bundle today can be produced for nobody and presented later as an answer: the claim has no nonce, no challenge, and no record of which tool version produced it. NEAR AI's attestation stack binds all three, and their separation is instructive (quote+nonce+signer, image provenance, verifier-owned policy).

Proposed, additive: claim.challenge (hex, supplied by the relying party) and claim.tool {name, version, digest}. Verifier refuses a challenge mismatch when one is expected; reports an absent tool digest. It changes the canonical bytes of new artifacts only, but it is a format decision, so it is queued rather than applied. Full reasoning: docs/27-NEAR-ATTESTATION.md.

