#!/usr/bin/env python3
"""Страж: все относительные ссылки между документами должны существовать.
Документы ссылаются друг на друга — битая ссылка это потерянное утверждение."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
bad = 0
checked = 0

for md in list(ROOT.glob('*.md')) + list((ROOT / 'docs').glob('*.md')) + list((ROOT / 'articles').glob('*.md')):
    for lineno, line in enumerate(md.read_text(encoding='utf-8').splitlines(), 1):
        for target in LINK.findall(line):
            t = target.strip()
            if t.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            t = t.split('#')[0]
            if not t:
                continue
            checked += 1
            if not (md.parent / t).exists():
                print(f'BROKEN {md.relative_to(ROOT)}:{lineno} -> {t}')
                bad += 1

print(f'links checked: {checked}, broken: {bad}')
sys.exit(1 if bad else 0)
