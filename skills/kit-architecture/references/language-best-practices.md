# Polyglot Language Best Practices

Comprehensive 12-Stack Polyglot Best-Practices Matrix covering idiomatic modularity, OOP/traits/composition, error handling, concurrency, and canonical tooling.

### 1. Python
- **Tooling:** Use `uv` for fast resolution, `ruff` for linting/formatting, and `mypy` for strict type checking.
- **Types & OOP:** Favor `@dataclass(frozen=True, slots=True)` and Pydantic v2 for immutable domain models. Use `typing.Protocol` for duck-typed interfaces.
- **Architecture:** Apply Constructor DI. 
- **Concurrency & Resources:** Use `asyncio` timeouts to prevent hanging coroutines. Manage resources strictly with `@contextmanager`.

### 2. TypeScript / Node.js
- **Types:** Use `unknown` + Zod for runtime boundary narrowing. Leverage discriminated unions + `never` for exhaustive `switch` cases.
- **Architecture:** Interface DI is preferred. Avoid barrel `index.ts` files to prevent circular dependency cycles.
- **Concurrency:** Use `stream/promises` `pipeline` for memory-efficient data processing. Rely on `AbortSignal.timeout` for fetch/async cancellations.

### 3. Go
- **Types & OOP:** Define small, consumer-side 1-3 method interfaces. Favor composition over inheritance.
- **Concurrency:** Pass `context.Context` everywhere. Use `errgroup` for structured concurrency.
- **Error Handling:** Wrap errors with `%w` and inspect them via `errors.Is`/`errors.As`.
- **Architecture:** Organize by domain packages. Avoid `init()` functions entirely. Always run `go test -race`.

### 4. Rust
- **Memory & Types:** Favor borrowing over `.clone()`. Use enum ADTs + traits to model state machines.
- **Error Handling:** Use `thiserror` for library errors and `anyhow` for applications. Achieve zero prod `.unwrap()` or `.expect()`.
- **Concurrency:** Use non-blocking `tokio` channels and async/await.
- **Tooling:** Run `cargo clippy -D warnings` to enforce strict idioms.

### 5. Java / Kotlin (JVM)
- **Types:** Use Java `record` or Kotlin `data class` for immutable DTOs. Leverage `sealed` classes + pattern matching for exhaustive domain events.
- **Architecture:** Enforce strict separation between Domain models and JPA entities. Use Constructor DI (Spring/Guice).
- **Concurrency:** Prefer Virtual Threads (Project Loom) in Java 21+, or structured `CoroutineScope` in Kotlin.

### 6. C# / .NET
- **Types:** Use primary constructors, `record`, or `readonly record struct` for immutability. Enable nullable reference types `<Nullable>enable</Nullable>`.
- **Concurrency & Resources:** Pass `CancellationToken` end-to-end. Use `await using` for async disposables.
- **Data:** Prevent N+1 queries by using EF Core `.AsNoTracking()` for read-only projections.

### 7. Frontend UI (React / Next.js / Vue / Svelte)
- **Components:** Keep components `<=150-200` LOC. Extract custom hooks/composables for logic.
- **State:** Prefer derived state over `useEffect` synchronization. Strictly separate Server state (React Query/SWR) from Client state (Zustand/Pinia).
- **Architecture:** Favor composition (passing `children`/`slots`) over deep prop-drilling. Ensure semantic `a11y` standards.

### 8. PHP (Modern 8.2+ / Symfony / Laravel)
- **Types:** Always use `declare(strict_types=1)`. Use `readonly class` and backed `enum`s for value objects.
- **Architecture:** Prefer PSR-11 Constructor DI over static facades in the core domain. Use FormRequest/DTOs for boundary validation.
- **Data:** Guard against N+1 queries using Eloquent/Doctrine eager-loading.
- **Tooling:** Run `phpstan --level=8` and test with `pest` or `phpunit`.

### 9. Ruby (Ruby 3+ / Rails)
- **Architecture:** Keep ActiveRecord models `<200-300` LOC, free of god-callbacks. Extract logic into Plain Old Ruby Objects (Service/Query/Form/Policy objects).
- **Types:** Use `Data.define` for immutable value objects.
- **Data:** Use `includes` and `strict_loading` to prevent N+1 queries.
- **Tooling:** Enforce style and specs with `rubocop` and `rspec`.

### 10. Elixir / OTP (Phoenix)
- **Architecture:** Build a functional core wrapped in an OTP process shell. Use Phoenix Context boundaries to separate business domains from Web controllers/LiveViews.
- **Data:** Use `Ecto.Multi` for explicit database transactions.
- **Concurrency:** Rely on supervision trees. Use `GenServer` *only* for runtime state and concurrency—never just for code organization!
- **Tooling:** Ensure `mix credo --strict && mix dialyzer && mix test` passes.

### 11. Swift / Dart (Mobile & Cross-Platform)
- **Types & Architecture:** Swift: Use Protocol-Oriented Programming and value-type `struct`s. Dart: Use sound null-safety, immutable `sealed class` states, and unidirectional BLoC/Riverpod architecture.
- **Concurrency & Memory:** Swift: Use `async/await` structured `Task` cancellation and `@MainActor` isolation. Use weak references `[weak self]` against retain cycles.
- **Tooling:** `swift test` / `flutter analyze && flutter test`.

### 12. C / C++ (Modern C++20/23 & Systems C)
- **Memory:** Rely on RAII deterministic ownership. Use `std::unique_ptr`, `std::span`, and `std::string_view`. Ensure zero raw owning `new`/`delete`.
- **Types:** Use `[[nodiscard]]` aggressively. Return `std::expected` or `std::optional` instead of raw error codes.
- **Architecture:** Follow the Rule of Zero/Five. 
- **Tooling:** Run `clang-tidy` and compile with `-fsanitize=address,undefined` (ASan/UBSan).


## Cross-Cutting Concerns: Logging, Metrics, and Tracing

Regardless of the language stack, cross-cutting concerns like logging and telemetry must be handled uniformly without polluting domain logic.
- **Structured Logging:** Emit logs as structured JSON (e.g., `pino` in Node, `structlog` in Python, `slog` in Go). Include correlation IDs to trace requests across microservice boundaries.
- **Middleware/Interceptors:** Inject logging, metrics, and tracing at the transport boundary (HTTP middleware, gRPC interceptors) or via Decorators, keeping the core domain pure.

## Dependency Management & CI/CD Tooling

A clean architecture requires strict automated enforcement.
- **Lockfiles:** Always commit `package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`, etc., to ensure reproducible builds.
- **Automated Dependency Updates:** Use tools like Dependabot or Renovate to keep libraries current, preventing technical debt from accumulating.
- **Continuous Integration:** Every PR must run the formatter, linter, static type checker, unit tests, and a build step. If the CI fails, the PR cannot be merged. This non-negotiable rule prevents architectural degradation.