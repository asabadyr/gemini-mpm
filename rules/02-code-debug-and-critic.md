---
trigger: model_decision
description: "Activate when writing or refactoring code, debugging errors or test failures, reviewing diffs, or dispatching Maker and Adversarial Checker (Code Critic) subagents."
---

# Code Hygiene, 5-Phase Debugging & Adversarial Critic (`02`)

## 1. Engineering Constraints & Call-Chain Integrity (`🔴`)
| Principle | Enforcement |
|---|---|
| **Right-Level Engineering** | Match abstraction to task size: `<200` LOC belongs in a single cohesive module without speculative factories, wrappers, or DI layers |
| **Ban Import-Time Side Effects** | Module top-level imports **MUST NEVER** open DB/network sockets, spawn background loops/threads, read unguarded secrets, or mutate disk/env |
| **Provided Artifacts Are Constraints** | Existing tests, fixtures (`conftest.py`, seed data), and public schemas are binding contracts: fix production code when existing tests fail—**NEVER** weaken assertions, delete failing tests, or shadow fixtures unless specs explicitly changed |
| **Whole Call-Chain Walk** | Trace `Entrypoint -> Caller/Orchestrator -> Callee -> DB/External Side-Effect -> Return/Error Handling` end-to-end before coding or approving a fix |
| **Contracts Before Bodies** | Specify preconditions, postconditions, invariants, and error surfaces before writing bodies (skip ceremony only on `<=20` LOC non-auth/crypto hotfixes) |

## 2. HSDF Delegation Prompt Template (`🟡`)
Structure subagent prompts with compact headers + exact paths/errors (never compress file paths, line numbers, tool names, or stack traces):
```yaml
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
  - **`CRITICAL` or `HIGH` finding** (across Correctness, Call-Chain Integrity, Concurrency, Test Quality, Git Dirty-Tree Hygiene, or Security) => **mandatory `VERDICT: BLOCK`** → return findings to Maker via `send_message`.
  - **`MEDIUM` / `LOW` only** => `VERDICT: WARN` (or `APPROVE` when clean).
- **Mandatory OWASP + Multi-Tenant Security Escalation Triggers**:
  Any diff touching **auth/JWT/sessions**, **crypto/key handling**, **SQL/NoSQL query construction**, **shell/subprocess exec**, **file paths/uploads**, **deserialization**, or **tenant isolation boundaries** automatically triggers an explicit injection, authz-bypass, secret-exposure, and cross-tenant data-leak audit inside Checker review (`CRITICAL`/`HIGH` => `BLOCK`).
