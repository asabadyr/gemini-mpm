---
trigger: glob
globs: "**/*.go, **/go.mod, **/go.sum"
description: "Go domain rules: consumer-defined interfaces, context propagation, error wrapping, domain packaging, and strict concurrency hygiene."
---

# Domain Pack: Go (`25`)

## Critical Go Guardrails

| Area | Trap / Smell | Mandatory Idiomatic Practice |
|---|---|---|
| **Consumer-Defined Small Interfaces** | Java-style producer `IFooService` bloat with 10+ methods; defining interfaces in the package that implements them rather than where they are used | *"Accept interfaces, return structs"*; interfaces should be defined by the consumer, keeping them to 1-3 methods max. Avoid pre-emptive interface abstractions entirely |
| **`context.Context` & Goroutine Lifecycle** | Storing `ctx` inside structs; launching background goroutines without bounded limits, synchronization, or exit channels | `ctx` must be the first parameter of any function requiring it. Every single goroutine must have an explicit exit path via `ctx.Done()` or `errgroup.WithContext` + bounded concurrency via `SetLimit`. Never leak goroutines into the background |
| **Error Wrapping & Domain Errors** | Ignoring returned `err`, logging and returning the same error twice, or returning opaque `fmt.Errorf` string errors without preserving the causal chain | Use `fmt.Errorf("...: %w", err)` to wrap and preserve causal chains. Use sentinel errors or explicitly typed structs checked via `errors.Is` / `errors.As`. Never just ignore an error |
| **Zero `init()` & Global State** | Using `init()` for database/network I/O, setting up global HTTP variables, and using `panic` outside of application startup | Wire dependencies explicitly via constructor injection in `main()`; completely ban `init()` for side effects, global mutable variables, and `panic` in normal control flow or HTTP handlers |
| **Cohesive Domain Packages** | Junk drawer packages named `util`, `common`, or `helpers`; import cycles caused by tight coupling between unrelated subdomains | Name packages for what they provide (`billing`, `auth`, `payment`); keep packages functionally cohesive; prevent import cycles through careful domain layering and clear separation of concerns |
| **Slice, Map & Mutex Safety** | Concurrent map access leading to fatal crashes; passing structs containing `sync.Mutex` by value; unbound slice growth leading to excessive garbage collection | Always synchronize concurrent map access using `sync.RWMutex` or channels; pre-size slices with `make([]T, 0, n)` to avoid continuous reallocations; never copy lock structs by value |
| **HTTP/gRPC Timeouts & Body Cleanup** | Unbounded `http.Server` accepting connections forever without dropping idle clients; forgetting to close `resp.Body` causing fd leaks | Configure `http.Server` Read/Write/Idle timeouts explicitly, use custom `http.Client{Timeout}` instead of the default, and always `defer resp.Body.Close()` immediately after checking `err == nil` |
| **Canonical Verification** | Shipping code to production without running the race detector or basic static analysis checks, assuming concurrent correctness | Ensure all code passes `go vet ./... && go test -race ./...` + `golangci-lint` where configured. Treat linting warnings as compilation errors and never merge failing CI checks |
