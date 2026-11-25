---
trigger: manual
description: "Pure-rules fallback for IDE/App (@90-playbook-bootstrap.md): scan a repository and scaffold a --lite, --full, or --migrate Antigravity Project Adapter without needing skills/."
---

# Manual Playbook: Project Adapter Bootstrap & Migration (`90`)

> **Surface Note**: Invoked in Antigravity IDE / App via `@90-playbook-bootstrap.md`. (`agy` CLI does not support `@` rule mentions—prefer `/kit-bootstrap`, `/kit-architecture`, or `/kit-handoff` when the `agy-mpm-core` plugin or `skills/` directory is available.)

## Execution Modes & Auto-Switch
- **`--lite`**: Single library, CLI, or small utility (`<5` modules, no prod cluster ops).
- **`--full`**: Production service, multi-repo/monorepo, K8s/cloud deploy, or compliance/confidentiality constraints.
- **`--migrate`**: Lossless migration and consolidation of existing rules (`GEMINI.md`, `CLAUDE.md`, `.cursorrules`, etc.).
- **Auto-Switch**: If existing instruction or rule files are detected, automatically switch to `--migrate` to protect against rule clobbering or duplicate rule injection.

---

## Step 1: Read-Only Discovery Scan (`<=60s`)
1. **Topology & Stack Scan**:
   - Detect git topology: check `<workspace>/.git` vs multi-repo non-git umbrella (`*/*/.git`).
   - Scan stack manifests (`package.json`, `tsconfig.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Dockerfile`, K8s YAML, Terraform `.tf`, `.mise.toml`, CI configs) and `git log --oneline -20` (where `.git` exists).
2. **Exhaustive Legacy & Cross-Agent Rule Discovery**:
   - Search for all existing agent instruction files:
     - `GEMINI.md`, `AGENTS.md` (root & subdirectories), `.agents/rules/*.md`, legacy `.agents/workflows/*.md`
     - `CLAUDE.md`, `.claude/**`
     - `.cursorrules`, `.cursor/rules/**`
     - `.windsurfrules`
     - `CODEX.md`, `.remember/**`
     - AI sections in `CONTRIBUTING.md`
3. **Lossless Backup Gate**:
   - If any existing instruction or rule files are found, copy all of them verbatim into:
     `<appDataDir>/brain/<conversation-id>/scratch/rule-migration-backup/`
     preserving relative paths before modifying any workspace files.
4. **Determine Mode**:
   - If instruction files were found or user requested migration: enter **`--migrate`**.
   - Otherwise, select `--lite` or `--full` based on stack complexity.

---

## Step 2: 4-Bucket Triage Matrix (For `--migrate`)
Categorize all discovered rules into 4 distinct buckets:
1. **Bucket 1 (Universal Core Duplicates)**: Generic guardrails, clean-code/LOC/DRY/OOP rules, item-by-item coverage, verification gates, git WIP protection, secret patterns, 3-strike stop, maker-checker escalation. -> **Drop / Omit** from adapter (provided globally by `00..04`, `20..28`).
2. **Bucket 2 (Behavioral Conflicts)**: Rules conflicting with core safety (auto-committing without staging, skipping tests, modifying user WIP). -> **Highlight and resolve** explicitly with the user.
3. **Bucket 3 (Always-On Repo Identity & Red Lines)**: Repo identity, directory map, canonical commands (`install`, `lint`, `typecheck`, `test`, `build`), top 3–5 non-negotiable `🔴` Red Lines, project-specific Subagent/teamwork Velocity-Optimized 5-Role Matrix (`Orchestrator`, `Researcher/Analyst`, `Developer/Tester`, `Reviewers of all kinds`, `Task Setter/Interviewer`), Promote-on-Review ladder, Milestone Child Visibility (`conversation://<id>`), 180s adaptive watchdog, and Pre-Wave Snapshot + Scope-Escape Kill Switch. -> Migrate to thin `<workspace>/GEMINI.md` (or shared `<workspace>/AGENTS.md`) without frontmatter (`~1.8–3.8 KB`).
4. **Bucket 4 (Ops, Subdir Rules, Lore & Workflows)**:
   - CI/CD, K8s, cloud deploys, secrets, DB traps -> `.agents/rules/10-project-operations.md` (`trigger: model_decision`).
   - Confidentiality / tenant privacy -> `.agents/rules/11-project-confidentiality.md` (`trigger: always_on`).
   - Subdirectory rules -> `.agents/rules/12-<subproject>.md` (`trigger: glob` + `globs: "**/packages/backend/**"`, single-string quoted `**/` patterns, mandatory `**/` prefix, zero `{a,b}` braces — never singular `glob:`!).
   - Architectural lore, memory, active tasks -> `.agents/knowledge/{00-INDEX.md, memories.md, active-tasks.md, postmortems.md}`.
   - Legacy workflows -> flag for conversion to `.agents/skills/<name>/SKILL.md`.

---

## Step 3: Single Confirmation via `ask_question`
Present discovery summary, triage matrix, and prompt user **once** via `ask_question`:
1. **Mode & Migration Plan**: Confirm `--lite`, `--full`, or `--migrate` along with the 4-bucket resolution.
2. **Repo Collaboration Mode**:
   - `(Recommended) Solo / Antigravity repo`: Commit thin Project Adapter to Git.
   - `Personal overlay on shared repo`: Add `GEMINI.md` and `.agents/` to `.git/info/exclude` ONLY when `<workspace>/.git` exists as a real Git directory (never create a fake `.git/info/exclude` in a non-git multi-repo umbrella root, where root adapter files are already outside child git repos!).
   - `Multi-tool team (Claude + Cursor + Antigravity)`: Shared root `AGENTS.md` + `.agents/rules/10-*`.
   - `Team repo with existing .agents/rules/`: Warn about `realpath` cumulative rule injection; advise toggling `[agy-mpm-core](customization://agy-mpm-core)` off, never copy Universal Core files.
3. **Optional Confidentiality Rule**: Whether to include `11-project-confidentiality.md`.

---

## Step 4: Scaffold Project Adapter (Zero Universal Core Copies!)
> **Anti-Duplication Invariant**: Never `cp` Universal Core rules (`00..04`, `20..28`) into `<workspace>/.agents/rules/` while global `agy-mpm-core` is enabled (`realpath` deduplication only deduplicates identical physical files!).
> **Reference-Aware Reading Protocol (`🟡`)**: Enforce `Read-Once` and pass exact `read_anchors` in subagent handoffs; following real code references (`imports`, base classes, callers/callees) and codebase similarity/DRY audits is unrestricted.

1. **`--lite`, `--full`, & `--migrate`**:
   - Write `<workspace>/GEMINI.md` (**plain Markdown, NO YAML frontmatter**, `~1.8–3.8 KB`): Workspace Identity, Top 3–5 `🔴` Project Red Lines (including Git & Subagent/`teamwork` Topology with Velocity-Optimized 5-Role Matrix, Promote-on-Review ladder, Milestone Child Visibility `conversation://<id>`, 180s adaptive watchdog, and Pre-Wave Snapshot + Scope-Escape Kill Switch if configured, plus `Read-Once` + `read_anchors` boot note), Directory/Sub-Project Map, Canonical Commands, and `.agents/knowledge/` links.
   - Create `.agents/knowledge/memories.md` with the 5-section FIFO-capped header (`CRITICAL` 20 no-evict, `Environment` 15, `Decisions` 20, `Patterns` 20, `Gotchas` 15, `<=4 KB`).
   - Git tracking: if personal overlay, update `.git/info/exclude` ONLY when `<workspace>/.git` exists as a real Git directory (never create a fake `.git/info/exclude` in a non-git multi-repo umbrella root, where root adapter files are already outside child git repos!); if shared/solo and `<workspace>/.git` exists, append `.agents/handoffs/` and `.agents/teamwork/` to `.gitignore` (idempotently ensuring both directories are present while preserving existing lines).
2. **`--full` & `--migrate` additions**:
   - `.agents/rules/10-project-operations.md` (`trigger: model_decision`): CI/CD pipelines, K8s/cloud rollout commands, namespace mappings, secret scripts, project-specific analytical traps.
   - `.agents/rules/11-project-confidentiality.md` (`trigger: always_on`, optional): client/tenant, cloud project, PII, and internal-stack non-disclosure rules.
   - `.agents/rules/12-*.md` (`trigger: glob` + `globs: "**/<subdir>/**"`, optional): directory-scoped conventions (mandatory `**/` prefix, zero `{a,b}` braces, never singular `glob:`!).
   - `.agents/knowledge/{00-INDEX.md, active-tasks.md, postmortems.md}` (smart-merging if files already exist).

---

## Step 5: Mandatory Lossless Verification Gate
When migrating existing rules or smart-merging:
- Run an adversarial check (or dispatch `code-critic` if subagent tools are enabled) comparing adapter files against `<scratch>/rule-migration-backup/`.
- Ensure:
  1. 0 project-specific invariants, commands, regexes, or links lost.
  2. 0 Universal Core duplicate rules copied into workspace.
  3. Every rule file in `.agents/rules/` is `<24,000` bytes with valid frontmatter.
  4. `GEMINI.md` has no frontmatter.
