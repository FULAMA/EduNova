# EduNova — Security and Load Testing Runbook

## Scope and safety boundary

This runbook is for systems owned by the EduNova team only. Run load and security tests against a disposable local environment or an explicitly authorized staging environment. Never run the 10,000-VU profile against production, a third-party host, or a shared environment without a written test window, monitoring, and rollback plan.

The load script refuses public internet hosts by default. It requires `ALLOW_LOAD_TEST=YES` and accepts only localhost, loopback, or RFC1918 IPv4 addresses. This network guard is a safety rail, not a substitute for authorization.

## Test sequence

1. Static checks: compileall, mypy, Ruff, Bandit, dependency audit.
2. Unit/integration security tests: authentication, role authorization, tenant isolation, input validation, financial invariants, replay/idempotency, concurrent writes.
3. Baseline: 50 VUs, then 250 and 1,000 VUs.
4. Capacity profile: ramp through 2,500, 5,000, then 10,000 VUs only after the previous stage is healthy.
5. Recovery: stop traffic and verify latency, error rate, database locks, connection count, memory, CPU, and queue depth return to baseline.

## k6 execution

Install k6 from its official distribution. Start a dedicated EduNova test instance with a disposable database and synthetic data. Then:

```powershell
$env:K6_BASE_URL = "http://127.0.0.1:8017"
$env:ALLOW_LOAD_TEST = "YES"
k6 run scripts/load/edunova_capacity.js
```

The script sends only GET requests to the health endpoint and a finance endpoint without credentials. The latter must be rejected (401 or 403); no login brute force, payment creation, data mutation, or destructive request is performed.

The 10,000 VUs are virtual users, not a guarantee of exactly 10,000 packets arriving in the same millisecond. Network, OS, k6 host resources, server worker count, and database limits shape the achieved concurrency. Record actual request rate and latency from k6 output and server metrics.

## Security test matrix

- Authentication: missing, malformed, expired, wrong-type, and revoked access token.
- Authorization: each role against each protected action; default deny.
- Tenant isolation: tenant A token cannot read, mutate, enumerate, or infer tenant B records by changing IDs.
- Finance: concurrent overpayment, duplicate idempotency key, immutable payment/receipt history, reversal consistency.
- Input handling: invalid UUIDs, oversized payloads, unexpected enum values, SQL-like strings, path and query parameter boundaries.
- Abuse controls: rate limits on authentication and expensive endpoints; bounded request body, timeouts, and pagination.
- Browser/API: strict CORS allowlist, security headers, HTTPS/HSTS in production, CSRF protection wherever cookie authentication is used.
- Supply chain: fail CI on actionable high/critical dependency vulnerabilities after triage and approved exceptions.

## Release gates

Do not declare the platform secure based on a passing load test. Capacity testing measures resilience and performance, not exploit resistance. A release candidate must have no unresolved critical/high security findings, passing tenant-isolation and authorization tests, reviewed dependency alerts, and documented backup/restore verification.

## Evidence to retain

For each run record commit SHA, environment, database fixture version, k6 version, VU profile, achieved requests/second, p50/p95/p99 latency, HTTP error rate, CPU, memory, DB connections/locks, and recovery time. Never include real student or payment data in test evidence.
