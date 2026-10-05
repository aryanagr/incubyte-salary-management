# Async Filtered Employee Export

## Product intent
HR Managers often need to take a focused employee slice into a spreadsheet for an offline review. The export therefore uses the **same applied directory filters** as the UI rather than introducing a second reporting query language.

The feature is intentionally **HR Manager only**. HR Staff can view directory and salary insights but cannot trigger bulk compensation-data egress.

## User flow
1. HR applies search/country/job-title/name-sort filters in the directory.
2. HR selects **Email filtered CSV**.
3. The dialog snapshots the currently applied filters and displays the matching employee count.
4. HR enters an approved recipient mailbox.
5. API returns `202 Accepted` after persisting and queuing the job.
6. The UI polls job status while the user can continue working.
7. A background worker builds a CSV and sends it as an email attachment.
8. Status becomes `sent` or `failed`.

The export contains all matching rows, not only the current pagination page.

## Why asynchronous
CSV generation and external email delivery are not part of the interactive HTTP response. Keeping them synchronous would couple user latency and request reliability to an external provider. The API instead persists a job and publishes only the job ID to a durable queue.

Vercel Queues is used because the deployed application already runs on Vercel and Queues provides durable at-least-once delivery and retry behavior without adding a second worker platform. A FastAPI in-process `BackgroundTasks` implementation was deliberately rejected because request/serverless lifecycle and job durability are different concerns.

## Data model
`employee_export_jobs` stores only job metadata:
- UUID job ID;
- requester and recipient;
- immutable filter snapshot;
- queued/processing/sent/failed status;
- attempts and row count;
- provider message ID;
- safe user-facing failure message;
- timestamps.

The generated CSV itself is not stored after email delivery.

## Filter correctness
Directory listing and CSV generation share `employee_filter_clauses()` and `employee_sort_clause()`. This is intentional: duplicating filter logic would allow the visible employee set and exported employee set to drift over time.

Snapshot fields:
- search term;
- country;
- job title;
- sort field/direction.

Soft-deleted employees are excluded because the shared directory filter always includes `deleted_at IS NULL`.

## Delivery and retry safety
Vercel Queues uses at-least-once delivery, so duplicate worker invocation is expected rather than exceptional.

Two idempotency layers are used:
1. a job already marked `sent` becomes a worker no-op;
2. the email request uses a stable provider idempotency key: `employee-export/{job_id}`.

This protects against the important failure window where the provider accepts the email but the worker crashes before committing `sent` to PostgreSQL.

## Spreadsheet safety
CSV cells derived from user-controlled text are neutralized when they begin with `=`, `+`, `-`, or `@`. Without this, opening a CSV in spreadsheet software can interpret employee data as a formula.

CSV is encoded as UTF-8 with a BOM for compatibility with Excel and still opens normally in Google Sheets and standards-compliant CSV tools.

## Operational limits
- Maximum export size: 25,000 rows. Current assessment scale is approximately 10,000 employees.
- Delivery requires `RESEND_API_KEY` and an explicit `EXPORT_FROM_EMAIL` sender configuration.
- Queue availability is required; an unconfigured runtime fails explicitly rather than returning a false queued state.
- Provider/stack exception details are logged server-side and are not exposed through the job-status API.

## Tests
Requirement-derived tests cover:
- manager can queue and inspect a job;
- HR Staff receives `403`;
- recipient email validation;
- CSV matches current directory filter semantics;
- queue redelivery does not duplicate email delivery;
- spreadsheet formula injection is neutralized;
- queue-unavailable environments fail explicitly.

The general CI also runs backend coverage, lint, dependency audit, frontend audit/typecheck/build, and a bounded 10k-record concurrent API load profile.

## Deliberately not built
- XLSX generation: CSV is sufficient for Excel/Sheets and avoids an extra binary-file dependency.
- persistent export-file storage: email attachment is the requested delivery channel.
- scheduled recurring reports: not requested.
- user-configurable templates/column selection: not required for the product outcome.
- separate Celery/Redis infrastructure: Vercel Queues provides the needed durable async primitive with less operational surface.
