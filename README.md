# Compensation Console — Incubyte Engineering Assessment

A production-minded salary-management workspace for an HR team managing roughly 10,000 employees. The solution emphasizes product reasoning, TDD, explicit trade-offs, deterministic high-volume seeding and an auditable AI-assisted engineering process.

## Live demo
Production: https://incubyte-salary-management-chi.vercel.app

The deployed demo includes two intentionally public test personas:

| Role | Email | Password | Permission |
| --- | --- | --- | --- |
| HR Manager | `manager@salary.demo` | `Manager@123` | Full employee CRUD + directory + salary analytics |
| HR Staff | `hr@salary.demo` | `Hr@123` | Read-only directory + salary analytics |

The demo credentials are deliberately visible so reviewers can switch roles. The backend still enforces the permission boundary: HR Staff mutation requests return `403` even if the API is called directly.

> The recruiter confirmed production authentication was not required for the assessment. This is therefore a lightweight review/demo RBAC layer, not a claim of production IAM. See `docs/15-DEMO_AUTH_RBAC.md` for the product and technical rationale.

## What the product does
- Login/logout with HR Manager and read-only HR Staff demo roles.
- Add, view and update employees as HR Manager; DELETE uses documented soft deletion so HR records are retained but removed from current views.
- Server-side search, filtering, sorting and pagination for a 10k employee directory.
- Country salary insights: headcount, min/max/average salary and total payroll.
- Job-title benchmarks within a country.
- Highest/lowest salary context for HR review.
- Deterministic, idempotent 10,000-row seed process based on `first_names.txt` + `last_names.txt`.

## Architecture

```text
Browser
  │
  ▼
Next.js / React / TypeScript
  │ same-origin /api/* + HttpOnly signed session
  ▼
FastAPI / Pydantic / SQLAlchemy
  │
  ▼
PostgreSQL / Neon
```

The application is a modular monolith rather than a distributed system: at 10k employees, indexed SQL aggregations and pagination are simpler, safer and fast enough.

## Repository map
- `frontend/` — Next.js HR workspace and demo login experience.
- `backend/` — FastAPI API, demo authorization, SQLAlchemy model, Alembic migrations and seed CLI.
- `backend/tests/` — requirement-derived API/unit/RBAC tests.
- `docs/00-ASSESSMENT_ANALYSIS.md` — brief decomposition, assumptions, user stories and edge cases.
- `docs/06-ROLE_BASED_DESIGN_REVIEW.md` — PM/architecture/backend/frontend/QA/security/performance debate.
- `docs/08-CODE_REVIEW.md` — independent review findings and fixes.
- `docs/09-PRODUCTION_RESEARCH.md` — Workday/Pave/Deel domain research and what was/wasn't adopted.
- `docs/12-INTERNAL_PRODUCT_TECH_DECISIONS.md` — detailed internal product/technical rationale and interview-prep decision record.
- `docs/13-FINAL_QA_SECURITY_PERFORMANCE_REVIEW.md` — final independent QA, security and performance evidence.
- `docs/14-FINAL_REQUIREMENTS_SIGNOFF.md` — final PM requirement-by-requirement completion and release-gate matrix.
- `docs/15-DEMO_AUTH_RBAC.md` — demo login/permission product and technical decision record.
- `docs/adr/` — architecture decision records.

## Quality status
- GitHub Actions enforces backend tests, the >=85% coverage gate, Python compile checks, frontend dependency installation, TypeScript typecheck and production Next.js build.
- RBAC regression tests cover manager login, invalid login, protected APIs, HR Staff read-only access, manager write access and logout.
- The deterministic 10k seed remains idempotent and benchmarkable.
- Frontend dependency pins use the reviewed security baseline: Next.js 16.3.8 and React/React DOM 19.3.0.

## Production data
The connected Neon PostgreSQL database was initialized through a one-time Git-triggered Vercel backend build running:

```text
alembic upgrade head
python -m app.seed --count 10000
```

That production deployment reached `READY`, which means migrations and the deterministic 10,000-row seed completed successfully. The temporary build seed and HTTP bootstrap surface were then removed from `master`; ordinary deployments are side-effect free again.

## Local backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test,postgres]" pytest-cov
alembic upgrade head
python -m app.seed --count 10000
uvicorn app.main:app --reload
```

## Local frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Docker / PostgreSQL
```bash
docker compose up --build
```
Then run the one-time migration/seed against the backend container/database before first use.

## Deployment
`vercel.json` uses Vercel Services to deploy Next.js + FastAPI as one Git-driven product. Production uses the connected Neon PostgreSQL `DATABASE_URL`; serverless-local SQLite is not used for compensation persistence.

## AI-assisted development
AI was used as multiple explicit engineering roles rather than as a code generator that was blindly accepted:
1. PM requirement analysis and ambiguity discovery.
2. Staff architecture review.
3. Backend implementation via TDD.
4. Frontend implementation.
5. Independent code review.
6. Independent QA pass derived again from the source brief.
7. Release/security/performance review.
8. Post-scope demo RBAC implemented with tests and backend enforcement.

The repo intentionally preserves failing-test and fix commits so reviewers can see how the solution evolved.

## Recruiter clarifications incorporated
Incubyte replied on 2026-10-05. The clarified core scope is reflected in the one-page PRD, ADRs, tests and implementation: annual gross base salary with currency, candidate-chosen controlled reference values and seed semantics, unique employee code, soft deletion by product choice, current salary only, and no production authentication requirement for the trusted-HR assessment environment.

The demo login/RBAC was added afterward as a clearly documented enhancement, without changing the stated production-IAM scope.

See `docs/01-PRODUCT_REQUIREMENTS.md` for the final one-page scope and deliberate exclusions.
