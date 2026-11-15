# {{PROJECT_NAME}} — Root Workspace & Project Adapter

{{TWO_SENTENCE_WORKSPACE_OVERVIEW}}

> **Rule Profile (`Full` Adapter + `agy-mpm-core`)**: Universal MPM guardrails (`00..04`, `20..28`), `/kit-bootstrap`, `/kit-architecture`, `/kit-handoff`, and `code-critic` load from global plugin `agy-mpm-core`. Project CI/CD, rollout, and ops runbooks live in [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md) (and confidentiality boundaries in [`.agents/rules/11-project-confidentiality.md`](file://{{WORKSPACE_PATH}}/.agents/rules/11-project-confidentiality.md) when enabled).

---

## 1. Top Project-Critical Red Lines (`🔴`)
1. **{{RED_LINE_1_TITLE}}**: {{RED_LINE_1_SUMMARY}}
2. **{{RED_LINE_2_TITLE}}**: {{RED_LINE_2_SUMMARY}}
3. **{{RED_LINE_3_TITLE}}**: {{RED_LINE_3_SUMMARY}}
4. **Git & Subagent/Teamwork Topology**: {{GIT_AND_ORCHESTRATION_RED_LINE}} <!-- Workspace git structure, explicit-path staging, plus exact Role -> Model+Effort matrix & Promote-on-Review ladder if configured -->
5. **Confidentiality & Secrets**: {{CONFIDENTIALITY_OR_SECRET_RED_LINE}}

---

## 2. Directory / Sub-Project Map

| Component / Path | Artifact / Runtime | Deploy Branch | Role |
|---|---|---|---|
| [`{{COMPONENT_1}}`](file://{{WORKSPACE_PATH}}/{{COMPONENT_1}}) | `{{ARTIFACT_1}}` | `{{BRANCH_1}}` | {{ROLE_1}} |
| [`{{COMPONENT_2}}`](file://{{WORKSPACE_PATH}}/{{COMPONENT_2}}) | `{{ARTIFACT_2}}` | `{{BRANCH_2}}` | {{ROLE_2}} |

---

## 3. Canonical Commands

| Scope | Lint / Typecheck | Test | Build / Rollout Reference |
|---|---|---|---|
| `{{SCOPE_1}}` | `{{LINT_1}}` | `{{TEST_1}}` | See [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md) |

---

## 4. Hierarchical Knowledge Repository (`.agents/knowledge/`)

> **Subagent & `teamwork` Boot (`🔴`)**: Pass `GEMINI.md`, `00-INDEX.md`, `memories.md`, and relevant doc paths in every `Prompt` / `DISPATCH.md` / `brief`; workers MUST read them first before broad code scans.

Consult [`.agents/knowledge/00-INDEX.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/00-INDEX.md) and [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md) before broad codebase exploration:
- **Master Index & Authority Matrix**: [`.agents/knowledge/00-INDEX.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/00-INDEX.md)
- **Bounded Project Memory (`FIFO`)**: [`.agents/knowledge/memories.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/memories.md)
- **Project Operations & CI/CD Rules**: [`.agents/rules/10-project-operations.md`](file://{{WORKSPACE_PATH}}/.agents/rules/10-project-operations.md)
- **Active Tasks & Postmortems**: [`.agents/knowledge/active-tasks.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/active-tasks.md), [`.agents/knowledge/postmortems.md`](file://{{WORKSPACE_PATH}}/.agents/knowledge/postmortems.md)
