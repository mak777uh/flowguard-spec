#!/usr/bin/env python3
"""fg_verify — does the claimed level follow from the inventory and the analysis report?

This is the consistency core of the product (ADR-0005). It does not prove anything about a system.
It answers one question and refuses to answer a stronger one:

    Given an independent inventory of paths, an analysis report, and a claim,
    is the claimed level supported — and if not, which obligation is missing?

Exit codes: 0 the verdict is what was claimed or stronger; 1 the claim was lowered; 2 refusal
(the artifact cannot be evaluated at all).

    python tools/fg_verify.py --claim c.json --inventory m.json [--report r.json] [--policy p.json]
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

LEVELS = ["CONSISTENT_DECLARED", "SCOPED_ASSURANCE", "PROVEN"]
ORDER = {lvl: i for i, lvl in enumerate(LEVELS)}

DEFAULT_POLICY = {
    "policy_id": "default",
    "max_excluded": 2,
    "full_coverage_for_proven": 1.0,
    "assurance_threshold": 0.75,
    "require_independent_inventory_for": ["PROVEN", "SCOPED_ASSURANCE"],
}


_NOT_CLAIMED_CACHE = {}

def load_not_claimed_registry() -> dict:
    """Read docs/NOT-CLAIMED.md: the code table and the required codes per level.

    Single source of truth: the document. If it is missing, every claim with not_claimed is
    refused, because a vocabulary that cannot be read is not a vocabulary.
    """
    if _NOT_CLAIMED_CACHE:
        return _NOT_CLAIMED_CACHE
    doc = Path(__file__).resolve().parent.parent / "docs" / "NOT-CLAIMED.md"
    codes, required, in_required = set(), {}, False
    if doc.exists():
        for line in doc.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("## Required by level"):
                in_required = True
                continue
            if in_required and line.startswith("|") and "`" in line:
                cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2 and cells[0] in LEVELS:
                    required[cells[0]] = [x.strip() for x in cells[1].split(",") if x.strip()]
            m = re.match(r"^\|\s*\*\*(NC-\d{2})\*\*\s*\|", line)
            if m:
                codes.add(m.group(1))
    _NOT_CLAIMED_CACHE.update({"codes": codes, "required": required})
    return _NOT_CLAIMED_CACHE

_PERIMETER = {}

def compute_perimeter(inventory, control_point=None, policy_path=None) -> dict:
    """Weighted perimeter from tools/fg_perimeter.py. Kept optional so a missing policy file
    degrades to counts rather than crashing a verdict."""
    if "fn" not in _PERIMETER:
        try:
            spec = importlib.util.spec_from_file_location(
                "fgp", Path(__file__).resolve().parent / "fg_perimeter.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _PERIMETER["fn"] = mod.compute
        except Exception:  # noqa: BLE001
            _PERIMETER["fn"] = None
    fn = _PERIMETER["fn"]
    if fn is None:
        return {"outside_weighted_risk": None, "note": "risk policy unavailable"}
    try:
        return fn(inventory, policy_path, control_point)
    except Exception as e:  # noqa: BLE001
        return {"outside_weighted_risk": None, "note": f"risk policy failed: {e}"}

def load(p, what):
    if not p:
        return None
    path = Path(p)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", required=True)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--report")
    ap.add_argument("--policy")
    ap.add_argument("--attempts", type=int, default=1)
    ap.add_argument("--max-attempts", type=int, default=3)
    a = ap.parse_args()

    claim = load(a.claim, "claim") or {}
    inventory = load(a.inventory, "inventory") or {}
    report = load(a.report, "report")
    policy = load(a.policy, "policy") or DEFAULT_POLICY

    errors = []

    def err(code, subject, expected, observed, next_action, retryable=True):
        errors.append({
            "code": code, "subject": subject, "expected": expected,
            "observed": observed, "next_action": next_action, "retryable": retryable,
        })

    # ---- 0. the artifact must be evaluable at all -------------------------
    if not claim:
        err("MISSING_EVIDENCE", "claim", "a claim document", "absent", "provide the claim", False)
        return emit("INVALID", None, errors, {}, 2)
    if not inventory.get("paths"):
        err("MISSING_EVIDENCE", "inventory", "at least one source with paths", "absent",
            "run an enumerator and merge its SourceRecord", False)
        return emit("INVALID", None, errors, {}, 2)

    if a.attempts > a.max_attempts:
        errors = [{"code": "RETRY_BUDGET_EXCEEDED", "subject": "attempts",
                   "expected": f"<= {a.max_attempts}", "observed": str(a.attempts),
                   "next_action": "escalate to a human", "retryable": False}]
        return emit("INVALID", None, errors, {}, 2)

    # ---- 1. conflicting inventories cannot be used -----------------------
    if inventory.get("conflicts"):
        for c in inventory["conflicts"]:
            err("REPORT_BUNDLE_INCONSISTENT", c.get("entry", "?"),
                "one control point per path",
                "conflicting: " + ", ".join(c.get("control_points", [])),
                "resolve the conflict between sources; coverage cannot be computed", False)

    # ---- 1b. the policy itself must be trusted ---------------------------
    if policy.get("trusted") is False:
        err("POLICY_UNTRUSTED", "policy",
            "a policy whose origin is verifiable", "policy declares itself untrusted",
            "obtain a trusted policy; nothing can be assessed against it", False)

    # ---- 2. target binding ----------------------------------------------
    want = (claim.get("target_lock") or {}).get("commit")
    got = inventory.get("target_lock") or (inventory.get("paths") and None)
    if want and got and want != got:
        err("TARGET_MISMATCH", "target_lock", f"commit {want}", f"commit {got}",
            "re-run the analysis on the claimed target", False)
    if want and not got:
        err("MISSING_EVIDENCE", "target_lock", "inventory bound to a commit",
            "inventory carries no target_lock", "record the target in the SourceRecord", True)

    # ---- 3. coverage, recomputed, never trusted -------------------------
    paths = inventory["paths"]
    control = claim.get("declared_control_point")
    # A path is inside the core when an attribution source says it passes through the declared
    # control point. Falling back to control_point keeps single-source bundles working.
    in_core = [
        p for p in paths
        if control and (
            (p.get("attribution") or {}).get("to") == control
            or p.get("control_point") == control
        )
    ]
    outside = [p for p in paths if p not in in_core]
    coverage = len(in_core) / len(paths) if paths else 0.0

    claimed = claim.get("claimed_coverage")
    if isinstance(claimed, (int, float)) and claimed > coverage + 1e-9:
        err("CLAIM_EXCEEDS_EVIDENCE", "coverage",
            f"<= {coverage:.3f} (recomputed from the inventory)", f"{claimed:.3f} (claimed)",
            "lower the claim to the recomputed coverage or supply evidence for the missing paths")

    # ---- 4. exclusions: counted, and bound to real paths -----------------
    # An exclusion is a claim that a known path is out of scope. It must therefore (a) name a path
    # that exists in the inventory, (b) not name a path that is inside the core, and (c) carry a
    # reason. Without these three, "excluded" is a free-text list that silently narrows the scope -
    # the T3 vacuum that round 7 warned about.
    excluded_raw = claim.get("excluded") or []
    ceiling = policy.get("max_excluded", 2)
    known_ids = {p.get("path_id") for p in paths}
    core_ids = {p.get("path_id") for p in in_core}
    excluded = []
    for item in excluded_raw:
        if isinstance(item, dict):
            pid, reason = item.get("path_id"), (item.get("reason") or "").strip()
        else:
            pid, reason = item, ""
        excluded.append(pid)
        if pid not in known_ids:
            err("UNKNOWN_OR_UNBOUND_PATH", f"excluded:{pid}",
                "a path_id present in the inventory", "not in the obligation manifest",
                "name an existing path or remove the exclusion", False)
        elif pid in core_ids:
            err("REPORT_BUNDLE_INCONSISTENT", f"excluded:{pid}",
                "an exclusion outside the core", "the path is inside the declared core",
                "a path cannot be both covered and excluded", False)
        if not reason:
            err("MISSING_EVIDENCE", f"excluded:{pid}",
                "a reason for the exclusion", "no reason recorded",
                "record why the path is out of scope", True)
    if len(excluded) > ceiling:
        err("POLICY_CEILING_EXCEEDED", "excluded",
            f"<= {ceiling}", f"{len(excluded)}",
            "reduce the exclusions or change the declared scope; this requires a human decision", False)

    # ---- 5. not_claimed must use the vocabulary, and must cover the level ---
    # Round 7: a free-text not_claimed is where boilerplate goes. Codes from docs/NOT-CLAIMED.md
    # are checkable: unknown code refused, required codes for the declared level refused if absent.
    registry = load_not_claimed_registry()
    declared = claim.get("not_claimed") or []
    if not isinstance(declared, list):
        err("REPORT_BUNDLE_INCONSISTENT", "not_claimed", "a list of NC codes", str(type(declared)), False)
        declared = []
    unknown = [c for c in declared if c not in registry["codes"]]
    if unknown:
        err("REPORT_BUNDLE_INCONSISTENT", "not_claimed",
            "codes from docs/NOT-CLAIMED.md",
            "unknown: " + ", ".join(str(u) for u in unknown),
            "use the vocabulary; free text is not checkable", False)
    required = registry["required"].get(claim.get("declared_level", "CONSISTENT_DECLARED"), [])
    missing = [c for c in required if c not in declared]
    if missing:
        err("MISSING_EVIDENCE", "not_claimed",
            f"codes required by level {claim.get('declared_level')}: {', '.join(required)}",
            "missing: " + ", ".join(missing),
            "state what the attestation does not assert, using the vocabulary", True)

    # ---- 6. independence ------------------------------------------------
    independent = bool(inventory.get("independent_of_agent"))
    if not independent:
        err("E_NO_INDEPENDENT_CLOSURE", "inventory",
            "at least one source that is not the analysing agent",
            "sources: " + ", ".join(s.get("kind", "?") for s in inventory.get("sources", [])),
            "supply an inventory from an enumerator the agent does not control, or accept the capped verdict",
            False)

    # ---- 6b. weighted perimeter: counts are not risk --------------------
    # Round-7 review 4: fourteen paths outside the core may be one payment endpoint and thirteen
    # caches, or the reverse. The weights come from policies/risk-classes.json, never from a model.
    risk = compute_perimeter(inventory, control_point=control)
    # Two ceilings can exist: one in the risk-weights file, one in the claim's policy. The stricter
    # wins, so a lenient claim policy cannot loosen the classification's own limit.
    ceilings = [x for x in (risk.get("max_outside_weighted_risk"),
                            policy.get("max_outside_weighted_risk")) if x is not None]
    max_risk = min(ceilings) if ceilings else None
    risk_exceeded = bool(max_risk is not None and risk["outside_weighted_risk"] > max_risk)
    # The ceiling blocks an UPGRADE, not the existence of a verdict: CONSISTENT_DECLARED promises
    # nothing about what is outside, so it cannot be refused for having a large outside.
    asked_above_floor = ORDER.get(claim.get("declared_level", "CONSISTENT_DECLARED"), 0) > 0
    if risk_exceeded and asked_above_floor:
        err("POLICY_CEILING_EXCEEDED", "perimeter",
            f"outside_weighted_risk <= {max_risk}",
            f"{risk['outside_weighted_risk']} (weights {risk['weights_outside']}/{risk['weights_total']})",
            "the risk outside the core is too large for the declared level; widen the core or lower the claim",
            False)

    # ---- 6. report vs claim --------------------------------------------
    if report:
        if report.get("control_point") and control and report["control_point"] != control:
            err("REPORT_BUNDLE_INCONSISTENT", "control_point",
                control, report["control_point"], "reconcile the report with the claim", True)
        known = {p["path_id"] for p in paths} | {p["path_id"] for p in outside}
        for rp in report.get("analysed_paths", []):
            pid = rp.get("path_id") if isinstance(rp, dict) else rp
            if pid and pid not in known:
                err("UNKNOWN_OR_UNBOUND_PATH", str(pid),
                    "every analysed path present in the inventory", "not in the obligation manifest",
                    "investigate the path; it may not be excluded without evidence", True)

    # ---- 7. the verdict ------------------------------------------------
    claimed_level = claim.get("declared_level", "CONSISTENT_DECLARED")
    capped = list(LEVELS)
    if any(e["code"] in ("TARGET_MISMATCH", "REPORT_BUNDLE_INCONSISTENT", "POLICY_UNTRUSTED") and not e["retryable"]
           for e in errors) or inventory.get("conflicts"):
        verdict = "INVALID"
    else:
        if not independent:
            capped = ["CONSISTENT_DECLARED"]
        if len(excluded) > ceiling:
            capped = capped[:1]
        if coverage >= policy.get("full_coverage_for_proven", 1.0) and independent and "PROVEN" in capped:
            verdict = "PROVEN"
        elif coverage >= policy.get("assurance_threshold", 0.75) and "SCOPED_ASSURANCE" in capped:
            verdict = "SCOPED_ASSURANCE"
        else:
            verdict = "CONSISTENT_DECLARED"
        if ORDER.get(claimed_level, 0) > ORDER.get(verdict, 0):
            if not any(e["code"] == "CLAIM_EXCEEDS_EVIDENCE" for e in errors):
                err("CLAIM_EXCEEDS_EVIDENCE", "level", f"<= {verdict}", claimed_level,
                    f"lower the claim to {verdict}")

    perimeter = {
        "known_paths": len(paths),
        "core_paths": len(in_core),
        "outside_paths": len(outside),
        "outside_weighted_risk": risk.get("outside_weighted_risk"),
        "unclassified_paths": risk.get("unclassified_paths"),
        "risk_policy_digest": risk.get("policy_digest"),
        "delta_since_previous": inventory.get("delta_since_previous"),
        "perimeter_growth": inventory.get("perimeter_growth", False),
        "level_upgrade_allowed": not inventory.get("perimeter_growth", False),
    }
    code = 0 if ORDER.get(verdict, 0) >= ORDER.get(claimed_level, 0) else 1
    if verdict == "INVALID":
        code = 2
    return emit(verdict, coverage, errors[:3], perimeter, code)


def emit(verdict, coverage, errors, perimeter, code) -> int:
    print(json.dumps({
        "verdict": verdict,
        "computed_coverage": None if coverage is None else round(coverage, 3),
        "errors": errors,
        "perimeter": perimeter,
    }, indent=1, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
