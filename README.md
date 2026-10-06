# Compensation Console — Incubyte Engineering Assessment

A production-minded salary-management workspace for an HR team managing roughly 10,000 employees.

The submission is intentionally optimized for the qualities called out in the assessment: **clear reasoning, proportional architecture, maintainable code, meaningful tests, product judgment, incremental delivery, and transparent AI-assisted development**.

## Reviewer quick path

If you have only a few minutes, review these in order:

1. `docs/00-ASSESSMENT_ANALYSIS.md` — decomposition of the brief, assumptions, edge cases and questions sent before implementation.
2. `docs/01-PRODUCT_REQUIREMENTS.md` — final one-page product scope after recruiter clarification.
3. `docs/02-ARCHITECTURE.md` + `docs/05-TRADEOFFS.md` — architecture and deliberate simplicity decisions.
4. `docs/07-REQUIREMENTS_TRACEABILITY.md` — requirement-to-code-to-test mapping.
5. `docs/14-FINAL_REQUIREMENTS_SIGNOFF.md` — current completion/evidence matrix.

The Git history intentionally preserves tests, implementation, review findings and subsequent fixes rather than presenting one generated final commit.

## Core assessment scope — complete

The following capabilities are the submission's **core assessment** and are the basis on which the project should be evaluated:

- employee add, view, update and delete flows;
- annual gross base salary with associated local currency;
- server-side search, filtering, sorting and pagination for ~10,000 employees;
- country salary insights: headcount, min/max/average salary and total payroll;
- average salary for a job title within a country;
- relational persistence using PostgreSQL/Neon with Alembic migrations;
- deterministic, idempotent 10,000-employee seed using repository-owned first/last-name datasets;
- bulk seeding and explicit performance verification;
- FastAPI backend + Next.js/React/TypeScript frontend;
- requirement-derived automated tests and enforced CI quality gates;
- documented architecture, trade-offs, AI workflow, code review and QA evidence.

### Deliberate core-scope exclusions

The project intentionally does **not** add speculative infrastructure just to appear more complex. For the stated scale, the following were rejected or deferred unless a real requirement emerges:

- microservices;
- Kafka/event streaming;
- Redis as a required cache/queue layer;
- Elasticsearch;
- FX conversion without a specified market-data source/as-of policy;
- compensation history beyond current salary;
- payroll/tax calculation;
- enterprise SSO/MFA/user provisioning.

At ~10,000 employees, a modular monolith with indexed PostgreSQL queries is simpler to operate and sufficient for the product requirements.

## Optional post-core enhancements

These features were added **after the clarified core assessment was already satisfied**. They demonstrate extension points and additional engineering judgment; they are **not presented as requirements Incubyte asked for**.

### Demo authentication / RBAC

The recruiter explicitly confirmed production authentication was not required. A lightweight demo layer was added later so reviewers can exercise two permission levels without introducing an external identity provider:

| Role | Email | Password | Demo permission |
| --- | --- | --- | --- |
| HR Manager | `manager@salary.demo` | `Manager@123` | Employee CRUD + directory + analytics + reports |
| HR Staff | `hr@salary.demo` | `Hr@123` | Read-only directory + analytics + reports |

The API enforces the write boundary; this is still intentionally **demo RBAC, not production IAM**. See `docs/15-DEMO_AUTH_RBAC.md`.

### Asynchronous filtered export

A later enhancement adds a durable PostgreSQL-backed export job that snapshots the current employee-directory filters, generates an `.xlsx`, and supports asynchronous email delivery. It deliberately avoids Redis/Celery at this workload size and documents retry/concurrency semantics.

Live SMTP delivery requires provider credentials and is treated as enhancement UAT, **not as a blocker for the original salary-management assessment**. See `docs/16-ASYNC_FILTERED_EXPORT.md`.

## Live demo

Production URL: https://incubyte-salary-management-chi.vercel.app

Production persistence uses the connected Neon PostgreSQL database. The database was initialized through a one-time Git-triggered migration/seed release and ordinary deployments are side-effect free.

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
PostgreSQL / Neon
```

This remains a **modular monolith**. At the required scale, that avoids distributed-system complexity while keeping boundaries clear enough to extract later if measurements justify it.

## Current quality evidence

GitHub Actions currently enforces:

- **42 backend functional/API tests passing**;
- **88.24% backend coverage**, above an enforced **85%** floor;
- Ruff correctness/static checks;
- Python dependency audit with no known vulnerabilities in the audited environment;
- a dedicated **10,000-employee performance regression gate**;
- Python compilation;
- frontend production dependency audit;
- TypeScript typecheck;
- optimized Next.js production build.

Detailed evidence is recorded in `docs/13-FINAL_QA_SECURITY_PERFORMANCE_REVIEW.md` and `docs/quality-loop/`.

## Repository map

### Core assessment evidence
- `frontend/` — Next.js salary-management UI.
- `backend/` — FastAPI API, SQLAlchemy models, Alembic migrations and seed CLI.
- `backend/tests/` — requirement-derived tests and performance regression coverage.
- `docs/00-ASSESSMENT_ANALYSIS.md` — brief decomposition, assumptions and edge cases.
- `docs/01-PRODUCT_REQUIREMENTS.md` — final clarified product scope.
- `docs/02-ARCHITECTURE.md` — architecture and system boundaries.
- `docs/03-TEST_STRATEGY.md` — test approach.
- `docs/04-AI_WORKLOG.md` — intentional AI-assisted development record.
- `docs/05-TRADEOFFS.md` — rejected alternatives and why.
- `docs/07-REQUIREMENTS_TRACEABILITY.md` — requirement mapping.
- `docs/08-CODE_REVIEW.md` — independent review findings/fixes.
- `docs/09-PRODUCTION_RESEARCH.md` — domain research and selective adoption.
- `docs/13-FINAL_QA_SECURITY_PERFORMANCE_REVIEW.md` — current QA/security/performance evidence.
- `docs/14-FINAL_REQUIREMENTS_SIGNOFF.md` — current PM sign-off.
- `docs/adr/` — architecture decision records.

### Optional enhancement evidence
- `docs/15-DEMO_AUTH_RBAC.md` — demo login/RBAC rationale.
- `docs/16-ASYNC_FILTERED_EXPORT.md` — asynchronous filtered export design.
- `docs/quality-loop/` — later professional-readiness review cycles.

## Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]" pytest-cov
alembic upgrade head
python -m app.seed --count 10000
uvicorn app.main:app --reload
```

Set `DATABASE_URL` to PostgreSQL for production-like persistence. The test suite uses an isolated SQLite test database where appropriate.

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

Run the one-time migration/seed against the database before first use.

## Deployment

`vercel.json` deploys Next.js + FastAPI as one Git-driven product. Production persistence uses Neon PostgreSQL via `DATABASE_URL`; serverless-local SQLite is not used for compensation data.

## AI-assisted development

AI was used as an explicit engineering workflow rather than as an unchecked code generator:

1. Product Manager — requirements, assumptions and clarification questions.
2. Staff Architect — boundaries, schema, indexes and scaling posture.
3. Backend Developer — API/persistence implementation with tests.
4. Frontend Developer — HR workflows and analytics UI.
5. QA Engineer — requirement-derived tests independent of implementation assumptions.
6. Code Reviewer — correctness, maintainability, security and failure-mode review.
7. Release/Performance Reviewer — deployment, dependency and 10k-scale verification.

Unknowns were documented as assumptions, recruiter clarification was handled as change control, and later enhancements remain explicitly separated from the original assessment scope.
