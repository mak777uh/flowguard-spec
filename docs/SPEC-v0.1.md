# SPEC v0.1 — flowguard (открытое ядро)

**Статус:** первая версия, проектная спецификация. Подготовлена к циклам критики.
**Метки достоверности:** `[Д]` — доказано машинной проверкой · `[И]` — измерено/воспроизведено · `[Г]` — гипотеза, требует проверки.
**Что это:** спецификация минимального вертикального среза, который можно реализовать силами 3–4 человек за 12–16 недель и который уже полезен публике.
**Чего это не является:** обещанием безопасности. v0.1 выдаёт проверяемое утверждение с явной границей, а не «система защищена».

---

## 1. Рамка: зачем именно так и что входит

### 1.1. Контекст, из которого следует приоритет

Массовые атаки с помощью агентов меняют экономику защиты: найти дефект стало дешевле, чем его починить, а «список возможных уязвимостей» перестал быть сигналом. Единственное, что сохраняет ценность, — **проверяемое утверждение с границей**. Поэтому первым выпускается не сканер и не гарантия, а **публично проверяемая машинерия**: формат утверждения, его верификатор и три инварианта, которые можно проверить на чужом контракте без разрешения.

### 1.2. Ключевое следствие для v0.1 (меняет план)

**On-chain поток не требует микроVM.** EVM-среда (`anvil`) — обычный процесс, работает на macOS, Linux и Windows. Значит полный цикл «инвентаризация → инварианты → 10 атак → бандл → verify → replay» **исполняется на ноутбуке**, без KVM, без железа, без NDA.

Отсюда решение: **v0.1 — целиком про on-chain (escrow), end-to-end, локально.** Legacy в v0.1 — только статическая инвентаризация и проверка политики, без динамики.

### 1.3. Что входит в v0.1

| Входит | Не входит (позже) |
|---|---|
| `flowguard.yml` (нормативная схема) | Legacy-динамика: witness, eBPF, DB-триггер |
| `scan` для escrow-контрактов: пути движения средств, роли, прокси | Медиатор и `Permit` (v0.2) |
| `scan` статический для репозиториев: writer'ы, IaC, OpenAPI | Verus-доказательство медиатора (v0.3) |
| `check`: политика → SMT (Z3), инварианты → Foundry/Halmos | Certora (v0.4, коммерческий бэкенд) |
| `attack`: 10 сценариев на `anvil`-форке | Автовыплаты и эскроу (v0.5, коммерческое) |
| `attest`: сборка бандла, подписи Ed25519 | Мультичейн за пределами L1+L2 |
| `verify`, `replay`, `diff`, `badge` | Браузерный UI |
| 3 инварианта escrow + 10 атак + финальность | Legacy Z из 12 элементов в полном объёме |

### 1.4. Чего v0.1 не обещает — прямым текстом

- Не находит «все уязвимости» и не является аудитом.
- Не гарантирует отсутствие атак вне объявленного замыкания `Z`.
- Не работает на целях, у которых нельзя получить bytecode и состояние.
- Не даёт юридической гарантии: подпись в v0.1 — техническая, не договорная.
- Не покрывает: мосты, оракулы, MEV, upgrade-пути, оставленные активными (это `INVALID`-условие, а не «покрыто»).

---

## 2. Доменная модель

Семь сущностей. Всё остальное — производные.

| # | Сущность | Определение | Инвариант существования |
|---|---|---|---|
| 1 | **Flow** | защищаемый поток: ресурс, который движется от входа к выходу | имеет `flow_id`, домен и владельца |
| 2 | **Resource** | адресуемая ценность: баланс эскроу, строка леджера, токен | адресуется через `StateProvider`, не «таблицей» и не «контрактом» |
| 3 | **Subject** | кто инициирует действие | идентифицируется только из проверенного источника, никогда из тела запроса |
| 4 | **Policy P** | что субъекту разрешено с ресурсом | выражается в DSL; deny-beats-allow; default deny |
| 5 | **Closure Z** | множество путей, по которым ресурс может измениться | полный перечень; **непустое множество неизвестных путей запрещает `PROVEN`** |
| 6 | **EnforcementPoint M** | единственная точка решения | каждый путь из Z проходит через M, либо объявлен вне гарантии |
| 7 | **Attestation** | подписанный бандл: утверждение + доказательства + границы | проверяется офлайн без доверия к издателю |

**Правило домена.** Любое поле, зависящее от домена, живёт в `subject`, а не в корне бандла:

```json
{"kind": "chain.escrow", "chain_id": 1, "address": "0x…", "code_hash": "0x…",
 "block": 21174321, "finality": "FINAL"}
{"kind": "legacy.flow",  "repo": "github.com/org/repo", "commit": "9f3a1c",
 "lockfiles": ["package-lock.json"], "toolchain": "node@22"}
```

---

## 3. Формат `flowguard.yml` (нормативно)

Ключевые слова: **MUST** — обязательно, **MUST NOT** — запрещено, **DEFAULT** — значение по умолчанию. Неизвестные поля в секциях `policy`, `closure`, `enforcement`, `evidence` — **MUST** отклоняться (fail-closed), чтобы опечатка не расширяла границу молча.

```yaml
schema_version: "1.0"            # MUST, ^1\.\d+$

flow:
  id: "escrow.payout"            # MUST, immutable, входит в хеш
  domain: onchain                # MUST: onchain | legacy
  assets:                        # MUST, ≥1
    - kind: token                # MUST: token | money | data | access
      id: "ERC20:USDC"           # MUST
      criticality: high          # MUST: low | medium | high

subject:                         # MUST
  kind: chain.escrow             # MUST: chain.escrow | chain.contract | legacy.flow
  chain_id: 1                    # MUST для chain.*
  address: "0x…"                 # MUST
  code_hash: "0x…"               # MUST, runtime bytecode hash
  proxy:                         # MUST
    type: none                   # MUST: none | transparent | uups | beacon
    implementation: null         # MUST если type != none
    admin: null                  # MUST если применимо; активный admin ⇒ INVALID

policy:
  id: "escrow-release-v1"        # MUST
  version: 1                     # MUST
  fail_closed: true              # MUST; false запрещён для аттестации
  invariants:                    # MUST, ≥1, из каталога §8.2
    - id: "INV-1"
  rules_file: null               # опционально для legacy

closure:
  declared_paths: [ … ]          # MUST, ≥1; пустой список запрещён
  excluded:                      # опционально
    - path: "bridge"
      reason: "вне гарантии"     # MUST, если path указан
  unknown_behavior: INCONCLUSIVE # MUST, фиксированное значение

enforcement:
  mode: onchain_guard            # MUST: in_process | single_writer | onchain_guard
  mediator_hash: "0x…"           # MUST для in_process/single_writer
  permit:                        # опционально
    algorithm: Ed25519           # DEFAULT Ed25519
    max_ttl_seconds: 900         # DEFAULT 900
    nonce_required: true         # DEFAULT true
    audience_required: true      # DEFAULT true; false запрещён

evidence:
  observation_channels: [chain_event, chain_state]   # MUST, ≥1
  finality_rule: l1_finalized    # MUST для onchain: l1_finalized | l2_optimistic | l2_zk
  finality_min: null             # DEFAULT по правилу; число блоков как единственный критерий — MUST NOT
  reorg_behavior: INVALID        # MUST, фиксированное значение
  prover_backend: [foundry, halmos]                  # MUST, ≥1
  require_replay: true           # DEFAULT true

attestation:
  expires_after_seconds: 86400   # DEFAULT 86400
  signatures_required: 4         # DEFAULT 4
  signer_roles:                  # MUST, ≥4, все разные
    - product_owner
    - custody_quorum             # заменяет infra_owner для on-chain
    - security_lead
    - verifier
  bundle_format: "fg-bundle/1"   # MUST

limits:                          # опционально
  max_compute_seconds: 1800      # DEFAULT 1800
  max_source_bytes: 5000000      # DEFAULT 5 MB
  max_contract_size_bytes: 24576 # DEFAULT 24 KB (EIP-170)

# FORBIDDEN (валидатор MUST отвергнуть):
# - secrets / private_keys / api_tokens / passwords в любом виде
# - подпись verifier, совпадающая с другой ролью
# - "PROVEN" как входное значение
# - wildcard-доверие адресам или ролям
# - excluded без reason
# - active proxy admin без явного объявления в closure.excluded
```

---

## 4. Бандл аттестации (нормативно)

```
bundle/
├── manifest.json            # хеши всех файлов, JCS-канон, SHA-256
├── flowguard.yml
├── subject.json             # домен, адрес, code_hash, proxy, block
├── chain/
│   ├── block.json           # number, hash, state_root, chain_id, timestamp
│   ├── finality.json        # правило, источник, checkpoint/proof
│   ├── state.json           # слоты: роли, owner, proxy impl, балансы
│   └── privileged-paths.json
├── closure/
│   ├── declaration.json     # Z: пути, исключения, unknown_behavior
│   └── reachability.json    # что проверено, что нет
├── policy/
│   └── invariants.json      # предикаты, домены, ожидаемые свойства
├── proof/
│   ├── results.json         # бэкенд, версия, статус, хеш доказательства
│   ├── counterexamples/     # если найдены
│   └── assumptions.json     # ledger допущений + TCB
├── attacks/
│   └── results.json         # 10 сценариев: результат, трасса, replay_cmd
├── replay/
│   └── manifest.json        # пины, seed, команда, окружение
├── verdict.json             # статус, причина, policy_hash, expiry
└── signatures/
    ├── product_owner.sig
    ├── custody_quorum.sig
    ├── security_lead.sig
    └── verifier.sig
```

| Файл | Обязательные поля | Кто подписывает |
|---|---|---|
| `manifest.json` | `bundle_id`, `schema`, `created_at`, `file_hashes[]`, `merkle_root` | verifier |
| `subject.json` | `kind`, `chain_id`, `address`, `code_hash`, `proxy`, `block` | verifier |
| `chain/finality.json` | `rule`, `source`, `checkpoint_ref`, `status ∈ {FINAL, PROVISIONAL}` | verifier |
| `closure/declaration.json` | `declared_paths`, `discovered_paths`, `diff`, `excluded[]`, `unknown_behavior` | security_lead |
| `policy/invariants.json` | `id`, `predicate`, `domain`, `expected` | автор доказательства |
| `proof/assumptions.json` | `assumptions[]`, `tcb[]` | verifier |
| `attacks/results.json` | `attack_id`, `expected`, `observed`, `replay_cmd` | security_lead + verifier |
| `verdict.json` | `status`, `reason_code`, `policy_hash`, `finality`, `expires_at` | verifier |
| `signatures/*` | `role`, `key_id`, `signed_digest` | соответствующая роль |

**Правило подписи:** подпись покрывает **канонический digest всего бандла** (JCS → SHA-256 → Ed25519), а не только `verdict.json`. Иначе можно перенести вердикт в другой бандл.

---

## 5. Вердикт: формальное правило

Четыре значения, без «в целом нормально»:

| Значение | Условие |
|---|---|
| `PROVEN` | все пять предикатов ниже истинны |
| `NOT_PROVEN` | инвариант опровергнут контрпримером |
| `INCONCLUSIVE` | доказательств недостаточно: неизвестный путь, недоступный bytecode, `PROVISIONAL`-финальность, таймаут |
| `INVALID` | свидетельство бито: код не совпал, реорг, подпись неверна, `address`/`chain_id` не совпали |

```
PROVEN(x) ⟺
      attacks_all_blocked(x)          # 10/10 атак дали BLOCKED
    ∧ invariants_discharged(x)        # каждый инвариант: proved ИЛИ offered+passed
    ∧ closure_complete(x)             # unknown_paths(x) = ∅
    ∧ witness_intact(x)               # все каналы подписаны, nonce сошёлся
    ∧ finality_is_final(x)            # не PROVISIONAL
    ∧ policy_matches(x)               # policy_hash совпадает с подписанным

closure_complete(x) ⟺ ∃p ∈ discovered_paths(x): p ∉ declared_paths(x) = ∅
```

**Правило, которое поддержали все пять рецензентов и которое здесь становится формальным:** неизвестный путь даёт `INCONCLUSIVE`, а не `PROVEN`. Молчаливое расширение границы — самый опасный дефект, поэтому `unknown_paths ≠ ∅` **блокирует** аттестацию, а не «предупреждает».

`PROVISIONAL` — не отдельный вердикт, а поле `finality`. Аттестация с `finality: PROVISIONAL` не может использоваться для освобождения денег, но валидна как отчёт.

---

## 6. CLI: команды, поведение, коды возврата

| Команда | Что делает | Коды возврата |
|---|---|---|
| `flowguard init [--template escrow]` | создаёт `flowguard.yml` с черновиком | 0 |
| `flowguard scan` | инвентаризация: пути движения средств, роли, прокси, writer'ы | 0 |
| `flowguard check` | инварианты и политика: Z3 / Foundry / Halmos; печатает контрпримеры | 0 ok · 1 violation · 3 usage |
| `flowguard attack` | 10 сценариев на `anvil`-форке | 0 all blocked · 1 any passed |
| `flowguard attest` | собирает бандл, считает manifest, просит подписи | 0 |
| `flowguard verify <bundle>` | офлайн-проверка | **0 PROVEN · 1 NOT_PROVEN · 2 INCONCLUSIVE · 4 INVALID** · 3 usage |
| `flowguard replay <bundle>` | воспроизводит с нуля на pinned block | 0 совпало · 5 расхождение |
| `flowguard diff <a> <b>` | что изменилось между аттестациями | 0 |
| `flowguard badge <bundle>` | SVG для README | 0 |

Коды возврата — часть контракта: в CI `flowguard verify` с кодом 2 и 4 должен останавливать сборку так же, как 1.

---

## 7. Движок

### 7.1. `scan` — инвентаризация

**On-chain.** Источники: ABI, runtime bytecode (EOF/legacy), storage slots, event-логи, реестры keeper'ов.
Метод: `slither` (AST + модификаторы) → `cast` (чтение слотов EIP-1967) → `evm disassembler` (опкоды `DELEGATECALL`, `SELFDESTRUCT`, `CALL` с value) → перечисление ролей через `RoleGranted`-логи.
Выход: `privileged-paths.json` — список с полями `path_id`, `kind`, `evidence`, `discoverable_by`, `gaps[]`.

**Legacy (только статика).** `semgrep` (SQL-записи, вызовы), `terraform/k8s`-парсеры, OpenAPI-парсер, извлечение правил авторизации через AST.
Выход: `writers.json` — `(сервис, кред, ресурс, тип записи)`.

**Правило честности:** каждый найденный путь несёт `gaps[]` — «что этот метод не видит». Путь без `gaps` считается дефектом анализатора.

### 7.2. `check` — политика и инварианты

- Legacy: YAML → SMT-LIB → Z3. `deny-beats-allow` кодируется как `allow ∧ ¬deny`. `unsat` = противоречий нет, `sat` = контрпример с конкретными значениями.
- On-chain: инвариант кодируется в Foundry invariant-тест + Halmos символическую проверку. `halmos --function check_INV_1` даёт `pass`/`fail`/таймаут; таймаут → `INCONCLUSIVE`, никогда не `PROVEN`.

### 7.3. `attack` — 10 сценариев

Исполняемые скрипты, не агенты. Каждый: `(setup, action, expected=BLOCKED, replay_cmd)`. Прогон на `anvil` с форком на pinned block. Провал атаки = **провал аттестации**, а не «замечание».

### 7.4. `prove` — доказательство

Интерфейс `Prover` (порт): `prove(invariant, artifact) → {status, certificate, assumptions[], tcb[]}`.
Бэкенды v0.1: Foundry (property/invariant), Halmos (символика). v0.4 — Certora (коммерческий).
Правило: `assumptions ≠ ∅` допустимо, но каждая попадает в `assumptions.json` с полем `what_breaks_if_false`.

---

## 8. Первая цель: escrow

### 8.1. Почему escrow (3 из 5 ответов)

Малый TCB (250–500 строк), машина состояний из трёх состояний, публичные референс-реализации, и — решающее — **escrow является первым потребителем нашей же автовыплаты**. Мы проверяем механизм на продукте, который сами продаём. `[Г]` что это даст достаточный коммерческий спрос.

### 8.2. Три инварианта (сведены из трёх независимых наборов)

| ID | Предикат | Что ловит | Доказуемость |
|---|---|---|---|
| **INV-1** Сохранение | `∀a: balanceOf(escrow,a) ≥ Σ_{e∈{LOCKED,DISPUTED}} amount[e][a]` и `totalDeposited = totalReleased + totalRefunded + Σlocked` | дренаж, скрытый mint/burn, обход учёта | арифметика над storage, индукция по `deposit/release/refund` `[Г]` 3–5 ч-дней |
| **INV-2** Монотонность | `released[e] + refunded[e] ≤ deposited[e]`; переходы только `CREATED→LOCKED→{RELEASED|REFUNDED|DISPUTED}`, без обратных | двойная выплата, refund после release | автомат из 3 состояний, все переходы через один guard `[Г]` 2–4 ч-дня |
| **INV-3** Предусловие выпуска | `release(e) ⇒ status[e]=LOCKED ∧ att_PROVEN ∧ att.subject=e.subject ∧ att.recipient=e.recipient ∧ att.amount=e.amount ∧ final(att.block)` | выплата по чужому/нефинальному/поддельному акту | один переход + сравнение полей `[Г]` 3–5 ч-дней |

**Оговорка, которую нельзя терять:** INV-1 в форме `≥` верна только для токенов без rebasing и fee-on-transfer. Для таких токенов нужна отдельная модель; без неё инвариант даёт `INCONCLUSIVE`.

### 8.3. Привилегированные пути (минимальный перечень)

| Путь | Как находится | Инструмент | Что пропускает |
|---|---|---|---|
| owner / admin / роли | AST-модификаторы + `RoleGranted`-логи + чтение слотов | slither, cast | самописная авторизация (`tx.origin`, подпись админа) |
| upgrade-прокси | EIP-1967 слоты, `slither-check-upgradeability` | cast, slither | нестандартные прокси, diamond без loupe |
| `delegatecall` | опкод-скан + taint цели | disassembler, slither | цель, вычисляемая в рантайме |
| `selfdestruct` | опкод-скан implementation | bytecode scan | поведение после EIP-6780 |
| внешние value-вызовы | `CALL` с value, `transfer/approve/permit` | static + 4byte-декод | динамически собранный calldata |
| keeper / callback | интерфейсы automation, реестры | interface detection | офчейн-keeper без ончейн-роли |
| sweep / rescue-функции | ABI: функции, двигающие произвольный токен | ABI-скан | «админский» rescue под ролью |

**Активный `proxy admin` ⇒ `INVALID`**, а не «покрыто»: если реализацию можно сменить, аттестация относится к другой логике через минуту.

### 8.4. Финальность

| Сеть | Правило | Что даёт `verify` |
|---|---|---|
| Ethereum L1 | `finalized` checkpoint (≈2 эпохи, ~12.8 мин). Счётчик блоков как единственный критерий — **MUST NOT** | `FINAL` только для блока ≤ finalized head |
| L2 optimistic | публикация batch + финализация L1-анкора + истёкший challenge-период | до анкора — `PROVISIONAL` |
| L2 zk | proof верифицирован на L1 и L1-блок финализирован | `FINAL` |
| Реорг между прогоном и подписью | повторный запрос блока по номеру, сверка `block_hash` | расхождение → `INVALID` |

В бандл: `chain_id`, `block_number`, `block_hash`, `state_root`, `finality_proof`, `code_hash`, `tx_hash` (если был).

### 8.5. Десять атак для escrow

| # | Атака | Ожидание | Провал |
|---|---|---|---|
| A1 | `release` от неавторизованного адреса | revert | выпуск прошёл |
| A2 | двойной `release` одного эскроу | revert | двойная выплата |
| A3 | `release` до истечения условия/дедлайна | revert | выпуск раньше |
| A4 | `release` с аттестацией от другого эскроу (replay `subject`) | revert | чужой акт принят |
| A5 | `release` с аттестацией на `PROVISIONAL`-блоке | revert | нефинальный блок принят |
| A6 | `refund` после `release` | revert | возврат после выплаты |
| A7 | вывод токена через `sweep`/`rescue` вне `Z` | revert или запись в `unknown_paths` | вывод прошёл |
| A8 | эскалация роли (`grantRole` себе) | revert | роль выдана |
| A9 | подмена implementation через прокси | `INVALID` | код не совпал с `code_hash` |
| A10 | drain через внешний вызов / реентранси / permit-злоупотребление | revert | средства ушли |

---

## 9. Legacy в v0.1: только статика

Поддерживается: `scan` (writer'ы из кода, IaC, OpenAPI), `check` (правила авторизации → Z3), `plan` (черновик Z из 12 элементов).
Не поддерживается: witness, eBPF, DB-триггер, `Permit`, динамические атаки. Всё это даёт `INCONCLUSIVE` с причиной `dynamic_not_available`, и это **явно печатается**, а не замалчивается.

---

## 10. Детерминизм и воспроизводимость

| Требование | Как обеспечено |
|---|---|
| Один вход → один выход | JCS-канонизация, SHA-256, сортировка ключей и списков |
| Пиннинг окружения | `chain_id` + `block_number` + `block_hash`; версии `slither`, `foundry`, `halmos` в manifest |
| Отсутствие времени в хеше | `created_at` вне подписываемого digest; `expires_at` — отдельным подписанным полем |
| Версионирование формата | `fg-bundle/1`; `verify` поддерживает **все** прошлые версии вечно |
| Запрет скрытой недетерминированности | нет обращений к сети при `verify`; `replay` работает на локальном RPC/форке |

**Гейт релиза:** `flowguard attest` + `flowguard replay` на эталонном escrow дают **байт-в-байт** одинаковый бандл на второй прогон. Красный гейт — релиз не выходит.

---

## 11. Безопасность самого инструмента

| Угроза | Мера |
|---|---|
| Подмена входных данных (чужой repo/адрес) | proof-of-control: OAuth read-only / подпись адреса / commit-челлендж |
| Подмена бандла | signature over весь digest; `verify` не читает ничего вне бандла |
| Атака через содержимое цели (prompt injection в комментариях) | в v0.1 LLM не участвует в вердикте вообще; анализ детерминированный |
| Атака через `flowguard.yml` | неизвестные поля отклоняются; `PROVEN` нельзя задать входом; нет `eval` |
| Supply chain самого инструмента | подписанные релизы, SBOM, воспроизводимая сборка |
| Утечка приватного репо | анализатор не пишет код в логи; бандл не содержит исходников, только хеши |

---

## 12. Критерии приёмки v0.1

Десять проверяемых пунктов. Всё остальное — «сделано, если зелёное».

1. `flowguard scan` на эталонном escrow находит **все** 7 классов путей из §8.3, каждый — с непустым `gaps[]`.
2. `flowguard check` доказывает INV-1..3 на эталонном escrow и находит контрпример в намеренно сломанной версии.
3. `flowguard attack` даёт `BLOCKED` на всех 10 сценариях для эталонного и ≥7/10 `PASSED` для сломанной версии.
4. `flowguard verify` возвращает 0 на валидном бандле и **4 на бандле с подменённым `code_hash`**.
5. `flowguard replay` воспроизводит бандл байт-в-байт на чистой машине.
6. Аттестация на блоке выше `finalized head` даёт `finality: PROVISIONAL` и код возврата 2, а не 0.
7. Симуляция реорга (смена `block_hash` в кэше RPC) даёт `INVALID`.
8. Активный `proxy admin` даёт `INVALID` без возможности обойти флагом.
9. `flowguard.yml` с неизвестным полем в `closure` отвергается с кодом 3.
10. Весь цикл на эталонном escrow исполняется на macOS и Linux, без KVM, ≤30 минут.

---

## 13. Дорожная карта

| Версия | Срок `[Г]` | Содержание |
|---|---|---|
| **v0.1** | 12–16 нед | on-chain escrow end-to-end на ноутбуке; legacy static |
| **v0.2** | +8 нед | legacy-динамика: `anvil`-аналог для репо не нужен, но нужен микроVM + eBPF + witness |
| **v0.3** | +8 нед | медиатор + `Permit` + PL/pgSQL-триггер + Verus |
| **v0.4** | +6 нед | Certora-бэкенд, 5 политик, формат `fg-bundle/1` заморожен |
| **v0.5** | +8 нед | автовыплата с эскроу, диспут-окно, бонды |

---

## 14. Известные слабости (свод из пяти независимых оценок)

Раздел обязательный: это не сноска, а перечень утверждений, которые скорее всего окажутся неверными.

| # | Слабость | Механизм | Горизонт | Ранний признак |
|---|---|---|---|---|
| **W1** | **Неполнота перечня путей** (5/5 рецензентов) | путь через самописную авторизацию, офчейн-keeper или внешний админ-ключ не находится автоматикой | первые 3–10 реальных целей | инцидент на `PROVEN`-цели с путём вне `Z` |
| **W2** | **Бюджет доказательства** (4/5) | моделирование зависимостей, настройка prover, proof-fixing съедают бюджет быстрее, чем появляется переиспользуемый конвейер | первые 5 целей | медиана трудозатрат > плана; ре-аттестация > 15 мин |
| **W3** | **Экономика автовыплат** (3/5) | бонд и потолок малы для крупных сделок; коррелированные ошибки верификатора дают серию клоубэков | 6–12 мес | резерв уходит в минус на первой серии |
| **W4** | **Шум witness / инфляция `INCONCLUSIVE`** (2/5) | нестабильные каналы, расхождения провайдеров по финальности | пилот | медиана `PROVEN` < 2 из-за технических `INCONCLUSIVE`, а не нарушений |
| **W5** | **Дрейф замыкания после хотфикса** (3/5) | новый endpoint/роль появляется вне окна ре-аттестации | 30–90 дней после пилота | `code_hash` расходится, путь отсутствует в `declaration.json` |
| **W6** | **Финальность L2** (2/5) | приём состояния до надёжного L1-анкора | первые 2 недели | диспут со ссылкой на нефинальный блок |
| **W7** | **Монорепо/полиглот ломают автоматизацию** (2/5) | растёт доля ручных исключений и стоимость | 60–90 дней после старта продаж | >30% сканов требуют ручного вмешательства |

**Решение по W1, принятое до кода:** правило `unknown_paths ≠ ∅ ⇒ INCONCLUSIVE` уже закрывает половину риска. Вторая половина — публичный список классов путей, которые анализатор **не видит**, в каждом бандле.

---

## 15. Лицензия, управление, версионирование

- **Код:** Apache-2.0.
- **Спецификация формата:** CC-BY-4.0, чтобы формат могли реализовать другие. Это не потеря: чем больше независимых реализаций, тем ценнее подпись.
- **Версионирование:** `fg-bundle/MAJOR`; MAJOR меняется только при несовместимом изменении; `verify` поддерживает все версии вечно.
- **Управление:** BDFL на старте, публичный RFC для изменений формата, ломающие изменения — только с миграционным тестом.
- **Чего нельзя:** закрывать верификатор, требовать наш сервер для `verify`, менять смысл `PROVEN` задним числом.

---

## Приложение A. Глоссарий

| Термин | Значение |
|---|---|
| `Z` (замыкание) | множество всех путей изменения ресурса, объявленных и обнаруженных |
| `M` (медиатор) | единственная точка решения, через которую проходит путь |
| `Permit` | подписанный непередаваемый токен права, привязанный к объекту, версии и политике |
| `PROVEN` | все пять предикатов §5 истинны; не означает «безопасно» |
| `PROVISIONAL` | валидно, но не финально; не годится для выплат |
| `unknown_path` | обнаруженный, но не объявленный путь; блокирует `PROVEN` |
| `assumptions ledger` | список допущений, при ложности которых утверждение не действует |

## Приложение B. Чек-лист ревьюера бандла

1. `manifest` сходится побайтово? (пересчитать)
2. `code_hash` совпадает с байткодом на `block`?
3. `finality.status = FINAL`?
4. `closure.declaration.diff` пуст (нет неизвестных путей)?
5. Все 10 атак `BLOCKED`?
6. Каждый инвариант: `proved` или `offered+passed`? Таймаут помечен как `INCONCLUSIVE`?
7. `assumptions.json`: каждое допущение имеет `what_breaks_if_false`?
8. Активного `proxy admin` нет?
9. Четыре подписи от четырёх разных ключей?
10. `expires_at` в будущем и не продлён «молча»?
