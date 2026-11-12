---
name: kit-handoff
description: "Pause session state to a redacted .agents/handoffs/LATEST.md snapshot, resume and reconcile against live git status/log, or distill session postmortem lessons into memories.md and /learn."
---

# `/kit-handoff` — Session Pause, Live-Git Resume & Postmortem

Manage cross-session continuity and post-task learning without leaking secrets or trusting stale notes over live repository state.

Determine the requested subcommand from the user's prompt (`pause`, `resume`, or `postmortem`; default to `pause` if unspecified when wrapping up work, or `resume` at the start of a fresh conversation when `.agents/handoffs/LATEST.md` exists).

---

## Mode 1: `pause` — Write Redacted 7-Section Snapshot (`<=10K` Tokens)
1. **Gitignore Protection (`🔴`)**:
   - Check if `<workspace>/.git` exists. If yes, verify `.agents/handoffs/` is listed in `<workspace>/.gitignore` (add it if missing, without staging unrelated files) so session state is **never** committed to VCS.
   - *(Note: Context handoffs are advisory and on-demand—never block or kill active background subagents mid-flight! Check `manage_subagents(Action="list")` and `manage_task(Action="list")` first and record any running IDs.)*
2. **Collect Live Repo State**:
   - Single git repo: run `git status -s` and `git log --oneline -5`.
   - Multi-repo non-git umbrella: run a loop across child `<subrepo>/.git` directories reporting dirty `git status -s` and the latest commit on any modified sub-repo.
3. **Mandatory Credential Redaction (`🔴`)**:
   - Scan planned snapshot content and redact any secret values (`sk-`, `ghp_`, `AKIA`, `npm_`, `xox`, `AIza`, PEM blocks, `Bearer ...`, connection strings, passwords) to `<REDACTED:VAR_NAME>`.
4. **Write `<workspace>/.agents/handoffs/LATEST.md`**:
   - Populate all 7 sections from [`resources/LATEST.template.md`](./resources/LATEST.template.md), keeping total size **`<=10,000` tokens (`~40 KB` max, ideally `2–6 KB`)**.
5. **Next-Step Guidance**:
   - Confirm the path written (`[LATEST.md](file://<workspace>/.agents/handoffs/LATEST.md)`). If staying in the current long conversation, suggest Antigravity's `/compact` slash command; if switching sessions, tell the user to run `/kit-handoff resume`.

---

## Mode 2: `resume` — Reconcile Snapshot Against Live Git (`🔴`)
1. Read `<workspace>/.agents/handoffs/LATEST.md` and `<workspace>/.agents/knowledge/memories.md` (if present).
2. **Mandatory Live Git Reconciliation**:
   - Run live `git status -s` and `git log --oneline -10` (across `<workspace>` if `.git` exists, or across child `*/*/.git` sub-repos).
   - Compare `LATEST.md` §2 (Commits) and §6 (Uncommitted Git State) against live git output:
     - **Live git always wins over stale handoff prose.** Explicitly call out any commits added, branches switched, or files modified since `LATEST.md` was written.
3. Present a crisp 5-line **Reconciled Resume Brief** (Mission, Verified Git Delta Since Pause, Untouched User WIP to Protect, Top Next Step) and proceed or ask if a conflict was detected.

---

## Mode 3: `postmortem` — Distill Session Lessons Into `memories.md` & `/learn`
1. **Inspect Session Evidence**:
   - Review current session errors, Checker `BLOCK` verdicts, 3-strike pivots, or user corrections (reading `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` via grep/targeted line reads if earlier steps scrolled out).
2. **Update Project Knowledge**:
   - Append single-line ISO-dated facts (`- [YYYY-MM-DD] <concise lesson>`) to the appropriate section of `<workspace>/.agents/knowledge/memories.md`, strictly enforcing `04-memory-knowledge-adr.md` **FIFO oldest-first caps** (`CRITICAL` 20 no-evict; `Environment` 15, `Decisions` 20, `Patterns` 20, `Gotchas` 15; `<=4 KB` total).
   - For multi-paragraph incidents, append a dated entry to `.agents/knowledge/postmortems.md` (or `.agents/knowledge/active-state/engineering-rules-and-postmortems.md` if used by the workspace) and register major state shifts in `00-INDEX.md`.
3. **Bridge to `/learn`**:
   - When a user correction or workflow insight applies across repositories or warrants a new reusable skill/rule update, explicitly recommend running `/learn`.
