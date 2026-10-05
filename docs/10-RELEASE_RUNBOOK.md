# Release Runbook

## Quality gates
1. `cd backend && PYTHONPATH=. pytest --cov=app --cov-fail-under=85`
2. `cd backend && PYTHONPATH=. python scripts/benchmark_seed.py`
3. `cd frontend && npm install && npm run typecheck && npm run build`
4. Apply migrations against production PostgreSQL: `alembic upgrade head`
5. Seed deterministic demo data: `python -m app.seed --count 10000`
6. Deploy Vercel Services project from repository root.
7. Smoke test `/health`, employee list/create/edit/delete, and country/job-title insights.
8. Check runtime logs for 5xx errors.

## Vercel shape
The repository uses Vercel Services so the Next.js frontend and FastAPI backend deploy atomically under one domain. `/api/*` routes to FastAPI; all other paths route to Next.js.

The backend requires a persistent `DATABASE_URL` pointing to PostgreSQL. SQLite is only for local development/tests and must not be treated as durable Vercel production storage.
