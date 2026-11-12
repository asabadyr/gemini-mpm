# {{PROJECT_NAME}} — Руководство по проекту и Проектный Адаптер

{{ONE_SENTENCE_PROJECT_PURPOSE}}

> **Профиль правил (`Lite`-адаптер + `agy-mpm-core`)**: Универсальные правила MPM (`00..04`, `20..24`), `/kit-bootstrap`, `/kit-handoff` и ревьюер `code-critic` подгружаются автоматически из глобального плагина `agy-mpm-core` (`agy-mpm-core-ru`). Долгоживущие факты о проекте хранятся в [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md).

---

## 1. Критические красные линии проекта (`🔴`)
- **Топология Git**: {{GIT_TOPOLOGY_NOTE}} — индексируйте только явные пути файлов задачи (`git status -s` до и после коммитов).
- **Целевое окружение тестов**: Запускайте тесты строго через `{{CANONICAL_TEST_CMD}}` (никогда не считайте зелёным результат `0 collected` или пропуск целевых наборов).
- **{{PROJECT_RED_LINE_3_TITLE}}**: {{PROJECT_RED_LINE_3_BODY}}

---

## 2. Канонические команды проекта

| Операция | Команда |
|---|---|
| **Установка / Синхронизация** | `{{INSTALL_CMD}}` |
| **Линтер и проверка форматирования** | `{{LINT_CMD}}` |
| **Проверка типов (Typecheck)** | `{{TYPECHECK_CMD}}` |
| **Запуск тестов** | `{{CANONICAL_TEST_CMD}}` |
| **Сборка / Пакет** | `{{BUILD_CMD}}` |

---

## 3. Структура репозитория

| Путь | Назначение |
|---|---|
| `{{DIR_1}}` | {{DIR_1_ROLE}} |
| `{{DIR_2}}` | {{DIR_2_ROLE}} |
| [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md) | Типизированная `FIFO`-память проекта (`<=4 KB`) |
