# Project Memory (`memories.md`)

> **Schema (`04-memory-knowledge-adr.md`)**: Single-line `- [YYYY-MM-DD] <fact>` entries, total size **`<=4 KB` (`4,096` B)**.
> **Eviction Policy**: `CRITICAL` (max 20, **never auto-evict**); `Environment` (max 15, **FIFO oldest-first**); `Decisions` (max 20, **FIFO**); `Patterns` (max 20, **FIFO**); `Gotchas` (max 15, **FIFO** — delete top-most oldest entry in section when full, append newest at bottom).

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
