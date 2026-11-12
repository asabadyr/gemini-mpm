---
trigger: manual
description: "Pure-rules fallback for IDE/App (@91-playbook-handoff.md): pause session to redacted .agents/handoffs/LATEST.md, resume with live git reconciliation, or run session postmortem."
---

# Manual Playbook: Session Handoff & Postmortem (`91`)

> **Surface Note**: Invoked in Antigravity IDE / App via `@91-playbook-handoff.md [pause | resume | postmortem]`. (`agy` CLI does not support `@` rule mentions—prefer `/kit-handoff` when `agy-mpm-core` is enabled.)

## Mode A: `pause` (Default When Context Is Growing or Ending Session)
1. **Ensure Gitignore**: If `<workspace>/.git` exists, verify `.agents/handoffs/` is listed in `.gitignore` so session state is never committed.
2. **Secret Redaction Scan (`🔴`)**: Never write tokens, passwords, `Authorization` headers, cookies, or keys (`sk-`, `ghp_`, `AKIA`, `npm_`, `xox`, `AIza`, PEM blocks) into handoff files—replace values with `<REDACTED:KEY_NAME>`.
3. **Capture Live Git State**: Run `git status -s` and `git log --oneline -5` (across active sub-repos if umbrella workspace).
4. **Write `.agents/handoffs/LATEST.md` (`<=10,000` tokens, 7 Sections)**:
   - `1. Mission & Acceptance Criteria`
   - `2. Completed Accomplishments & Commits`
   - `3. Key Technical Findings & Verified Observables`
   - `4. Decisions & Rationale`
   - `5. Ordered Next Steps`
   - `6. Uncommitted Git State & Untouched User WIP`
   - `7. Open Blockers / Risks`
5. Recommend `/compact` if continuing in the current conversation, or `/kit-handoff resume` (`@91-playbook-handoff.md resume`) in a fresh session.

## Mode B: `resume`
1. Read `.agents/handoffs/LATEST.md` and `.agents/knowledge/memories.md` (if present).
2. **Mandatory Live Git Reconciliation (`🔴`)**: Run `git status -s` and `git log --oneline -10` in the workspace (or touched sub-repos). Whenever `LATEST.md` disagrees with live git commits or working-tree state, **live git state wins**—flag discrepancies explicitly before executing Next Step #1.

## Mode C: `postmortem`
1. Inspect `<appDataDir>/brain/<conversation-id>/.system_generated/logs/transcript.jsonl` (or current turn history) for failed commands, Checker `BLOCK` findings, user corrections, or 3-strike loops.
2. Distill single-line dated lessons (`- [YYYY-MM-DD] ...`) into `.agents/knowledge/memories.md` (`Gotchas` / `Patterns` / `CRITICAL` obeying FIFO caps), append multi-paragraph root-cause writeups to `postmortems.md` (if present), and recommend `/learn` when a reusable rule or skill update is warranted.
