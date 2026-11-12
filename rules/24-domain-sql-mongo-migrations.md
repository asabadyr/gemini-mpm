---
trigger: glob
globs: "**/migrations/**, **/*.sql, **/*schema*, **/*model*, **/*repo*"
description: "SQL, MongoDB, and data-layer guardrails: timestamp/ID type traps, driver return-shape changes, active-population filters, index selectivity, and expand-contract migrations."
---

# Domain Pack: SQL, MongoDB & Migrations (`24`)

## Critical Data-Layer & Migration Guardrails
| Area | Trap | Mandatory Practice |
|---|---|---|
| **ID & Timestamp Representation (`🔴`)** | Querying `ObjectId` columns with hex `string` (or vice versa), or mixing Unix seconds (`10` digits) with milliseconds (`13` digits) / `Date` objects | Inspect real collection/table documents and model schemas first; normalize IDs and timestamp units explicitly at repository boundaries |
| **Driver / ORM Return Shapes (`🔴`)** | Assuming `findOneAndUpdate` / `upsert` returns raw `doc` vs `{ value: doc }` across driver upgrades (e.g. MongoDB Node driver v4 → v5/v6) | Check exact installed driver version in lockfile and unwrap/type-test return values in unit/integration tests |
| **Tenant & Survival Filters (`🔴`)** | Missing `tenantId`/`companyId` predicates or counting soft-deleted (`deleted: true`) / disabled records in business or analytical queries | Scope every multi-tenant read/write by tenant key and explicitly filter active/non-deleted records unless querying raw audit logs |
| **Index & Cursor Safety** | Unindexed collection scans, unbounded `.toArray()` / `SELECT *` on multi-million-row tables, or non-ESR compound indexes | Follow **Equality → Sort → Range (ESR)** index order, paginate or stream cursors with batch sizes, and project only needed fields |
| **Zero-Downtime Migrations** | Renaming/dropping columns or adding `NOT NULL` locks in the same deploy as application code | Use **Expand → Backfill → Switch Reads/Writes → Contract** phases; build large indexes concurrently/in background |
| **Non-Atomic Multi-Collection Writes** | Updating mirrored state across 2+ collections without compensating audit/reconciliation | Use transactions where supported, or pair `Promise.allSettled` / idempotent upserts with explicit divergence logging and reconciliation |
