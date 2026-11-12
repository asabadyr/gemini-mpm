---
trigger: glob
globs: "**/*test*.py, **/*_test.go, **/*.test.ts, **/*.test.tsx, **/*.spec.ts, **/*.spec.js, **/tests/**"
description: "Test quality inspector, anti-tautology assertions, mental mutation check, no-sleep condition polling, no test-only prod methods, and 3-level contract testing."
---

# Domain Pack: Test Quality & Contract Pyramid (`20`)

## 1. Anti-Tautology & Mental Mutation Gate (`🔴`)
| Trap | Banned Example | Required Standard |
|---|---|---|
| **Existence-Only Assertion** | `assert res is not None`, `expect(out).toBeDefined()`, `expect(arr.length).toBeGreaterThan(0)` | Assert exact values, state transitions, error codes/messages, and relational postconditions |
| **Mock Echoing** | Mocking a helper to return `X` and asserting output equals `X` without exercising business logic | Assert transformation, branching, boundary handling, and side-effect payloads |
| **Mental Mutation Check** | Writing a green test without checking fault sensitivity | Before finishing, ask: *"If I invert the target `if` branch or shift `<` to `<=` in prod code, does at least one test fail?"* If not, tighten assertions |

## 2. Async Determinism & SUT Isolation (`🔴`)
| Rule | Enforcement |
|---|---|
| **Ban Arbitrary `sleep()` / `setTimeout()`** | **NEVER** synchronize async tests with fixed wall-clock sleeps (`time.sleep(0.5)`, `await new Promise(r => setTimeout(r, 200))`). Poll observable state (`waitFor`, event promises, deterministic fake timers) with bounded timeouts |
| **Never Mock the SUT** | Mock external I/O boundaries only (network, clock, third-party APIs); **NEVER** stub internal methods on the System Under Test |
| **Ban Test-Only Production Methods** | **NEVER** add `_for_testing()`, `resetForTest()`, or test-only flags onto production classes; use constructor/dependency injection or test-scoped fixtures |
| **Protect Shared Fixtures** | Never mutate module/session-scoped fixtures in place; copy inputs per test and honor existing `conftest.py` / test helpers as hard constraints |

## 3. 3-Level Contract Testing Pyramid (`🟡`)
For contract-bearing, financial, parsing, or state-machine functions, layer tests across 3 levels:
1. **Level 1 — Postcondition & Boundary Unit Tests**: Cover nominal paths, empty/zero/max boundaries, idempotency, and exact error outcomes.
2. **Level 2 — Property-Based Invariant Tests** (`hypothesis` / `fast-check` / `rapid`): Encode preconditions directly in **generators** (avoid heavy `assume()` filtering that starves test cases) and assert structural invariants (round-trip, conservation, ordering, monotonicity).
3. **Level 3 — Negative Precondition Tests**: Feed invalid types, out-of-range values, expired/malformed tokens, and concurrent races to prove explicit rejection without partial state corruption.
