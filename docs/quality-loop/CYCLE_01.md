# Professional Readiness Loop — Cycle 01

Status: **OPEN**

This document records the independent review → UAT → lead scope → development → QA → manager loop requested for the project. The purpose is to make the quality process inspectable rather than silently editing the final snapshot.

## 1. Code Reviewer findings

| ID | Severity | Finding | Decision |
| --- | --- | --- | --- |
| CR-01 | High | Employee search replaced all rows with one loading row, causing visible layout collapse/expand on each request. | Fix immediately. |
| CR-02 | High | Overlapping search/filter requests could resolve out of order and let stale data overwrite newer results. | Fix immediately. |
| CR-03 | High | Demo session signing silently falls back to a known development secret if `AUTH_SECRET` is missing in production. | Fail closed in production. |
| CR-04 | Medium | Authenticated salary API responses do not explicitly opt out of intermediary/browser caching. | Add `Cache-Control: no-store`. |
| CR-05 | Medium | Retired bootstrap implementation remains as dead production code after the bootstrap route was removed. | Delete it. |
| CR-06 | Medium | HR Staff permissions are visually implemented through a body CSS class even though the API is correctly protected. | Render role-aware controls explicitly. |
| CR-07 | Medium | Any `/auth/me` failure redirects to login, including transient 5xx/network failures. | Show recoverable workspace error for non-401 failures. |
| CR-08 | Medium | Session expiry during an already-open dashboard produces API errors instead of a clean return to login. | Add centralized unauthorized handling. |
| CR-09 | Medium | Health check confirms process liveness but not database readiness. | Add DB readiness endpoint. |
| CR-10 | Medium | `employee_code` is unique but not canonicalized, allowing case variants in PostgreSQL. | Normalize employee code to uppercase. |
| CR-11 | Medium | CI has tests/typecheck/build but no Python lint or dependency vulnerability gate. | Add bounded static/security checks. |
| CR-12 | Medium | No repeatable automated load test exists for the required 10k-row operating size. | Add bounded CI load test. |

## 2. UAT findings

Acceptance scenarios reviewed independently from the implementation:

- Login as HR Manager.
- Login as HR Staff.
- Invalid login.
- Session expiry / unavailable API.
- Browse 10k employee directory.
- Search by name/code while continuously typing.
- Combine country + job-title filters.
- Sort and paginate.
- Create, edit and soft-delete as manager.
- Confirm HR Staff cannot mutate through UI or API.
- Country salary metrics.
- Empty result handling.
- Error and loading states.
- Mobile/table overflow behavior.

### UAT defects/gaps

1. **Search layout shift** — confirmed; rows disappeared during background fetch.
2. **No stale-response protection** — rapid search could theoretically render an older response last.
3. **Authentication error state** — transient auth API failures looked like an expired login.
4. **Role UX coupling** — read-only presentation relied on a global body class instead of the role being explicit in the component contract.
5. **No bounded load-test evidence** tied to the current 10k dataset.

## 3. Lead scope

### Must fix in Cycle 01
- CR-01 through CR-10.
- Add lint/dependency checks that are deterministic enough for CI.
- Add a bounded 10k-record load-test harness with explicit thresholds.
- Update tests and documentation for changed contracts.

### Deliberately deferred
- Enterprise SSO/MFA/user provisioning.
- Persistent audit/event log.
- Redis/Kafka/Elasticsearch.
- FX conversion and cross-country salary normalization.
- Effective-dated compensation history.
- Large-scale search infrastructure; SQL `%term%` remains acceptable for ~10k rows.

These are not blockers for the assessment product and would add speculative complexity.

## 4. Developer implementation

Pending.

## 5. QA evidence

Pending.

## 6. Manager verdict

**Cycle remains OPEN** until all approved fixes are implemented, CI is green, bounded load thresholds pass, and there are no unresolved High-severity findings.
