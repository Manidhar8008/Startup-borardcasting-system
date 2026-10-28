# Initial SaaS API Security Review

Review scope: current `api/server.py`, `auth/auth_routes.py`, `database/models.py`, `core/subscription_manager.py`, and `core/brand_manager.py` on `main`.

## Findings

### Critical — implicit identity in SaaS endpoints
`GET/POST /brands` and `GET /subscription` currently default `user_id` to `1`. That makes tenant identity implicit and may return or mutate another user's records. Replace with `get_current_user` dependency and derive the user/workspace from the token, never from a caller-supplied ID.

### Critical — unsafe placeholder publishing path
`POST /publish` constructs a draft string from the request ID and invokes the publisher with `dry_run=False`. It does not load a persisted draft or verify an approval for the specific draft version/platform. Replace with persisted look-up, tenant ownership, state-machine and approval checks; fail closed when provider is not configured.

### High — permissive CORS
`api/server.py` allows all origins. Restrict to exact configured production origins; keep local-only origins in development config.

### High — schema creation at runtime / migration drift
`Base.metadata.create_all()` runs at import/startup. Adopt reviewed database migrations (Alembic) for production schema changes and keep startup free of implicit schema mutation.

### High — subscription limits are not a billing system
Current `SubscriptionManager` only checks an in-memory/simple database count and has large sentinel limits for paid plans. It does not verify billing-provider state or reserve usage atomically. Add centralized entitlements, trusted billing reconciliation and atomic usage reservations before exposing paid plans.

### Medium — in-process rate limiter does not scale
`InfrastructureMiddleware` maintains per-IP timestamps in a process-local dictionary. It resets per process, uses unbounded per-IP keys, and is not shared across replicas. Replace or supplement with a shared rate-limiting store at the SaaS edge/API layer.

### Medium — publishing result correctness
Any connector stub or uncertain provider response must be represented honestly. Store provider receipt IDs, errors and attempt state; retry with idempotency/reconciliation to avoid duplicate posts.

## Release-blocking test matrix

- Anonymous request cannot read brands, subscription or content.
- User A cannot read/update/delete User B's brand/content/publishing job.
- Approval for a prior version does not authorize a changed version.
- No live publish without approval and an active supported provider connection.
- Provider timeout does not yield a false `published` state; retry cannot duplicate a post.
- Concurrent generation requests cannot exceed workspace quota.
- Billing webhook with invalid signature has no effect; repeated valid webhook is idempotent.
- Production startup rejects missing critical secrets/config and wildcard CORS.

This is an initial code review, not a complete penetration test or certification.
