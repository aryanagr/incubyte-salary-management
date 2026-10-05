# Assessment Analysis

## Source brief distilled
The assessment asks for a minimal but usable salary-management product for an HR Manager at an organization of roughly 10,000 employees. The required product capabilities are:

1. Manage employees through a UI: add, view, update, delete.
2. Store at minimum: full name, job title, country, salary, plus meaningful extra data chosen by the candidate.
3. Show salary insights through the UI:
   - minimum, maximum and average salary for employees in a country;
   - average salary for a given job title in a country;
   - additional useful HR metrics chosen by the candidate.
4. Deliver an end-to-end product: backend, relational database and React/Next UI.
5. Provide a seed script for 10,000 employees, generating names from `first_names.txt` + `last_names.txt`.
6. Treat seed performance as a first-class concern because engineers will run it regularly.
7. Demonstrate product thinking, architecture/design judgment, production-quality code/tests, intentional AI use and incremental commits.

## Product-manager questions asked to hiring team
The following clarifications were sent before implementation because each can alter product semantics or schema:
- salary period/currency semantics;
- controlled vs free-form country/job-title values;
- repeated seed behavior;
- whether source name files are supplied;
- business employee identifier;
- hard vs soft delete;
- current salary vs salary history;
- authentication/authorization scope.

Implementation proceeds with documented assumptions until answers arrive. Their reply will be treated as a requirements change and reconciled through an ADR + tests.

## Working assumptions
These assumptions are deliberately reversible:

1. Salary means annual base/gross salary in local country currency.
2. Country and job title are canonical reference data exposed as select/autocomplete values, not arbitrary strings.
3. An employee has a stable `employee_code` independent from database ID.
4. Seed runs are idempotent: deterministic employees are upserted rather than duplicated.
5. Deletion uses soft delete (`deleted_at`) by product choice; deleted employees are excluded from current views/analytics while the row is retained.
6. The employee record stores current salary only in MVP; salary-history modeling is documented as a production extension.
7. The assessment deployment is a trusted HR-user environment; production requires SSO/RBAC before handling real compensation data.

## User stories and acceptance criteria

### US-01 — Browse employees
As an HR Manager, I want to browse employees without loading all 10,000 rows at once.

Acceptance criteria:
- server-side pagination;
- total count is returned;
- default deterministic sorting;
- page size has an upper bound;
- empty result is a valid state.

### US-02 — Find relevant employees
As an HR Manager, I want to search/filter employee data quickly.

Acceptance criteria:
- search by full name or employee code;
- filter by country and job title;
- filters compose;
- search is case-insensitive;
- invalid sort fields are rejected or normalized safely.

### US-03 — Create employee
Acceptance criteria:
- required data is validated client- and server-side;
- employee code is unique;
- salary must be positive and fixed precision;
- controlled values reject unsupported country/job title;
- created employee appears in list and analytics.

### US-04 — Update employee
Acceptance criteria:
- mutable fields can be updated;
- partial updates do not null unspecified fields;
- invalid salary/reference values are rejected;
- analytics immediately reflect the committed update.

### US-05 — Delete employee
Acceptance criteria:
- destructive action requires confirmation in UI;
- deleting an unknown employee returns 404;
- after deletion the employee disappears from list and analytics.

### US-06 — Country salary insights
Acceptance criteria for a country:
- headcount;
- minimum salary;
- maximum salary;
- arithmetic mean salary;
- total payroll as an additional HR metric;
- empty country has a well-defined zero/empty response, never divide-by-zero.

### US-07 — Job-title salary insight in country
Acceptance criteria:
- average is scoped by BOTH country and canonical job title;
- no leakage from the same job title in other countries;
- zero employees returns a stable empty result.

### US-08 — Repeated high-volume seed
Acceptance criteria:
- exactly 10,000 deterministic employee identities are generated;
- names are composed from source text files;
- repeated execution does not grow employee count unexpectedly;
- database writes use batches/bulk operations, not 10,000 commits;
- runtime is measured and printed;
- seed process is safe to rerun after a partial prior run.

## Edge-case catalogue

### Identity/data quality
- duplicate full names are allowed;
- employee code duplicates are not;
- leading/trailing whitespace normalized;
- Unicode names are accepted;
- blank-after-trim strings rejected;
- country/job title casing cannot split analytics groups because values are canonical.

### Salary
- zero rejected;
- negative rejected;
- more than two decimals normalized/rejected consistently;
- very large but valid values stay inside numeric range;
- database uses decimal/numeric, never binary float.

### Pagination/filtering
- page < 1 rejected/normalized;
- page_size > max is capped/rejected;
- page beyond end returns empty rows with correct total;
- special characters in search stay parameterized;
- sort direction only accepts allowlisted values.

### Analytics
- one employee => min=max=avg;
- multiple employees with equal salary;
- decimal averages use explicit rounding rule;
- deleting/updating an employee changes aggregates correctly;
- country with zero active records.

### Concurrency/integrity
- duplicate employee-code creation races are ultimately stopped by a DB unique constraint;
- transactions prevent partial writes;
- idempotent seed can recover after interruption.

## Scope consciously rejected
- microservices;
- Redis/cache for 10k records;
- event streaming/Kafka;
- Elasticsearch;
- payroll/tax calculation;
- compensation benchmarking against market data;
- multi-currency FX conversion without a specified FX source/date;
- complex org hierarchy.

These are rejected to preserve quality and avoid speculative complexity while keeping extension points documented.


## Recruiter clarification resolution — 2026-10-05
- Salary: annual gross base salary with an associated currency; local currencies are acceptable.
- Country/Job Title: no prescribed masters; controlled reference values are our chosen consistency strategy.
- Repeated seed: no prescribed behavior; deterministic idempotent upsert is our chosen contract.
- Name files: repository may provide its own suitable source files.
- Identity: unique employee code is reasonable/recommended.
- Delete: product decision; soft delete chosen.
- Salary history: current salary is sufficient; history is deliberately excluded.
- Authentication/RBAC: not required; trusted single-HR-user environment accepted.
