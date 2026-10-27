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

echo
echo "controls passed: $PASS   failed: $FAIL"
[[ "$FAIL" -eq 0 ]] || { echo "RESULT: fail"; exit 1; }
echo "RESULT: ok"
