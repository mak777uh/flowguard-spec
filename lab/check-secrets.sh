#!/usr/bin/env bash
# Страж: в публичном репозитории не должно быть секретов и локальных путей.
# Запускается локально и в CI. Выход 1 — публикация запрещена.
set -uo pipefail
fail=0

# Корень определяется по расположению скрипта, а не по текущему каталогу.
# Иначе запуск из подкаталога молча проверяет не то дерево — это найдено негативным
# контролем lab/selftest-guards.sh, а не чтением кода.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2

PATTERNS='ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}|ghs_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|xox[baprs]-[A-Za-z0-9-]{10,}'
LOCALPATH='C:\\111|C:\\Users\\|/home/[a-z]+/|\\.dsh'

echo "== tracked files =="
hits=$(git grep --cached -nEI "$PATTERNS" -- . ':!lab/check-secrets.sh' ':!lab/history-path-allowances.txt' 2>/dev/null || true)
if [ -n "$hits" ]; then echo "LEAK: секретные паттерны в файлах"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== git history =="
hits=$(git log -p --all 2>/dev/null | grep -aEI "$PATTERNS" | head -20 || true)
if [ -n "$hits" ]; then echo "LEAK: секретные паттерны в истории"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== local paths in history =="
# Named exceptions only: every allowance carries a reason, and the count is printed. A path that
# appears in a CURRENT file still fails the check below.
hist_all=$(git log --all -p -- . ':(exclude)lab/check-secrets.sh' ':(exclude)lab/history-path-allowances.txt' 2>/dev/null | grep -aEI "$LOCALPATH" || true)
allowed_n=0
hist_paths="$hist_all"
if [ -f lab/history-path-allowances.txt ]; then
  frags=$(grep -v '^#' lab/history-path-allowances.txt | sed 's/#.*//' | sed 's/[[:space:]]*$//' | grep -v '^$' | tr -d '\r' || true)
  if [ -n "$frags" ]; then
    hist_paths=$(printf '%s\n' "$hist_all" | grep -aFv -f <(printf '%s\n' "$frags") || true)
    allowed_n=$(printf '%s\n' "$hist_all" | grep -aF -f <(printf '%s\n' "$frags") | wc -l | tr -d ' ')
  fi
fi
hist_paths=$(printf '%s\n' "$hist_paths" | grep -av '^$' | head -3 || true)
if [ -n "$hist_paths" ]; then
  # Reported, counted, and NOT fatal: published history cannot be rewritten without a force-push
  # that would break every clone. Every occurrence is named in lab/history-path-allowances.txt, the
  # count is printed, and a path in a CURRENT file still fails the check below. The front page says
  # exactly this (E-M44) rather than promising a scan it does not perform.
  echo "warn: локальные пути в истории (не смертельно, см. lab/history-path-allowances.txt)"
  echo "$hist_paths"
  echo "     $allowed_n occurrence(s) named as exceptions"
else echo "ok ($allowed_n occurrence(s) named as exceptions)"; fi

echo "== local paths =="
hits=$(git grep --cached -nEI "$LOCALPATH" -- '*.md' '*.yml' '*.sh' '*.py' '*.json' '*.log' '*.txt' '*.sql' ':!lab/check-secrets.sh' ':!lab/history-path-allowances.txt' 2>/dev/null || true)
if [ -n "$hits" ]; then echo "LEAK: локальные пути"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== .git/config =="
if grep -qE "$PATTERNS" .git/config 2>/dev/null; then echo "LEAK: токен в .git/config"; fail=1; else echo "ok"; fi

[ "$fail" -eq 0 ] && echo "RESULT: clean" || echo "RESULT: BLOCKED"
exit "$fail"
