# JAN AI SaaS — Implementation Backlog

Tracking issue: https://github.com/Manidhar8008/Startup-borardcasting-system/issues/1
Architecture: [SAAS_FOUNDATION.md](./SAAS_FOUNDATION.md)

## P0 — Block unsafe public use
- [ ] Replace wildcard CORS with exact configured frontend origins.
- [ ] Remove `user_id=1` defaults on `/brands` and `/subscription`; require authenticated identity.
- [ ] Verify the authenticated user's ownership of every brand/content ID before reading or mutating it.
- [ ] Replace `/publish` placeholder draft with a persisted content lookup and explicit approval check.
- [ ] Keep live publishing disabled unless `DRY_RUN=false`, the provider is configured, and the stored version has approval.
- [ ] Add tests proving unauthenticated and cross-workspace access is rejected.

## P1 — Coherent tenant foundation
- [ ] Choose one frontend. Recommended: React/TypeScript UI; FastAPI is the authoritative business API.
- [ ] Add workspace and workspace-membership entities, roles, migrations and indexes.
- [ ] Migrate brands, subscriptions, content and analytics to a workspace boundary without losing existing data.
- [ ] Add explicit API request/response schemas and `/api/v1` route namespace.
- [ ] Set production config validation, exact CORS allowlist, secure credential handling and secret redaction.

## P2 — Approval-first content operations
- [ ] Add content version, approval/audit event, publishing job and publication receipt records.
- [ ] Make approval refer to one exact draft version and target platform.
- [ ] Add persistent queue, retry/backoff, cancellation, idempotency and dead-letter inspection.
- [ ] Mark absent/mocked connectors as `not_configured` / `simulated`, never `published`.
- [ ] Add job status, calendar and integration-health UI.

## P3 — Billing and usage
- [ ] Central plan/entitlement catalog.
- [ ] Atomic usage reservations and usage events for generation/research/publishing.
- [ ] Billing provider adapter, verified webhook signatures and idempotent event processing.
- [ ] Plan/usage UI; never trust client-submitted plan status.

## P4 — Release engineering
- [ ] Add pytest coverage for auth, tenant isolation, state machine, quota concurrency and provider failure.
- [ ] Add CI for tests, lint/type checks, dependency and secret scanning.
- [ ] Add Alembic migration workflow, health/readiness checks, staging deployment and rollback runbook.
- [ ] Document backup/restore, privacy/data retention and incident response.
