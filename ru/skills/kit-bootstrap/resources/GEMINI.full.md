# {{PROJECT_NAME}} — Корневое рабочее пространство и Проектный Адаптер

{{TWO_SENTENCE_WORKSPACE_OVERVIEW}}

> **Профиль правил (`Full`-адаптер + `agy-mpm-core`)**: Универсальные правила MPM (`00..04`, `20..24`), `/kit-bootstrap`, `/kit-handoff` и ревьюер `code-critic` загружаются из глобального плагина `agy-mpm-core` (`agy-mpm-core-ru`). Правила CI/CD, выкатки и эксплуатации проекта находятся в [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md) (а границы конфиденциальности — в [`.agents/rules/11-project-confidentiality.md`](file://{{WORKSPACE_PATH}}/.agents/rules/11-project-confidentiality.md), если модуль включён).

---

## 1. Главные красные линии проекта (`🔴`)
1. **{{RED_LINE_1_TITLE}}**: {{RED_LINE_1_SUMMARY}}
2. **{{RED_LINE_2_TITLE}}**: {{RED_LINE_2_SUMMARY}}
3. **{{RED_LINE_3_TITLE}}**: {{RED_LINE_3_SUMMARY}}
4. **Топология Git и песочниц субагентов**: {{GIT_TOPOLOGY_RED_LINE}}
5. **Конфиденциальность и секреты**: {{CONFIDENTIALITY_OR_SECRET_RED_LINE}}

---

## 2. Карта директорий и подпроектов

| Компонент / Путь | Артефакт / Рантайм | Ветка деплоя | Назначение |
|---|---|---|---|
| [`{{COMPONENT_1}}`](file://{{WORKSPACE_PATH}}/{{COMPONENT_1}}) | `{{ARTIFACT_1}}` | `{{BRANCH_1}}` | {{ROLE_1}} |
| [`{{COMPONENT_2}}`](file://{{WORKSPACE_PATH}}/{{COMPONENT_2}}) | `{{ARTIFACT_2}}` | `{{BRANCH_2}}` | {{ROLE_2}} |

---

## 3. Канонические команды

| Контур | Lint / Typecheck | Тесты | Сборка и регламент выкатки |
|---|---|---|---|
| `{{SCOPE_1}}` | `{{LINT_1}}` | `{{TEST_1}}` | См. [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md) |

---

## 4. Иерархическая база знаний (`.agents/knowledge/`)

Перед широким поиском по кодовой базе сверяйтесь с [`.agents/knowledge/00-INDEX.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/00-INDEX.md) и [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md):
- **Главный индекс и матрица авторитетности**: [`.agents/knowledge/00-INDEX.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/00-INDEX.md)
- **Ограниченная память проекта (`FIFO`)**: [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md)
- **Регламент эксплуатации и CI/CD**: [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md)
- **Активные задачи и постмортемы**: [`.agents/knowledge/active-tasks.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/active-tasks.md), [`.agents/knowledge/postmortems.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/postmortems.md)
