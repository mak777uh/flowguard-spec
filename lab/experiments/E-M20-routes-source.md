---
id: E-M20
hypothesis: H-M20
status: completed
base_commit: "uncommitted tree"
started: "2026-10-27T23:44:00+03:00"
finished: "2026-10-27T23:58:00+03:00"
environment: "Windows, CPython 3.13.11; PostgreSQL 17.2 for the catalogue leg"
command: "python enumerators/routes-json/fg_enum_routes.py --manifest fixtures/http-routes/routes.json --schema bank --table accounts --control transfer && python tools/merge_inventory.py ..."
threshold: "Pre-registered: (a) of seven endpoints, exactly the four that write bank.accounts are kept and the three that do not are excluded, (b) the two endpoints that reach the control point are marked inside the core - one directly, one transitively through a declared call, (c) the two endpoints that write the table directly stay outside, with zero false inclusions, (d) adding routes does not reduce the catalogue path count."
result: "4 of 7 endpoints kept, 3 excluded; 2 in the core (http:POST /transfer direct, http:POST /transfer/batch transitive via merge:declared_calls + pgcalls); 2 outside (admin/credit, accounts/{id}); 0 false inclusions; manifest 19 paths from 3 sources versus 16 from 2."
verdict: supports
---

# E-M20 — entrypoints as inventory, and the transitive attribution nobody owned

## What was built

`enumerators/routes-json` reads a route manifest — the artifact a framework, a gateway or an OpenAPI export can
produce without running the service — and emits `http_entry` paths for the endpoints that **write the target
table**.

The filter is the point. A manifest is per-target (`ADR-0012`): an endpoint writing `notes` is not a path to
`accounts`. Without that rule, an endpoint count would inflate coverage of a table it never touches.

## Run

```
routes: 4 endpoint(s) reach bank.accounts, 1 through the control point
manifest: 19 paths from 3 sources
in core:
  caller  function:bank.transfer_batch        transitive
  caller  function:bank.transfer_via_api      direct
  http_entry  http:POST /transfer             direct
  http_entry  http:POST /transfer/batch       transitive  sources: merge:declared_calls, pgcalls
outside: http:POST /admin/credit, http:PUT /accounts/{id}
```

| expectation | result |
|---|---|
| 4 kept, 3 excluded | **4 / 3** |
| 2 in the core (direct + transitive) | **2 / 2** |
| 0 false inclusions | **0** |
| catalogue paths not reduced | 16 → 19 (routes added, nothing lost) |

## Two defects found while measuring

**1. The merger dropped `calls`.** The path record kept only five fields, so the declared call list vanished on the
way into the manifest and transitive resolution was silently impossible. The field is now preserved, with a comment
saying why it exists.

**2. The resolution indexed the wrong name.** The lookup map was keyed by the control point's name (`transfer`) while
the question asked is about the called function (`transfer_batch`), so every transitive lookup missed. Fixed by
indexing both the path's own name and the target's.

Neither defect would have appeared without a case that actually needs a two-hop route. A one-hop fixture would have
passed and hidden both.

## What this does not do

- It does not verify that a handler's `writes` list is true. The manifest is trusted, and a wrong list is a wrong
  inventory — `NC-03` in every claim covers interpretation, and this source is built on interpretation.
- It does not see routes absent from the manifest. Spec drift is the most likely real-world failure and is declared.
- It does not resolve calls beyond one declared hop plus the call graph's reachability; a handler calling a service
  calling a function is invisible.

## Consequence

`routes` now qualifies as a coverage denominator kind under `ADR-0011` — built, then measured — and returns to
`DENOMINATOR_KINDS` with a measurement behind it rather than an intention.

## Log

re-run on 2026-10-28 with the output captured, because the original run was a command sequence
whose transcript was the only record: `lab/logs/e-m20-2026-10-28.log` — sha256 `c57af71d6f476a5b885338e7508c2f59804be68433724e31045f2afd64c10a91`.
