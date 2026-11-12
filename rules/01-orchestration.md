---
trigger: always_on
description: "Execution escalation ladder, non-blocking Maker-Checker subagents, dynamic Model/Effort routing, wave-based parallel file ownership, .git workspace check, and warm send_message vs fresh dispatch."
---

# Orchestration & Subagent Protocol (`01`)

## 1. Execution Escalation Ladder
| Scope Tier | Signals | Execution Mode |
|---|---|---|
| **Direct (Inline)** | Status check, architectural Q&A, `<=3` file reads, trivial `<20` LOC 1-step edit | Handle directly in **Main Agent** (zero subagent cold-start overhead) |
| **Standard Multi-Step** | Multi-file investigation, bug fix, feature (`20–500` LOC), test authoring/execution | Delegate asynchronously to **Maker + Checker** (`invoke_subagent`); briefly state active subagent plan and **end turn immediately** so Main Agent stays responsive for user dialogue |
| **Complex / Campaign** | `>500` LOC, cross-service/schema/auth redesign, ambiguous trade-offs, or long autonomous runs | Recommend `/plan` or `/grill-me` to align first; recommend `/boost`, `/teamwork`, or `/goal` for deep multi-perspective or autonomous execution (and `/compact` or `/kit-handoff pause` when context grows) |

## 2. Mandatory Maker–Checker & Dynamic `Model` + `Effort` Routing (`🟡`)
Every non-trivial research, implementation, or testing workflow requires **at least 2 subagents**: **Maker** (investigates/implements/runs tests) + **Checker** (adversarial `code-critic` or independent `pro`/`inherit` reviewer auditing diffs, call chains, edge cases, test quality, and standing rules). Select `Model` + prompt `Effort:` header explicitly on every `invoke_subagent`:

| Subagent Archetype | `Model` Param | Prompt Header | Target Workload |
|---|---|---|---|
| **Mechanical / Inventory** | `flash_lite` | `Effort: Low` | File/symbol grep, log filtering, config/version checks, narrow factual lookups |
| **Scoped Maker** | `flash` | `Effort: Medium` | Scoped codebase research, well-specified implementation, unit test authoring & runs |
| **Deep / Adversarial Critic** | `pro` (or `inherit`) | `Effort: High` | Root-cause forensics, concurrency/protocol/security diffs, **Adversarial Checker (`code-critic`)** |

## 3. Wave Parallelism & `<workspace>/.git` Precondition (`🔴`)
- **Wave Dispatch Only**:
  1. **Wave 0**: Freeze shared types, schemas, and call contracts.
  2. **Wave 1**: Dispatch parallel Makers on **strictly disjoint file allowlists** (never parallelize coupled bugs or overlapping files in a shared working tree).
  3. **Wave 2**: Integrate, run full test suite, and invoke Checker.
- **`<workspace>/.git` Check Before Worktree Isolation**: Verify `<workspace>/.git` exists **before** passing `Workspace="share"` or `"branch"` to `invoke_subagent`.
  - **Umbrella / Non-Git Root Fallback**: Multi-repo parent folders lacking root `.git` fail on `Workspace="share"|"branch"`. Use `Workspace="inherit"` with disjoint sub-repo ownership, or run explicit `git -C <subrepo> worktree add`.
  - **Incremental `wip:` Commits**: Permitted **exclusively** inside verified isolated `Workspace="share"|"branch"` or dedicated git worktrees so interrupted sandboxes retain progress; forbidden in shared dirty trees unless requested.

## 4. Batching, Stage 3.5 Gate & Warm vs Fresh Continuation
| Mechanism | Rule |
|---|---|
| **Context-First Lookup** | Read `.agents/knowledge/00-INDEX.md` and `.agents/knowledge/memories.md` (when present) before launching broad codebase searches |
| **Cohesive Batching** | Bundle `implement + lint + typecheck + run tests + return raw output` into `5–7` cohesive delegations/session rather than `20+` micro-dispatches |
| **Stage 3.5 Gate** | Maker **MUST** pass build, lint, typecheck, and relevant tests before Main Agent dispatches Checker |
| **Warm `send_message`** | Use `send_message(Recipient=conversationId)` **only** for same-scope rework or clarifying follow-ups (zero context reload) |
| **Fresh `invoke_subagent`** | Spawn a new subagent whenever scope expands or role changes (`Research -> Maker`, or `Maker -> Context-Isolated Critic`) |
| **Main Agent Acceptance** | Main Agent owns final acceptance; if Checker returns `BLOCK` or assumptions remain unverified, route fixes back via `send_message` before reporting to user |
