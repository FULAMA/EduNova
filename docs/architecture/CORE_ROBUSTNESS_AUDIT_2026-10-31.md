# EduNova Core — Robustness Audit and Six-Stage Hardening Plan

Date: 2026-10-31
Branch: `maintenance/edunova-mypy-cleanup`
Scope: repository-level review; no production database or local database was opened or migrated.

## Executive status

The audited billing core now has database-enforced protections for fee applicability snapshots, reversal/receipt linkage, immutable counter-entries, counter-entry/payment amount and currency consistency, immutable receipts, and immutable payment ledger rows (migrations 032–038).

Migration 038 and its test suite both completed GitHub Actions successfully:
- Migration workflow: https://github.com/FULAMA/EduNova/actions/runs/41177107888
- Test workflow: https://github.com/FULAMA/EduNova/actions/runs/41177114281

These results validate the workflow jobs for those commits; they do not constitute a full security certification of the platform.

## Findings confirmed during source review

### Authorization
- Billing endpoints use explicit finance-role dependencies.
- Fee catalogue management is restricted to ADMIN and DIRECTION.
- Finance access is checked against the active tenant membership role, not merely the global JWT role.
- Existing HTTP integration tests cover unauthorized roles, cashier restrictions, inactive memberships, inactive tenants, inactive users, and invalid tokens.
- Remaining audit: systematically compare every route's required role against the domain action and test role escalation across all modules.

### Tenant isolation
- Tenant context is extracted from a signed access token and checked against an active tenant and active membership.
- Billing repository queries inspected are tenant-scoped; key finance tables use tenant-composite keys and foreign keys.
- Cross-tenant integrity migrations and tests exist.
- Remaining audit: enumerate every repository query and every relationship for tenant predicates/composite foreign keys; add adversarial two-tenant HTTP tests for all sensitive endpoints.

### Concurrency
- Payment recording and fee assignment use SQLite `BEGIN IMMEDIATE`, and uniqueness/idempotency constraints backstop retries.
- Reversal also uses `BEGIN IMMEDIATE` and a unique key per tenant/original payment.
- Remaining audit: stress concurrent payment, duplicate idempotency-key, duplicate assignment, and duplicate reversal requests; verify behavior on the intended production database engine before claiming cross-engine guarantees.

### Financial ledger
- Payments are recorded with receipts in one transaction.
- Corrections append counter-entries; the original payment is preserved.
- Reversal entries must match a confirmed payment's amount and currency; reason/actor/time are required.
- Receipts and payments are immutable after issuance/recording; corrections are represented by counter-entries.
- Remaining audit: validate charge lifecycle constraints, receipt/payment consistency for legacy data, decimal precision rules, and all failure/rollback paths.

### Authentication and sessions
- Access JWTs have expiry and type checks; current-user resolution checks account existence and active status.
- Refresh tokens have unique JTIs and a persistent consume/revocation mechanism.
- Tenant membership is revalidated against persistence on protected tenant routes.
- Remaining audit: confirm refresh rotation/replay behavior, logout semantics, access-token revocation expectations, signing-key rotation, issuer/audience policy, and rate limits on login/2FA endpoints.

### Resilience and observability
- Migration runner wraps migration execution in a savepoint and rolls back on failure.
- Database initialization rejects an existing non-empty database without migration history.
- Remaining audit: test crash/retry behavior, migration failure recovery, SQLite busy/timeout policy, structured audit events, correlation IDs, health checks, backup/restore, and operational alerting.

## Six authorized hardening stages

1. **Authorization matrix** — inventory routes, roles, tenant membership, ownership and action-level permissions; add negative integration tests.
2. **Tenant isolation campaign** — inspect all repositories and joins; build two-tenant adversarial tests and fix leaks.
3. **Concurrency and idempotency** — add parallel request tests for payments, fee assignments, reversals and academic transitions; document engine-specific guarantees.
4. **Financial integrity** — inspect charge lifecycle, decimal/currency invariants, ledger consistency and rollback; add database constraints/triggers only where compatible with existing workflows.
5. **Identity and session security** — inspect login, 2FA, refresh rotation, replay, logout, JWT configuration and brute-force protections; harden with regression tests.
6. **Resilience and observability** — validate migration rollback/restart, database failure handling, audit logging, health/diagnostic signals and recovery procedures.

## Guardrails

- Keep all work on this maintenance branch until the relevant tests and review gates pass.
- Do not merge to `main` automatically.
- Do not run migrations against `edunova.db` or `edunova_dev.db`.
- Do not replace append-only financial corrections with destructive updates.
- Keep the modular monolith; do not introduce microservices without measured operational need.
- Do not claim a stage is complete without evidence from tests or source-level verification.

## Current assessment

The financial persistence layer is materially stronger after migrations 032–038. A numeric platform-wide robustness score is intentionally withheld until the six stages are completed: the current evidence is concentrated in finance and selected identity/tenant paths, not a full-system penetration test or operational resilience exercise.
