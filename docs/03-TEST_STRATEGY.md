# Test Strategy

## Requirement-derived cases

### Employee creation
- creates a valid employee
- rejects blank name/title/country/department
- rejects zero or negative salary
- rejects invalid employment status
- rejects duplicate employee code

### Listing
- paginates and returns total count
- caps page size
- filters by country
- filters by job title
- searches by full name / employee code
- sorts salary ascending/descending

### Update/delete
- updates selected mutable fields
- rejects invalid salary on update
- returns 404 for unknown employee
- deletes existing employee
- repeated delete returns 404

### Insights
- country min/max/average are mathematically correct
- total payroll is correct
- empty country returns zero-count response without divide-by-zero
- job-title average is scoped to both country and title
- similarly named titles do not leak into each other

### Seed
- generates exactly 10,000 deterministic records
- rerun does not duplicate records
- uses bounded batches rather than per-row transactions

## Test pyramid
1. Service/repository unit tests on an isolated SQLite database.
2. API contract tests through FastAPI TestClient.
3. Frontend typecheck/build as a static contract gate.
4. Deployment smoke tests: health, list, create, edit, delete, insight endpoints.

## Quality gates
- Backend tests pass.
- Python formatting/linting clean.
- Frontend TypeScript build clean.
- No unhandled API errors in browser smoke flow.
