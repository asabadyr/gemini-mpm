---
trigger: model_decision
description: "Activate when writing or refactoring code, designing modules, refactoring giant/duplicated files, applying OOP/design patterns, debugging errors or test failures, reviewing diffs, or dispatching Maker and Adversarial Checker (Code Critic) subagents."
---

# Code Hygiene, 5-Phase Debugging & Adversarial Critic (`02`)

## 1. Engineering Constraints, Modularity & Architecture (`🔴`)

### 1.1. Core Call-Chain & Constraint Principles
| Principle | Enforcement |
|---|---|
| **Ban Import-Time Side Effects** | Module top-level imports **MUST NEVER** open DB/network sockets, spawn background loops/threads, read unguarded secrets, or mutate disk/env |
| **Provided Artifacts Are Constraints** | Existing tests, fixtures (`conftest.py`, seed data), and public schemas are binding contracts: fix production code when existing tests fail—**NEVER** weaken assertions, delete failing tests, or shadow fixtures unless specs explicitly changed |
| **Whole Call-Chain Walk** | Trace `Entrypoint -> Caller/Orchestrator -> Callee -> DB/External Side-Effect -> Return/Error Handling` end-to-end before coding or approving a fix |
| **Contracts Before Bodies** | Specify preconditions, postconditions, invariants, and error surfaces before writing bodies (skip ceremony only on `<=20` LOC non-auth/crypto hotfixes) |

### 1.2. Production Mainline vs Prototype/Scratch Calibration
| Context / Scope | Allowed Architecture & Enforcement |
|---|---|
| **Production Mainline**<br>*(DEFAULT whenever ambiguous)* | `src/`, `app/`, `pkg/`, `internal/`, `lib/`, services. Requires full SOLID/OOP/DI boundaries, hard LOC & complexity caps, zero copy-paste duplication, proven design patterns over ad-hoc branching, full `code-critic` enforcement. |
| **Prototype / Scratch / One-Off** | `scratch/`, `scripts/oneoff*`, user-labeled throwaway PoC/spike. Single cohesive file (`<200-300` LOC) allowed without speculative factories/DI; **MUST NEVER** be imported by or merged into mainline production code without modularization. |

### 1.3. Hard Modularity, Size & Complexity Caps (Mainline Code)
| Scope | Thresholds & Guardrails |
|---|---|
| **File** | Plan modular split at **`400` LOC**, hard cap **`600` LOC** (ban `600+` LOC God files). |
| **Class / Struct / UI Component** | **`<=300` LOC** (`<=200` LOC for UI components), strict Single Responsibility (`SRP`). |
| **Function / Method** | Target **`<=30` LOC**, hard cap **`50` LOC**; Cyclomatic Complexity **`<=10`**; Max nesting depth **`<=3`** (enforce guard clauses / early returns over arrow-spaghetti). |

### 1.4. Search-Before-Create & DRY Deduplication
| Principle | Action |
|---|---|
| **Search First & One Implementation** | Grep/search existing modules, helpers, and services *before* writing new code; **One Implementation Per Feature** (delete superseded inline/dead code immediately). |
| **Consolidation Thresholds** | Extract reusable functions/collaborators when **`2+` blocks share `>80%` similarity** in the same domain, when shared logic is **`>=30` LOC**, or **`>50%` structural similarity** across modules. |
| **Anti-Wrong-DRY Guard** | Never merge distinct business domains that merely share incidental 5-line shapes, and never merge test-only helpers into production modules. |

### 1.5. OOP, SOLID, Composition & Code-Smell Patterns
Apply to solve concrete smells, never speculative YAGNI; cross-reference `/kit-architecture`.

| Code Smell / Structural Defect | Required Design Pattern / Architecture Fix |
|---|---|
| Deep Inheritance | **Composition over Inheritance** (inheritance depth `<=2`; prefer interfaces/`Protocol`/traits + injected collaborators). |
| Hidden Side-Effects / Global State | **Constructor/Parameter Dependency Injection (DI)** (ban instantiating concrete DB/HTTP/SDK clients or mutating global state inside domain classes). |
| `3+` repeated `if/elif`/`switch` branches on type/provider/status | **Strategy / Polymorphic Handler Registry / Dispatch Map**. |
| Domain logic coupled to SQL/ORM/NoSQL queries | **Repository**. |
| External 3rd-party API/SDK models leaking into domain | **Adapter / Anti-Corruption Layer (ACL)**. |
| Complex multi-variant object creation | **Factory / Builder**. |
| Cyclic service dependencies (`A -> B -> C -> A`) | **Domain Events / Pub-Sub**. |
| Cascading slow upstream failures | **Circuit Breaker / Bulkhead + Timeout**. |
| Cross-cutting logging/caching/retry/auth | **Decorator / Middleware** instead of copy-pasted wrappers. |

## 2. HSDF Delegation Prompt Template (`🟡`)
Structure subagent prompts with compact headers + exact paths/errors (never compress file paths, line numbers, tool names, or stack traces):
```yaml
tier: T1 | T2a | T2b | T3
Effort: Low | Medium | High
task: "<one-sentence objective>"
scope_allowlist: ["exact/path/file1.ts", "exact/path/file1.test.ts"]
contracts: ["<pre/postconditions, invariants, untouched constraints>"]
observable: "<exact command/HTTP/DB/file output that proves runtime behavior>"
return: ["git diff --stat", "verbatim lint/typecheck/test stdout", "observable proof"]
context: |
  <concise background, relevant .agents/knowledge/ pointers, raw error logs>
```

## 3. 5-Phase Systematic Debugging Gate (`🔴`)
Never guess-and-patch. Walk all 5 phases sequentially:
| Phase | Required Action | Anti-Pattern Banned |
|---|---|---|
| **1. Reproduce** | Trigger failure deterministically on demand and capture verbatim error/state | Editing code before observing a reproducible failure |
| **2. Isolate** | Narrow fault boundary via `git bisect`, minimal input, or binary search across layers | Changing multiple variables at once |
| **3. Root Cause** | Trace corrupted value/state backward through callers to the exact origin invariant break | Stopping at the crash line instead of where bad state entered |
| **4. Fix Cause** | Repair the broken invariant at its source and verify all callers in the call chain | Symptom-masking `try/catch`, null-coalescing over corrupt state, arbitrary sleeps, or blind retries |
| **5. Regression Test** | Add a deterministic test that **fails without the fix** and passes with the fix | Closing a bug fix without regression coverage |

## 4. Context-Isolated Adversarial Checker (`code-critic`) Protocol (`🔴`)
- **Anchoring-Bias Isolation**: Dispatch `code-critic` (or independent `pro`/`inherit` Checker) with **ONLY**:
  1. User requirement & acceptance criteria,
  2. Interface/data contracts,
  3. `git diff` / `git status -s` & touched files,
  4. Verbatim lint/typecheck/test output,
  5. Exact **runtime observable** to verify.
  **STRIP** the Maker's narrative rationale, excuses, and commit prose so the Critic evaluates evidence unanchored.
- **Confidence Filter & Verdict Matrix**:
  - Report **only** findings with **`>=80%` confidence** (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  - **`CRITICAL` or `HIGH` finding** (across Correctness, Call-Chain Integrity, Architecture/DRY/Modularity, Concurrency, Test Quality, Git Dirty-Tree Hygiene, or Security) => **mandatory `VERDICT: BLOCK`** → route localized mechanical fixes via warm `send_message` (`WARM_FIX`) and escalate structural/invariant defects or bounced retries via **Promote-on-Review** (`PROMOTE_MAKER` -> fresh `+1/+2` tier `invoke_subagent` with stripped failed rationale per `01-orchestration.md` §2.2).
  - **`MEDIUM` / `LOW` only** => `VERDICT: WARN` (or `APPROVE` when clean).
- **Mandatory OWASP + Multi-Tenant Security Escalation Triggers**:
  Any diff touching **auth/JWT/sessions**, **crypto/key handling**, **SQL/NoSQL query construction**, **shell/subprocess exec**, **file paths/uploads**, **deserialization**, or **tenant isolation boundaries** automatically triggers an explicit injection, authz-bypass, secret-exposure, and cross-tenant data-leak audit inside Checker review (`CRITICAL`/`HIGH` => `BLOCK`).
