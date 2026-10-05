# Trade-offs and Decisions

## FastAPI + Next.js instead of full-stack Next.js
**Chosen:** aligns directly with the Python/React role and makes backend design/testing visible.
**Cost:** two application surfaces and explicit API boundary/configuration.

## PostgreSQL for production
Relational aggregates, fixed-precision numeric fields, constraints and indexed filters match the workload. SQLite remains useful for deterministic local tests only.

## Controlled Country and Job Title
Both are reporting dimensions. Canonical reference rows prevent values such as `Software Engineer`, `software engineer` and typos from fragmenting aggregates.
**Cost:** joins/reference-data management instead of free-form input.

## Salary currency inherited from Country
The recruiter confirmed salary needs a currency and local currencies are acceptable. Because required analytics are country-scoped, the currency is canonical on Country rather than duplicated on every Employee row.
**Trade-off:** this assumes one reporting currency per country for the assessment. A production system supporting employees paid in a non-local currency would move `currency_code` onto the compensation record.

## Idempotent deterministic seed
Repeated runs upsert stable `EMP-xxxxx` codes and restore the canonical seeded state instead of appending another 10k rows.
**Benefit:** predictable demos/tests and safe routine execution.
**Trade-off:** rerunning seed intentionally overwrites manual edits to seeded identities; that behavior is documented and appropriate for fixture/demo data, not production HR imports.

## Soft delete
`DELETE` sets `deleted_at` and current list/detail/analytics queries exclude deleted employees.
**Why:** HR/compensation records should not disappear physically just because they are removed from the active product view.
**Trade-off:** restore/history UI is deliberately not added; full audit retention remains out of scope.

## Current salary only
Recruiter confirmed current salary is sufficient. We therefore keep salary on Employee rather than introducing effective-dated compensation tables.
**Future path:** add CompensationRecord with `effective_from/effective_to` when salary history becomes a requirement.

## No authentication/RBAC
Recruiter explicitly confirmed the assessment may assume a single trusted HR Manager. This avoids spending assignment scope on identity plumbing.
**Production caveat:** SSO, least-privilege RBAC and audit logging are release blockers for real compensation data.

## No Redis/cache
At 10k employees, indexed SQL aggregations are inexpensive. A cache would create invalidation/staleness failure modes without measured need.

## Offset pagination
Chosen for simplicity and predictable HR table navigation at 10k rows. Cursor pagination would be preferred at much larger cardinality or under heavy concurrent writes.

## No FX normalization
Required comparisons are scoped to one country. Cross-country comparison without an FX source/date would be misleading, so the product does not silently normalize currencies.
