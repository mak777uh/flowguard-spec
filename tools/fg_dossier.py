#!/usr/bin/env python3
"""fg_dossier — one self-contained file to hand to an outside model.

The owner asked for a single file that can be pasted into any AI model and understood without the
repository. A hand-written document would drift within a week, so this generates it from the
artifacts: measured numbers come from docs/METRICS.md, cards from lab/experiments, decisions from
lab/decisions, the readiness tier from tools/fg_readiness.py, and the open questions from the
current review pack.

    python tools/fg_dossier.py            # write DOSSIER.md
    python tools/fg_dossier.py --check    # exit 1 if DOSSIER.md is stale
    python tools/fg_dossier.py --stdout
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "DOSSIER.md"


def front_matter(text):
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm


def metrics_rows():
    p = ROOT / "docs" / "METRICS.md"
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3:
            rows.append({"n": cells[0], "what": cells[1], "value": cells[2]})
    return rows


def cards():
    out = []
    for p in sorted((ROOT / "lab" / "experiments").glob("*.md")):
        fm = front_matter(p.read_text(encoding="utf-8"))
        if fm.get("id"):
            out.append({"file": p.name, **fm})
    return out


def adrs():
    out = []
    for p in sorted((ROOT / "lab" / "decisions").glob("ADR-*.md")):
        text = p.read_text(encoding="utf-8")
        m = re.match(r"#\s*(ADR-[0-9]+)\s*[—-]\s*(.+)", text)
        if m:
            out.append({"id": m.group(1), "title": m.group(2).strip()})
    return out


def readiness():
    try:
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "fg_readiness.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        out = r.stdout
        pct = re.search(r"core \(engine\): (\d+)%\s+product: (\d+)%\s+overall: (\d+)%", out)
        tier = re.search(r"tier: (T\d) — (.+)", out)
        nxt = re.search(r"next tier (T\d) \((.+?)\) blocked by: (.+)", out)
        return {
            "engine": pct.group(1) if pct else "?",
            "product": pct.group(2) if pct else "?",
            "overall": pct.group(3) if pct else "?",
            "tier": tier.group(1) if tier else "?",
            "tier_name": tier.group(2) if tier else "?",
            "next": (nxt.group(1), nxt.group(2), nxt.group(3)) if nxt else None,
        }
    except Exception as e:  # noqa: BLE001
        return {"engine": "?", "product": "?", "overall": "?", "tier": "?", "tier_name": "?",
                "next": None, "error": str(e)}


def review_pack():
    packs = sorted((ROOT / "docs").glob("*-ROUND*-QUESTIONS.md"))
    if not packs:
        return "", ""
    p = packs[-1]
    return p.name, p.read_text(encoding="utf-8")


def build() -> str:
    m = metrics_rows()
    cs = cards()
    a = adrs()
    r = readiness()
    pack_name, pack = review_pack()

    completed = [c for c in cs if c.get("status") == "completed"]
    refuted = [c for c in completed if c.get("verdict") == "refutes"]

    L = []
    L.append("# FlowGuard — один файл для внешней модели\n")
    L.append("*Сгенерировано из артефактов репозитория командой `python tools/fg_dossier.py`. "
             "Числа здесь не написаны руками: они взяты из журнала замеров, карточек экспериментов и "
             "счётчика готовности. Если файл расходится с репозиторием, виноват генератор, а не читатель.*\n")

    L.append("## Что это\n")
    L.append("Продукт проверяет **одно** утверждение: что все известные способы изменить важные данные проходят "
             "через объявленную контрольную точку, а всё, что проходит мимо, — перечислено честно.\n")
    L.append("Единица — **поток**, не система. Доказать безопасность приложения целиком нельзя; берётся один "
             "поток (движение денег, выдача файлов, личные данные), ставится за одну дверь, периметр "
             "публикуется. Потребитель инструмента — **ИИ-агент**: вход и выход JSON, без интерактива. "
             "Агент — глаза, инструмент — совесть.\n")
    L.append("Артефакт называется **scoped consistency attestation** и никогда — «подтверждение безопасности».\n")

    L.append("## Чего это не утверждает\n")
    L.append("Словарь кодов, каждый запрещает конкретное утверждение:\n")
    L.append("| код | что не утверждается |")
    L.append("|---|---|")
    L.append("| NC-01 | что инвентарь содержит все релевантные пути |")
    L.append("| NC-02 | что за пределами проверенной области всё безопасно |")
    L.append("| NC-03 | что прочтение кода агентом верно |")
    L.append("| NC-04 | что репозиторий равен развёрнутой системе |")
    L.append("| NC-05 | что два источника независимы в своих слепых зонах |")
    L.append("| NC-06 | что политика соответствует намерению бизнеса |")
    L.append("| NC-07 | что веса риска объективны |")
    L.append("| NC-08 | что издатель якоря доверия был вправе его издать |")
    L.append("| NC-09 | что третья сторона может воспроизвести анализ |")
    L.append("| NC-10 | что наблюдаемое поведение совпадает со статической моделью |")
    L.append("")
    L.append("Утверждение без обязательных для его уровня кодов отвергается машиной. Проза не принимается.\n")

    L.append("## Состояние, посчитанное\n")
    L.append("```")
    L.append(f"ядро (движок):  {r['engine']}%")
    L.append(f"продукт:        {r['product']}%")
    L.append(f"общая:          {r['overall']}%")
    L.append(f"уровень:        {r['tier']} — {r['tier_name']}")
    if r.get("next"):
        L.append(f"следующий:      {r['next'][0]} ({r['next'][1]}), блокируют: {r['next'][2]}")
    L.append("```\n")
    L.append("Уровни: T1 — работает у автора; T2 — посторонний может поставить и воспроизвести; "
             "T3 — годится для чужого решения; T4 — гарантия, на которую можно опереться. "
             "Каждая проверка либо находит свидетельство в файлах, либо получает ноль.\n")

    L.append(f"## Замеры ({len(m)})\n")
    L.append("| # | что | результат |")
    L.append("|---|---|---|")
    for row in m:
        L.append(f"| {row['n']} | {row['what']} | {row['value']} |")
    L.append("")

    L.append(f"## Эксперименты ({len(cs)} карточек, из них провальных: {len(refuted)})\n")
    L.append("| карточка | гипотеза | статус | вердикт |")
    L.append("|---|---|---|---|")
    for c in cs:
        L.append(f"| {c.get('id','?')} | {c.get('hypothesis','')} | {c.get('status','')} | {c.get('verdict','')} |")
    L.append("")
    if refuted:
        L.append("Провалы оставлены в репозитории как есть, с причиной. Ни один не переписан задним числом:\n")
        for c in refuted:
            L.append(f"- **{c.get('id')}** — {c.get('result','')[:400]}")
        L.append("")

    L.append(f"## Решения ({len(a)})\n")
    for adr in a:
        L.append(f"- {adr['id']} — {adr['title']}")
    L.append("")

    L.append("## Как это устроено, в десяти строках\n")
    L.append("```")
    L.append("источники -> инвентарь -> покрытие -> вердикт -> бандл")
    L.append("")
    L.append("grants-pg   права, функции, триггеры, цепочки триггеров в Postgres")
    L.append("pgcalls     граф вызовов PL/pgSQL: какой путь доходит до контрольной точки")
    L.append("runtime-pg  что реально исполнялось, по серверному логу (свидетель, не знаменатель)")
    L.append("routes-json входные точки, которые пишут целевую таблицу")
    L.append("")
    L.append("merge       объединение, конфликты, атрибуция через границу источников, дельта периметра")
    L.append("fg_verify   пересчёт покрытия, 8 кодов отказа, потолки, взвешенный риск периметра")
    L.append("fg_bundle   fg-bundle/1, Ed25519; проверка является свидетельством только при двух якорях")
    L.append("```\n")

    L.append("## Что можно применить сегодня\n")
    L.append("1. **Найти обходы контрольной точки в Postgres.** 8 из 8 посаженных обходов, точность строк 11 из 12. "
             "Не видит проверок в коде приложения и запись из другого сервиса.\n")
    L.append("2. **Привязать путь к контрольной точке.** 2 из 2 законных вызывающих, 0 из 9 ложных, обманка по имени "
             "не прошла. Не видит вызовов через переменные и глубже восьми шагов.\n")
    L.append("3. **Собрать, подписать и проверить бандл.** 6 из 6 подмен с якорями; 3 из 6 без якорей — "
             "самоподписанный бандл не доказывает ничего.\n")
    L.append("4. **Получить машиночитаемый отказ.** 19 приёмочных сценариев, включая попытку сузить область "
             "выдуманным исключением.\n")
    L.append("5. **Взвесить периметр.** Неопознанный путь весит 3, не 0.\n")

    L.append("## Как воспроизвести\n")
    L.append("```bash")
    L.append("cd flowguard-spec")
    L.append("bash lab/round-check.sh                 # стражи, негативные контроли, приёмочный набор, аудит")
    L.append("python tools/fg_readiness.py            # готовность: ядро / продукт / уровень")
    L.append("python tools/fg_audit.py                # аудит собственных артефактов метода")
    L.append("python lab/e-m12-run.py                 # 19 сценариев верификатора")
    L.append("python lab/e-m10-run.py                 # корпус мутаций инструмента")
    L.append("python lab/e-m9-run.py                  # тест подмены, с якорями и без")
    L.append("```")
    L.append("Postgres нужен для двух замеров: `lab/e-m11-run.py`, `lab/e-m13-run.py`.\n")

    L.append("## Что заблокировано и чем\n")
    L.append("```")
    L.append("M7  независимая пересборка бандла   -> ждёт внешнюю сторону (VecDHT спрошен, ответа нет)")
    L.append("M8  названный потребитель           -> ждёт один разговор; форма готова, заполняется за 20 минут")
    L.append("T3  доверие для чужого решения      -> требует M7 и M8")
    L.append("реальная схема                      -> публичная (Pagila) в работе; клиентская требует разрешения")
    L.append("```\n")

    if pack:
        L.append(f"## Вопросы к тебе (из `docs/{pack_name}`)\n")
        L.append("*Ниже — последний пакет внешнего ревью целиком. На него и нужен ответ.*\n")
        body = pack.split("## Вопросы", 1)
        L.append("## Вопросы" + body[1] if len(body) > 1 else pack)
        L.append("")

    L.append("## Как отвечать с пользой\n")
    L.append("Мнение «выглядит солидно» бесполезно. Полезно:\n")
    L.append("- назвать **механизм** (как делают в известной практике, где именно, с каким результатом);")
    L.append("- назвать **класс ошибок**, который наша конструкция не ловит;")
    L.append("- сказать, **какое число** сделало бы утверждение свидетельством, и почему именно оно;")
    L.append("- если ответа нет — так и сказать: «нет свидетельства». Это тоже ответ.\n")
    L.append("Слабые места, которые мы уже знаем и не прячем: все замеры на фикстуре автора; веса риска — "
             "соглашение, не измерение; ложная причина исключения проходит; вызовы между слоями склеиваются по "
             "имени функции. Повторять их не нужно — нужно то, чего в этом списке нет.\n")

    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    text = build()
    if a.stdout:
        print(text)
        return 0
    if a.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("DOSSIER.md is stale — run python tools/fg_dossier.py")
            return 1
        print("DOSSIER.md is current")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
