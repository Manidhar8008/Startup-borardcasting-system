# SaaS Safety Baseline Changelog

Branch: `feat/jan-ai-saas-safety-baseline`

## Added
- `core/saas_security.py`: reusable dependencies for active authenticated users and brand ownership checks.
- `tests/test_saas_security.py`: focused unit tests for inactive account rejection, active account acceptance and non-disclosing brand ownership failure.
- Product specification, implementation backlog and initial API security review are on `main` and tracked in issue #1.

## Important limitation
The helper module is not yet wired into every existing endpoint. Current routes in `api/server.py` still need systematic migration to these dependencies, and the legacy publishing endpoint needs the placeholder/live-publishing behavior removed before the API is exposed as a public SaaS. Do not treat this branch as a deployable security fix until integration tests prove the full route set is protected.
