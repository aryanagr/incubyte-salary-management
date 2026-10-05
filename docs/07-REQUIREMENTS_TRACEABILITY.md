# Requirements Traceability

| Requirement / clarified decision | Implementation evidence | Verification |
|---|---|---|
| Add/view/update/delete employees via UI | Next.js employee workspace + FastAPI CRUD endpoints | CRUD API tests + UI mutation flow |
| Annual gross base salary + associated currency | `employees.salary` NUMERIC + `countries.currency_code`; UI currency formatting | schema/reference/insight tests |
| Controlled Country/Job Title chosen for consistency | `countries` + `job_titles` reference tables and select controls | reference-data tests |
| Stable employee identifier | unique `employee_code` | uniqueness/normalization tests |
| Soft delete chosen as product behavior | `employees.deleted_at`; current-view filters in detail/list/analytics | soft-delete retention + insight regression tests |
| Current salary sufficient; no salary history | salary stored on Employee; ADR 003 | deliberate exclusion documented |
| Authentication not required | trusted HR persona; no auth middleware | deliberate exclusion documented |
| Min/max/avg salary by country | country insights endpoint + dashboard | analytics tests |
| Average salary for job title in country | country/job-title insight endpoint | analytics tests |
| Other meaningful metrics | headcount, payroll, extrema, role breakdown | analytics tests |
| Server-side handling of 10k records | pagination/filter/sort + indexed columns | list tests + full-scale seed test |
| Seed 10,000 employees | `backend/app/seed.py` | 10k test + benchmark |
| Repository-provided first/last name files | `backend/data/first_names.txt`, `last_names.txt` | seed tests |
| Repeated seed behavior chosen/documented | deterministic `ON CONFLICT` upsert; clears `deleted_at` | idempotency + deleted-seed restoration tests |
| Relational DB | PostgreSQL production config + Alembic migrations | fresh migration smoke test |
| Unit tests | `backend/tests/` | CI/coverage gate |
| Incremental commits | Git history preserves tests-before-fixes and review changes | repository history |
| Planning/design/AI artifacts | `docs/` + ADRs + AI worklog | repository review |
