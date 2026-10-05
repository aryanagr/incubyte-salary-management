# Product Requirements Document

## Product framing
A salary-management workspace for an HR Manager in an organization of roughly 10,000 employees. The product should make employee records easy to maintain and make compensation patterns easy to inspect without exporting data to spreadsheets.

## Primary user
**HR Manager** — needs accurate employee records, quick salary comparisons, and enough context to spot outliers or inconsistent compensation.

## Goals
1. Manage employees through a usable UI: create, view, update and delete.
2. Answer country-level compensation questions quickly.
3. Answer job-title compensation questions within a country.
4. Remain responsive with 10,000 seeded employees and routine reseeding.
5. Be understandable to another engineer through tests, architecture notes, trade-offs and incremental commits.

## Core employee data
- Full name (required)
- Job title (required)
- Country (required)
- Annual salary (required, positive)
- Department (required)
- Employment status (active, leave, terminated)
- Hire date
- Stable external employee code
- Created/updated timestamps

## Functional requirements
### Employee management
- Paginated employee table.
- Search by name or employee code.
- Filter by country, job title, department and status.
- Sort by name, salary, hire date or updated date.
- Add employee with field validation.
- Edit employee.
- View employee detail.
- Delete employee with confirmation.

### Salary insights
For a selected country:
- Employee count
- Minimum salary
- Maximum salary
- Average salary
- Total payroll
- Average salary by selected job title
- Role breakdown with headcount and average salary
- Highest-paid and lowest-paid employee as useful HR context

## Non-functional requirements
- API pagination is mandatory; never return all 10k employees to the browser by default.
- Numeric salary values are stored as fixed precision decimal, never floating point.
- Indexed country/job-title fields support analytics queries.
- Deterministic seed data allows repeatable tests and demos.
- Seed operation is idempotent and uses batched writes/upserts.
- Tests are isolated, fast and deterministic.
- Errors return stable machine-readable JSON.
- Health endpoint supports deployment verification.
- CORS is environment-configured.

## Product assumptions
1. Salary is annual gross salary in the employee country's local currency. Because required analytics compare salaries *within the same country*, no FX conversion is performed.
2. Authentication/authorization is deliberately out of MVP scope because the assessment does not define identity or roles. In a real HR system, SSO + RBAC is a release blocker.
3. Deleting an employee is a hard delete for assessment simplicity. Production HR systems would usually require audit history or soft deletion.
4. 10,000 employees is small enough for indexed relational aggregation; no warehouse is needed.

## Explicit clarification candidates for Incubyte
These are not blockers, but would be good questions if there is time to contact the recruiter:
- Should salary values be compared only within a country's local currency, or normalized to one currency?
- Is authentication/RBAC expected for the assessment deployment?
- Is hard delete acceptable, or should deleted employees be retained for auditability?
