---
trigger: glob
globs: "**/*.rs, **/Cargo.toml"
description: "Rust domain rules: ownership, trait composition, fallible error discipline, non-blocking async hygiene, and unsafe isolation."
---

# Domain Pack: Rust (`26`)

## Critical Rust Guardrails

| Area | Trap / Smell | Mandatory Idiomatic Practice |
|---|---|---|
| **Ownership & Borrowing Over `.clone()` Spam** | Defaulting to `.clone()` or wrapping everything in `Arc<Mutex<T>>` to satisfy the borrow checker; unnecessary allocations | Accept `&str`, `&[T]`, or `impl AsRef<Path>` for inputs; reserve `.clone()` and `Arc<T>` strictly for genuine shared ownership requirements and multi-threaded lifetimes |
| **Algebraic Enums, `Newtype` & Trait Composition** | Using boolean flags to represent state; implementing deep OOP-style inheritance emulation; primitive obsession for domain IDs | Model state machines as exhaustive `enum` variants so invalid states are unrepresentable; use `Newtype` wrappers (`struct UserId(String)`); compose small traits over large abstractions |
| **Fallible Error Discipline** | Using `.unwrap()` or `.expect()` on runtime I/O, network requests, or user inputs; returning plain `String` errors | Use `Result<T, E>` with `?`. Use `thiserror` for typed enums in library/domain crates, and `anyhow::Context` at CLI/app entrypoints. Absolutely ban `.unwrap()` on external inputs |
| **Non-Blocking Async (`tokio`) Hygiene** | Calling blocking std `fs`/`net` operations, holding `std::sync::Mutex` across an `.await` point, or running heavy CPU-bound loops on async workers | Never block the async reactor. Use `tokio::task::spawn_blocking` for CPU-heavy tasks and bounded `mpsc::channel` for communication. Use async-aware mutexes only when strictly required |
| **`unsafe` Isolation & Soundness** | Sprinkling `unsafe` blocks throughout business logic; bypassing borrow checker for convenience | Forbid `unsafe` unless absolutely proven necessary for FFI or extreme performance. If required, encapsulate it inside a tiny safe wrapper module with explicit `// SAFETY:` invariant proofs and validate via `miri` |
| **Module Cohesion & Visibility** | Dumping everything into `lib.rs`; over-exposing internal implementation details via `pub` instead of restricting visibility | Keep crate modules under `<=400-600` LOC; aggressively restrict internal functions and types to `pub(crate)`; expose only the minimal, stable `pub` surface necessary for consumers |
| **Allocation & Iterator Idioms** | Eagerly allocating intermediate `Vec` collections in transformation chains; failing to preallocate when the size is known | Prefer lazy iterator adapters (`.map()`, `.filter()`) over intermediate `Vec` allocations unless readability suffers. Always use `with_capacity` in hot loops or when parsing bulk data |
| **Canonical Verification** | Merging PRs with compiler warnings or unformatted code; skipping test suites | Always run `cargo clippy --all-targets --all-features -- -D warnings && cargo fmt -- --check && cargo test`. Treat all warnings as hard errors to maintain a pristine codebase |
