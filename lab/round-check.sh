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
  # A stage command that cannot exist is a BROKEN stage, not a failed check: this session produced four
  # mangled interpreter paths (PowerShell ate the quotes and backslashes), and each one reported FAIL for a
  # reason unrelated to what the stage checks. Refuse it before it runs, and name the token.
  if [[ "$1" == */* || "$1" == *\\* ]]; then
    if [[ ! -x "$1" ]]; then
      LINES+=("  BROKEN  $name (command does not exist: $1)")
      RC=1
      return
    fi
  fi
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
stage "no two documents share a number" "$PY" lab/check-doc-numbers.py
stage "new experiment cards are pre-registered" "$PY" lab/check-preregistration.py
stage "the elimination registry matches the cards" "$PY" lab/check-eliminations.py
stage "claim registry" "$PY" lab/check-claims.py
stage "claims map to evidence types (M3)" "$PY" lab/claims-map.py
stage "backticked paths resolve" "$PY" lab/check-artifact-refs.py
stage "claimant text decomposed into units" "$PY" lab/e-m82-run.py
stage "the verifier counts the denominator itself" "$PY" lab/e-m81-run.py
stage "every card and note is indexed" "$PY" lab/check-evidence-reachability.py
stage "every runner is in CI or declared" "$PY" lab/check-runner-coverage.py
stage "the mirror never contradicts the canon" "$PY" lab/check-readme-parity.py
stage "README covers every document" "$PY" lab/check-readme.py
stage "negative controls for every guard" bash lab/selftest-guards.sh
stage "acceptance scenarios" "$PY" lab/e-m12-run.py
stage "instrument corpus" "$PY" lab/e-m10-run.py --per-class 4 --valid 4
# A10 (clean worktree) is skipped here: a round is checked before its commit. Run
# `python tools/fg_audit.py` after the commit to include it.
stage "attack suite (own attempts)" "$PY" lab/e-m36-run.py >/dev/null
stage "attack suite (independent attacker)" "$PY" lab/e-m42-run.py
stage "every refusal code is exercised" "$PY" lab/check-refusal-coverage.py
# The cadence report is information, not a gate: it says whether a model attack is due. It is printed
# unconditionally and cannot fail, because "due" is not an error (the audit of 2026-10-29 called `|| true` a
# step that cannot fail; the difference is that this step does not claim to be a check, and says so).
echo "  cadence (not a gate):"
"$PY" lab/cross-family-due.py 2>&1 | sed 's/^/    /' || true
stage "cross-family findings stay closed" "$PY" lab/e-m60-run.py
stage "fourth check: mapping refusals and ceiling" "$PY" lab/e-m72-run.py
stage "both cores on the cross-family divergences" "$PY" lab/e-m69-run.py
stage "bundle signature and role binding" "$PY" lab/e-m9-run.py
stage "bundle acceptance scenarios" "$PY" lab/e-m28-run.py
stage "attack suite: refusal codes" "$PY" lab/e-m31-run.py
stage "attack suite: escalation" "$PY" lab/e-m33-run.py
stage "migrations enumerator, end to end" "$PY" lab/e-m70-run.py
stage "Rust claim CLI vs Python" "$PY" lab/e-m68-run.py
stage "Rust arithmetic vs Python on the attack cases" "$PY" lab/e-m67-run.py
# The Rust differential needs a toolchain and a compiled binary. Absent either, it is SKIPPED - printed as
# skipped, never as passed - because a green line for a test that did not run is the defect this repository
# keeps finding in other people's CI (E-M76) and in its own ritual (audit 2026-10-29, T10).
if command -v cargo >/dev/null 2>&1 && [ -x core-rs/target/debug/fg-core.exe -o -x core-rs/target/debug/fg-core ]; then
  stage "differential: Rust core vs Python core" "$PY" lab/e-m66-run.py
else
  echo "  SKIPPED differential: Rust core vs Python core (no cargo, or no built core-rs binary)"
fi
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
