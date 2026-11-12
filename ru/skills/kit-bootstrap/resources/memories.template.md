# Память проекта (`memories.md`)

> **Схема (`04-memory-knowledge-adr.md`)**: Однострочные записи `- [YYYY-MM-DD] <факт>`, общий объём **`<=4 KB` (`4,096` байт)**.
> **Политика вытеснения**: `CRITICAL` (макс. 20, **без авто-вытеснения**); `Environment` (макс. 15, **FIFO**); `Decisions` (макс. 20, **FIFO**); `Patterns` (макс. 20, **FIFO**); `Gotchas` (макс. 15, **FIFO** — при заполнении удалять самую старую верхнюю строку секции, новую добавлять вниз).

## CRITICAL
- [{{YYYY_MM_DD}}] {{CRITICAL_FACT_1}}

## Environment
- [{{YYYY_MM_DD}}] {{ENV_FACT_1}}

## Decisions
- [{{YYYY_MM_DD}}] {{DECISION_FACT_1}}

## Patterns
- [{{YYYY_MM_DD}}] {{PATTERN_FACT_1}}

## Gotchas
- [{{YYYY_MM_DD}}] {{GOTCHA_FACT_1}}
