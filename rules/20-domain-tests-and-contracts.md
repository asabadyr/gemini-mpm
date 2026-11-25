---
trigger: glob
globs: "**/tests/**, **/test/**, **/__tests__/**, **/*test*.*, **/*spec*.*"
description: "Test quality inspector, anti-tautology assertions, mental mutation check, no-sleep condition polling, safe multi-core runner/batch parallelism, and 3-level contract testing."
---

# Domain Pack: Test Quality & Contract Pyramid (`20`)

## 1. Anti-Tautology & Mental Mutation Gate (`🔴`)
| Trap | Banned Example | Required Standard |
|---|---|---|
| **Existence-Only Assertion** | `assert res is not None`, `expect(out).toBeDefined()`, `expect(arr.length).toBeGreaterThan(0)` | Assert exact values, state transitions, error codes/messages, and relational postconditions |
| **Mock Echoing** | Mocking a helper to return `X` and asserting output equals `X` without exercising business logic | Assert transformation, branching, boundary handling, and side-effect payloads |
| **Mental Mutation Check** | Writing a green test without checking fault sensitivity | Before finishing, ask: *"If I invert the target `if` branch or shift `<` to `<=` in prod code, does at least one test fail?"* If not, tighten assertions |
| **Parameterized Test Deduplication** | Copy-pasting repetitive per-input test functions; scaling test count to `4x3` copy-paste permutations | Use `@pytest.mark.parametrize`, `it.each`/`test.each`, or Go table-driven subtests instead of duplicating test bodies; scale test count to behavior/branch count |

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

## 4. Safe Multi-Core Parallelism for Long Tests & Local Compute Scripts (`🟡`)
- **When to Parallelize**: For CPU-bound test suites or multi-item local scripts (grid sweeps, simulations, batch processing `>15–30s` across independent scenarios/items), avoid pegging a single CPU core when batches are independent.
- **Runner Parallelism First**: Use `pytest -n auto` (when `pytest-xdist` exists in the repo venv, excluding explicitly single-process/monkey-patched suites), `vitest`/`jest` worker pools, `cargo test`/`nextest`, or `go test -p <cores>` + `t.Parallel()`.
- **Chunked Multi-Core Script Batches**: Shard independent items across `workers = min(max(1, (os.cpu_count() or 2) - 1), len(batches), memory_safe_cap)` (`ProcessPoolExecutor` in Python; worker pool in Node/Go/Rust) instead of sequential 1-core loops.
- **4 Safety Invariants (`🔴`)**:
  1. *Disjoint State & Deterministic Merge*: Workers read immutable slices/paths and write only disjoint temp paths or returned objects (never race on shared files, global dicts, or a single SQLite writer); sort/merge results in deterministic input order.
  2. *`__main__` Guard & `spawn` Context*: Always guard process pool entrypoints with `if __name__ == "__main__":`; use `multiprocessing.get_context("spawn")` when threads, async loops, DB pools, or monkey-patched C-extensions are imported (never unsafe `fork`).
  3. *Anti-Oversubscription*: Pin inner linear-algebra/BLAS threads (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`) when spawning multiple worker processes.
  4. *Memory Budget*: Bound worker count by `available_RAM / per_worker_peak_RAM`; pass file paths/lightweight slice indices rather than duplicating huge datasets per item.
