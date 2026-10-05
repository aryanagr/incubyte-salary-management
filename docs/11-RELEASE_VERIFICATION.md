# Release Verification Evidence

## Clarified-scope regression — 2026-10-05
This verification was run after incorporating the recruiter response and soft-delete product decision.

### Automated tests
- Backend tests: **21 passing**.
- Coverage: **89.81%**, above the enforced 85% gate.
- Coverage includes CRUD, validation, analytics, deterministic 10k seed, soft-delete retention, repeat DELETE and seed restoration of a deleted fixture identity.

### Fresh migration
A new SQLite verification database was migrated from zero through:
1. `20261004_0001` — initial salary-management schema;
2. `20261005_0002` — `employees.deleted_at` soft-delete column/index.

SQLite is used only as deterministic release-test infrastructure; production remains PostgreSQL.

### Seed performance and idempotency
On the current assessment execution environment:
- first deterministic 10,000-row upsert: **2.942s**;
- immediate repeated upsert: **2.774s**;
- physical employee rows after rerun: **10,000**;
- soft-deleted rows after clean rerun: **0**.

These are environment-specific evidence, not an SLA.

### Real HTTP smoke test
A Uvicorn process was exercised against the fresh migrated/seeded database.

Verified before deletion:
- `GET /health` => 200;
- employee directory => 10,000 current employees;
- seeded `EMP-00001` resolves with Canada/CAD salary context;
- Canada insight => 2,000 current employees.

Verified soft deletion:
- `DELETE /api/v1/employees/1` => 204;
- repeated DELETE => 204;
- `GET /api/v1/employees/1` => 404;
- current directory total => 9,999;
- Canada insight headcount => 1,999;
- physical database rows remain => 10,000;
- rows with `deleted_at` => 1.

Verified deterministic restoration:
- reran the 10,000-row seed;
- current directory returned to 10,000;
- `deleted_at` row count returned to 0.

This demonstrates the documented distinction between retained HR storage and the current employee product view.

## Frontend verification
The main TSX component and typed API modules pass syntax transpilation with the locally installed TypeScript compiler. Full Next.js dependency typecheck/build remains a CI/Vercel release gate when npm dependencies are available.

## Production deployment prerequisites
1. persistent PostgreSQL `DATABASE_URL`;
2. Git remote / Vercel project connection;
3. `alembic upgrade head` against production;
4. deterministic seed/demo initialization if required;
5. browser smoke test of CRUD, soft delete and salary insights.
