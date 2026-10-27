#!/usr/bin/env python3
"""fg_exclusions — an exclusion is a claim, and its preconditions are checked.

Round-8 review, all three models, said the same thing: verifying that an excluded path exists and
that its reason is at least eight characters long is *syntactic* validity. A reason can be formally
complete and factually false, and the code most likely to be false is `DATA_NOT_SENSITIVE` applied to
a money path.

This module checks:

  * the reason code is known;
  * the code's required evidence is present and non-empty;
  * the code is not applied to a risk class it is forbidden for;
  * an unknown risk class may not be excluded with `DATA_NOT_SENSITIVE` - the class is precisely what
    that code claims to know.

It cannot check that the reason is TRUE. That limit is stated in the verdict, not hidden.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "policies" / "exclusion-reasons.json"

_CACHE = {}


def load_policy(path=None):
    p = Path(path) if path else POLICY
    key = str(p)
    if key not in _CACHE:
        _CACHE[key] = json.loads(p.read_text(encoding="utf-8"))
    return _CACHE[key]


def _get(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def check(excluded, class_of, policy_path=None):
    """Return a list of findings: {code, path_id, reason_code, detail}."""
    policy = load_policy(policy_path)
    reasons = policy["reasons"]
    findings = []

    for item in excluded or []:
        if not isinstance(item, dict):
            findings.append({"code": "MISSING_EVIDENCE", "path_id": str(item),
                             "reason_code": None, "detail": "an exclusion must be an object with a reason_code"})
            continue
        pid = item.get("path_id")
        rc = item.get("reason_code")
        if not rc:
            findings.append({"code": "MISSING_EVIDENCE", "path_id": pid, "reason_code": None,
                             "detail": "no reason_code; free text cannot be checked"})
            continue
        spec = reasons.get(rc)
        if spec is None:
            findings.append({"code": "EXCLUSION_REASON_UNKNOWN", "path_id": pid, "reason_code": rc,
                             "detail": f"unknown reason code; known: {', '.join(sorted(reasons))}"})
            continue

        for req in spec.get("requires", []):
            if not _get(item, req):
                findings.append({"code": "MISSING_EVIDENCE", "path_id": pid, "reason_code": rc,
                                 "detail": f"{rc} requires {req}"})

        cls = class_of(pid) if callable(class_of) else "unknown"
        forbidden = spec.get("forbidden_for_classes") or []
        if cls in forbidden:
            findings.append({"code": "EXCLUSION_REASON_CONTRADICTION", "path_id": pid, "reason_code": rc,
                             "detail": f"{rc} may not be applied to a path of class {cls}"})
        if cls in ("unknown", "unclassified") and rc == "DATA_NOT_SENSITIVE":
            findings.append({"code": "EXCLUSION_REASON_CONTRADICTION", "path_id": pid, "reason_code": rc,
                             "detail": "the class is unknown, so a claim that the data is not sensitive is "
                                       "exactly what cannot be established"})
    return findings
