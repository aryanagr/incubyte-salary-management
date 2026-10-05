# Release Runbook

## Quality gates
1. `cd backend && PYTHONPATH=. pytest --cov=app --cov-fail-under=85`
2. `cd backend && PYTHONPATH=. python scripts/benchmark_seed.py`
3. `cd frontend && npm install && npm run typecheck && npm run build`
4. Apply migrations against production PostgreSQL: `alembic upgrade head`
5. Seed deterministic demo data: `python -m app.seed --count 10000`
6. Deploy Vercel Services project from repository root through the linked GitHub `master` branch.
7. Smoke test `/health`, employee list/create/edit/delete, and country/job-title insights.
8. Check runtime logs for 5xx errors.

## Vercel shape
The repository uses Vercel Services so the Next.js frontend and FastAPI backend deploy atomically under one domain. `/api/*` routes to FastAPI; all other paths route to Next.js.

The backend requires a persistent `DATABASE_URL` pointing to PostgreSQL. SQLite is only for local development/tests and must not be treated as durable Vercel production storage.

## Production deployment state
- Vercel project: `incubyte-salary-management`
- Source of truth: GitHub `aryanagr/incubyte-salary-management`, branch `master`.
- Database: Neon PostgreSQL connected through the Vercel integration for Preview and Production.
- Production deployments must originate from Git; direct local-source deployment is intentionally avoided.

## First database initialization
The first live environment requires schema migration plus the deterministic 10,000-employee seed. The release process uses a temporary token-protected bootstrap endpoint at `/api/internal/bootstrap` only for this one-time initialization because the Vercel/Neon integration keeps database credentials opaque to external automation.

After successful initialization and verification:
1. Remove the bootstrap route and helper from application code.
2. Remove `BOOTSTRAP_TOKEN` from Vercel environments.
3. Deploy the cleanup commit from GitHub `master`.
4. Confirm the removed bootstrap route returns 404.
5. Re-run live CRUD, analytics, and runtime-error checks.

## Rollback
If the release fails before data initialization, roll back the Vercel deployment. If a schema migration has already run, treat the database migration separately: inspect Alembic state and use an explicit downgrade only when the migration is documented as reversible. Do not assume application rollback also rolls back PostgreSQL.
