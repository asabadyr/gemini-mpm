---
trigger: always_on
description: "Execution escalation ladder across 3 modes (T0 inline, teamwork/swarm exact model+effort pinning, coarse invoke_subagent fallback), asymmetric Maker<Checker routing, live Promote-on-Review dynamic escalation, wave-based file ownership, and cache-first gates."
---

# Orchestration & Subagent Protocol (`01`)

## 1. Execution Escalation Ladder
| Scope Tier | Signals | Execution Mode |
|---|---|---|
| **Direct (Inline)** | Status check, architectural Q&A, `<=3` file reads, trivial `<20` LOC 1-step edit | **Mode 1 — Inline (Main Agent)** (zero subagent cold-start overhead) |
| **Standard Multi-Step** | Multi-file investigation, bug fix, feature (`20–500` LOC), test authoring/execution | **Mode 2 — Exact Model + Effort Multi-Agent (`teamwork` / native `swarm`)** when role matrix defined; otherwise **Mode 3 — Asymmetric Maker + Checker (`invoke_subagent`)** |
| **Complex / Campaign** | `>500` LOC, cross-service/schema/auth redesign, ambiguous trade-offs, or long autonomous runs | Recommend `/plan` or `/grill-me` to align first; execute via **Mode 2 (`teamwork` / native `swarm`)** or recommend `/boost` / `/goal` (and `/compact` or `/kit-handoff pause` when context grows) |

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

### 2.3. Exact Model + Effort Execution Flows (`teamwork` & `swarm` vs `invoke_subagent`)

#### Why Standard `invoke_subagent` Cannot Pin Exact Models or Effort
In standard chat, `invoke_subagent` is restricted to 4 coarse tier aliases (`Model: "flash_lite" | "flash" | "pro" | "inherit"`) and exposes **no API-level `effort` parameter**. Prompt headers like `Effort: High` are only soft textual instructions, `Model: "inherit"` silently tracks the user's interactive UI dropdown, and `send_message` preserves the original bound model without mutation. When a project requires exact model families, deterministic thinking budgets, or live in-place promotion, use the 3 execution modes below.

#### The 3 Execution Modes for Model & Effort Control
1. **Mode 1 — `T0` Direct Inline (Main Agent)**:
   - For `<=3` file reads, status/Q&A, or `<20` LOC 1-step edits. Handled directly in the Main Agent with zero subagent/`teamwork` overhead.

2. **Mode 2 — Exact Model + Effort Multi-Agent Flow (`teamwork` & Native `swarm`)**:
   - **Mandatory** whenever `GEMINI.md`, `AGENTS.md`, or the user defines an explicit `Role -> Exact Model + Effort` matrix, and strongly recommended for multi-step `T1..T3` engineering campaigns.
   - **Built-in `teamwork` Flow (`invoke_subagent(TypeName="teamwork")` / `/teamwork`)**:
     Launches the built-in multi-agent engine (`Sentinel -> Task Interviewer -> Orchestrator -> teamwork_explorer / teamwork_worker / teamwork_reviewer / teamwork_challenger / teamwork_victory_auditor`) with state tracked under `.agents/teamwork/`.
     * **Prompt-Top Matrix Rule (`🔴`)**: The `teamwork` subagent tree cannot inspect parent conversation history. Whenever invoking `TypeName="teamwork"`, prepend the workspace's **Role -> Exact Model + Effort Matrix + `Promote-on-Review` Ladder** verbatim at the very top of `Prompt` (and store it canonically in `GEMINI.md` / `AGENTS.md`).
     * **Knowledge-First Subagent Boot (`🔴`)**: Subagents boot with a blank slate. The parent agent or orchestrator **MUST** explicitly pass `knowledge_refs:` in every `Prompt` (top-level alongside the Role Matrix), `DISPATCH.md`, and `swarm` `add` `brief` (exact paths to root `GEMINI.md`/`AGENTS.md`, `.agents/knowledge/00-INDEX.md`, `.agents/knowledge/memories.md`, and 1–3 relevant topic docs). Every newly spawned agent/worker **MUST** read these in its **first tool batch BEFORE** launching broad file searches. When `.agents/knowledge/` + `00-INDEX.md` already map architecture, schemas, traps, and canonical commands, **skip blind survey waves** (Anti-Cold-Survey Gate) and target files directly.
     * **`[skip-interview]` Fast-Path**: Prefix `Prompt` with `[skip-interview]` when requirements, acceptance criteria, and file scopes are concrete (`>=90%` clear) to bypass `teamwork_interviewer` and jump straight to implementation; omit `[skip-interview]` on ambiguous tasks so the interviewer clarifies first.
     * **`Promote-on-Review` inside `teamwork`**: Workers inside `teamwork` are single-iteration (`handoff.md` -> never reused). Start routine subtasks (`T1`/`T2a`) 1–2 levels below max, standard multi-file (`T2b`) 1 level below or workhorse `High`, and keep `Critical Reviewer` (`teamwork_reviewer`) & `Victory Auditor` on `<frontier-model> (High)`. When `Stage 3.5` stalls or the reviewer returns `BLOCK`/`REJECT`, `teamwork_orchestrator` spawns `iter2` promoted `+1/+2` model/effort levels higher with clean unanchored `DISPATCH.md`.
     * **Git Hygiene**: Always ensure `.agents/teamwork/` is ignored in `.gitignore` alongside `.agents/handoffs/`.
   - **Native `swarm` Flow (when `native_swarm` tools `swarm`, `post_message`, `read_board`, `swarm_wait` are active)**:
     * Inspect exact catalog and live quota via `swarm{action:"models"}`.
     * Pin exact model + effort IDs per worker via `swarm{action:"add", name:"<role>", model:"<exact-model-id>", workspace:"inherit"|"share"|"branch", brief:"..."}` (workspace/user Role Matrix overrides `swarm`'s default same-model rule).
     * **Live In-Place Promotion**: Switch a `waiting` worker's model+effort dynamically via `swarm{action:"model", name:"<worker>", model:"<promoted-model-id>"}` while keeping conversation history (or `add` fresh worker when clean anti-anchoring reset is needed for `PROMOTE_MAKER`).

3. **Mode 3 — Coarse `invoke_subagent` Fallback (`Model: flash_lite | flash | pro | inherit`)**:
   - Used when no exact model/effort matrix is required or when `teamwork`/`swarm` is unavailable in the host session. Follows the standard `T1..T3` pre-dispatch rubric and spawns a fresh `invoke_subagent` on Promote-on-Review.

#### Standing Schedule Cron Ban (`🔴`)
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
| **Knowledge-First Boot & Anti-Cold-Survey (`🔴`)** | Parent/orchestrator passes `knowledge_refs:` in HSDF/briefs. Subagents **MUST** read `GEMINI.md`/`AGENTS.md`, `00-INDEX.md`, and `memories.md` in Step 0 before broad file/grep scans. When knowledge base already maps architecture and traps, skip blind survey waves. |
| **Cache-First Gate (`🟡`)** | When `>=75%` of requested benchmark, analytics, or report data already exists in cached JSON/CSV/Parquet/scratch files, **NEVER** spawn a heavy top-tier subagent to recompute from scratch—slice/render cached data inline or via a `T1` (`Low/Medium`) helper |
| **Cohesive Batching** | Bundle `implement + lint + typecheck + run tests + return raw output` into `5–7` cohesive delegations/session rather than `20+` micro-dispatches |
| **Stage 3.5 Gate** | Maker **MUST** pass build, lint, typecheck, and relevant tests before Main Agent dispatches Checker |
| **Warm `send_message` (`WARM_FIX`)** | Use `send_message(Recipient=conversationId)` **only** for localized mechanical slips or same-scope rework within the same model tier (zero context reload) |
| **Promoted `invoke_subagent` (`PROMOTE_MAKER`)** | Spawn a fresh subagent with clean unanchored handoff whenever promoting model tier (+1/+2), when role changes (`Research -> Maker`, `Maker -> Critic`), or scope expands |
| **Stream-Timeout False-Liveness Check** | When checking long-running subagent progress, inspect the tail of its `transcript.jsonl` (not `lastStepTime` alone) to catch repeated `The stream was interrupted` loops caused by oversized `write_file` calls |
| **Main Agent Acceptance** | Main Agent owns final acceptance; if Checker returns `BLOCK`, route `WARM_FIX` via `send_message` or escalate to `PROMOTE_MAKER` via fresh `invoke_subagent` before reporting to user |
