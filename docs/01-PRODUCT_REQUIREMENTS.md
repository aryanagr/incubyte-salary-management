# One-Page Product Requirements — Salary Management

> Initial version was written before implementation. Recruiter clarification received on 2026-10-05 confirmed/refined the decisions below; the clarification is treated as a requirements change, not a history rewrite.

## User and outcome
**Primary user:** a trusted HR Manager managing roughly 10,000 full-time employees.

The product must let HR maintain employee records and answer salary questions quickly without exporting data to spreadsheets.

## In-scope product behavior
### Employee management
- Create, view, update and delete employees through the UI.
- Required business data: unique employee code, full name, controlled job title, controlled country, annual gross base salary, department and employment status; hire date is optional.
- Employee list is server-paginated, searchable by name/code, filterable and sortable.
- **Delete is a soft delete:** the record is retained with `deleted_at`, but disappears from the normal employee directory and all current salary analytics.

### Salary representation
- Salary means **annual gross base salary**.
- Salary has an associated currency through the employee's controlled Country record (`currency_code`).
- Salaries are retained in local currency; required analytics are scoped to one country, so the product does **not** perform FX conversion or cross-country salary comparison.
- Money is stored as fixed-precision decimal, never floating point.

### Salary insights
For a selected country:
- employee count, minimum, maximum and average salary;
- total payroll;
- average salary by job title;
- job-title breakdown/headcount;
- highest- and lowest-paid current employee as additional useful context.

Deleted employees are excluded from every current insight.

### Seed workflow
- Repository provides suitable `first_names.txt` and `last_names.txt` files.
- Script generates/upserts **10,000 deterministic employees** using a stable employee code.
- Re-running the seed is intentionally **idempotent**: it restores the canonical seeded dataset instead of appending duplicates, including reactivating a previously soft-deleted seeded record.
- Writes are batched and benchmarkable because seed performance is an explicit assessment concern.

## Demo enhancement added after core scope
The recruiter explicitly confirmed that production authentication was not required. After the core assessment was complete, a lightweight **demo login + two-role permission model** was added to make the deployed product easier to review without turning the assignment into an IAM project:
- **HR Manager:** employee create/update/delete, directory access and salary analytics.
- **HR Staff:** read-only directory access and salary analytics; mutation endpoints return `403`.
- Authentication uses an HttpOnly, SameSite session cookie signed with a server-side secret in deployed environments.
- Demo credentials are intentionally visible on the login page; this layer demonstrates product permissions, not production identity management.

Production SSO, user provisioning, password storage/recovery, MFA and enterprise IAM remain deliberately out of scope.

## Key product/engineering decisions
- Country and Job Title are controlled reference tables to prevent analytics fragmentation from spelling/case variants.
- Unique employee code is the stable business identifier.
- Current salary lives on Employee for this MVP; no effective-dated salary-history model is added.
- PostgreSQL is the production database; indexed SQL aggregation is sufficient at 10k rows.
- Modular monolith: Next.js/React UI + FastAPI API; no microservices or cache without measured need.

## Deliberately out of scope
- **Production** authentication/SSO/IAM, user provisioning, MFA and enterprise RBAC. The deployed demo login is intentionally lightweight and separate from the assessment's core scope.
- Salary history/effective-dated compensation — optional, not needed for the assessment.
- FX-rate ingestion or normalized cross-country reporting.
- Full audit/event log, restore UI, approvals/workflows, payroll calculation, bonuses/equity/benefits.
- Redis, Kafka, warehouse, search cluster or precomputed analytics at this dataset size.

## Acceptance criteria
1. HR can create/view/edit/delete an employee from the UI with validation and stable error handling.
2. Deleted employees are retained in storage but absent from normal list/detail APIs and salary analytics.
3. Country and country+job-title salary metrics are mathematically correct and currency-aware.
4. Employee listing remains paginated and responsive with 10,000 records.
5. Re-running the 10k seed does not increase row count and restores canonical seeded records.
6. Tests cover CRUD, validation, analytics, deletion semantics and seeding; CI enforces the test/coverage gate.
7. Repository documents architecture, trade-offs, deliberate exclusions, AI workflow and incremental Git history.
8. Demo HR Staff cannot mutate employee records through either the UI or API; HR Manager retains full CRUD access.
