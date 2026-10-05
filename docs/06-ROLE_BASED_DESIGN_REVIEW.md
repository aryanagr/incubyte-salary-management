# Role-based AI Design Review

This file records intentionally separate review passes. They are role-separated AI passes rather than a claim that multiple human developers authored the repository.

## Product Manager pass
**Concern:** The literal CRUD brief is under-specified around identity, currency, deletion, salary history and seed reruns.

**Recommendation:** Ask only product questions that can alter behavior/schema. Proceed on reversible assumptions for everything else. Make HR workflows fast: pagination, search/filter, obvious analytics, clear destructive confirmation.

## Staff Architect pass
**Concern:** A 10,000-row requirement can tempt unnecessary distributed-system complexity.

**Recommendation:** Modular monolith with two deployable surfaces: Next.js UI + FastAPI API backed by PostgreSQL. Use SQL aggregation and composite indexes. Keep service/repository boundaries so future salary history or authorization can be added without rewriting HTTP handlers.

## Backend Developer pass
**Concern:** Data integrity matters more than cleverness.

**Recommendation:** DB-level uniqueness for employee code, fixed-precision `NUMERIC`, canonical reference values, typed request schemas, allowlisted sorting, transactional updates, bulk upsert for seed data.

## Frontend Developer pass
**Concern:** HR Manager should not need technical knowledge to use the tool.

**Recommendation:** One employee workspace with filters + pagination, create/edit modal/page, detail view, and a country insight dashboard. Show loading/error/empty states. Never pull all 10k rows client-side.

## QA Engineer pass
**Concern:** AI implementation can optimize for its own code and miss the brief.

**Recommendation:** Derive tests directly from the assessment and PRD. Maintain a traceability matrix. Include update/delete effects on analytics and rerun seed idempotency.

## Security Reviewer pass
**Concern:** Compensation data is sensitive even though auth is not specified.

**Recommendation:** Explicitly label no-auth as an assessment assumption, avoid logging salaries in normal request logs, validate all input, no wildcard CORS in production, no secrets in source. Document SSO/RBAC/audit as mandatory for real use.

## Performance Reviewer pass
**Concern:** Seed requirement explicitly says performance matters.

**Recommendation:** deterministic generation + chunked `INSERT ... ON CONFLICT`/bulk ORM execution. Benchmark seed duration. Avoid row-at-a-time commits. Required analytics should be computed in SQL over indexed columns.

## Debate and decision summary

### Separate compensation table now?
- **Architect:** Good production modeling for salary history.
- **PM:** Recruiter confirmed current salary is sufficient and history is optional.
- **Decision:** Keep current salary on Employee for MVP; document the effective-dated CompensationRecord migration path but do not implement it.

### Normalize Country/JobTitle into tables now?
- **Data/QA:** Prevents fragmented aggregates.
- **Backend:** Adds joins and seed complexity.
- **Decision:** Keep Country and JobTitle as normalized reference tables. Recruiter confirmed there are no prescribed masters and asked us to document our chosen consistency strategy.

### Cache analytics?
- **Performance:** 10k rows + proper indexes is trivial for PostgreSQL.
- **Decision:** No cache. Measure before adding complexity.

### Soft delete?
- **Security/production:** Prefer retention/audit.
- **Assessment guidance:** deletion semantics are intentionally left to product judgment.
- **Decision:** Soft delete using `deleted_at`; exclude deleted rows from current directory/analytics and keep restore UI outside scope.


### Authentication/RBAC?
- **Security:** compensation data would require strict authorization in production.
- **Recruiter guidance:** authentication is not required for the assessment; a single trusted HR Manager is acceptable.
- **Decision:** Do not add auth plumbing to the take-home. Document SSO/RBAC/audit as production requirements rather than speculative assessment scope.
