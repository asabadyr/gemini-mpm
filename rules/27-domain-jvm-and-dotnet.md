---
trigger: glob
globs: "**/*.java, **/*.kt, **/*.kts, **/*.cs, **/pom.xml, **/build.gradle, **/build.gradle.kts, **/*.csproj"
description: "JVM & .NET domain rules: immutable records, exhaustive pattern matching, structured concurrency, and persistence separation."
---

# Domain Pack: JVM & .NET (`27`)

## Critical JVM & .NET Guardrails

| Area | Trap / Smell | Mandatory Idiomatic Practice |
|---|---|---|
| **Constructor Injection Only** | Using Spring `@Autowired` field injection, `ServiceLocator` patterns, or static mutable singletons for dependencies | Use exclusively `final` (Java) / `readonly` (C#) constructor fields for dependency injection. Ban field injection and static singletons to ensure classes are fully testable without container magic |
| **Immutable Records & Value Objects** | Mutable Java Beans with getters/setters for DTOs; passing raw primitives instead of semantic types | Use Java `record`, Kotlin `data class` (`val`), or C# `record` / `readonly record struct` for DTOs, commands, and events. Maintain strict immutability at the edges of the application |
| **Sealed Hierarchies & Exhaustive Pattern Matching** | Sprawling `instanceof` checks or type-code `if-else` ladders; throwing `IllegalArgumentException` on unknown types | Use `sealed interface`/`sealed class` (Java/Kotlin) or bounded records + switch expressions / `when` patterns to enforce exhaustive compiler checks instead of brittle runtime conditionals |
| **Domain vs Persistence & Transport Separation** | Leaking JPA/Hibernate `@Entity` or EF Core tracked entities directly into HTTP controllers or JSON API responses | Maintain strict separation of concerns: never leak persistence entities to the transport layer. Use Repository interfaces and explicit mappers to translate between domain objects and DTOs |
| **ORM N+1, Transaction & Lazy-Loading Safety** | Making outbound HTTP/RPC calls inside DB `@Transactional` boundaries; unbounded lazy-loading leading to N+1 queries | Keep `@Transactional` narrow. Never do network I/O inside a transaction. Use explicit `JOIN FETCH` / `EntityGraph` / `.Include()` + `.AsNoTracking()` for read queries to prevent performance cliffs |
| **Nullability & Resource Cleanup** | Returning raw `null` leading to NPEs; leaving database connections, streams, or file handles open | Use `Optional<T>` for return types (never fields/params), Kotlin non-null types, or C# `<Nullable>enable</Nullable>`. Always use `try-with-resources` / Kotlin `.use {}` / C# `await using` for cleanup |
| **Structured Concurrency & Cancellation** | Fire-and-forget threads; sync-over-async deadlocks via `.Result`/`.Wait()`; failing to propagate cancellation | Use Java Virtual Threads / bounded executors, Kotlin structured `CoroutineScope`, or C# `CancellationToken` threaded end-to-end. Never block async execution with `.Wait()` causing thread-pool starvation |
| **Canonical Verification** | Shipping without compiling cleanly or running unit/integration tests | Ensure all code passes `mvn test`, `./gradlew check`, or `dotnet build -warnaserror && dotnet test`. Enforce zero compiler warnings and consistent formatting via integrated tooling |
