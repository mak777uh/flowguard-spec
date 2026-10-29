#!/usr/bin/env bash
# Negative controls for the guards.
#
# Five reviewers of round 6 converged on one gap: our guards are asserted to work, never shown to fail.
# A guard that has never been seen to fail is a guard that may be doing nothing.
#
# For each guard: plant a known defect, run the guard, require a non-zero exit, remove the defect.
# The planted defects are synthetic and named in the code — never in the real tree.
#
#   bash lab/selftest-guards.sh          # all controls
#   bash lab/selftest-guards.sh secrets  # one control
#
# Exit 0 only if every control caught its planted defect.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
ONLY="${1:-all}"

pass() { printf '  ok    %s\n' "$1"; PASS=$((PASS+1)); }
fail() { printf '  FAIL  %s\n' "$1"; FAIL=$((FAIL+1)); }

# A copy of the tree without .git, then a fresh repository: the secrets guard searches tracked
# files and history, so an untracked temp file would be invisible to it.
stage() {
  rm -rf "$TMP/repo"
  mkdir -p "$TMP/repo"
  ( cd "$ROOT" && git ls-files -z | tar --null -T - -cf - ) 2>/dev/null | ( cd "$TMP/repo" && tar xf - )
  ( cd "$TMP/repo" && git init -q . && git add -A && git -c user.email=t@t -c user.name=t commit -qm base )
}

echo "negative controls"

# ---- control 1: secrets ------------------------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "secrets" ]]; then
  stage
  # split so this file itself does not match the guard's pattern
  printf 'token = "ghp_%s"\n' "$(printf 'A%.0s' {1..36})" > "$TMP/repo/docs/_negative_control.md"
  ( cd "$TMP/repo" && git add -A && git -c user.email=t@t -c user.name=t commit -qm plant )
  if bash "$TMP/repo/lab/check-secrets.sh" >/dev/null 2>&1; then
    fail "secrets: a planted GitHub-shaped token was NOT caught"
  else
    pass "secrets: planted token caught"
  fi
fi

# ---- control 2: broken relative link ----------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "links" ]]; then
  stage
  printf 'A [link](this-file-does-not-exist.md) that resolves nowhere.\n' > "$TMP/repo/docs/_negative_control.md"
  if python "$TMP/repo/lab/check-links.py" >/dev/null 2>&1; then
    fail "links: a dangling relative link was NOT caught"
  else
    pass "links: dangling link caught"
  fi
fi

# ---- control 3: claim wording above its evidence -----------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "claims" ]]; then
  stage
  # an unknown evidence type: the linter must refuse it, not silently pass
  printf '\n| C-98 | A synthetic claim | telepathy | may be stated freely | x | y |\n' >> "$TMP/repo/docs/CLAIMS.md"
  if python "$TMP/repo/lab/check-claims.py" >/dev/null 2>&1; then
    fail "claims: an unknown evidence type was NOT caught"
  else
    pass "claims: unknown evidence type caught"
  fi
fi

# ---- control 4: interop kit detection ---------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "interop" ]]; then
  stage
  # remove the experiment card: M1 must stop being 'present'
  rm -f "$TMP/repo/lab/experiments/"*.md 2>/dev/null
  if python "$TMP/repo/lab/check-interop.py" 2>/dev/null | grep -q 'M1 experiment cards *present'; then
    fail "interop: M1 still reported present after the card was removed"
  else
    pass "interop: missing experiment card detected"
  fi
fi

# ---- control 5: the README covers every document -----------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "readme" ]]; then
  stage
  printf '# orphan\n' > "$TMP/repo/docs/_negative_control_orphan.md"
  if python "$TMP/repo/lab/check-readme.py" >/dev/null 2>&1; then
    fail "readme: an unlinked document was NOT caught"
  else
    pass "readme: unlinked document caught"
  fi
fi
# ---- control 6: a dangling backticked path is caught -------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "refs" ]]; then
  stage
  printf 'see `lab/does-not-exist.py` for details\n' > "$TMP/repo/docs/_negative_control_ref.md"
  if python "$TMP/repo/lab/check-artifact-refs.py" >/dev/null 2>&1; then
    fail "refs: a dangling backticked path was NOT caught"
  else
    pass "refs: dangling backticked path caught"
  fi
fi
# ---- control 7: a claim worded above its evidence type ------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "wording" ]]; then
  stage
  # a real type, but a reserved word it may not use: the ceiling must catch it
  printf '\n| C-97 | A synthetic claim over a measured corpus | statistics | the result is PROVEN and carries a guarantee | x | y |\n' >> "$TMP/repo/docs/CLAIMS.md"
  if python "$TMP/repo/lab/check-claims.py" >/dev/null 2>&1; then
    fail "wording: a statistics claim using a reserved word was NOT caught"
  else
    pass "wording: reserved word above the evidence ceiling caught"
  fi
fi
# 8. the attack suite must be able to fail: a planted wrong expectation must turn it red.
#    Without this control, a suite that has quietly stopped checking anything still looks green.
selftest_out=$(FG_ATTACK_SELFTEST=1 python lab/e-m42-run.py 2>&1 || true)
if printf '%s' "$selftest_out" | grep -q 'still breaking: 1'; then
  pass 'the attack suite notices a planted wrong expectation'
else
  fail 'the attack suite did not notice a planted wrong expectation'
fi

# ---- control 8: line endings ----------------------------------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "line-endings" ]]; then
  stage
  # a shell script with CRLF must be reported: it breaks under bash on every POSIX system.
  # The guard reads `git ls-files`, so the plant has to be committed or it is invisible - and the first
  # version of this control passed only because the real tree happened to be dirty, which is the worst
  # kind of green: a control that goes green for a reason unrelated to its plant.
  printf '#!/usr/bin/env bash\r\necho hi\r\n' > "$TMP/repo/lab/_negative_crlf.sh"
  ( cd "$TMP/repo" && git add -A && git -c user.email=t@t -c user.name=t commit -qm plant )
  if python "$TMP/repo/lab/check-line-endings.py" >/dev/null 2>&1; then
    fail "line-endings: a CRLF shell script was NOT caught"
  else
    pass "line-endings: CRLF caught"
  fi
fi

# ---- control 9: metric digests ---------------------------------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "metric-digests" ]]; then
  stage
  # point a metric row at a digest that does not exist: the guard must refuse it
  printf '\n| 999 | synthetic | **n/a** | `true` | `%s` | x | y |\n' \
    "0000000000000000000000000000000000000000000000000000000000000000" \
    >> "$TMP/repo/docs/METRICS.md"
  if python "$TMP/repo/lab/check-metric-digests.py" --cards >/dev/null 2>&1; then
    fail "metric-digests: a forged digest was NOT caught"
  else
    pass "metric-digests: forged digest caught"
  fi
fi

# ---- control 10: refusal coverage ------------------------------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "refusal-coverage" ]]; then
  stage
  # A code that exists in the document but that no script ever raises must be reported. The name is built at
  # run time on purpose: a literal here would be found by the guard in THIS file, which is itself a carrier,
  # and the planted code would count as exercised (found the first time this control was written).
  PLANTED="SYNTHETIC_$(date +%s)_UNRAISED"
  printf '\n| `%s` | planted by the selftest | n/a | no |\n' "$PLANTED" \
    >> "$TMP/repo/docs/37-REFUSAL-CODES.md"
  if python "$TMP/repo/lab/check-refusal-coverage.py" >/dev/null 2>&1; then
    fail "refusal-coverage: an unraised code was NOT caught"
  else
    pass "refusal-coverage: unraised code caught"
  fi
fi

echo

# ---- control 11: claims value ----------------------------------------------------------------
if [[ "$ONLY" == "all" || "$ONLY" == "claims-value" ]]; then
  stage
  # a sentence that asserts a number none of its artifacts contains must fail, even though the wording ceiling
  # is legal (herness, 2026-10-29: the ceiling was checked, the value was not)
  printf '\n| C-99 | The tool refuses 4242 stale rows | test | measured | `lab/experiments/E-M73-paired-eval.md` | y |\n' \
    >> "$TMP/repo/docs/CLAIMS.md"
  if python "$TMP/repo/lab/check-claims.py" --strict >/dev/null 2>&1; then
    fail "claims-value: a number absent from the cited artifact was NOT caught"
  else
    pass "claims-value: stale number caught"
  fi
fi

echo "controls passed: $PASS   failed: $FAIL"
[[ "$FAIL" -eq 0 ]] || { echo "RESULT: fail"; exit 1; }
echo "RESULT: ok"
