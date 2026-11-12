---
name: kit-architecture
description: "Clean architecture, SOLID/OOP design patterns, safe chunked refactoring of giant/God files, DRY deduplication, and polyglot language best practices (/kit-architecture [audit | refactor | patterns | lang])."
---

# `kit-architecture` Progressive-Disclosure Skill

This skill provides a comprehensive toolkit for enforcing clean architecture, applying SOLID and OOP design patterns, executing safe and chunked refactoring of God files, maintaining DRY deduplication, and adhering to polyglot language best practices. 

The skill is automatically activated when designing multi-module code, splitting large files (>400 LOC), consolidating duplicated code, or working in a stack outside standard rules (rules 21..28).

## Modes of Operation

You can trigger specific workflows using the `/kit-architecture` command followed by the desired mode:

### 1. `/kit-architecture audit [path]`
Runs a quantitative codebase hygiene scan on the specified path (or current directory if omitted).
- **Checks executed:**
  - Files exceeding `400` (or `600`) LOC.
  - Classes exceeding `300` LOC.
  - Functions exceeding `50` LOC.
  - Deep indentation exceeding `3` levels.
  - Repeated `if/elif` or `switch` chains indicating missing polymorphism.
  - Duplicated blocks (`>80%` similarity).
  - Concrete I/O coupled inside domain classes.
  - Circular imports.
- **Classification:** Categorizes code into `Production Mainline` vs `Prototype/Scratch`.
- **Output:** A prioritized remediation table ranked by business impact and change-frequency.

### 2. `/kit-architecture refactor <target>`
Executes behavior-preserving chunked decomposition of the target file or module.
- Loads `references/refactoring-god-files.md`.
- Applies safe, chunked steps (`<=200` LOC per step).
- Requires characterization or existing tests to pass green before and after each step.
- Ensures zero dead or parallel implementations.
- Requires Maker + `code-critic` verification.
- Concludes with an `Added / Removed / Net LOC` summary.

### 3. `/kit-architecture patterns [problem]`
Diagnoses coupling and complexity smells to select the minimal foundational or situational OOP/architectural pattern.
- Loads `references/design-patterns-and-solid.md`.
- Avoids speculative YAGNI (You Aren't Gonna Need It) bloat.
- Provides a tailored pattern recommendation to solve the concrete structural smell.

### 4. `/kit-architecture lang <stack>`
Provides idiomatic modularity, OOP/traits/composition patterns, error handling, concurrency, and canonical build/lint/test commands across 12 tech stacks.
- Loads `references/language-best-practices.md`.
- Integrates with standard rules (21..28) when applicable.

## Automatic Activation Triggers
- When the agent detects a file growing beyond `400` LOC.
- When `>3` repeated `switch` or `if/elif` chains over the same type tag are detected.
- When cross-domain code duplication approaches `80%`.
- When cyclical dependencies or tight I/O coupling in domain logic are noticed.

By adhering to these structured protocols, we ensure that the codebase remains maintainable, scalable, and decoupled, avoiding the accumulation of technical debt and architectural anti-patterns.


### Detailed Usage Guidelines

When deciding to run an architecture audit, keep in mind that legacy projects may require multiple chunked refactor sessions. An initial run of `/kit-architecture audit` might output dozens of warnings. Do not attempt to fix all of them simultaneously. Instead, sort by business impact and file modification frequency (files modified frequently with high complexity are your primary targets).

When using the `refactor` mode, you are delegating the cognitive load of safe decomposition to the agent. The agent will strictly follow the chunked refactoring playbook, meaning you can expect smaller, iterative pull requests rather than a massive rewrite. This dramatically reduces regression risk and makes code review manageable.

For the `patterns` and `lang` modes, use them proactively when starting a new module. For example, typing `/kit-architecture lang python` before laying out a new microservice guarantees that your dependency injection, typing, and modularity start off on the right foot without accumulating early technical debt.