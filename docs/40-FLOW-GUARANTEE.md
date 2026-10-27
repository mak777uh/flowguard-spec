# 40. Protected flows: the unit of work is not a finding but a guarantee per flow

> Proposal: treat the product's responsibility not as "vulnerability discovery" but as the **protection of important flows** — money, PII, traffic, storage access — from entry to exit, and declare the "glue" out of scope. The highest grid is a formally checkable protection of a flow.
>
> Assessment: the direction is right and stronger than the current one. But the wording "unbreakable" is a legal and engineering trap. Below is how to make it precise and, at the same time, more sellable.

---

## 1. Why this is better than "hunting for bugs"

One argument, and it is decisive. All five second-round reviewers independently named the product's death mechanism: **`PROVEN` starvation** — too few findings for the client to pay and renew. The cause is not the agent but the **unit of work**: "find the defects" is a negative, unbounded, and always partial claim. No positive deliverable can be made from it, which is why "we found nothing" is indistinguishable from "a broken scanner".

A flow changes this:

| | "Find the defects" | "Protect the flow" |
|---|---|---|
| Unit | a finding | a flow + a policy |
| Claim | "we found nothing" (negative) | "the flow passes through the mediator, a bypass within closure Z is impossible" (**positive**) |
| Boundedness | unbounded, always incomplete | bounded by the declared closure |
| What is sold on a zero result | nothing | architecture + proof |
| Who is to blame on an incident | we are ("we found nothing") | it becomes visible whether the incident was outside the closure |
| Relation to the "glue" | it is in scope too, hence in the noise | out of scope, and this is **declared** |

This answers the question all five reviewers left open: the buyer does not accept a negative claim (reviewer No. 5, "coverage without a purchase"). A guarantee per flow does, because it is checkable.

---

## 2. The trap of the wording

"Formally verifiable with no possibility of compromise" is a promise that cannot be kept, and therefore cannot be sold without unlimited liability. Three corrections:

1. **Not the "system" but the mediator.** What is provable is not the application but the **decision point** and its conformance to the policy. The application remains "glue" and may be leaky — that is acceptable as long as it cannot bypass the mediator.
2. **Not "unbreakable" but "a bypass is impossible within closure Z".** Always with a condition. Formally: the property is conditional, and the condition is part of the delivered artifact.
3. **Not "proven" but "proven + measured".** The closure is partly proven and partly broken by the red team. Both parts go into the report.

The correct product statement:

> **For a declared flow F and policy P: a mediator M is isolated, it is proven that M implements P, and it is proven (or demonstrated by the red team) that within closure Z there is no path bypassing M. Outside Z the guarantee does not apply.**

That is a precise, checkable and bounded responsibility. And it is stronger than "we found 12 bugs".

---

## 3. Three levels, of which only two are provable

**Level A — policy (what is permitted).** Who, which resource, under what condition. Provable: the policy is consistent, has no implicit permits, does not escalate (no delegation cycle), deny beats allow. This is exactly what SMT analysis of IAM policies does in industrial form (AWS Zelkova is a publicly described example), and it is already provable without any formal verification of code. **Cheap. Sells immediately.**

**Level B — mediator (what it does).** The code that makes the decision. Provable: the mediator refines the policy (refinement), there is no bypass through an error in the code, there is no TOCTOU. Verus/Creusot/Dafny/SPARK work here; at the limit, a seL4-like approach (a verified kernel as the TCB). The mediator is small (hundreds of lines), so the proof is realistic. **Expensive but bounded. This is the "highest grid" that makes sense.**

**Level C — closure (that nothing goes past the mediator).** **This is where it all breaks.** Complete mediation is a property of the *system*, not of the code: one must prove that there is not a single bypass path. Formally this is provable only for closed systems (a microkernel, an isolated process with a single entry point). In an ordinary cloud application it is **not provable, only checkable**:

- enumeration of all entry points (ingress, batch, cron, queue, admin, backup, restore, migrations, debugging) — an audit, not a proof;
- prohibition of ambient authority: no long-lived credentials, no direct DB access in bypass, egress deny-all, a single ingress;
- a red team that attempts a bypass and **fails** the attempt.

So the honest architecture: **A and B are proof, C is measurement.** Do not mix them.

---

## 4. Formal statement (so as not to reinvent it)

The idea is the classic **separation of privilege through a reference monitor** plus **information-flow security**:

- **Reference monitor** (Anderson, 1972): three properties — complete mediation, tamper-proof, verifiable. Our formulation is exactly these three, except that we honestly call property No. 1 "measurable" rather than "proven".
- **Noninterference** (Goguen–Meseguer, 1982): the formal meaning of "the flow is protected" — the actions of a high-level subject do not affect the observations of a low-level subject. This is what "there is no leak" actually means, and it is provable for the mediator but not for the application.
- **Object-capability**: preferable to checks, because "no right — no interface" requires no proof: a bypass is impossible by construction. For flows this means: the component has no ambient authority, only issued capabilities.
- **seL4 / IronFleet** — the benchmarks: "prove the kernel and the protocol" is realistic, "prove the whole application" is not.

The product does not invent the theory. It **sells its application to a specific client flow**, with artifacts.

---

## 5. How this changes the R0–R5 ladder

The highest grid is redefined: it is no longer "rewrite the parser in Rust".

| R | Was | Became for a flow |
|---|---|---|
| R0 | mitigation | inventory of the flow, revocation of excess rights, prohibition of one bypass path |
| R1 | patch | close a specific bypass (shadow endpoint, batch job, debug port) |
| R2 | hardening/detector | prohibition of ambient authority: short-lived credentials, egress deny-all, a single ingress |
| R3 | refactoring | **introduce a mediator**: all access to the resource goes through it |
| R4 | memory-safe | a mediator in a safe language, a capability model instead of checks |
| **R5** | verified kernel | **prove the policy (A) + prove the mediator (B) + measure the closure (C)** |

Thus R5 becomes not "an academic project for aviation" but **a commodity for any service that has money or PII in a flow**. This sharply widens the premium segment: previously it was only for regulated companies, now for fintech, payment providers, any marketplace.

---

## 6. Where the "glue" takes its revenge

"Glue however you like" is exactly where real leaks happen. Seven bypass paths that must be closed or explicitly excluded:

1. **Batch / cron / ETL** — the same resource, but past the API.
2. **Admin console and support access** — legitimate, but not mediated.
3. **Backups and restore** — a copy of the flow without a policy.
4. **Mobile/partner API** — a second ingress.
5. **Direct DB access** from another service (a shared credential).
6. **Logs and analytics** — a copy of the PII in another store, outside the policy.
7. **Supply chain and CI** — access to secrets at deployment time.

Each of them is either inside the closure (and then it must be mediated) or explicitly declared outside the guarantee. **There is no third option**, and this is exactly where the product must be ruthless: "outside the closure" is not an excuse but a declared risk with a price.

---

## 7. Economics: the trap and the way out

**Plus.** A positive deliverable → no empty-report problem → no `PROVEN` starvation. The price is higher: this is architecture + proof, not a scan.

**Minus, and it is serious.** "Introduce a mediator and prove it" is **design and migration**, that is, consulting with a 35–45% margin (like R3/R4 in our own analysis). The product turns into a project with a six-month cycle.

**The way out is a product component.** The mediator must be a **deployable artifact**, not custom work: a gateway/library with the policy in declarative form, whose proof is generated automatically for standard policies. Then:

```
mediator license + subscription to the proof and its freshness
+ one-time migration (consulting, but with a predictable scope)
```

This is exactly the path that the second round called a "reusable proof harness": if it covers 3–5 standard policies (tenant isolation, ownership check, amount limit, PII classification, state machine), the margin rises from 45% to 65%+, and a repeat client comes for a revision rather than for a new project.

---

## 8. Pilot: one flow, 30 days

Not "we will prove everything". One flow, one mediator, one closure.

| Days | What |
|---|---|
| 1–4 | choose the flow (money or PII), draw all 7 paths from §6, fix what is included in Z |
| 5–10 | policy P in declarative form + SMT check (level A: contradictions, implicit allows, cycles) |
| 11–18 | mediator M: refines P; capabilities instead of checks; the mediator is the only path to the resource |
| 19–24 | close the bypasses from §6, apply egress deny-all, short-lived credentials |
| 25–27 | proof of B (mediator contracts; Verus/Dafny/SPARK depending on the class) |
| 28–30 | red team: 3 bypass attempts; publication of the proven + measured + negative scope |

**Failure criterion:** the red team found at least one path bypassing the mediator **within the declared Z**, or policy P is not checked automatically (which means level A does not work), or the mediator is not proven and cannot be proven within budget.

---

## 9. What this changes in what has already been decided

| Decision | Change |
|---|---|
| Three classes of oracles (SQLi/BOLA/traversal) | **are not cancelled but change role**: they are not the commodity but **diagnostics** — proof that the current flow is not yet mediated. They sell the migration |
| Coverage attestation | becomes a **guarantee per flow** — a positive claim instead of "we found nothing" |
| K6 (`PROVEN` starvation) | stops being fatal: the deliverable does not depend on the number of findings |
| R5 as "R&D for aviation" | becomes **a commodity for any service with money/PII in a flow** |
| I3 (negative scope) | is strengthened: closure Z is a mandatory, contractual, public artifact |
| The fatal risk | shifts from "too few findings" to **"being unable to declare the closure honestly"** — that is, to discipline rather than to technology |

---

## 10. Conclusion

The idea is right as a **change of the unit of work** and as an **answer to the main death mechanism** of the product. It is wrong in exactly one word — "unbreakable". Replace it with "mediator + proven policy + declared closure", and you get:

- a positive deliverable (solves the empty report);
- bounded liability (solves the legal risk);
- a commodity for a broad market, not only for aviation;
- and an honest boundary: **what is proven, what is measured, what is outside the guarantee** — the same three columns that we already require of any verdict.

There is exactly one weak spot and it is not technical: **declaring the closure honestly**. Everything else is engineering that has already been done (seL4, Zelkova, IronFleet) and that LLMs are now, for the first time, making available at a price.
