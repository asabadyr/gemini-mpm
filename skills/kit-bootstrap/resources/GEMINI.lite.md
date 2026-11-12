# {{PROJECT_NAME}} — Workspace Guide & Project Adapter

{{ONE_SENTENCE_PROJECT_PURPOSE}}

> **Rule Profile (`Lite` Adapter + `agy-mpm-core`)**: Universal MPM guardrails (`00..04`, `20..24`), `/kit-bootstrap`, `/kit-handoff`, and `code-critic` load automatically from global plugin `agy-mpm-core`. Persistent project facts live in [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md).

---

## 1. Project-Critical Red Lines (`🔴`)
- **Git Topology**: {{GIT_TOPOLOGY_NOTE}} — stage explicit task paths only (`git status -s` before/after commits).
- **Target Test Environment**: Always execute tests via `{{CANONICAL_TEST_CMD}}` (never treat `0 collected` or skipped target suites as green).
- **{{PROJECT_RED_LINE_3_TITLE}}**: {{PROJECT_RED_LINE_3_BODY}}

---

## 2. Canonical Single-Path Commands

| Operation | Command |
|---|---|
| **Install / Sync** | `{{INSTALL_CMD}}` |
| **Lint & Format Check** | `{{LINT_CMD}}` |
| **Typecheck** | `{{TYPECHECK_CMD}}` |
| **Test Suite** | `{{CANONICAL_TEST_CMD}}` |
| **Build / Package** | `{{BUILD_CMD}}` |

---

## 3. Repository Layout

| Path | Role |
|---|---|
| `{{DIR_1}}` | {{DIR_1_ROLE}} |
| `{{DIR_2}}` | {{DIR_2_ROLE}} |
| [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md) | Typed FIFO-bounded project memory (`<=4 KB`) |
