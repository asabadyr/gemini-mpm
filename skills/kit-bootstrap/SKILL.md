---
name: kit-bootstrap
description: "Bootstrap, refresh, or migrate a repository's Antigravity Project Adapter (--lite for small libs/CLIs, --full for production/multi-service workspaces, --migrate for lossless cross-agent rule migration) by scanning stack manifests, legacy rules, and git history."
---

# `/kit-bootstrap` — Project Adapter Scaffolder & Migrator (`--lite` | `--full` | `--migrate`)

Scaffold, smart-merge, or losslessly migrate into a thin **Tier-2 Project Adapter** (`GEMINI.md` or `AGENTS.md`, `.agents/rules/10-*`, `.agents/knowledge/*`) in ~90 seconds while leaving **Tier-1 Universal Core** rules inside the global `agy-mpm-core` plugin.

## Execution Modes & Auto-Switch
- **`--lite`**: Single library, CLI, script collection, or small utility (`<5` modules, no cluster/cloud rollout traps).
- **`--full`**: Production service, multi-repo/monorepo, K8s/cloud infra, or confidential client/multi-tenant workload.
- **`--migrate`**: Lossless discovery, triage, and consolidation of pre-existing rules and cross-agent instruction files.
- **Auto-Switch Guard**: If any existing instruction or rule files (`GEMINI.md`, `CLAUDE.md`, `.cursorrules`, `.agents/rules/*.md`, etc.) are detected during discovery, `/kit-bootstrap` **automatically upgrades to `--migrate` mode** to prevent accidental overwrites or duplicate rule injection!

---

## Mandatory Safety & Anti-Duplication Rules (`🔴`)
1. **Zero Duplicate Rule Injection (`realpath` Invariant)**: Antigravity deduplicates rules strictly by resolved physical path (`realpath`), and Global + Workspace rules are **cumulative**. **NEVER** `cp` Universal Core rules (`00..04`, `20..28`) into `<workspace>/.agents/rules/` while `agy-mpm-core` is enabled! (If setting up a shared team repo for coworkers without the plugin, either symlink via `ln -s` locally or advise toggling `[agy-mpm-core](customization://agy-mpm-core)` off.)
2. **Lossless Backup Gate**: Before modifying or creating any adapter file, copy every existing or discovered instruction file preserving relative paths into `<appDataDir>/brain/<conversation-id>/scratch/rule-migration-backup/`.
3. **Never Revert Dirty Working Trees**: Inspect `git status -s` read-only; never discard or stage pre-existing user changes.
4. **Reference-Aware Reading Protocol (`🟡`)**: Adhere to `Read-Once` (no duplicate unchanged reads) and hand off exact `read_anchors` in subagent briefs (`Explorer -> Developer`). Real code references (`imports`, base classes, interfaces, callers/callees) and codebase-wide similarity/DRY analysis are **explicitly unrestricted**.

---

## Step 1: Fast Read-Only Workspace & Rule Discovery

### 1. Git Topology Check
- Check whether `<workspace>/.git` exists (`Single/Monorepo Git Root`) or whether `.git` directories live inside child folders `<workspace>/*/.git` (`Multi-Repo Non-Git Umbrella` — critical for `Workspace: inherit` subagent protocol!).

### 2. Stack & Toolchain Scan
- Check indicator files: `package.json` + lockfile, `tsconfig.json`, `pyproject.toml` / `uv.lock`, `go.mod`, `Cargo.toml`, `Makefile` / `.mise.toml` / `Taskfile.yml`, `Dockerfile` / `docker-compose.yml`, Kubernetes YAML / Helm / Terraform `.tf`, and CI configs (`.github/workflows/`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`, etc.).
- Run `git log --oneline -20` (on root `.git` or 2–3 primary sub-repos) to infer branch/release conventions.

### 3. Exhaustive Legacy & Cross-Agent Rule Discovery
Scan for all instruction and agent rule files across the workspace:
- **Antigravity / Gemini**: `GEMINI.md`, `AGENTS.md` (root & nested subdirs), `.agents/rules/*.md`, legacy `.agents/workflows/*.md`.
- **Claude Code**: `CLAUDE.md`, `.claude/**`.
- **Cursor**: `.cursorrules`, `.cursor/rules/**`.
- **Windsurf / Codeium**: `.windsurfrules`.
- **OpenAI / Codex / Other Agents**: `CODEX.md`, `.remember/**`.
- **General Docs**: AI/agent instruction sections in `CONTRIBUTING.md`.

### 4. Mode Determination
- If user explicitly specified `--migrate` OR if any files from Step 1.3 were found, proceed in **`--migrate` mode**.
- Otherwise, pick `--lite` (small app/library) or `--full` (multi-module, cluster, or cloud deployment).

---

## Step 2: Lossless Backup & 4-Bucket Triage Matrix

When in `--migrate` mode (or refreshing an existing adapter):

### 1. Lossless Backup Gate
Copy every discovered instruction file preserving its relative path into:
`<appDataDir>/brain/<conversation-id>/scratch/rule-migration-backup/`
*(e.g., `scratch/rule-migration-backup/GEMINI.md`, `scratch/rule-migration-backup/.cursor/rules/api.md`).*

### 2. 4-Bucket Triage Matrix
Categorize discovered rules across 4 buckets and formulate the triage summary:

| Bucket | Content Type | Migration Action | Target Destination |
|---|---|---|---|
| **Bucket 1: Universal Core Duplicates** | Generic guardrails, clean-code/LOC/DRY/OOP rules, 3-strike stop, item-by-item coverage, dirty-tree git protection, secret patterns, maker-checker ladders, test anti-tautology | **DROP / OMIT** (already provided globally by `agy-mpm-core` `00..04`, `20..28`) to save prompt budget | Omitted from repo adapter |
| **Bucket 2: Behavioral Conflicts** | Rules conflicting with core safety (e.g. auto-committing without staging, bypassing verification, altering untouched WIP, mock-only test mandates) | **HIGHLIGHT & RESOLVE** via user question (default to keeping safe core behavior while accommodating true repo-specific needs) | Reconciled in adapter |
| **Bucket 3: Always-On Identity & Red Lines** | Repo purpose, directory/sub-project map, single-path canonical commands (`install`, `lint`, `typecheck`, `test`, `build`), top 3–5 non-negotiable `🔴` Red Lines, project-specific Subagent/teamwork Velocity-Optimized 5-Role Matrix (`Orchestrator`, `Researcher/Analyst`, `Developer/Tester`, `Reviewers of all kinds`, `Task Setter/Interviewer`), Promote-on-Review ladder, Milestone Child Visibility (`conversation://<id>`), 180s adaptive watchdog, and Pre-Wave Snapshot + Scope-Escape Kill Switch | **MIGRATE & CONDENSE** into a clean, thin always-on instruction file | `<workspace>/GEMINI.md` (or shared `<workspace>/AGENTS.md`) without frontmatter (`~1.8–3.8 KB`) |
| **Bucket 4: Ops, Subdir Rules, Lore & Workflows** | CI/CD pipelines, K8s/cloud rollouts, namespace maps, secret scripts, DB traps, sub-project specifics, compliance/confidentiality, persistent architectural lore | **SPLIT & STRUCTURE** into specialized rules, knowledge base, or modern skills | `.agents/rules/10-project-operations.md` (`model_decision`), optional `11-project-confidentiality.md` (`always_on`), optional `12-<subproject>.md` (`trigger: glob` + `globs: "**/<subdir>/**"`), `.agents/knowledge/{00-INDEX,memories,active-tasks,postmortems}.md`; convert `.agents/workflows/*.md` to `.agents/skills/<name>/SKILL.md` |

---

## Step 3: Single Confirmation via `ask_question`

Present a structured discovery summary and call `ask_question` **once** before touching workspace files:

1. **Adapter Profile & Migration Plan**:
   - For `--migrate`: List discovered files, Bucket 1 dropped duplicates, Bucket 2 resolved conflicts, and proposed Bucket 3 & 4 files.
   - For fresh `--lite` or `--full`: Present topology, detected stack, canonical commands, and proposed red lines.
2. **Repo Collaboration Mode Selection**:
   - `(Recommended) Solo / Antigravity repo`: Commit thin Project Adapter directly to Git.
   - `Personal overlay on shared repo`: Add `GEMINI.md` and `.agents/` to `.git/info/exclude` ONLY when `<workspace>/.git` exists as a real Git directory (never create a fake `.git/info/exclude` in a non-git multi-repo umbrella root, where root adapter files are already outside child git repos!) to keep zero footprint in team VCS.
   - `Multi-tool team (Claude + Cursor + Antigravity)`: Create shared root `AGENTS.md` + `.agents/rules/10-*` and maintain lightweight pointer files for other tools.
   - `Team repo with existing .agents/rules/`: Warn about `realpath` cumulative rule injection; recommend keeping repo rules and toggling `[agy-mpm-core](customization://agy-mpm-core)` off for this workspace, never copying core files.
3. **Include `11-project-confidentiality.md`?**: (`always_on` non-disclosure rules for private/client/cloud workloads).
4. **Role -> Exact Model + Effort Matrix & Watchdog Controls**: Confirm preservation or definition of the Velocity-Optimized 5-Role Matrix (`Orchestrator`, `Researcher/Analyst`, `Developer/Tester`, `Reviewers of all kinds`, `Task Setter/Interviewer`) for `teamwork`/`swarm`, plus 180s adaptive watchdog, milestone child links, and pre-wave snapshot controls when configuring multi-agent workflows.

Wait for user response before writing any workspace files.

---

## Step 4: Scaffold & Populate Project Adapter

Read templates from `./resources/` and write concrete repo values (zero `{{...}}` or `<...>` placeholders left behind!):

### A. Core Adapter Files
1. **`<workspace>/GEMINI.md`** (from [`./resources/GEMINI.lite.md`](./resources/GEMINI.lite.md) or [`./resources/GEMINI.full.md`](./resources/GEMINI.full.md), or `<workspace>/AGENTS.md` for multi-tool setups):
   - **Plain Markdown ONLY — NO YAML frontmatter** (must not contain `---` metadata header).
   - Target `~1.8–3.8 KB`: Workspace Identity + `agy-mpm-core` adapter note, Top 3–5 `🔴` Project Red Lines (including Git & Subagent/`teamwork` Topology with Velocity-Optimized 5-Role Matrix, Promote-on-Review ladder, Milestone Child Visibility `conversation://<id>`, 180s adaptive watchdog, and Pre-Wave Snapshot + Scope-Escape Kill Switch if configured, plus `Read-Once` + `read_anchors` boot note), Directory/Sub-Project Map table, Single-Path Canonical Commands, and `.agents/knowledge/` links.
2. **`<workspace>/.agents/knowledge/memories.md`** (from [`./resources/memories.template.md`](./resources/memories.template.md)):
   - Seed with 3–5 verified facts discovered in Step 1 (topology, test runner, deploy target) under the standard 5-section FIFO header (`CRITICAL`, `Environment`, `Decisions`, `Patterns`, `Gotchas`, `<=4 KB`).
3. **Git Integration & v2.3.0 Migration Checklist**:
   - If `Personal overlay` selected: append `GEMINI.md`, `AGENTS.md`, and `.agents/` to `<workspace>/.git/info/exclude` ONLY when `<workspace>/.git` exists as a real Git directory (never create a fake `.git/info/exclude` in a non-git multi-repo umbrella root, where root adapter files are already outside child git repos!).
   - If `Solo / Team` selected and `<workspace>/.git` exists: append `.agents/handoffs/` and `.agents/teamwork/` to `<workspace>/.gitignore` (idempotently ensuring both directories are present while preserving existing lines).
   - **v2.3.0 Migration Checklist (`--migrate`)**:
     * **PreToolUse Guard**: Verify `hooks.json` executes via the portable `./scripts/mpm-py` wrapper (which pins `Python >= 3.8` stdlib-only in `~/.gemini/config/agy-mpm-core.env` or kit `.venv`, preventing breakage when project `.venv`s activate or when launching from GUI IDE Dock with empty `PATH`).
     * **Gitignore Hygiene**: Ensure `.agents/teamwork/` and `.agents/handoffs/` are both ignored in `.gitignore`.
     * **Multi-Project Check Reminder**: Remind the user they can audit all existing local repositories at once by running `./install.sh --check-projects ~/Projects/*` from the kit repository.

### B. Extended Files for `--full` and `--migrate`
1. **`<workspace>/.agents/rules/10-project-operations.md`** (from [`./resources/10-project-operations.template.md`](./resources/10-project-operations.template.md)):
   - `trigger: model_decision` — CI/CD pipelines, K8s/cloud rollout commands, namespace maps, secret retrieval scripts, and analytical query traps.
2. **`<workspace>/.agents/rules/11-project-confidentiality.md`** *(when selected)* (from [`./resources/11-project-confidentiality.template.md`](./resources/11-project-confidentiality.template.md)):
   - `trigger: always_on` — cloud project isolation, tenant/client/PII redaction, internal stack confidentiality.
3. **Sub-Project Rules `<workspace>/.agents/rules/12-<subproject>.md`** *(if needed)*:
   - `trigger: glob` + `globs: "**/packages/backend/**"` — use Antigravity's exact plural YAML frontmatter key with a single quoted comma-separated string, mandatory `**/` prefix, and zero `{a,b}` braces (NEVER singular `glob:`!).
4. **Knowledge Base Files `<workspace>/.agents/knowledge/{00-INDEX.md, active-tasks.md, postmortems.md}`** (from [`./resources/00-INDEX.template.md`](./resources/00-INDEX.template.md), [`./resources/active-tasks.template.md`](./resources/active-tasks.template.md), [`./resources/postmortems.template.md`](./resources/postmortems.template.md)):
   - Create missing files. If `00-INDEX.md` already exists, smart-merge authority tables and knowledge links.
5. **Convert Legacy Workflows**:
   - If legacy `.agents/workflows/<name>.md` files were found, migrate them into `.agents/skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`).

---

## Step 5: Mandatory Lossless Verification Gate (`code-critic`)

When migrating from existing rule files or smart-merging:
1. Invoke the adversarial **`code-critic`** subagent (`Model="pro"` or `inherit`, `Effort: High`):
   - Supply the backup directory path `<appDataDir>/brain/<conversation-id>/scratch/rule-migration-backup/` and the newly generated adapter files.
   - Task: Audit all migrated adapter files against the pre-migration originals to verify:
     - **0 project-specific invariants or red lines dropped.**
     - **0 canonical commands, test scripts, or rollout commands omitted.**
     - **0 critical regexes, namespace mappings, or architectural links lost.**
     - **0 Universal Core duplicates injected into `.agents/rules/`.**
2. If `code-critic` returns `BLOCK` or `WARN` for missing invariants, patch the adapter files and re-verify before completing.

---

## Step 6: Verify & Report
1. Verify exact file sizes with `wc -c`: confirm every `.agents/rules/*.md` is `<24,000` bytes.
2. Verify frontmatter syntax (`GEMINI.md` must have **no** frontmatter; rules must have valid `trigger:`).
3. Check `git status -s` to verify clean staging boundary.
4. Present clickable `file://` links to all created/updated adapter files and a concise post-migration summary.
