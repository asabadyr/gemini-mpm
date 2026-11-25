# `agy-mpm-core-ru` — Нативная русскоязычная редакция `agy-mpm-kit`

Каталог `ru/` содержит полную нативную русскоязычную редакцию плагина **`AGY MPM Core Kit (RU)` (`v1.9.0`)** для **Google Antigravity** (IDE, Antigravity 2.0 App и `agy` CLI): все универсальные и предметные правила (`rules/`), слэш-скиллы и шаблоны (`skills/`), контекстно-изолированный субагент-ревьюер (`agents/code-critic.md`) и фоллбэк-плейбуки (`extras/manual-rules-fallback/`).

- 📖 **[Полная документация на русском](../README.ru.md)**
- 🌐 **[English Documentation](../README.md)**

---

## Быстрая установка и переключение языка

Используйте штатный установщик из корня репозитория (переключает единый слот `~/.gemini/config/plugins/agy-mpm-core` на каталог `ru/`):

```bash
../install.sh --lang ru
```

Или создайте симлинк вручную:

```bash
ln -sfn ~/Projects/gemini-mpm/ru ~/.gemini/config/plugins/agy-mpm-core
```

> [!CAUTION]
> **Держите подключённой только ОДНУ языковую редакцию одновременно!**
> Antigravity дедуплицирует правила строго по физическому пути файла (`realpath`), а активные плагины суммируются. Использование единого слота `~/.gemini/config/plugins/agy-mpm-core` через `./install.sh --lang ru` гарантирует отсутствие задвоения правил между `en` и `ru`. Управление в 1 клик доступно через `/plugin` (`[agy-mpm-core](customization://agy-mpm-core)` — ссылка всегда строится по имени директории установки `agy-mpm-core`).

---

## Состав русскоязычного пакета (`ru/`)

- **`plugin.json` + `assets/logo.svg`** — манифест (`agy-mpm-core-ru`, `v1.9.0`) и иконка плагина.
- **`rules/00..04`** — универсальное ядро (приоритеты, Item-by-Item покрытие, верификация артефактов, гигиена Git/WIP и секретов с защитой `.agents/teamwork/` в `.gitignore`, 3 режима оркестрации: T0 inline, скоростная 5-ролевая матрица `teamwork`/`swarm` с живым `Promote-on-Review` и резервный `invoke_subagent`, прозрачность по вехам (Milestone Visibility), одноразовый 180s Watchdog, Pre-Wave снимок и Scope-Escape Tilt Kill Switch, безопасный многоядерный батчинг, анти-латентные правила, протоколы Knowledge-First Boot (`knowledge_refs`) и `Read-Once` по референсам (`Grep-Before-Read`, `read_anchors`), шлюз Cache-First, 5-фазная отладка, 6-пунктный аналитический самоконтроль `Visible Self-Check`, `FIFO`-память `memories.md` и ADR).
- **`rules/20..28`** — предметные `glob`-правила (тесты и контракты, безопасный многоядерный параллелизм батчей и тестов `pytest -n auto` / воркеры, Python со `spawn`/`ProcessPoolExecutor`, TypeScript/Node.js, Kubernetes/Docker/Terraform/Shell, SQL/MongoDB и миграции, Go, Rust, JVM/.NET, Frontend UI), расходующие `0` токенов вне целевых файлов.
- **`skills/kit-architecture/`** — слэш-скилл `/kit-architecture` + 3 `references/` шаблона.
- **`skills/kit-bootstrap/`** — слэш-скилл `/kit-bootstrap` (`--lite`, `--full`, `--migrate`) + 8 русскоязычных шаблонов проектного адаптера (`resources/`) с сохранением скоростной матрицы моделей, протокола `Read-Once` и подсказок `knowledge_refs`/`read_anchors`.
- **`skills/kit-handoff/`** — слэш-скилл `/kit-handoff` (`pause`, `resume`, `postmortem`) + шаблон `LATEST.template.md`.
- **`agents/code-critic.md`** — контекстно-изолированный ревьюер без прав записи (`>=80%` фильтр уверенности, Knowledge-First аудит, `Read-Once` + `Grep-Before-Read`, Scope-Escape Guard и защита от тильт-ослабления тестов, оценка маршрута доработки `Rework Routing: WARM_FIX | PROMOTE_MAKER`, вердикты `APPROVE | WARN | BLOCK`).
- **`extras/manual-rules-fallback/`** — ручные плейбуки `@90-playbook-bootstrap.md`, `@91-playbook-handoff.md` и `@92-playbook-architecture.md` (`trigger: manual`) для сред без `skills/`.

### Обновление (`v1.x` -> `v1.9.0`)

1. **Глобальный плагин**: при установке через `install.sh` достаточно `git pull --ff-only` в каталоге `gemini-mpm` (`../install.sh --status` покажет `v1.9.0`). Если папка копировалась вручную — обновите через `../install.sh --lang ru --force`.
2. **Уже инициализированные проекты**: ядро `00..04` и `20..28` обновится само, но для добавления `.agents/teamwork/` в `.gitignore` (после `v1.2–v1.4`) и обновления локального `GEMINI.md` выполните в проекте **`/kit-bootstrap --migrate`** (сохранит все проектные правила с проверкой через `code-critic`).
