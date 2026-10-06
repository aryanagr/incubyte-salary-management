# Async Filtered Employee Export

## Product intent
HR can export the employee directory using the **exact search, country, job-title and sort state active when the request is queued**. The export contains all matching rows, not only the current pagination page, and is emailed as an `.xlsx` workbook.

The request is intentionally asynchronous so generating a report and contacting a mail provider never blocks directory browsing.

## User flow
1. Apply directory search/filters/sort.
2. Choose **Export filtered employees**.
3. Enter the destination email address.
4. UI creates a durable export job and immediately displays `queued`.
5. A separate worker request processes the job while the UI polls persisted status.
6. On success the UI reports the number of rows emailed; failures/retries remain visible through durable job state.

Both demo HR roles can export because this is a read/reporting permission. Employee mutations remain HR-Manager-only.

## Architecture

```text
Browser
  │ POST /api/v1/exports (fast: durable queue only)
  ▼
PostgreSQL export_jobs
  │
  ├── browser fire-and-forget dispatch ──► worker invocation
  │                                        │
  │                                        ├── query matching employees
  │                                        ├── generate XLSX in memory
  │                                        └── SMTP attachment delivery
  │
  └── Vercel Cron daily recovery ─────────► retries queued jobs
```

### Why a database-backed queue instead of FastAPI BackgroundTasks
Vercel/serverless compute may end after a response. A database job survives process termination and captures attempts, error details and completion state. `BackgroundTasks` alone would therefore be weaker operational semantics.

### Why not Redis/Celery
Export volume is tiny and the product already requires PostgreSQL. A dedicated queue broker/worker platform would add deployment, observability and failure modes disproportionate to this assessment. The `export_jobs` table is sufficient at the current scale and leaves a clean migration path if workload grows.

### Why immediate dispatch plus cron recovery
The Vercel Hobby deployment cannot provide a frequent cron cadence suitable for interactive reports. The browser therefore kicks a separate authenticated worker invocation immediately after the queue request returns. The durable job remains authoritative; a scheduled recovery worker later retries jobs if the dispatch request is interrupted.

## Job lifecycle
- `queued` — durable request exists and is eligible for processing.
- `processing` — worker claimed the request.
- `sent` — workbook delivered successfully; row count recorded.
- `failed` — delivery exhausted the configured retry limit.

The worker currently allows up to three delivery attempts and persists a bounded error message instead of losing failure context.

## Filter snapshot
The export job stores:
- search term;
- country;
- job title;
- optional department/status at API level;
- sort field/direction;
- recipient;
- requesting user.

This prevents later UI changes from altering an already-requested report.

## XLSX generation
`openpyxl` write-only mode creates the workbook in memory. Columns include employee code, name, job title, department, country, currency, annual salary, status and hire date. Deleted employees are excluded exactly as they are from the live directory.

## Authorization and privacy
- Queue/status/dispatch endpoints require an authenticated demo HR session.
- Status and dispatch lookups are scoped to the user who created the job; another HR persona receives `404` rather than learning the job exists.
- The cron worker requires Vercel `CRON_SECRET` and is not accessible through ordinary user authentication.
- SMTP credentials are environment variables and never committed to Git.
- Employee exports are intentionally marked `no-store` through the existing API cache policy.

## Mail provider configuration
The implementation is SMTP-provider-neutral. Production delivery requires:

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME       # optional when provider does not require it
SMTP_PASSWORD       # secret
SMTP_FROM
SMTP_USE_TLS
```

The worker fails explicitly if a mail transport is not configured. It never records a job as `sent` merely because XLSX generation succeeded.

## Test evidence
Automated tests cover:
- filter snapshot normalization;
- all matching rows rather than one page;
- XLSX structure/order;
- successful delivery state transition;
- retry behavior on provider failure;
- export authentication;
- requester ownership boundary;
- cron-secret authorization.

## Production extension path
At higher export volume, replace the DB polling/HTTP worker with a managed durable queue while preserving the existing `ExportJob` domain contract. For large datasets, stream rows and store generated files in object storage with expiring links rather than attaching large workbooks directly to email.
