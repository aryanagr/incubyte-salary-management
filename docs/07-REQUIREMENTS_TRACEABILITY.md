# Requirements Traceability

This document maps the **clarified Incubyte assessment requirements** to implementation and verification evidence. Later demo enhancements are listed separately so they are not mistaken for required scope.

## Core assessment traceability

| Requirement / clarified decision | Implementation evidence | Verification |
|---|---|---|
| Add/view/update/delete employees via UI | Next.js employee workspace + FastAPI CRUD endpoints | CRUD API tests + UI mutation flow |
| Annual gross base salary + associated currency | `employees.salary` NUMERIC + `countries.currency_code`; UI currency formatting | schema/reference/insight tests |
| Controlled Country/Job Title chosen for consistency | `countries` + `job_titles` reference tables and select controls | reference-data tests |
| Stable employee identifier | unique normalized `employee_code` | uniqueness/normalization tests |
| Soft delete chosen as product behavior | `employees.deleted_at`; current-view filters in detail/list/analytics | soft-delete retention + insight regression tests |
| Current salary sufficient; no salary history | salary stored on Employee; ADR 003 | deliberate exclusion documented |
| Authentication/RBAC not required by recruiter | core domain does not depend on production IAM | recruiter clarification + scope documentation |
| Min/max/avg salary by country | country insights endpoint + dashboard | analytics tests |
| Average salary for job title in country | country/job-title insight endpoint | analytics tests |
| Other meaningful metrics | headcount, payroll, extrema, role breakdown | analytics tests |
| Server-side handling of ~10k records | pagination/filter/sort + indexed columns | list tests + dedicated 10k performance gate |
| Seed 10,000 employees | `backend/app/seed.py` | 10k count/performance tests |
| Repository-provided first/last-name files | `backend/data/first_names.txt`, `last_names.txt` | seed tests |
| Repeated seed behavior chosen/documented | deterministic `ON CONFLICT` upsert; clears `deleted_at` | idempotency + deleted-seed restoration tests |
| Relational database | PostgreSQL/Neon production config + Alembic migrations | migration/release evidence |
| Unit/automated tests | `backend/tests/` | CI coverage gate: 42 tests, 88.24% coverage |
| Incremental commits | Git history preserves requirements, tests, fixes, review and hardening | repository history |
| Planning/design/AI artifacts | `docs/` + ADRs + AI worklog | repository review |
| Product/architecture trade-offs | modular monolith, indexed SQL, deliberate rejection of speculative infrastructure | architecture + trade-off docs |

## Optional post-core enhancements

These are **not Incubyte requirements** and do not change the core acceptance criteria.

| Enhancement | Why it exists | Evidence |
|---|---|---|
| Demo login + HR Manager/HR Staff RBAC | Makes the deployed demo easier to exercise and demonstrates server-side authorization thinking without claiming production IAM | `docs/15-DEMO_AUTH_RBAC.md` + RBAC tests |
| Asynchronous filtered XLSX export | Demonstrates a durable reporting workflow and retry/concurrency reasoning after the core product was complete | `docs/16-ASYNC_FILTERED_EXPORT.md` + export tests |
| Professional-readiness review cycles | Makes code review/UAT/QA findings and closure evidence inspectable | `docs/quality-loop/` |

## Scope note

Core assessment completeness must be judged independently from optional-enhancement release gates. For example, real SMTP delivery is useful UAT for the export enhancement but is **not a blocker for the original salary-management assessment**.
