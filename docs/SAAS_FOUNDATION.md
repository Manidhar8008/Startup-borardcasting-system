# JAN AI SaaS — Product and Technical Specification

**Status:** Foundation specification  
**Source engine:** https://github.com/Manidhar8008/Startup-borardcasting-system  
**Related UI prototype:** https://github.com/Manidhar8008/JANANI.AI  
**Tracking issue:** https://github.com/Manidhar8008/Startup-borardcasting-system/issues/1

## 1. Product definition

JAN AI is an AI co-founder and media operations SaaS for solo founders, small teams, and agencies. It turns founder context and market signals into researched content, runs a reviewable multi-agent production pipeline, publishes only through configured integrations after explicit approval, and learns from analytics.

Core loop: `Capture → Research → Strategy → Draft → Quality check → Human approval → Schedule/Publish → Measure → Learn`.

The existing Startup Broadcasting System remains the execution engine. SaaS concerns (identity, tenancy, billing, audit, job execution, API contracts) should be isolated around it. The separate JANANI.AI repo is currently a Vite/React/Express/Prisma starter with generic task/log entities; do not merge it blindly or maintain two competing backends.

## 2. Target users and jobs

- **Solo founder:** operate one brand and a consistent publishing workflow without hiring a full marketing team.
- **Creator/operator:** manage ideas, drafts, calendar and publishing across multiple channels.
- **Agency:** manage multiple client workspaces and brands with clear permissions and separate analytics.

The first paid value proposition should be one repeatable, approval-first content workflow that saves founder time. Avoid claiming full autonomy or integrations until verified end-to-end.

## 3. MVP scope

### Required
1. Sign up, sign in, sign out, profile and workspace.
2. Workspace and brand setup: industry, audience, positioning, voice, offer, exclusions and reference material.
3. Research/idea feed using existing research and topic-ranking agents.
4. Content studio: generate per-platform drafts, edit, version and run quality checks.
5. Approval queue with explicit approve/reject actions and actor/timestamp audit.
6. Calendar and publishing queue; provider capability and credential status shown honestly.
7. Analytics: per-post performance, engagement and reporting freshness.
8. Subscription/usage page with server-side plan enforcement.
9. Settings: team roles, connections, data export and account deletion workflow.
10. Operations: job state, retry visibility, structured logs, health checks and error reporting.

### Deferred until the core loop is stable
- Automatic posting without approval (do not build for MVP).
- Scraping or integrations that violate a platform's terms.
- Multi-agent autonomous financial spend or outbound messaging.
- Complex agency white-labeling, referral program, advanced attribution and mobile applications.

## 4. Recommended architecture

### Preserve and reuse
- Python/FastAPI in `api/`.
- Existing agent/research/content/memory/distribution and analytics modules.
- SQLAlchemy models in `database/` after migration review.
- Existing CLI pipeline for local/offline and operator workflows.

### SaaS boundary
- **Frontend:** React + TypeScript. JANANI.AI may become the frontend after removing its unrelated task/log model, or a dedicated frontend can live in this repository. Pick one authoritative frontend before shipping.
- **API:** FastAPI remains the source of truth for application logic; avoid adding Express as a second business backend.
- **Database:** PostgreSQL in production. SQLite may remain a local development/test adapter if intentionally supported. Use Alembic migrations rather than relying on `create_all` at application startup.
- **Jobs:** a persistent queue for research/generation/publishing jobs with retries, exponential backoff, idempotency keys and dead-letter visibility. Choose the implementation after measuring current infrastructure; do not run expensive jobs inside HTTP request handlers.
- **Blob storage:** object storage abstraction for uploaded reference files and generated media; never store user uploads inside the source tree.
- **LLM providers:** provider adapter layer with timeouts, budgets, token/cost accounting, schema validation and fallback policies.
- **Integrations:** explicit provider capability contracts; provider credentials encrypted at rest and never exposed back to clients.
- **Observability:** structured logs, correlation/request IDs, job IDs, health/readiness endpoints, error reporting and metrics.

## 5. Tenant and authorization model

Every tenant-owned row must be linked to a `workspace_id` or equivalent tenant boundary. Do not use a client-supplied integer as proof of identity.

Core entities:
- `users`: identity, state and timestamps.
- `workspaces`: tenant, name, owner and lifecycle.
- `workspace_members`: user, workspace, role, invite state.
- `brands`: workspace, voice profile, audience, industry and settings.
- `subscriptions`: workspace, plan, billing customer/subscription IDs, status and renewal data.
- `usage_events`: workspace, meter, quantity, idempotency key, timestamp and metadata.
- `ideas`: workspace/brand, source, rationale, score and lifecycle status.
- `content_items`: workspace/brand, platform, draft, status and version.
- `content_versions`: immutable revisions, author/agent, source references and timestamp.
- `approvals`: content/version, approver, decision, reason and timestamp.
- `publishing_jobs`: content/version, provider, schedule, idempotency key, attempt state and retry timing.
- `provider_accounts`: workspace, provider, encrypted credential reference, scopes, status and last validation.
- `publication_receipts`: provider post ID/URL, published timestamp and response metadata (redacted).
- `analytics_snapshots`: publication, metrics, collection timestamp and source.
- `audit_events`: workspace, actor, action, entity, timestamp and safe metadata.

All database reads/writes must be tenant-scoped through authenticated dependencies and tested for cross-tenant access. Add indexes for `workspace_id`, entity IDs, status and created/scheduled timestamps. Use database constraints for uniqueness and referential integrity.

## 6. Content lifecycle and safety gates

Canonical state machine: `idea → draft → review_pending → approved → scheduled → publishing → published`.

Alternative terminal/recovery states: `rejected`, `failed`, `cancelled`.

Rules:
- Editing a draft creates a new version. Approval applies to one exact content version and target platform.
- Any edit after approval invalidates that approval and returns the new version to review.
- Live publishing requires stored approval, a valid connection, supported provider capability, available quota, and a due/authorized job.
- Use dry-run by default in local and test environments. Make live publishing an explicit production configuration.
- Record provider response IDs and timestamps. If a provider is unconfigured or mocked, status must be `not_configured` or `simulated`, never `published`.
- Idempotency keys must prevent duplicate posts on retries. Handle unknown provider outcomes as reconciliation-required rather than blindly retrying.
- Keep audit logs for approvals, credential changes, schedule changes and publish attempts.

## 7. API contract (initial target)

Prefix versioned endpoints with `/api/v1`. Existing routes can be retained temporarily for compatibility but must be brought under auth/tenant scope before public SaaS exposure.

- `GET /health/live`, `GET /health/ready`
- `GET/POST /api/v1/workspaces`
- `GET/POST /api/v1/brands`
- `GET/POST /api/v1/ideas`
- `POST /api/v1/ideas/{id}/generate`
- `GET/POST /api/v1/content`
- `GET/PATCH /api/v1/content/{id}`
- `POST /api/v1/content/{id}/submit-review`
- `POST /api/v1/content/{id}/approve`
- `POST /api/v1/content/{id}/reject`
- `GET/POST /api/v1/publishing-jobs`
- `POST /api/v1/publishing-jobs/{id}/cancel`
- `GET /api/v1/calendar`
- `GET /api/v1/analytics/overview`
- `GET /api/v1/integrations`
- `POST /api/v1/integrations/{provider}/connect` (OAuth/callback flow as provider supports)
- `GET /api/v1/billing/plan`, `GET /api/v1/billing/usage`
- `POST /api/v1/billing/checkout`, `POST /api/v1/billing/webhook` (signature verification required)

Use Pydantic request/response models, consistent error envelopes, pagination, validation, rate limits and OpenAPI contracts.

## 8. Plans and usage

Start with three plan definitions, and validate price/limits with customers before publishing final pricing:
- **Free:** one workspace/brand, small monthly generation allowance, manual export and dry-run workflow.
- **Creator/Pro:** more brands, higher generation allowance, calendar, supported integrations and analytics.
- **Agency:** multiple brands/workspaces, team roles, client separation and higher limits.

Implementation requirements:
- Keep entitlements in a central plan catalog, not scattered conditionals.
- Enforce limits server-side and reserve usage atomically before starting costly jobs.
- Track units such as generation requests, model tokens/cost, research jobs and successful publications.
- Billing webhook handlers must verify signatures and be idempotent.
- Never grant a paid tier based only on a client request. A provider event or trusted admin action must reconcile the subscription.
- Show the user consumption, reset period and what happens at the limit.

## 9. Security and privacy baseline

- Remove `allow_origins=["*"]` for production; configure exact origins.
- Remove `user_id=1` defaults and never accept user identity from query/body as authority.
- Eliminate live publishing based on fabricated in-memory drafts.
- Validate all environment variables and fail startup when production-required configuration is absent.
- Use secure, HttpOnly, SameSite cookies or a well-defined token strategy; protect state-changing cookie-authenticated requests against CSRF.
- Apply rate limiting, password/session security, email verification and recovery if local credentials are supported.
- Encrypt provider tokens and secrets at rest; redact them from logs/errors.
- Implement deletion/export retention policy and disclose which data is sent to third-party LLM/provider services.
- Do not commit local databases, media, credentials or `.env` files.
- Use migrations, dependency scanning, tests and secret scanning in CI.

## 10. UI information architecture

Navigation: Overview; Research & Ideas; Content Studio; Approval Queue; Calendar; Distribution / Integrations; Analytics; Brand Voice / Knowledge; Team & Workspace; Plan & Usage; Settings.

The overview should surface what needs attention now: ideas awaiting selection, drafts awaiting approval, scheduled jobs, failed jobs, integration health and recent performance. Avoid vanity metrics with no actionable next step.

## 11. Delivery plan

### Phase 0 — harden the boundary
- Document import/dependency graph and current routes.
- Add tests reproducing default-user, cross-tenant and publishing-placeholder risks.
- Decide authoritative frontend and persistence configuration.
- Add migration baseline and production config validation.

### Phase 1 — usable single-workspace beta
- Auth, workspace, tenant-scoped brands.
- Content/version lifecycle and approval audit.
- Draft, review and calendar APIs.
- UI onboarding and content studio.
- Dry-run publishing adapter and honest provider status.

### Phase 2 — reliable execution
- Persistent queue, idempotency, retries, cancellation and dead-letter view.
- Connect one provider end-to-end after verifying permitted API access.
- Analytics ingestion and attribution to publication receipts.
- Observability and operator tools.

### Phase 3 — revenue infrastructure
- Plan catalog, atomic usage metering and signed billing webhooks.
- Checkout/portal integration with one chosen billing provider.
- Workspace roles, invitations and agency separation.
- Export/deletion and operational runbooks.

### Phase 4 — measured intelligence
- Retrieval quality/evaluation for founder context.
- Strategy and quality agents with versioned prompts and evaluations.
- Learning from trustworthy, timestamped analytics.
- Optional scheduled automation, still approval-gated by default.

## 12. Release gates

- [ ] No tenant can read/change another tenant's data (automated tests).
- [ ] Approval is tied to a specific content version and channel.
- [ ] Publishing retries cannot create duplicate posts.
- [ ] Stubbed or missing integrations cannot report success.
- [ ] Usage cannot be exceeded by concurrent requests.
- [ ] Production secrets/configuration are validated and redacted.
- [ ] Database changes run through migrations.
- [ ] Tests, lint/type checks and build pass in CI.
- [ ] User can understand data handling, subscription status and failure states.
