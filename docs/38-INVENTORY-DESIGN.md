# 38 — Path inventory: a composable set of sources, not one analyser

The round-7 verdict was that the artifact is capped without an independent inventory of paths. This is the design of
that inventory: how we produce it, how a customer plugs theirs in, how new discovery methods are added later without
changing the format, and how it stays honest about what it cannot see.

The core idea is the same one used for the six runtime ports, applied to discovery:

> An inventory is not a tool. It is a **merge of sources**, each declaring what it covers and, mandatorily, what it
> is blind to.

---

## 1. The port

```
Enumerator  →  SourceRecord[]  →  merge()  →  InventoryManifest
```

Anything that can produce `SourceRecord`s is a valid enumerator. Our own implementations and a customer's tooling
are indistinguishable to the merger, which is the point: we can start with two sources and add five later without
touching the verifier.

Sources we expect, in rising cost:

| kind | what it sees | typical blind spot |
|---|---|---|
| `routes` | HTTP/RPC entrypoints from framework configuration | dynamically registered routes; background workers |
| `grants` | who may write which table or call which function | application-level checks above the database |
| `static` | call graph and state mutations from code | reflection, dynamic dispatch, generated code |
| `runtime` | paths actually exercised, via eBPF or DB audit | paths not taken during the trace window |
| `agent` | semantic reading of code by an AI agent | misreading; inventing paths that do not exist |
| `manual` | a named person's audit of a subsystem | whatever that person did not look at |

## 2. `SourceRecord` — what a source must declare

```json
{
  "source_id": "grants-pg-v1",
  "kind": "grants",
  "tool": { "name": "fg-enum-grants", "version": "0.1.0", "digest": "sha256:…" },
  "run": { "target_lock": "sha256:…", "started": "…", "finished": "…", "environment": "…" },
  "covers": ["direct table writes", "privilege grants"],
  "blind_spots": ["application-level access control", "writes through a SECURITY DEFINER function"],
  "paths": [
    {
      "path_id": "wp_9f2c…",
      "kind": "state_mutation",
      "entry": "table:accounts.update",
      "control_point": "procedure:transfer()",
      "witness": ["evidence:pg_trigger_log", "evidence:grant_inventory"]
    }
  ],
  "completeness_claim": "exhaustive_within_covers"
}
```

Three fields carry the discipline:

- **`blind_spots` must be non-empty.** A source claiming universal vision is refused by the merger. "We can see
  everything" is a `judgment` claim with an artifact, not a blank list.
- **`covers` bounds every completeness word.** `exhaustive_within_covers` is the only completeness value the format
  accepts, and it is always relative.
- **`path_id` is a content hash** of `kind + entry + control_point`, so two sources that find the same path produce
  the same id, and a source that finds it differently produces a conflict instead of a duplicate.

## 3. Merge rules

1. **Union by `path_id`.** Duplicates collapse; **provenance accumulates** — a path found by two independent methods
   is marked with both.
2. **Conflict is an error, not a preference.** Same `path_id`, different `control_point` or different `witness`
   ⇒ `PATH_CONFLICT` in the manifest. The verifier refuses to compute coverage over conflicting inventories until it
   is resolved. Silently preferring one source is how two sources become one source again.
3. **Coverage denominator is the union**, never a single source's list.
4. **Corroboration is published per path class**: how many *independent* sources found it. `agent` + `agent` is one
   source, not two.
5. **Nothing is ever deleted by the merger.** A path a source reported last run and does not report now stays in the
   manifest as `vanished`, with the source that dropped it. That is how inventory shrinkage becomes visible rather
   than convenient.

## 4. What the manifest tells the verifier

```json
{
  "inventory": {
    "sources": [ { "source_id": "…", "kind": "…", "covers": [], "blind_spots": [] } ],
    "paths_total": 41,
    "by_class": { "money": 7, "personal_data": 4, "files": 9, "other": 21 },
    "corroborated_by_2plus": 12,
    "conflicts": [],
    "vanished_since_previous": 3,
    "unclassified": 5,
    "independent_of_agent": true
  }
}
```

`independent_of_agent: true` requires at least one source whose `kind` is not `agent`. That single boolean is what
lifts the round-7 ceiling from `CONSISTENT_DECLARED` to `SCOPED_ASSURANCE` — and it cannot be set by the analysing
agent, because the merger writes it from the source kinds it actually received.

## 5. Adding a new method later — the extensibility the owner asked for

Adding an enumerator costs three things and changes no existing file:

1. a **template** in `enumerators/<kind>/README.md` — what it sees, what it is blind to, how to run it;
2. an **adapter** that emits `SourceRecord` — any language, any runtime;
3. a **landing test** — a fixture where this method must find a known path and must report its known miss.

The manifest schema does not change when a method is added. That is the test of whether the design is extensible:
a new method must not require a new format version.

## 6. What we build first, and what we do not

**Build now** (small, and it is the gateway to every real verdict):

- `fg-enum-grants` — for Postgres: privileges, `SECURITY DEFINER` functions, triggers. This is cheap, reliable, and
  it is exactly the class where AI-generated attacks land first.
- `fg-enum-routes` — entrypoints from a framework's own configuration, not from parsing code.

**Then** `static` via an existing call-graph tool; **later** `runtime`, which needs a target we can run.

**We do not build:** our own code analyser from scratch (the `agent` kind covers it), and a universal graph database
of a customer's system (we consume sources, we do not become their CMDB).

## 7. Honest limits of this design

- **Two sources with the same blind spot are still one source.** `independent_of_agent` is a weak guarantee: a
  `routes` enumerator and a `static` analyser can both miss a background worker that writes money. Corroboration
  counts what was found twice, never what was missed twice.
- **The union can grow because the world changed or because discovery improved**, and the format cannot tell the
  difference. That is why the perimeter block gates upgrades and why `vanished` is kept.
- **The manifest is not a proof of completeness**, and no arrangement of sources makes it one. It is a statement of
  what was looked for, by whom, and with what declared blindness.
