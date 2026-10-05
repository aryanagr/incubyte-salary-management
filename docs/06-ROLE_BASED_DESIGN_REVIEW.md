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
- **PM:** History is not asked and hiring team has not answered yet.
- **Decision:** Keep current salary on employee for MVP; document migration path to effective-dated compensation. This minimizes speculative scope.

### Normalize Country/JobTitle into tables now?
- **Data/QA:** Prevents fragmented aggregates.
- **Backend:** Adds joins and seed complexity.
- **Decision:** Use canonical controlled values in application/domain initially; schema can promote them to reference tables if recruiter confirms master-data expectation. Composite string indexes still satisfy current workload cleanly.

### Cache analytics?
- **Performance:** 10k rows + proper indexes is trivial for PostgreSQL.
- **Decision:** No cache. Measure before adding complexity.

### Soft delete?
- **Security/production:** Prefer retention/audit.
- **Assessment literal CRUD:** Hard delete is simpler and observable.
- **Decision:** Hard delete until recruiter clarifies, with explicit production caveat.
