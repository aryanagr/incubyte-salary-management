# Final QA, Security & Performance Review

## Review scope
Final independent pass after recruiter clarification and implementation changes.

## Automated quality
- Backend tests: **21 passing**.
- Coverage: **89.81%**.
- Coverage floor: **85%**.
- Python compilation: pass.
- FastAPI service-root import (`main:app`): pass.
- TS/TSX syntax transpilation: pass.

## Performance verification
Fresh migrated SQLite verification database with 10,000 seeded employees.

### Seed
- 10,000-row deterministic upsert: **1.246s** on this final review run.

### Endpoint timing samples
20 post-warmup requests using FastAPI TestClient:

| Request | Median | P95 |
|---|---:|---:|
| paginated employee list | 8.09 ms | 10.08 ms |
| employee-code search through list | 17.33 ms | 21.86 ms |
| country filter | 7.71 ms | 11.14 ms |
| country insight | 8.09 ms | 10.43 ms |
| country + job-title insight | 4.61 ms | 7.26 ms |

Environment-specific measurements only; they are not an SLA.

### Query-plan evidence
SQLite query planner selected:
- `ix_employees_country_salary` for country aggregate and salary extrema;
- `ix_employees_country_job_title` for country/job-title aggregation;
- unique employee-code index for employee-code lookup.

### Known performance caveat
Substring search uses `%term%`, so a standard PostgreSQL B-tree cannot fully optimize it. At 10k rows this is acceptable. If measured search cost grows, use `pg_trgm` with an appropriate GIN/GiST index before considering a separate search service.

## Security review

### Input/query safety
- SQLAlchemy parameter binding used for user data.
- No user-controlled SQL identifiers; sort field is regex/whitelist constrained.
- Salary is positive and fixed precision.
- Country/job-title references are validated.
- API list page size is capped.

### Browser/XSS
- UI renders normal data through React escaping.
- No `dangerouslySetInnerHTML` usage.
- No arbitrary HTML rendering from API data.

### CORS
- Origins are environment-controlled and default to localhost for development.
- Credentials are disabled because auth is deliberately out of scope.

### Secrets
- No production secrets/private keys discovered in application source.
- Docker Compose includes only an explicitly local development PostgreSQL password.
- `.env.example` files are tracked; real `.env` files are ignored.

### Authentication exception
No authentication/RBAC is implemented because recruiter clarification explicitly permits a single trusted HR Manager environment. This is acceptable for the assessment, not for real compensation data.

### Dependency security
The original frontend pins were outdated against the current October 2026 security baseline. Updated before submission:
- Next.js `16.3.8`;
- React `19.3.0`;
- React DOM `19.3.0`.

Official Next.js September 2026 security guidance recommends 16.3.8 as the Active LTS security release.

## UI/source review findings addressed
- Analytics country and directory country filters are independent.
- Analytics refresh after create/edit/delete.
- Search requests are debounced by 250ms.
- Search input has an accessible label.
- Dialogs close with Escape.
- Backend array-style validation errors surface a useful message.
- Delete wording accurately describes retained soft-deleted records.

## Outstanding UI verification limitation
A full local Next.js browser session could not be executed because npm dependencies could not be fetched in the current sandbox. Two install attempts timed out. This is recorded as a release gate rather than falsely marked complete.

Required next verification when package access/deployment is available:
1. `npm install`;
2. `npm run typecheck`;
3. `npm run build`;
4. run application through Vercel Services or equivalent;
5. browser-check create/edit/delete/search/filter/pagination/modal flows;
6. verify mobile viewport;
7. inspect browser console/network errors;
8. inspect Vercel runtime logs after deployed smoke traffic.

## Production-only security follow-ups
- SSO/OIDC and least-privilege RBAC.
- Audit ledger for employee/salary changes.
- Content Security Policy / production security headers.
- Rate/abuse controls.
- Secret manager and credential rotation.
- Dependency scanner / Dependabot-style workflow.
- PostgreSQL backups, PITR, encryption and retention policy.
- Structured security logging and alerts.

## Final assessment judgement
Within the assignment's clarified scope, the backend/data architecture is release-quality for a take-home submission and deliberately avoids unjustified infrastructure. The only material verification gap remaining is the real Next.js/deployed browser pass, which depends on frontend package/deployment access outside this sandbox.
