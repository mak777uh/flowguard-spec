# The stack question, answered by what the artifact has to be

Advice from the chat, verbatim in substance: Python backend + React for the web artifacts; **shadcn + TanStack** as
the base, because models are trained on it and integrate it easily; NestJS if the backend is Node (used in the US and
Europe even under high load); hono for small things. The reasoning behind it is explicit and correct on its own
terms: **pick what modern LLMs are best trained on, and name the high-reliability libraries in the prompt.**

That is an argument about **how fast an agent builds a UI**. Our product optimises something else, and the
difference decides the stack.

## What our artifact has to satisfy

| requirement | consequence |
|---|---|
| a stranger reads it offline, without our service | no server, no build step, no network |
| re-generating from the same bundle gives the same bytes | deterministic, stdlib-only generator |
| it must not itself be a supply chain | no npm tree, no CDN font, no JS runtime |
| the verdict must come from the gate, not from the viewer | the page calls `fg_bundle.py verify` and prints what it says |
| a reader must be able to point at one path | the page leads with paths, not with the verdict ([the usefulness survey](43-POU-SURVEY.md), insight C) |

React + shadcn + TanStack is excellent for the first two of those only if the consumer is willing to build — and a
consumer who has to run `pnpm i` is not a stranger reading an artifact, he is a developer with our toolchain.

## What was built instead

`tools/fg_report_html.py` — one self-contained HTML file from a bundle:

```
python tools/fg_report_html.py --bundle fixtures/sample-bundle --out report.html
  wrote report.html (2598 bytes)
  external links: 0   <script>: 0
```

It carries: the address and format, the verdict **as the gate prints it**, the path table with per-path attribution
(so a reader sees `none` against the bypass), the claim with its `not_claimed` list verbatim, the refusals, and a
closing block naming what the page cannot tell you (`NC-01`, `NC-02`, authority).

## Where the chat's advice does apply, and what would trigger it

- **A hosted viewer** — if a consumer wants to read bundles they did not generate, with history and search. Then
  shadcn + TanStack is the right choice precisely because an agent can build it quickly, and hono or Nest sits behind
  it. The trigger is a named consumer asking for it, which is `Q9`.
- **An intake form** — if claimants submit rather than send files. Same trigger.
- **Anything internal** (a bench dashboard) — no trigger needed, but also no product value; that is the 15% and 5%
  of the usefulness rubric where we are already strong ([the usefulness survey](43-POU-SURVEY.md)).

## The rule this settles

> The artifact's viewer must be as trustworthy as the artifact. A React app is a second supply chain, and a page
> that needs a build to read a claim about provenance is a page that asks for exactly the trust the claim was
> supposed to remove.

## What is not claimed

- The page is not pretty, and a generated report is not a product surface. It is the smallest thing that lets a
  stranger read the artifact offline.
- It does not verify anything itself: it shells out to the gate and prints the answer, so a viewer bug cannot
  manufacture a verdict.
- The stack advice is not wrong. It answers a different question than the one this repository is asking.
