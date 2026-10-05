# Compensation Console — Incubyte Engineering Assessment

A production-minded salary-management workspace for an HR Manager managing roughly 10,000 employees. The solution emphasizes product reasoning, TDD, explicit trade-offs, deterministic high-volume seeding and an auditable AI-assisted engineering process.

## What the product does
- Add, view and update employees; DELETE uses documented soft deletion so HR records are retained but removed from current views.
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
  │ same-origin /api/*
  ▼
FastAPI / Pydantic / SQLAlchemy
  │
  ▼
PostgreSQL
```

The application is a modular monolith rather than a distributed system: at 10k employees, indexed SQL aggregations and pagination are simpler, safer and fast enough.

## Repository map
- `frontend/` — Next.js HR workspace.
- `backend/` — FastAPI API, SQLAlchemy model, Alembic migrations and seed CLI.
- `backend/tests/` — requirement-derived API/unit tests.
- `docs/00-ASSESSMENT_ANALYSIS.md` — brief decomposition, assumptions, user stories and edge cases.
- `docs/06-ROLE_BASED_DESIGN_REVIEW.md` — PM/architecture/backend/frontend/QA/security/performance debate.
- `docs/08-CODE_REVIEW.md` — independent review findings and fixes.
- `docs/09-PRODUCTION_RESEARCH.md` — Workday/Pave/Deel domain research and what was/wasn't adopted.
- `docs/12-INTERNAL_PRODUCT_TECH_DECISIONS.md` — detailed internal product/technical rationale and interview-prep decision record.
- `docs/13-FINAL_QA_SECURITY_PERFORMANCE_REVIEW.md` — final independent QA, security and performance evidence.
- `docs/14-FINAL_REQUIREMENTS_SIGNOFF.md` — final PM requirement-by-requirement completion and release-gate matrix.
- `docs/adr/` — architecture decision records.

## Quality status
- Backend: **21 tests passing** after recruiter-clarification regression coverage.
- Backend coverage: **89.81%**, enforced at >=85%.
- Latest fresh-db 10k seed regression: **2.942s first run / 2.774s repeat** on the assessment environment; rerun remains exactly 10,000 physical/current fixture employees.
- Frontend TS/TSX syntax passes local transpilation; full Next.js typecheck/build and browser smoke remain deployment gates because package installation is unavailable in this sandbox.
- Frontend dependency pins were updated to the current security baseline: Next.js 16.3.8 and React/React DOM 19.3.0.

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
`vercel.json` uses Vercel Services to deploy Next.js + FastAPI as one product. Production requires a persistent PostgreSQL `DATABASE_URL`; do not rely on serverless-local SQLite for compensation data.

## AI-assisted development
AI was used as multiple explicit engineering roles rather than as a code generator that was blindly accepted:
1. PM requirement analysis and ambiguity discovery.
2. Staff architecture review.
3. Backend implementation via TDD.
4. Frontend implementation.
5. Independent code review.
6. Independent QA pass derived again from the source brief.
7. Release/security/performance review.

The repo intentionally preserves failing-test and fix commits so reviewers can see how the solution evolved.

## Recruiter clarifications incorporated
Incubyte replied on 2026-10-05. The clarified scope is now reflected in the one-page PRD, ADRs, tests and implementation: annual gross base salary with currency, candidate-chosen controlled reference values and seed semantics, unique employee code, soft deletion by product choice, current salary only, and no authentication requirement for the trusted-HR assessment environment.

See `docs/01-PRODUCT_REQUIREMENTS.md` for the final one-page scope and deliberate exclusions.
