---
trigger: manual
description: "@92-playbook-architecture.md playbook for quick manual clean architecture audits, refactoring strategies, pattern selection, and language idioms."
---

# Manual Fallback Playbook: Architecture (`92-playbook-architecture`)

This playbook is the manual checklist for enforcing clean architecture and safe chunked refactoring when automatic progressive disclosure is bypassed.

## 1. Quick Audit Thresholds (`audit`)
If a file or module crosses these thresholds, it requires immediate decomposition:
- **Files:** `> 400` (or `600`) LOC.
- **Classes:** `> 300` LOC.
- **Functions:** `> 50` LOC.
- **Complexity:** Deep indentation `> 3`, or cyclomatic complexity `> 10`.
- **Duplication:** `> 80%` identical code in the same domain.
- **Anti-patterns:** Circular imports or concrete I/O inside pure domain classes.

## 2. Safe Refactoring Protocol (`refactor`)
Never refactor without a safety net. Apply these constraints:
- **Test First:** Ensure existing tests or characterization tests are green BEFORE touching the code.
- **Chunked Steps:** Move a maximum of `<= 200` LOC per refactoring step.
- **Verify Immediately:** Run the test suite after every chunk. Rollback on red.
- **One Implementation:** Delete old implementations; leave no dead code or parallel pathways.
- **Calculate Net LOC:** Track `Added`, `Removed`, and `Net` LOC.

## 3. Pattern Selection Matrix (`patterns`)
Only apply a pattern if the specific structural smell exists:
- **Tight Coupling ->** Constructor Dependency Injection (DI).
- **Scattered Domain Logic ->** Service Layer (Facade).
- **Database Leakage ->** Repository Pattern.
- **External API Churn ->** Anti-Corruption Layer (Adapter).
- **Endless Switch Statements ->** Strategy / Handler Registry.
- **Cyclic `A->B->C->A` ->** Domain Events / Mediator.

## 4. Universal Polyglot Rules (`lang`)
Regardless of the tech stack:
- **Dependencies:** Inject dependencies (Constructor DI / Interface DI).
- **Immutability:** Map boundaries to immutable DTOs (e.g., `readonly`, `frozen`, `record`, `dataclass`).
- **N+1 Guard:** Always eager-load or use dataloaders in ORMs.
- **Concurrency:** Pass cancellation tokens/contexts end-to-end; never leave hanging promises or routines.
- **Linting:** Maintain zero warnings in the native linter/compiler (`ruff`, `clippy`, `tsc`, `phpstan`, etc.).


## 5. Escalation & Reviews
When manual refactoring exceeds standard limits (e.g., refactoring an intertwined 5,000+ LOC legacy file with zero test coverage), trigger a manual escalation:
- Do not attempt to refactor without first writing characterization tests.
- Discuss the planned abstractions with a senior engineer or domain expert.
- Keep PRs small and focused. A PR should strictly only contain the refactoring changes without any new feature additions. Mixing refactoring and feature work in the same PR obscures intent and dramatically increases the risk of regressions. Reviewers must be able to focus solely on structural equivalence.