---
trigger: model_decision
description: "Activate when building images/packages, deploying, updating Kubernetes/cloud manifests, managing secrets, running CI/CD pipelines, or running domain metrics/queries in {{PROJECT_NAME}}."
---

# Project Operations, CI/CD & Infrastructure Runbook (`10`)

## 1. CI/CD & Artifact Build Pipeline (`🔴`)
| Component | Build Trigger & Registry | Local Build Allowed? | Notes |
|---|---|---|---|
| `{{COMPONENT_1}}` | Push to `{{BRANCH_1}}` → `{{CI_SYSTEM}}` → `{{IMAGE_REGISTRY}}` | {{LOCAL_BUILD_POLICY}} | {{CI_NOTES}} |

## 2. Deployment & Rollout Guardrails (`🔴`)
- **Rollout Command**: `{{SAFE_ROLLOUT_COMMAND}}`
- **Replica / Autoscaler Ownership**: {{REPLICA_OWNERSHIP_TRAP}}
- **Manifest Image Bump Regex**: Anchor replacements on the full registry path (`{{REGISTRY_REGEX_EXAMPLE}}`)—never `<name>:[0-9.]+`, which rewrites port numbers in service URLs.
- **Directory ↔ Environment / Namespace Mapping**:
  - `{{FOLDER_1}}` → `{{NAMESPACE_1}}`

## 3. Secrets & Environment Configuration (`🔴`)
- {{SECRETS_STORAGE_AND_MANAGEMENT_SCRIPT}}

## 4. Domain-Specific Analytical & Query Traps (`🟡`)
- **Timestamps & IDs**: {{TIMESTAMP_AND_ID_CONVENTIONS}}
- **Active Population Filters**: {{SURVIVAL_FILTER_CONVENTIONS}}
