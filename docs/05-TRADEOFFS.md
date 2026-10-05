# Trade-offs and Decisions

## FastAPI + Next.js instead of full-stack Next.js
**Chosen:** better alignment with the Python/React role and clearer backend engineering signal.
**Cost:** two deployable units and cross-origin configuration.

## PostgreSQL for production
Relational aggregates, fixed precision numeric fields and indexed filters match the workload. SQLite remains useful for deterministic local tests but is not relied on for serverless production persistence.

## No Redis/cache
At 10k employees, indexed SQL aggregations are inexpensive. A cache would add staleness/invalidation failure modes before there is a demonstrated need.

## Offset pagination
Chosen for simplicity and usability at 10k rows. Cursor pagination would be preferred at much larger cardinality or under heavy concurrent writes.

## Hard delete
Matches a literal CRUD assessment. Real HR compensation software should usually use soft deletion/audit events and authorization checks.

## Local-currency analytics
The required comparisons are scoped to one country. Cross-country salary comparison without an FX date/source would be misleading, so the product does not silently normalize currencies.
