# Internal Product & Technical Decision Record

> Internal engineering document for Aryan's Incubyte Salary Management assessment. This is intentionally more detailed than the one-page PRD and is useful for review, interview preparation, and explaining why the system looks the way it does.

## 1. Executive summary
The assignment asks for a salary-management product for roughly 10,000 employees, a React/Next.js UI, a Python backend, salary analytics, a repeatable high-volume seed process, tests, deployment, and evidence of structured AI-assisted engineering.

The final design is a **modular monolith**:

```text
HR Manager
   │
   ▼
Next.js / React / TypeScript
   │  HTTP / same-origin API
   ▼
FastAPI / Pydantic / SQLAlchemy
   │
   ▼
PostgreSQL
```

The product optimizes for correctness, maintainability, traceable product decisions, and fast delivery. At 10k employees there is no justified need for microservices, Kafka, Redis, Elasticsearch, a data warehouse, or a precomputed analytics platform.

## 2. Product problem we are solving
The primary user is a trusted HR Manager who needs two things in the same workspace:

1. Maintain employee compensation records without relying on spreadsheets.
2. Answer compensation questions quickly by country and job title.

The assignment is not a payroll engine. It is a compensation-management and reporting tool. That distinction drove several deliberate exclusions such as taxation, payslips, bonuses, benefits, approvals, payroll calculations, and FX-market integration.

## 3. Product decisions

| Decision | What we chose | Why | Trade-off |
|---|---|---|---|
| Salary meaning | Annual gross base salary | Recruiter explicitly confirmed this interpretation | Does not represent total compensation |
| Currency | Currency is associated with Country | Required analytics are country-scoped, so it avoids duplicated data | Assumes one canonical reporting currency per country |
| Country | Controlled reference values | Prevents `India`, `india`, `IND` style fragmentation | Requires reference-data management |
| Job title | Controlled reference values | Job title is an analytics dimension | Less flexible than arbitrary free text |
| Employee identity | Unique `employee_code` | Names are not unique, especially with generated seed data | Introduces one more required field |
| Deletion | Soft delete with `deleted_at` | HR/compensation records should not disappear physically | Needs explicit restore/history behavior later |
| Salary history | Current salary only | Recruiter confirmed history is optional; keeps MVP focused | Cannot answer historical compensation questions |
| Authentication | Not implemented | Recruiter explicitly allows one trusted HR Manager | Real production deployment would require SSO/RBAC |
| Seed reruns | Deterministic idempotent upsert | Safe repeated execution and predictable demos | Rerun intentionally overwrites edits to seeded fixtures |
| Analytics currency | No cross-country normalization | Avoids misleading FX assumptions and external-rate complexity | No global compensation comparison |

## 4. What is intentionally in scope

### Employee management
- Create employee.
- View employee details.
- Edit employee.
- Soft-delete employee from current views.
- Search by employee code/name.
- Filter by country and job title.
- Sort and paginate server-side.

### Salary analytics
For a selected country:
- employee count;
- minimum salary;
- maximum salary;
- average salary;
- total payroll;
- average salary by job title;
- role headcount breakdown;
- highest-paid employee;
- lowest-paid employee.

### Dataset workflow
- deterministic first/last-name source files;
- 10,000 generated employees;
- stable employee codes;
- bulk database upsert;
- safe reruns;
- seeded record restoration after soft deletion.

## 5. What is intentionally out of scope
This list matters because Incubyte explicitly asked us to document what we chose **not** to build.

- Authentication, SSO, RBAC, permissions matrix.
- Salary history / effective-dated compensation.
- Full audit event ledger.
- Restore-deleted-employee UI.
- Payroll calculation and tax logic.
- Bonuses, stock, benefits, allowances.
- Approval workflows and compensation cycles.
- Cross-country FX conversion.
- Live exchange-rate feeds.
- Redis caching.
- Kafka/event streaming.
- Search cluster.
- Data warehouse / BI pipeline.
- Microservices.

These are not forgotten features. They were deliberately rejected because they add operational and cognitive cost without helping the assessment's required outcomes.

## 6. Why a modular monolith
At 10,000 employees, the dominant workload is simple transactional CRUD plus indexed aggregate SQL queries. A distributed architecture would introduce:
- deployment coordination;
- network failures;
- distributed transactions;
- event consistency;
- more observability requirements;
- extra local development complexity.

A modular monolith gives clear boundaries while keeping transactions and deployment simple. If the product later develops independently scaling workloads, modules can be extracted behind the existing API/domain boundaries.

## 7. Why FastAPI + Next.js

### Backend: FastAPI
Chosen because:
- role is Python/React focused;
- Python backend competency remains visible in the assessment;
- Pydantic provides explicit input contracts;
- SQLAlchemy provides strong relational modelling and testability;
- OpenAPI documentation is available automatically.

### Frontend: Next.js + React + TypeScript
Chosen because:
- React is directly relevant to the role;
- typed API contracts reduce UI integration mistakes;
- Vercel supports Next.js and FastAPI together through Services;
- the UI can be kept focused on the HR workflow rather than framework complexity.

## 8. Data model

### Country
```text
code PK
name UNIQUE
currency_code
```
Country is a canonical reporting dimension.

### JobTitle
```text
id PK
name UNIQUE
```
Job title is also a canonical reporting dimension.

### Employee
```text
id PK
employee_code UNIQUE
full_name
job_title_id FK
country_code FK
salary NUMERIC(14,2)
department
employment_status
hired_at
created_at
updated_at
deleted_at nullable
```

### Why salary is DECIMAL/NUMERIC
Money must not use binary floating point because values such as `0.1` cannot be represented exactly. The database uses fixed precision and Pydantic normalizes values to two decimal places.

### Why no CompensationRecord table yet
A production compensation-history system would likely separate employee identity from effective-dated compensation records. We deliberately do not add that table because the recruiter confirmed current salary is sufficient for this exercise. The design is documented as an extension path, not silently omitted.

## 9. Soft-delete semantics
A DELETE request sets `deleted_at` instead of physically removing the row.

Current product views always include:
```text
deleted_at IS NULL
```

This applies to:
- employee list;
- employee detail;
- country analytics;
- job-title analytics.

Repeated DELETE is idempotent and returns success for an already soft-deleted physical row.

The deterministic seed can restore its canonical fixture record by clearing `deleted_at` during upsert.

## 10. Seed architecture
The seed process is designed as fixture/bootstrap infrastructure, not as a production HR import pipeline.

### Behavior
1. Read source names.
2. Generate deterministic employee identities.
3. Assign deterministic country, title, department, status, salary, and hire date values.
4. Bulk upsert using employee code.
5. On conflict, restore canonical seeded values and clear soft-deletion.

### Why idempotent
A regularly run seed script should be safe. Appending 10,000 rows every run would create duplicates and make demos/tests unpredictable.

### Important trade-off
If someone manually edits a seeded employee and reruns the seed, that record is reset to canonical fixture data. That is acceptable for deterministic demo/test fixtures and would be inappropriate for a real production HR import.

## 11. Query and index strategy
Existing indexes target the actual product queries:

- unique employee code lookup;
- full-name lookup/search support;
- country + job title aggregation;
- country + salary extrema/aggregations;
- department/status filtering;
- soft-delete filtering.

Observed on a local 10k SQLite verification dataset:

| Operation | Median local test latency |
|---|---:|
| employee list page | ~8 ms |
| exact employee-code search through list endpoint | ~17 ms |
| country filter | ~8 ms |
| country insight | ~8 ms |
| country + job-title insight | ~5 ms |

These are environment-specific engineering measurements, not production SLAs.

### Search caveat
The directory search intentionally supports substring matching using `%term%`. At 10k rows this is inexpensive. At much larger scale on PostgreSQL, ordinary B-tree indexes are not enough for arbitrary substring search; the next step would be a `pg_trgm` GIN/GiST index or a dedicated search system only if measured demand justified it.

## 12. API contract choices

### Validation
Pydantic validates:
- positive salary;
- employee-code/name/department lengths;
- valid country shape;
- positive job-title ID;
- allowed employment statuses;
- null semantics for PATCH.

### Business validation
The service layer verifies referenced Country and JobTitle records exist.

### Conflict handling
Duplicate employee code returns HTTP 409 rather than leaking a raw database integrity error.

### Pagination
Offset pagination was chosen because 10k rows and an HR table are a good fit for explicit page navigation. Cursor pagination becomes attractive with far larger tables or heavy concurrent writes.

## 13. Frontend product design
The UI is a single HR workspace, not a collection of admin pages.

### Top section: compensation overview
HR selects an analytical country independently from directory filters. This separation is important: changing analytical context must not unexpectedly filter the employee directory.

### Directory
- search;
- country filter;
- title filter;
- name sort;
- pagination;
- employee detail modal;
- edit modal;
- soft-delete action.

### UX hardening added during review
- search is debounced to avoid a network request on every keystroke;
- search has an accessible label;
- dialogs close on Escape;
- backend validation-array errors are surfaced more clearly;
- salary mutations invalidate analytics so insight cards do not become stale.

## 14. Development process / AI workflow
The system was not generated in one pass. AI was deliberately used as multiple engineering roles.

### PM role
- decomposed the brief;
- identified ambiguities;
- created user stories and acceptance criteria;
- drafted recruiter clarification questions.

### Research role
- reviewed real compensation-platform patterns;
- separated useful production practices from enterprise overengineering.

### Architect role
- chose modular monolith;
- normalized analytics dimensions;
- designed persistence/indexing;
- documented ADRs and trade-offs.

### Backend developer role
- wrote requirement-derived tests first;
- implemented CRUD, analytics, seed, migrations;
- kept changes incremental.

### Frontend developer role
- built the HR workflow;
- separated analytics context from directory filtering;
- integrated mutation-driven refresh.

### Code-review role
Found and fixed issues including:
- coupled insight/filter state;
- stale analytics after salary edit;
- leaking test DB engines;
- unrealistic cross-currency seed values;
- repository hygiene problems;
- deployment URL/config caveats;
- stale ORM identity state after seed upsert.

### Independent QA role
Re-read the original brief and recruiter clarification rather than deriving tests from implementation behavior. This produced additional edge-case tests, including PATCH null validation and soft-delete semantics.

## 15. Security decisions

### Implemented
- no raw SQL string concatenation for user input;
- query sorting is whitelist-controlled;
- strong schema validation;
- constrained CORS origins;
- React escaping protects normal rendered values from DOM injection;
- no credentials stored in application source;
- API page size is capped;
- current Next.js/React versions are moved to security-patched releases before submission.

### Explicit assessment exception
Authentication/RBAC is not implemented because the recruiter explicitly said a trusted single-HR-user model is sufficient.

### Real production blockers
Before real salary data, we would require:
- SSO/OIDC;
- role/attribute-based access control;
- audit logging;
- secrets manager;
- database encryption/backup policy;
- observability and alerting;
- request abuse/rate controls;
- security headers/CSP;
- privacy/retention policy;
- dependency scanning in CI.

## 16. Dependency-security correction
The initial frontend dependency pins were old relative to the October 2026 security baseline. The final review upgraded:
- Next.js to 16.3.8;
- React to 19.3.0;
- React DOM to 19.3.0.

Reason: Next.js published multiple 2026 security releases, including critical/high issues, and React Server Components also received security fixes. Production-minded review means current dependency security is part of correctness, not just functionality.

## 17. Deployment architecture
Vercel Services is used to deploy the Next.js and FastAPI applications as one product under one domain.

```text
/                 -> frontend service
/api/*            -> backend service
/health           -> backend service
```

The backend exposes `main:app` from the backend service root and the implementation stays in `app/main.py`.

Production persistence must use PostgreSQL through `DATABASE_URL`. Serverless-local SQLite is deliberately not accepted as production storage.

## 18. Verification performed
- backend automated tests: 21 passing;
- backend coverage: 89.81% against an 85% floor;
- fresh Alembic migration from zero;
- 10k deterministic seed and rerun;
- real FastAPI HTTP CRUD/analytics smoke verification;
- soft-delete storage/current-view verification;
- seed restoration verification;
- query-plan inspection;
- source-level security scan;
- TS/TSX syntax transpilation;
- Vercel service entrypoint import verification.

## 19. Verification not honestly claimed
A full local Next.js browser run could not be completed in the current execution environment because frontend packages could not be fetched/installed. Therefore the project does **not** claim a browser-tested production frontend from this environment.

This remains a release gate in CI/Vercel:
- `npm install`;
- `npm run typecheck`;
- `npm run build`;
- deployed browser smoke test.

The distinction is intentional: engineering evidence should state what was actually verified, not what was assumed.

## 20. Important future improvements
If this were moving from assessment to real HR production, the priorities would be:

1. SSO + RBAC.
2. Audit event ledger.
3. Effective-dated compensation records.
4. Restore/deactivation lifecycle instead of only hidden soft delete.
5. Optimistic concurrency/version field to prevent lost HR edits.
6. PostgreSQL partial indexes for current (`deleted_at IS NULL`) employees if deletions grow significantly.
7. PostgreSQL trigram search if employee count/search traffic grows.
8. Background export/report jobs if reports become expensive.
9. Observability: structured logs, tracing, metrics, alerts.
10. Data retention, backup, encryption and privacy governance.

## 21. Interview-ready summary
A concise explanation of the system:

> I treated the assignment as a small production product rather than a CRUD demo. I clarified domain ambiguity first, then deliberately kept the architecture simple for 10,000 employees: a Next.js UI, FastAPI API and PostgreSQL modular monolith. Country and job title are canonical reporting dimensions, money uses fixed precision, repeated seed runs are deterministic and idempotent, and employee deletion is soft deletion because compensation records should not disappear physically. I explicitly avoided microservices, caching and event infrastructure because the scale does not justify them. I used AI as separate PM, architecture, development, code-review and QA roles, preserved the iteration trail in Git, and independently re-tested the final system against the original requirements.
