#!/usr/bin/env python3
"""merge_inventory — combine SourceRecords into one InventoryManifest (ADR-0007).

Rules, all of them load-bearing:

  * union by path_id; provenance accumulates
  * a conflicting control point for the same path is an ERROR, never a preference
  * the denominator is the union, never one source
  * nothing is deleted: a path that disappears becomes `vanished`
  * `independent_of_agent` is computed from the source kinds received, not asserted

    python tools/merge_inventory.py --out manifest.json sources/source-*.json [--previous prev.json]
"""
import argparse
import glob
import json
import sys
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path


def load(paths):
    sources = []
    for pattern in paths:
        for f in sorted(glob.glob(pattern)):
            sources.append(json.loads(Path(f).read_text(encoding="utf-8")))
    return sources


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--previous")
    a = ap.parse_args()

    sources = load(a.sources)
    if not sources:
        raise SystemExit("no source records")

    for s in sources:
        if not s.get("blind_spots"):
            raise SystemExit(f"refused: source {s.get('source_id')} declares no blind spots")

    merged, conflicts = {}, []
    for s in sources:
        for p in s.get("paths", []):
            pid = p["path_id"]
            if pid in merged:
                prev = merged[pid]
                if prev["control_point"] != p["control_point"]:
                    conflicts.append({
                        "path_id": pid,
                        "entry": p["entry"],
                        "control_points": sorted({prev["control_point"], p["control_point"]}),
                        "sources": prev["found_by"] + [s["source_id"]],
                    })
                prev["found_by"] = sorted(set(prev["found_by"] + [s["source_id"]]))
                prev["kinds"] = sorted(set(prev["kinds"] + [s["kind"]]))
            else:
                merged[pid] = {
                    "path_id": pid,
                    "entry": p["entry"],
                    "kind": p["kind"],
                    "control_point": p["control_point"],
                    "confidence": p["confidence"],
                    "found_by": [s["source_id"]],
                    "kinds": [s["kind"]],
                }

    # Attribution is contributed separately from paths: a source may say "this writer goes through the
    # control point" without claiming to have discovered the writer. Applied by entry.
    attributions = {}
    for s in sources:
        for at in s.get("attributions", []):
            attributions.setdefault(at["entry"], []).append({
                "source": s["source_id"], "to": at["attributed_to"],
                "method": at.get("method", ""), "confidence": at.get("confidence", ""),
            })
    attributed = 0
    for p_ in merged.values():
        hits = [a for a in attributions.get(p_["entry"], []) if a["to"]]
        if hits:
            p_["attribution"] = {
                "to": hits[0]["to"],
                "method": min(h["method"] for h in hits),
                "confidence": min(h["confidence"] for h in hits),
                "sources": [h["source"] for h in hits],
            }
            attributed += 1

    # A caller that reaches the control point but never writes the table itself is invisible to a
    # writer enumerator. It is still a path into the flow, and it is inside the core. Without this,
    # coverage would count only writers and every legitimate caller would be missing.
    for entry, hits in attributions.items():
        active = [h for h in hits if h["to"]]
        if not active or any(p_["entry"] == entry for p_ in merged.values()):
            continue
        pid = "wp_" + sha256(("caller|" + entry).encode()).hexdigest()[:16]
        merged[pid] = {
            "path_id": pid, "entry": entry, "kind": "caller",
            "control_point": active[0]["to"], "confidence": active[0]["confidence"],
            "found_by": [h["source"] for h in active], "kinds": ["static"],
            "attribution": {"to": active[0]["to"], "method": active[0]["method"],
                            "confidence": active[0]["confidence"],
                            "sources": [h["source"] for h in active]},
        }
        attributed += 1

    previous = {}
    if a.previous and Path(a.previous).exists():
        prev_doc = json.loads(Path(a.previous).read_text(encoding="utf-8"))
        previous = {p["path_id"]: p for p in prev_doc.get("paths", [])}

    vanished = [pid for pid in previous if pid not in merged]
    for pid in vanished:
        entry = dict(previous[pid])
        entry["vanished"] = True
        merged[pid] = entry

    # The perimeter delta is computed here, not taken on trust from the caller: ADR-0006 requires
    # an upgrade to be blocked while the perimeter grows, and a field nobody computes is a claim
    # about a number that does not exist (E-M19).
    new_ids = [pid for pid in merged if pid not in previous]
    delta = {
        "new_paths": len(new_ids),
        "vanished_paths": len(vanished),
        "net_change": len(new_ids) - len(vanished),
        "published": bool(previous),
    }
    # Growth counts NEW paths, and a path that vanished does not cancel one that appeared: a
    # replacement is still a change of shape, and the reader has to see it.
    perimeter_growth = bool(previous) and len(new_ids) > 0

    # target_lock is carried by the manifest, not left in the SourceRecords: without it a verdict
    # cannot be bound to a commit, and the verifier refuses (found by the E-M12 integration run).
    locks = {s.get("run", {}).get("target_lock") for s in sources if s.get("run", {}).get("target_lock")}
    target_lock = locks.pop() if len(locks) == 1 else None
    target_lock_conflict = sorted(locks) if len(locks) > 1 else []

    kinds = {s["kind"] for s in sources}
    independent_of_agent = bool(kinds - {"agent"})
    non_agent_sources = [s["source_id"] for s in sources if s["kind"] != "agent"]

    manifest = {
        "manifest_version": "inventory/0.1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [
            {
                "source_id": s["source_id"], "kind": s["kind"],
                "covers": s.get("covers", []), "blind_spots": s.get("blind_spots", []),
                "completeness_claim": s.get("completeness_claim"),
            } for s in sources
        ],
        "target_lock": target_lock,
        "target_lock_conflict": target_lock_conflict,
        "independent_of_agent": independent_of_agent,
        "non_agent_sources": non_agent_sources,
        "paths_total": len(merged),
        "in_core_attributed": attributed,
        "corroborated_by_2plus": sum(1 for p in merged.values() if len(p.get("kinds", [])) > 1),
        "conflicts": conflicts,
        "vanished_since_previous": vanished,
        "delta_since_previous": delta,
        "perimeter_growth": perimeter_growth,
        "paths": sorted(merged.values(), key=lambda p: (p["kind"], p["entry"])),
    }
    Path(a.out).write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"manifest: {manifest['paths_total']} paths from {len(sources)} source(s)")
    print(f"independent_of_agent: {independent_of_agent} ({', '.join(non_agent_sources) or 'none'})")
    if conflicts:
        print(f"CONFLICTS: {len(conflicts)} — coverage cannot be computed until resolved")
    if vanished:
        print(f"vanished since previous: {len(vanished)}")
    if previous:
        print("delta: +{} new, -{} vanished, net {:+d}; perimeter_growth={}".format(
            delta["new_paths"], delta["vanished_paths"], delta["net_change"], perimeter_growth))
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
