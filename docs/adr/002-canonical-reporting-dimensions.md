# ADR 002 — Canonical country and job-title dimensions

**Status:** Accepted; recruiter clarification permits this candidate-defined approach

## Context
Country and job title are used as grouping dimensions in required salary analytics. Free-form values can fragment aggregates through casing/spelling differences.

## Decision
Model countries and job titles as controlled relational reference data and reference them from employees through foreign keys.

## Consequences
- analytics groups are stable;
- UI uses selects rather than arbitrary text;
- adding new countries/job titles is an administrative/reference-data concern;
- if the hiring team explicitly prefers free-form input, API contracts can be relaxed without changing the analytics service shape.
