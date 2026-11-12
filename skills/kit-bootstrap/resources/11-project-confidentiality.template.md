---
trigger: always_on
description: "Mandatory confidentiality, shared cloud project isolation, client/tenant/PII non-disclosure, and external communication redaction rules for {{PROJECT_NAME}}."
---

# Project Confidentiality & Redaction Rules (`11`)

## 1. Environment & Account Scope Boundaries (`🔴`)
- **Account & Scope Isolation**: Scope all diagnostics, queries, and documentation strictly to `{{PROJECT_NAME}}` (`{{CLOUD_PROJECT_ID}}`); never include out-of-scope services or sibling environments in deliverables.

## 2. External & Public Content Redaction (`🔴`)
In any external-facing material (public repos, blog posts, docs, customer/partner briefs):
- **NEVER** disclose customer/tenant identifiers or private environment names (`{{EXAMPLE_REDACTED_SCOPE}}`).
- **NEVER** disclose employee or end-user PII (names, emails, phone numbers, or account IDs).
- **NEVER** expose internal hostnames, private endpoints, schema internals, or credential/key paths—use generic architectural descriptions instead.
