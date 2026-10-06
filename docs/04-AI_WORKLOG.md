# AI Worklog

This repository intentionally records the AI-assisted workflow because the assessment asks candidates to demonstrate how AI is used, not merely to produce code.

## Core assessment role passes
1. **Product Manager pass** — converted the brief into persona, goals, explicit assumptions, unanswered questions, acceptance criteria and edge cases.
2. **Staff Architect pass** — selected Python/FastAPI + Next.js + relational DB, defined service boundaries, data model, indexes and scaling posture.
3. **Backend Developer pass** — implemented API contracts, persistence, validation, insight queries and deterministic bulk seeding.
4. **Frontend Developer pass** — implemented the HR workflow, employee management UI, filters and salary insight views.
5. **QA Engineer pass** — translated requirements into deterministic tests and edge cases rather than testing implementation details.
6. **Code Reviewer pass** — reviewed correctness, query behavior, failure handling, API semantics, maintainability and security assumptions.
7. **Release Engineer pass** — validated production configuration, health checks, environment variables and deployment documentation.

## AI-use principles
- Requirements are written before implementation.
- Architectural decisions are recorded, not hidden.
- AI-generated code is treated as a draft and must pass tests/review.
- Review and test passes are intentionally separated from the implementation pass to reduce confirmation bias.
- Unknown product decisions are labeled as assumptions instead of invented facts.
- Later ideas are not silently promoted into original requirements; core scope and optional enhancements remain distinguishable.

## Recruiter clarification change-control pass — 2026-10-05
The recruiter replied after the initial implementation and intentionally left several choices to the candidate. The response was treated as product change control rather than silently rewriting earlier reasoning.

Decisions locked after the reply:
- annual gross base salary;
- currency required, local-currency reporting accepted;
- controlled Country/Job Title retained by choice;
- deterministic idempotent seed retained by choice;
- repository-owned name files;
- unique employee code retained;
- soft deletion selected over hard delete;
- current salary only (no compensation history);
- production authentication/RBAC not required for the trusted-HR assessment persona.

The clarified domain changes were handled test-first: refine the PRD, add regression tests, then change model/query behavior and rerun the suite.

## Post-core enhancement passes

The following work happened **after the clarified assessment scope was already satisfied**. It is retained as additional engineering evidence, not retroactively described as a recruiter requirement.

### Demo authentication/RBAC
A lightweight HR Manager / HR Staff demo permission model was added so the deployed product can demonstrate a server-enforced read/write boundary. The work deliberately avoided pretending to solve enterprise IAM. See `docs/15-DEMO_AUTH_RBAC.md`.

### Asynchronous filtered XLSX export
A durable PostgreSQL-backed export workflow was added later to demonstrate asynchronous job design, retry/concurrency reasoning and report generation. It remains an optional enhancement; real SMTP delivery is enhancement UAT rather than a core-assessment gate. See `docs/16-ASYNC_FILTERED_EXPORT.md`.

### Professional-readiness quality loop
Independent reviewer/UAT/lead/developer/QA/manager passes were recorded under `docs/quality-loop/`. These passes found and closed concrete defects such as search layout instability, stale responses, export worker races, security/dependency gates and the missing 10k regression gate.

## Why the history is preserved
Older documents and commits may describe the state that existed at that point in development. The final reviewer-facing status is intentionally consolidated in:

- `README.md`;
- `docs/07-REQUIREMENTS_TRACEABILITY.md`;
- `docs/13-FINAL_QA_SECURITY_PERFORMANCE_REVIEW.md`;
- `docs/14-FINAL_REQUIREMENTS_SIGNOFF.md`.

This preserves authentic evolution while avoiding ambiguity about the final scope and state.
