# ADR 004 — Soft delete employee records

## Status
Accepted after recruiter clarification on 2026-10-05.

## Context
The assessment requires delete behavior but does not require physical deletion. Recruiter guidance explicitly leaves hard-vs-soft deletion to product design. Salary/HR records are sensitive business records where physical deletion reduces traceability.

## Decision
Add nullable `employees.deleted_at`.

- `DELETE /employees/{id}` sets `deleted_at` and remains idempotent from the caller's point of view.
- Normal employee list/detail/update operations treat deleted employees as not found.
- Salary analytics exclude deleted employees.
- Seed upsert resets `deleted_at` for seeded employee codes so a rerun restores the canonical fixture dataset.
- No restore UI/API is added in this assessment.

## Consequences
We preserve the row without implementing a full audit subsystem. Every current-view query must consistently include `deleted_at IS NULL`, which is protected by tests. If legal deletion or retention policies were real requirements, this design would need policy-specific hard purge/anonymization workflows.
