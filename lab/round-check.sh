#!/usr/bin/env bash
# round-check — the end-of-round ritual, as a script instead of a memory.
#
# Every round ends the same way: guards, negative controls, acceptance suite, audit, readiness.
# Running them by hand meant occasionally forgetting one, which is exactly how a process rots.
#
#   bash lab/round-check.sh            # human summary
#   bash lab/round-check.sh --quiet     # one line per stage
#
# Exit 0 only if every stage passes. A10 ("worktree clean") is expected to fail before the commit
# and to pass after it, so run this twice around a commit, or accept the A10 failure as a reminder.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
PY="${PYTHON:-python}"
QUIET="${1:-}"
RC=0
declare -a LINES=()

stage() {
  local name="$1"; shift
  local out code
  out="$("$@" 2>&1)"; code=$?
  if [[ $code -eq 0 ]]; then
    LINES+=("  ok    $name")
  else
    LINES+=("  FAIL  $name")
    RC=1
    if [[ "$QUIET" != "--quiet" ]]; then
      printf '%s\n' "$out" | tail -12 | sed 's/^/        /'
    fi
  fi
}

echo "round-check"

stage "secrets (files + history + index)" bash lab/check-secrets.sh
stage "relative links" "$PY" lab/check-links.py
stage "claim registry" "$PY" lab/check-claims.py
stage "claims map to evidence types (M3)" "$PY" lab/claims-map.py
stage "backticked paths resolve" "$PY" lab/check-artifact-refs.py
stage "README covers every document" "$PY" lab/check-readme.py
stage "negative controls for every guard" bash lab/selftest-guards.sh
stage "acceptance scenarios" "$PY" lab/e-m12-run.py
stage "instrument corpus" "$PY" lab/e-m10-run.py --per-class 4 --valid 4
# A10 (clean worktree) is skipped here: a round is checked before its commit. Run
# `python tools/fg_audit.py` after the commit to include it.
stage "attack suite (own attempts)" "$PY" lab/e-m36-run.py >/dev/null
stage "attack suite (independent attacker)" "$PY" lab/e-m42-run.py
stage "every refusal code is exercised" "$PY" lab/check-refusal-coverage.py
stage "cross-family attack cadence" "$PY" lab/cross-family-due.py || true
stage "cross-family findings stay closed" "$PY" lab/e-m60-run.py
stage "Rust arithmetic vs Python on the attack cases" "$PY" lab/e-m67-run.py
stage "differential: Rust core vs Python core" "$PY" lab/e-m66-run.py || true
stage "differential against a third-party verifier" "$PY" lab/e-m57-run.py
stage "role terms are covered by the signature" "$PY" lab/e-m53-run.py
stage "no CRLF, every shell script parses" "$PY" lab/check-line-endings.py
stage "published schemas accept the artifacts" "$PY" tools/fg_schema_check.py --claim fixtures/attack/k-proven.json
stage "no tracebacks on malformed input" "$PY" lab/e-m48-run.py
stage "metric and card digests resolve" "$PY" lab/check-metric-digests.py --cards
stage "status page is current" "$PY" tools/fg_status.py --check
stage "dossier is current" "$PY" tools/fg_dossier.py --check
stage "repository and method audit" "$PY" tools/fg_repo_audit.py >/dev/null
stage "process audit (without A10)" "$PY" tools/fg_audit.py --allow-dirty

printf '%s\n' "${LINES[@]}"

echo
echo "readiness:"
"$PY" tools/fg_readiness.py 2>&1 | tail -4 | sed 's/^/  /'

METRICS=$("$PY" - <<'EOF'
import re, pathlib
p = pathlib.Path("docs/METRICS.md")
rows = [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
print(len(rows))
EOF
)
CARDS=$(ls lab/experiments/*.md 2>/dev/null | wc -l)
ADRS=$(ls lab/decisions/ADR-*.md 2>/dev/null | wc -l)
echo "  artifacts: metrics=$METRICS cards=$CARDS adrs=$ADRS"

if [[ $RC -eq 0 ]]; then echo "RESULT: ok"; else echo "RESULT: fail"; fi
exit $RC
