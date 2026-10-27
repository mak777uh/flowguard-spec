#!/usr/bin/env python3
"""fg_perimeter — weighted residual risk of what sits outside the core.

Counts are not risk: fourteen paths outside the core may be one payment endpoint and thirteen
read-only caches, or the other way round. Round-7 review 4 said the weights must come from an agreed
classification, never from a model's judgement. This tool reads `policies/risk-classes.json`, applies
ordered rules, and publishes:

    outside_weighted_risk   sum(weights of outside paths) / sum(weights of all paths)
    unclassified_paths      paths that matched no rule - counted, never weighted as zero
    policy_digest           so a verdict can be tied to the exact weights it used

A path that matches no rule keeps weight `unclassified` (3), which is deliberately not zero.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = ROOT / "policies" / "risk-classes.json"


def load_policy(path=None):
    p = Path(path) if path else DEFAULT_POLICY
    raw = p.read_bytes()
    return json.loads(raw.decode("utf-8")), "sha256:" + hashlib.sha256(raw).hexdigest()


def classify(path: dict, policy: dict) -> str:
    for rule in policy.get("rules", []):
        field = path.get(rule.get("field", "entry"), "") or ""
        if re.search(rule["regex"], str(field)):
            return rule["class"]
    return "unclassified"


def compute(manifest: dict, policy_path=None, control_point=None):
    policy, digest = load_policy(policy_path)
    weights = {name: cfg["weight"] for name, cfg in policy["classes"].items()}
    cp = control_point or (manifest.get("claim") or {}).get("declared_control_point")

    classes = {}
    total_w = 0.0
    outside_w = 0.0
    unclassified = 0
    for p in manifest.get("paths", []):
        cls = classify(p, policy)
        classes[cls] = classes.get(cls, 0) + 1
        w = weights.get(cls, weights.get("unclassified", 1))
        total_w += w
        if cls == "unclassified":
            unclassified += 1
        attributed = (p.get("attribution") or {}).get("to")
        in_core = bool(cp) and (attributed == cp or p.get("control_point") == cp)
        if not in_core:
            outside_w += w

    return {
        "outside_weighted_risk": round(outside_w / total_w, 3) if total_w else 0.0,
        "weights_total": round(total_w, 1),
        "weights_outside": round(outside_w, 1),
        "classes": classes,
        "unclassified_paths": unclassified,
        "policy_id": policy.get("policy_id"),
        "policy_digest": digest,
        "max_outside_weighted_risk": policy.get("thresholds", {}).get("max_outside_weighted_risk"),
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--policy")
    ap.add_argument("--control-point")
    a = ap.parse_args()
    manifest = json.loads(Path(a.inventory).read_text(encoding="utf-8"))
    out = compute(manifest, a.policy, a.control_point)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
