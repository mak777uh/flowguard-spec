#!/usr/bin/env bash
# Страж: в публичном репозитории не должно быть секретов и локальных путей.
# Запускается локально и в CI. Выход 1 — публикация запрещена.
set -uo pipefail
fail=0

PATTERNS='ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}|ghs_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|xox[baprs]-[A-Za-z0-9-]{10,}'
LOCALPATH='C:\\111|C:\\Users\\|/home/[a-z]+/|\\.dsh'

echo "== tracked files =="
hits=$(git grep -nEI "$PATTERNS" -- . ':!lab/check-secrets.sh' 2>/dev/null || true)
if [ -n "$hits" ]; then echo "LEAK: секретные паттерны в файлах"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== git history =="
hits=$(git log -p --all 2>/dev/null | grep -aEI "$PATTERNS" | head -20 || true)
if [ -n "$hits" ]; then echo "LEAK: секретные паттерны в истории"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== local paths =="
hits=$(git grep -nEI "$LOCALPATH" -- '*.md' '*.yml' '*.sh' '*.py' ':!lab/check-secrets.sh' 2>/dev/null || true)
if [ -n "$hits" ]; then echo "LEAK: локальные пути"; echo "$hits"; fail=1; else echo "ok"; fi

echo "== .git/config =="
if grep -qE "$PATTERNS" .git/config 2>/dev/null; then echo "LEAK: токен в .git/config"; fail=1; else echo "ok"; fi

[ "$fail" -eq 0 ] && echo "RESULT: clean" || echo "RESULT: BLOCKED"
exit "$fail"
