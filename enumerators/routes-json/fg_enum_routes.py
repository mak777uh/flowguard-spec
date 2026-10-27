#!/usr/bin/env python3
"""fg-enum-routes — HTTP entrypoints that reach a target table, from a route manifest.

A route manifest is what a framework, a gateway or an OpenAPI export can produce without running the
service. It is a catalogue source: it enumerates, so it may form a coverage denominator - but only
for paths that actually reach the target (ADR-0012). A manifest is per-target; an endpoint that
writes a different table is not a path to this one.

    python fg_enum_routes.py --manifest fixtures/http-routes/routes.json \
        --schema bank --table accounts --control transfer --out routes.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

COVERS = [
    "HTTP endpoints declared in the route manifest",
    "which of them write the target table, as declared by the handler's `writes` list",
    "which of them call the declared control point, as declared by the handler's `calls` list",
]
BLIND_SPOTS = [
    "routes that exist in the deployed service but not in the manifest (spec drift)",
    "dynamically registered routes, gateways that rewrite paths, websocket handlers",
    "handlers whose `writes` list is incomplete or wrong - the manifest is trusted, not verified",
    "authorisation: the manifest says nothing about who may call a route",
    "the actual call chain inside a handler beyond the declared `calls` list",
]


def path_id(kind: str, entry: str, control: str) -> str:
    return "wp_" + sha256(f"{kind}|{entry}|{control}".encode()).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--control", required=True, help="declared control point function name")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-lock", default="")
    a = ap.parse_args()

    doc = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    routes = doc.get("routes")
    if routes is None:  # tolerate a bare OpenAPI `paths` object
        routes = []
        for path, ops in (doc.get("paths") or {}).items():
            for method in ops:
                routes.append({"method": method.upper(), "path": path,
                               "handler": "", "writes": [], "calls": []})

    paths, attributions = [], []
    for r in routes:
        writes = {w.lower() for w in (r.get("writes") or [])}
        if a.table.lower() not in writes:
            continue  # not a path to this target
        entry = f"http:{r.get('method', '?')} {r.get('path', '?')}"
        calls = {str(c) for c in (r.get("calls") or [])}
        inside = a.control in calls
        cp_entry = f"function:{a.schema}.{a.control}"
        paths.append({
            "path_id": path_id("http_entry", entry, cp_entry if inside else ""),
            "kind": "http_entry",
            "entry": entry,
            "control_point": cp_entry if inside else "",
            "detail": f"handler {r.get('handler') or '?'} writes {a.table}"
                      + (" via the control point" if inside else " directly"),
            "confidence": "catalog",
            "calls": sorted(calls),
        })
        if inside:
            attributions.append({
                "entry": entry,
                "attributed_to": cp_entry,
                "method": "direct",
                "confidence": "catalog",
            })

    source = {
        "source_id": "routes-json-v0.1",
        "kind": "routes",
        "tool": {"name": "fg-enum-routes", "version": "0.1.0",
                 "digest": "sha256:" + sha256(Path(__file__).read_bytes()).hexdigest()},
        "run": {"target_lock": a.target_lock or doc.get("target_lock", ""),
                "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "environment": f"route manifest {Path(a.manifest).name}",
                "scope": f"{a.schema}.{a.table}"},
        "covers": COVERS,
        "blind_spots": BLIND_SPOTS,
        "paths": paths,
        "control_points": [],
        "attributions": attributions,
        "completeness_claim": "exhaustive_within_covers",
    }
    Path(a.out).write_text(json.dumps(source, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"routes: {len(paths)} endpoint(s) reach {a.schema}.{a.table}, "
          f"{len(attributions)} through the control point -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
