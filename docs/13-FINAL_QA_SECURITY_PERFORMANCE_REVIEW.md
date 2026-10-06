# Final QA, Security & Performance Review

## Review scope
Independent QA/security/performance evidence for the current implementation. This document was refreshed in Cycle 2 after authentication/RBAC and asynchronous export functionality were added.

## Current automated quality evidence
Latest code-bearing Cycle 2 CI run (`15866d2314c7ffd9838f3b36bc2569eb27503dbb`) completed successfully.

- Backend tests: **42 passing**.
- Backend coverage: **88.24%**.
- Enforced backend coverage floor: **85%**.
- Python compilation: pass.
- Frontend TypeScript typecheck: pass.
- Frontend optimized Next.js production build: pass.
- Frontend dependency install/audit in CI: pass.

The backend CI output includes one upstream Starlette/TestClient deprecation warning about the future `httpx2` transition. It does not currently fail tests, but it is tracked as dependency-maintenance noise rather than ignored.

## Performance verification baseline
Earlier final-review measurements used a fresh migrated SQLite verification database with 10,000 seeded employees. These measurements remain useful as a local baseline but were **not rerun in Cycle 2**, because the Cycle 2 changes were isolated to export-job lifecycle/recovery and documentation.

### Seed baseline
- 10,000-row deterministic upsert: **1.246s** on the recorded review run.

### Endpoint timing baseline
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

### Authentication and role boundary
The original assessment did not require authentication, but the current implementation includes a small signed-cookie demo authentication boundary as a production-minded extension:
- HR Manager: read + employee mutation access;
- HR Staff: read/report/export access, no employee mutation access.

Sensitive API responses use `Cache-Control: no-store`, and export status/dispatch lookups are scoped to the authenticated requester.

This remains intentionally lighter than enterprise identity. Production compensation data would require SSO/OIDC, user lifecycle management, least-privilege roles and stronger session governance.

### Input/query safety
- SQLAlchemy parameter binding used for user data.
- No user-controlled SQL identifiers; sort field is constrained/whitelisted.
- Salary is positive and fixed precision.
- Country/job-title references are validated.
- API list page size is capped.
- Export recipient uses validated email input.

### Browser/XSS
- UI renders normal data through React escaping.
- No `dangerouslySetInnerHTML` usage.
- No arbitrary HTML rendering from API data.

### CORS/session behavior
- Allowed origins are environment-controlled.
- Credentialed requests are enabled because the current demo authentication uses an HTTP-only session cookie.
- Production deployments mark the session cookie secure.

### Secrets
- Production secrets are environment variables rather than source-controlled values.
- `AUTH_SECRET`, database secrets, cron secret and future SMTP credentials are not committed to Git.
- `.env.example` files document required configuration while real `.env` files remain ignored.

### Async export security/reliability
- Queue/status/dispatch APIs require an authenticated HR session.
- Export jobs are requester-scoped.
- Recovery cron requires `CRON_SECRET`.
- Job claiming is a conditional atomic database update to prevent overlapping workers from deliberately processing the same queued job.
- Stale processing jobs are requeued while retries remain and terminally failed when the final attempt has timed out.
- Live SMTP delivery is intentionally not marked verified until provider credentials are configured.

### Dependency security
Submission pins use:
- Next.js `16.3.8`;
- React `19.3.0`;
- React DOM `19.3.0`.

## UI/source review findings addressed
- Analytics country and directory country filters are independent.
- Analytics refresh after create/edit/delete.
- Search requests are debounced by 250ms.
- Search input has an accessible label.
- Dialogs close with Escape.
- Backend array-style validation errors surface a useful message.
- Delete wording accurately describes retained soft-deleted records.
- Manager-only mutation controls are driven from explicit role state.
- Export dialog snapshots current directory filters/sort and reports durable job state.

## Current QA limitations / release gates
These are deliberately recorded as open rather than being presented as completed:

1. **Frontend automated interaction coverage:** CI currently proves TypeScript correctness and a production Next.js build, but there is no React component-test or browser E2E suite.
2. **Browser UAT evidence:** a full interactive browser pass for login, CRUD, search/filter/pagination, role restrictions and export status flow should be captured before final submission if browser automation/manual evidence is available.
3. **Live email UAT:** SMTP provider credentials are not configured, so end-to-end delivery of the generated `.xlsx` attachment has not been verified against a real mailbox.
4. **Latest deployment observation:** Vercel deployment checks were previously successful during Cycle 1/export migration, but the Vercel connector later returned a scope re-authentication error during Cycle 2. Current code CI is green; the latest Cycle 2 deployment state must be rechecked after connector access is restored.

## Production-only security follow-ups
- SSO/OIDC and least-privilege enterprise RBAC.
- Audit ledger for employee/salary changes.
- Content Security Policy / stronger production security headers.
- Rate/abuse controls.
- Secret manager and credential rotation.
- Dependency scanner / Dependabot-style workflow.
- PostgreSQL backups, PITR, encryption and retention policy.
- Structured security logging and alerts.
- Mail provider idempotency/event callbacks if exactly-once-like delivery semantics become important.

## Current assessment judgement
The core backend/data behavior, role boundaries and export job lifecycle have automated evidence and meet the configured quality gate. Cycle 2 closed the stale-final-attempt export defect and corrected evidence drift. The main remaining verification gaps are **frontend interaction/E2E evidence**, **live SMTP delivery**, and **rechecking the newest Vercel deployment once connector scope access is restored**.
