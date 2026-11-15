---
trigger: always_on
description: "Execution escalation ladder, non-blocking Maker-Checker subagents, asymmetric Maker<Checker model routing, Promote-on-Review dynamic escalation, wave-based parallel file ownership, .git workspace check, and warm vs fresh continuation."
---

# Orchestration & Subagent Protocol (`01`)

## 1. Execution Escalation Ladder
| Scope Tier | Signals | Execution Mode |
|---|---|---|
| **Direct (Inline)** | Status check, architectural Q&A, `<=3` file reads, trivial `<20` LOC 1-step edit | Handle directly in **Main Agent** (zero subagent cold-start overhead) |
| **Standard Multi-Step** | Multi-file investigation, bug fix, feature (`20–500` LOC), test authoring/execution | Delegate asynchronously to **Maker + Checker** (`invoke_subagent`); briefly state active subagent plan and **end turn immediately** so Main Agent stays responsive for user dialogue |
| **Complex / Campaign** | `>500` LOC, cross-service/schema/auth redesign, ambiguous trade-offs, or long autonomous runs | Recommend `/plan` or `/grill-me` to align first; recommend `/boost`, `/teamwork`, or `/goal` for deep multi-perspective or autonomous execution (and `/compact` or `/kit-handoff pause` when context grows) |

## 2. Asymmetric Maker–Checker & Pre-Dispatch Model + Effort Routing (`🔴`)
Every non-trivial research, implementation, or testing workflow requires **at least 2 subagents**: **Maker** (investigates/implements/runs tests) + **Checker** (adversarial `code-critic` or independent `pro`/`inherit` reviewer auditing diffs, call chains, edge cases, test quality, and standing rules).
- **Explicit Standing Override of `Model='inherit'`**: **NEVER** omit `Model` or default Explorers/Makers to `inherit`/`pro` + `Effort: High`. Makers run **1–2 tiers BELOW** max by default, reserving `pro` (or `inherit` top-tier) + `Effort: High` for the Checker (`code-critic`) and true T3 tasks.

### 2.1. Pre-Dispatch Complexity Rubric
Select `Model` param + prompt `Effort:` header explicitly on every `invoke_subagent`:

| Tier | Archetype | `Model` | Prompt Header | Scope & Complexity |
|---|---|---|---|---|
| **T0** | **Inline (Main Agent)** | *(none)* | *(inline)* | `<=3` file reads, status/Q&A, `<20` LOC 1-step edit (0 subagents) |
| **T1** | **Light (-2 lvls)** | `flash_lite` | `Effort: Low` | Zero design ambiguity, 1–3 files, mechanical transform, symbol/log grep, config/version/doc sync |
| **T2a** | **Standard-Low (-1.5 lvls)** | `flash` | `Effort: Low` | Clear spec & existing pattern, 1–3 files (20–120 LOC), single module, routine CRUD/bugfix with known repro, basic unit tests |
| **T2b** | **Standard-Med (-1 lvl)** | `flash` | `Effort: Medium` | Multi-file (2–6 files, 100–400 LOC), local interface/DRY extraction, `<=200` LOC God-file chunk, multi-case tests, scoped research |
| **T3** | **Deep / Max (Top Tier)** | `pro` *(or `inherit`)* | `Effort: High` | **Mandatory default for Checker (`code-critic`)**; allowed for Maker **ONLY** on concurrency/locks, auth/crypto/tenant boundaries, subtle cross-service root-cause forensics, or after Promote-on-Review escalation |

- **Downward Tie-Breaker**: On boundary tasks between T1/T2a or T2b/T3 (outside auth, crypto, concurrency, or destructive migrations), start 1 tier lower and rely on `code-critic` (`pro` + `High`) + Promote-on-Review.

### 2.2. Review-Driven Dynamic Model Promotion (Promote-on-Review)
- **Platform Binding Rule**: Subagent `Model` is bound when `invoke_subagent` creates its `conversationId` (`send_message` preserves model). Use warm `send_message` **ONLY** for `WARM_FIX` (localized mechanical slips or minor Effort bump within same model). To promote `Model` (+1 or +2 tiers: `flash_lite Low` -> `flash Medium`, or `flash Low/Medium` -> `pro High`), spawn a fresh `invoke_subagent`.
- **4 Mandatory Promotion Triggers** (Stage 3.5, wave reviews, critic verdicts):
  1. **Stage 3.5 Gate Stall**: 2 consecutive lint/typecheck/test failures on same subtask (promote before burning Strike 3 on low-tier model).
  2. **Critic PROMOTE_MAKER Verdict**: `code-critic` returns `BLOCK` (or structural `WARN`) with `Rework Routing: PROMOTE_MAKER` due to call-chain, concurrency, security, or architectural/contract incomprehension.
  3. **Warm-Rework Bounce**: Warm `send_message` fix fails to clear a `BLOCK` on retry #1.
  4. **Mid-Flight Complexity Discovery**: Maker uncovers hidden cross-service coupling, race conditions, or auth/tenant impact (T3 scope).
- **Clean Promotion Handoff (Anti-Anchoring)**: Pass promoted Maker **ONLY**: (a) original HSDF spec & contracts, (b) current `git status -s` / `git diff` on disk, and (c) verbatim test error or `code-critic` `BLOCK` table. **STRIP** failed lower-tier Maker reasoning/narratives.

### 2.3. Workspace Role Pinning & Standing Cron Ban
- **Exact Role Model/Effort Pinning via `teamwork`**: When a workspace (`AGENTS.md`) or user specifies exact model + effort profiles per role (e.g., `Implementer: Flash Medium, Researcher: Flash Low, Critical Reviewer: Pro High, Others: Flash_Lite Low`), route all multi-step subagent work through **`invoke_subagent(TypeName="teamwork")`** and **end the Main Agent turn immediately** so the chat stays non-blocking.
- **Ban Standing `schedule` Crons in Interactive Chats (`🔴`)**: Never run recurring monitoring crons via in-chat `schedule` (keeps the session stuck in `Running`); extract standing schedules to external **Scheduled Automations (`~/.gemini/config/sidecars/`)**, and isolate autonomous code-editing monitors in dedicated git worktrees so they do not collide with active development.

## 3. Wave Parallelism & `<workspace>/.git` Precondition (`🔴`)
- **Wave Dispatch Only**:
  1. **Wave 0**: Freeze shared types, schemas, and call contracts.
  2. **Wave 1**: Dispatch parallel Makers on **strictly disjoint file allowlists** (never parallelize coupled bugs or overlapping files in a shared working tree).
  3. **Wave 2**: Integrate, run full test suite, and invoke Checker.
- **`<workspace>/.git` Check Before Worktree Isolation**: Verify `<workspace>/.git` exists **before** passing `Workspace="share"` or `"branch"` to `invoke_subagent`.
  - **Umbrella / Non-Git Root Fallback**: Multi-repo parent folders lacking root `.git` fail on `Workspace="share"|"branch"`. Use `Workspace="inherit"` with disjoint sub-repo ownership, or run explicit `git -C <subrepo> worktree add`.
  - **Incremental `wip:` Commits**: Permitted **exclusively** inside verified isolated `Workspace="share"|"branch"` or dedicated git worktrees so interrupted sandboxes retain progress; forbidden in shared dirty trees unless requested.

## 4. Batching, Stage 3.5 Gate & Warm vs Promoted Continuation
| Mechanism | Rule |
|---|---|
| **Context-First Lookup** | Read `.agents/knowledge/00-INDEX.md` and `.agents/knowledge/memories.md` (when present) before launching broad codebase searches |
| **Cohesive Batching** | Bundle `implement + lint + typecheck + run tests + return raw output` into `5–7` cohesive delegations/session rather than `20+` micro-dispatches |
| **Stage 3.5 Gate** | Maker **MUST** pass build, lint, typecheck, and relevant tests before Main Agent dispatches Checker |
| **Warm `send_message` (`WARM_FIX`)** | Use `send_message(Recipient=conversationId)` **only** for localized mechanical slips or same-scope rework within the same model tier (zero context reload) |
| **Promoted `invoke_subagent` (`PROMOTE_MAKER`)** | Spawn a fresh subagent with clean unanchored handoff whenever promoting model tier (+1/+2), when role changes (`Research -> Maker`, `Maker -> Critic`), or scope expands |
| **Stream-Timeout False-Liveness Check** | When checking long-running subagent progress, inspect the tail of its `transcript.jsonl` (not `lastStepTime` alone) to catch repeated `The stream was interrupted` loops caused by oversized `write_file` calls |
| **Main Agent Acceptance** | Main Agent owns final acceptance; if Checker returns `BLOCK`, route `WARM_FIX` via `send_message` or escalate to `PROMOTE_MAKER` via fresh `invoke_subagent` before reporting to user |
