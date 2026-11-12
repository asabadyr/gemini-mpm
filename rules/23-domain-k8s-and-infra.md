---
trigger: glob
globs: "**/*.yaml, **/*.yml, **/Dockerfile, **/*.tf, **/*.sh"
description: "Kubernetes, Docker, Terraform, and shell guardrails: registry-anchored image regexes, dynamic replica safety, secret redaction, and strict shell error handling."
---

# Domain Pack: Kubernetes, Containers & Infra (`23`)

## Critical Infrastructure & Deployment Guardrails
| Area | Trap | Mandatory Practice |
|---|---|---|
| **Dynamic `spec.replicas` Trap (`🔴`)** | Running `kubectl apply -f deployment.yaml` when git stores `replicas: 0` (or static count) while an HPA or custom orchestrator owns live scaling | Inspect live replica ownership first (`kubectl get deploy <name> -n <ns>`); roll out images via `kubectl set image` or targeted patch so active pods are never scaled to `0` |
| **Narrow Image-Tag Regex (`🔴`)** | Replacing `<name>:[0-9.]+` across YAML files, accidentally rewriting port numbers in ConfigMap URLs (`http://my-service:4000`) | Always anchor image tag edits on the **full registry path** (`<registry>/<project>/<image>:[0-9]+\.[0-9]+\.[0-9]+`) or `image:` YAML key, and inspect `git diff` line-by-line |
| **Folder ↔ Namespace Mapping (`🔴`)** | Assuming directory names in IaC repos always equal live K8s namespaces or cloud workspaces | Verify actual `metadata.namespace` inside manifests / project operations docs before running `kubectl -n <ns>` or `terraform apply` |
| **Secrets & Git Hygiene (`🔴`)** | Committing plaintext/base64 `Secret` manifests, `.tfvars`, kubeconfigs, or service-account JSON keys | Keep secret manifests gitignored and backed by Secret Manager / sealed vaults; verify `git diff --cached` contains zero credentials |
| **Container & Pod Sizing** | Unpinned `:latest` tags, root user processes, or missing `requests`/`limits` and readiness probes | Pin immutable tags/digests, define explicit CPU/memory `requests` & `limits`, handle `SIGTERM` gracefully, and configure `readinessProbe`/`livenessProbe` |
| **Shell Script Safety** | Silent partial execution on unset variables, failed pipes, or unquoted paths | Start bash/zsh scripts with `set -euo pipefail`, quote `"$var"` expansions, and guard destructive commands (`rm`, `kubectl delete`) with explicit target checks |
