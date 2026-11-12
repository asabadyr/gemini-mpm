# {{PROJECT_NAME}} — Hierarchical Knowledge Base Index (`00-INDEX`)

> **Last Consolidated:** `{{YYYY_MM_DD}}`

---

## 1. Chronological Authority & Conflict Resolution Matrix

When older notes or static docs conflict with newer findings, **the newer verified date and live codebase win**:

| Topic | Older / Superseded State | Current Authoritative State | Authority Source & Date |
|---|---|---|---|
| **Initial Adapter Bootstrap** | Unstructured ad-hoc notes | Initialized structured `.agents/knowledge/` + `agy-mpm-core` adapter | `/kit-bootstrap` (`{{YYYY_MM_DD}}`) |

---

## 2. Directory Structure of `.agents/`

```text
.agents/
├── rules/
│   ├── 10-project-operations.md      # CI/CD, cloud/K8s rollout, secrets & query traps (model_decision)
│   └── 11-project-confidentiality.md # Optional non-disclosure & tenant redaction (always_on)
├── knowledge/
│   ├── 00-INDEX.md                   # Master index & chronological authority matrix
│   ├── memories.md                   # Typed 5-section FIFO-capped project memory (<=4 KB)
│   ├── active-tasks.md               # Active workstreams & OUT-OF-SCOPE parked backlog
│   └── postmortems.md                # Dated root-cause engineering postmortems
└── handoffs/                         # Gitignored session pause/resume snapshots
    └── LATEST.md
```
