# routes-json — HTTP entrypoints that reach a target table

A route manifest is what a framework, a gateway or an OpenAPI export can produce **without running the service**.
This source turns it into inventory paths.

## Covers

- HTTP endpoints declared in the manifest
- which of them write the target table, as declared by the handler's `writes` list
- which of them call the declared control point, as declared by the handler's `calls` list

## Blind spots (declared)

- routes that exist in the deployed service but not in the manifest (spec drift)
- dynamically registered routes, gateways that rewrite paths, websocket handlers
- handlers whose `writes` list is incomplete or wrong — the manifest is trusted, not verified
- authorisation: the manifest says nothing about who may call a route
- the real call chain inside a handler beyond the declared `calls` list

## The rule that makes it usable

A manifest is **per-target** (`ADR-0012`). An endpoint that writes a different table is not a path to this one, so
it is filtered out rather than added to the denominator. Without that rule, an endpoint count would inflate coverage
of a table it never touches.

## Transitive attribution happens in the merger, not here

`/transfer/batch` calls `transfer_batch`, which reaches the control point two hops away. This source cannot see
that — it has one list of calls, not a graph. The merger resolves it, because only there are both the route's calls
and the call-graph's reachability visible at once (`E-M20`).

## Run

```bash
python fg_enum_routes.py --manifest fixtures/http-routes/routes.json \
    --schema bank --table accounts --control transfer --out routes.json
```

## Landing test

`fixtures/http-routes/routes.json` has seven endpoints: two through the control point (one direct, one transitive),
two writing the table directly, two read-only, one writing a different table. Expected: four paths, two in the
core, zero false inclusions. Recorded in `lab/experiments/E-M20-routes-source.md`.
