# `agy-mpm-core-ru` — Нативная русскоязычная редакция `agy-mpm-kit`

Каталог `ru/` содержит полную нативную русскоязычную редакцию плагина **`AGY MPM Core Kit (RU)` (`v2.3.1`)** для **Google Antigravity** (IDE, Antigravity 2.0 App и `agy` CLI): все универсальные и предметные правила (`rules/`), слэш-скиллы и шаблоны (`skills/`), контекстно-изолированный субагент-ревьюер (`agents/code-critic.md`), хук защиты от удаления (`hooks.json`), симлинк на скрипты (`scripts/ -> ../scripts`) и фоллбэк-плейбуки (`extras/manual-rules-fallback/`).

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

## Python-окружение, менеджеры пакетов и виртуальные среды (`v2.3.0`)

### 1. Требования к рантайму
- **`Python >= 3.8`**.
- **Только стандартная библиотека**: `0` внешних зависимостей PyPI в рантайме хуков и скриптов (`sys`, `os`, `re`, `json`, `subprocess`, `argparse`, `time`, `pathlib`).
- В корне репозитория присутствует `pyproject.toml` со спецификацией проекта и опциональной группой `[dev]` (`pytest`, `ruff`) исключительно для тестирования самого кита.

### 2. Принцип работы `scripts/mpm-py` и пиннинга интерпретатора
Для надёжного запуска `PreToolUse` хука и вспомогательных CLI-скриптов используется обёртка `scripts/mpm-py`:
- **Auto-detect + Pin**: при установке `./install.sh` автоматически находит подходящий интерпретатор Python `>=3.8` и пинит его абсолютный путь в глобальном файле окружения `~/.gemini/config/agy-mpm-core.env`.
- **Dock / GUI Launchpad**: когда IDE Antigravity запускается из GUI/Dock, переменная `PATH` часто урезана до системного минимума (`/usr/bin:/bin`). Пин в `agy-mpm-core.env` гарантирует безотказный запуск хука даже при отсутствии Python в урезанном GUI `PATH`.
- **Чистота Git**: пиннинг через внешний файл окружения оставляет отслеживаемый репозиторный `hooks.json` абсолютно чистым и переносимым между разработчиками и ОС.
- **Цепочка разрешения (Resolution Chain)** в `scripts/mpm-py`:
  1. Явная переменная окружения `$AGY_MPM_PYTHON` (если задана).
  2. Запиненный путь в `~/.gemini/config/agy-mpm-core.env` (создаётся установщиком).
  3. Локальный виртуальный venv кита (`.venv/bin/python`).
  4. Активное окружение текущей сессии (`$VIRTUAL_ENV/bin/python` или `$CONDA_PREFIX/bin/python`).
  5. Поиск в `PATH` / Homebrew (`/opt/homebrew/bin/python3`, `/usr/local/bin/python3`, `python3`, `python`).
  6. Менеджеры версий: `uv`, `pyenv`, `mise`, `asdf`.

### 3. Поддержка менеджеров пакетов и виртуальных окружений
Вы можете использовать любой инструмент управления Python:

- **Системный Python / Homebrew** (по умолчанию):
  ```bash
  ./install.sh --lang ru
  ```
- **Встроенный `venv` / `virtualenv`**:
  ```bash
  ./install.sh --lang ru --venv=stdlib          # Создаст .venv через python3 -m venv
  ./install.sh --lang ru --venv=virtualenv      # Создаст .venv через virtualenv
  # Либо передайте существующий venv напрямую:
  ./install.sh --lang ru --python .venv/bin/python
  ```
- **`uv`** (быстрый менеджер пакетов):
  ```bash
  ./install.sh --lang ru --venv=uv              # Создаст .venv через uv venv
  # Если нужен конкретный рантайм:
  uv python install 3.12
  ./install.sh --lang ru --python "$(uv python find 3.12)"
  ```
- **Poetry / PDM / Hatch**:
  ```bash
  ./install.sh --lang ru --python "$(poetry run which python)"
  # или для PDM:
  ./install.sh --lang ru --python "$(pdm info --where)/.venv/bin/python"
  ```
- **Conda / Mamba**:
  ```bash
  ./install.sh --lang ru --python "$CONDA_PREFIX/bin/python"
  ```
- **Pyenv / Mise / asdf**:
  ```bash
  ./install.sh --lang ru --python "$(pyenv which python3)"
  # или mise:
  ./install.sh --lang ru --python "$(mise which python)"
  ```

### 4. Совместимость с `.venv` рабочих проектов
Интерпретатор для хуков плагина и проверочных скриптов полностью изолирован: запуск тестов внутри целевого репозитория (например, `pytest`) запускается агентом в проектном виртуальном окружении проекта, тогда как хук безопасности `PreToolUse` выполняется через независимый интерпретатор `mpm-py`.

### 5. Диагностика и проверка статуса
```bash
./install.sh --doctor        # Глубокая проверка Python, пиннинга, прав и хуков
./install.sh --status        # Быстрая сводка активной редакции, версии и пути плагина
```

---

## Состав русскоязычного пакета (`ru/`)

- **`plugin.json` + `assets/logo.svg`** — манифест (`agy-mpm-core-ru`, `v2.3.1`) и иконка плагина.
- **`hooks.json`** — хук жизненного цикла `PreToolUse` (Deletion Shield на `run_command` с запуском `scripts/mpm-py scripts/destructive-cmd-guard.py --lang ru`; в `v2.3.1` устранены ложные `parse_failure` промпты на комментариях `#`, переносах строк `\`, heredoc `<<EOF`, bash-массивах, безопасных glob `/tmp/prefix_*` и недеструктивных командах).
- **`scripts/` -> `../scripts`** — симлинк на скрипты стандартной библиотеки Python 3: `mpm-py` (обёртка auto-detect + pin), `guard_common.py`, `destructive-cmd-guard.py`, `mpm-git-guard.py`, `mpm-live-watch.py`.
- **`rules/00..04`** — универсальное ядро (приоритеты, Item-by-Item покрытие, верификация артефактов, Deletion Shield и нативные файловые инструменты вместо шелла, гигиена Git/WIP и секретов с `mpm-git-guard` snapshot/audit/restore через `mpm-py`, цикл локальных коммитов `teamwork` без push, 3 режима оркестрации: T0 inline, скоростная 5-ролевая матрица `teamwork`/`swarm` с живым `Promote-on-Review` и резервный `invoke_subagent`, шлюз Pre-Dispatch T1 trivial opt-in & hard veto, Contract-First DISPATCH (`file_contracts`), замороженные `acceptance_checks`, Pre-Dispatch T3 Escalation, общий multi-agent scratch `<appDataDir>/scratch/<slug>/`, прозрачность по вехам Milestone Visibility, непрерывный нулевой по токенам монитор `mpm-live-watch` и резервный 180s Watchdog, Pre-Wave снимок и Scope-Escape Tilt Kill Switch, безопасный многоядерный батчинг, протоколы Knowledge-First Boot (`knowledge_refs`) и `Read-Once` по референсам (`Grep-Before-Read`, `read_anchors`), шлюз Cache-First, 5-фазная отладка, 6-пунктный аналитический самоконтроль `Visible Self-Check`, `FIFO`-память `memories.md` и ADR).
- **`rules/20..28`** — предметные `glob`-правила (тесты и контракты, безопасный многоядерный параллелизм батчей и тестов `pytest -n auto` / воркеры, Python со `spawn`/`ProcessPoolExecutor`, TypeScript/Node.js, Kubernetes/Docker/Terraform/Shell, SQL/MongoDB и миграции, Go, Rust, JVM/.NET, Frontend UI), расходующие `0` токенов вне целевых файлов.
- **`skills/kit-architecture/`** — слэш-скилл `/kit-architecture` + 3 `references/` шаблона.
- **`skills/kit-bootstrap/`** — слэш-скилл `/kit-bootstrap` (`--lite`, `--full`, `--migrate`) + 8 русскоязычных шаблонов проектного адаптера (`resources/`) с сохранением скоростной матрицы моделей, протокола `Read-Once`, чеклиста `v2.3.0` и подсказок `knowledge_refs`/`read_anchors`.
- **`skills/kit-handoff/`** — слэш-скилл `/kit-handoff` (`pause`, `resume`, `postmortem`) + шаблон `LATEST.template.md`.
- **`agents/code-critic.md`** — контекстно-изолированный ревьюер без прав записи (`>=80%` фильтр уверенности, Knowledge-First аудит, `Read-Once` + `Grep-Before-Read`, Deletion Shield & Scope-Escape Guard с проверкой через `mpm-py`, аудит локальных коммитов, проверка `file_contracts`, замороженных проверок и защита от бутафории, защита от тильт-ослабления тестов, оценка маршрута доработки `Rework Routing: WARM_FIX | PROMOTE_MAKER | PROMOTE_REVIEWER -> <frontier-model> (High)`, вердикты `APPROVE | WARN | BLOCK`).
- **`extras/manual-rules-fallback/`** — ручные плейбуки `@90-playbook-bootstrap.md`, `@91-playbook-handoff.md` и `@92-playbook-architecture.md` (`trigger: manual`) для сред без `skills/`.

---

## Миграция и обновление с версий до `v2.0` (`v1.x`) и `v2.0–v2.2` до `v2.3.0`

### Маршрут для пользователей устаревших версий (до `v2.0` / `v1.x` и `v2.0–v2.2`)
Если вы обновляетесь с версий до `v2.0` (где ещё не было слоя Python и `hooks.json`, либо плагин был скопирован вручную без симлинка), следуйте пошаговому алгоритму:

1. **Получите актуальный код**:
   ```bash
   cd ~/Projects/gemini-mpm
   git pull --ff-only
   ```
2. **Запустите автоматическую миграцию**:
   ```bash
   ./install.sh --migrate --lang ru
   ```
   *Что делает флаг `--migrate`*:
   - Безопасно сохраняет старую не-симлинк папку плагина в резервную копию `~/.gemini/config/plugins/agy-mpm-core.bak.<timestamp>`.
   - Проверяет наличие Python `>=3.8` в системе или разворачивает виртуальное окружение через `uv` / `virtualenv` / `venv`.
   - Пинит интерпретатор в `~/.gemini/config/agy-mpm-core.env`.
   - Прогоняет smoke-тест скрипта `destructive-cmd-guard.py` **ДО** активации хуков в Antigravity.
   - Создаёт корректный симлинк на выбранную редакцию (`ru/`).
3. **Проверьте окружение**:
   ```bash
   ./install.sh --doctor
   ```
   Убедитесь, что все пункты отмечены зелёным (`PASS`).
4. **Проверьте и обновите проекты**:
   ```bash
   ./install.sh --check-projects ~/Projects/*
   ```
   В каждом проекте, где утилита порекомендует обновиться, откройте Antigravity и выполните:
   ```text
   /kit-bootstrap --migrate
   ```
   Это обновит проектный `GEMINI.md` и добавит `.agents/teamwork/` в `.gitignore` с гарантией нулевых потерь проектных правил.
