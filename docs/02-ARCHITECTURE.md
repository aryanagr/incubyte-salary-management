# Architecture

## System overview

```mermaid
flowchart LR
  U[HR Manager] --> W[Next.js Web UI]
  W -->|HTTPS JSON| A[FastAPI API]
  A --> S[Service layer]
  S --> R[Repository / SQLAlchemy]
  R --> P[(PostgreSQL)]
  A --> H[/health]
  SEED[Seed CLI] --> R
```

## Why this split
The role emphasizes Python + React, so the solution deliberately uses a Python backend and React-based UI rather than hiding backend logic in Next.js route handlers. It keeps domain validation and analytics independently testable and makes the architecture representative of a production service boundary.

## Backend
- FastAPI for typed HTTP contracts and OpenAPI.
- SQLAlchemy 2.x for database access.
- Pydantic v2 for request/response validation.
- PostgreSQL in deployed environments; SQLite can be used for local tests.
- Thin routers, domain logic in services, SQL in repositories.

## Frontend
- Next.js App Router + TypeScript.
- Server-rendered shell with client components only where interactivity is required.
- Typed API client with explicit error handling.
- Accessible semantic controls and responsive layout.

## Data model

### employees
| Column | Type | Notes |
|---|---|---|
| id | bigint PK | Internal surrogate key |
| employee_code | varchar(24) unique | Stable public identifier |
| full_name | varchar(160) | Required |
| job_title | varchar(120) | Indexed with country |
| country | varchar(80) | Indexed |
| department | varchar(100) | Filterable |
| salary | numeric(14,2) | Annual local-currency salary |
| employment_status | varchar(20) | active/leave/terminated |
| hired_at | date | Optional |
| created_at | timestamp tz | Audit metadata |
| updated_at | timestamp tz | Audit metadata |

Indexes:
- `(country, job_title)` for required insight query.
- `(country, salary)` for country compensation scans and extrema.
- `(department)` and `(employment_status)` for common HR filtering.

## API surface
- `GET /api/v1/employees`
- `POST /api/v1/employees`
- `GET /api/v1/employees/{id}`
- `PATCH /api/v1/employees/{id}`
- `DELETE /api/v1/employees/{id}`
- `GET /api/v1/insights/countries/{country}`
- `GET /api/v1/insights/countries/{country}/job-titles/{job_title}`
- `GET /health`

## Scaling posture
10k rows does not justify caching or distributed systems. Correct indexing, pagination and SQL aggregation are enough. Premature Redis/cache layers would create invalidation complexity with no meaningful benefit at this scale.

## Security posture
- Strict input validation.
- ORM parameterization prevents SQL injection.
- Configurable CORS allowlist.
- No secrets committed.
- Production database URL only via environment variable.
- Security headers should be provided by hosting layer / frontend config.
- Authentication/RBAC called out as a deliberate scope gap rather than silently ignored.
