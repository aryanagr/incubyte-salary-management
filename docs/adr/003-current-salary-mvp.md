# ADR 003 — Current salary in MVP; effective-dated history as extension

**Status:** Provisional

## Context
Production compensation products commonly preserve effective-dated salary changes, but the assessment asks for employee salary CRUD and does not explicitly require history.

## Decision
Store current salary on the employee for the assessment MVP. Recruiter confirmed current salary is sufficient; do not add a review/history workflow to the assessment scope.

## Production migration path
Introduce `compensation_records(employee_id, amount, currency, effective_from, effective_to, reason, created_by)` and derive current compensation from effective dates. Existing employee salary becomes the initial record during migration.
