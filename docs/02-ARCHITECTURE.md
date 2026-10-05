# Architecture

## System overview

```mermaid
flowchart LR
  U[Trusted HR Manager] --> W[Next.js Web UI]
  W -->|HTTPS JSON| A[FastAPI API]
  A --> S[Service layer]
  S --> O[SQLAlchemy ORM]
  O --> P[(PostgreSQL)]
  A --> H[/health]
  SEED[Deterministic Seed CLI] --> O
```

## Why this split
The target role emphasizes Python + React, so the solution deliberately uses a Python backend and React-based UI instead of hiding backend logic inside Next.js route handlers. The HTTP boundary keeps validation, lifecycle rules and analytics independently testable while remaining a small modular monolith.

## Backend
- FastAPI for typed HTTP contracts and OpenAPI.
- SQLAlchemy 2.x for persistence and SQL aggregation.
- Pydantic v2 for request/response validation.
- Alembic for explicit schema evolution.
- PostgreSQL in deployed environments; SQLite only for isolated tests/local verification.
- Service functions own domain behavior such as soft deletion and analytics scoping.

## Frontend
- Next.js App Router + TypeScript.
- Server-rendered shell with a focused interactive HR workspace.
- Typed API client with explicit error handling.
- Semantic controls, loading/error/empty states and server pagination.

## Data model

### countries
| Column | Type | Notes |
|---|---|---|
| code | char(2) PK | ISO-style controlled key |
| name | varchar(80) unique | Canonical display value |
| currency_code | char(3) | Currency associated with local salary reporting |

### job_titles
| Column | Type | Notes |
|---|---|---|
| id | integer PK | Surrogate key |
| name | varchar(120) unique | Controlled analytics dimension |

### employees
| Column | Type | Notes |
|---|---|---|
| id | integer PK | Internal surrogate key |
| employee_code | varchar(24) unique | Stable business identifier |
| full_name | varchar(160) | Required |
| job_title_id | FK | Canonical job title |
| country_code | FK | Canonical country/currency context |
| department | varchar(100) | Filterable |
| salary | numeric(14,2) | Annual gross base salary in country's local currency |
| employment_status | varchar(20) | active/leave/terminated |
| hired_at | date | Optional |
| created_at | timestamp tz | Record metadata |
| updated_at | timestamp tz | Record metadata |
| deleted_at | timestamp tz nullable | Soft-delete marker |

Indexes include `(country_code, job_title_id)`, `(country_code, salary)`, `department`, `employment_status`, `employee_code`, `full_name` and `deleted_at`.

## Lifecycle semantics
- Normal list/detail/update queries use the **current employee view**: `deleted_at IS NULL`.
- DELETE timestamps the row rather than physically removing it.
- Country and country+job-title analytics use the same current-view predicate.
- Repeat DELETE is safe and returns the same success response.
- Seed upsert clears `deleted_at` for seeded employee codes so the deterministic fixture can be restored.

## Salary/currency semantics
Salary means annual gross base salary. Currency is associated via the employee's Country reference row. This is deliberately sufficient because every required salary aggregate is scoped to one country. Cross-country FX conversion is not performed.

## API surface
- `GET /api/v1/reference-data`
- `GET /api/v1/employees`
- `POST /api/v1/employees`
- `GET /api/v1/employees/{id}`
- `PATCH /api/v1/employees/{id}`
- `DELETE /api/v1/employees/{id}`
- `GET /api/v1/insights/countries/{country}`
- `GET /api/v1/insights/countries/{country}/job-titles/{job_title}`
- `GET /health`

## Scaling posture
10,000 rows does not justify caching, queues or distributed data infrastructure. Correct indexes, pagination and database-side aggregation are enough. If cardinality or read volume materially grows, query plans/latency would be measured before considering materialized views or caching.

## Security posture
Recruiter guidance explicitly allows a single trusted HR Manager and does not require authentication for the exercise. The assessment therefore focuses on validation, constrained CORS, parameterized ORM queries and secret management. For real compensation data, SSO, least-privilege RBAC and audit logging would be production release requirements.
