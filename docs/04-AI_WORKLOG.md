# AI Worklog

This repository intentionally records the AI-assisted workflow because the assessment asks candidates to demonstrate how AI is used, not merely to produce code.

## Role passes
1. **Product Manager pass** — converted the brief into persona, goals, explicit assumptions, unanswered questions, acceptance criteria and edge cases.
2. **Staff Architect pass** — selected Python/FastAPI + Next.js + relational DB, defined service boundaries, data model, indexes and scaling posture.
3. **Backend Developer pass** — implemented API contracts, persistence, validation, insight queries and deterministic bulk seeding.
4. **Frontend Developer pass** — implemented the HR workflow, employee management UI, filters and salary insight views.
5. **QA Engineer pass** — translated requirements into deterministic tests and edge cases rather than testing implementation details.
6. **Code Reviewer pass** — reviews correctness, query behavior, failure handling, API semantics, maintainability and security assumptions.
7. **Release Engineer pass** — validates production configuration, health checks, environment variables and deployment documentation.

## AI-use principles
- Requirements are written before implementation.
- Architectural decisions are recorded, not hidden.
- AI-generated code is treated as a draft and must pass tests/review.
- Review and test passes are intentionally separated from the implementation pass to reduce confirmation bias.
- Unknown product decisions are labeled as assumptions instead of invented facts.

## Recruiter clarification change-control pass — 2026-10-05
The recruiter replied after the initial implementation and intentionally left several choices to the candidate. The response was treated as a product change request rather than silently rewriting earlier reasoning.

Decisions locked after the reply:
- annual gross base salary;
- currency required, local-currency reporting accepted;
- controlled Country/Job Title retained by choice;
- deterministic idempotent seed retained by choice;
- repository-owned name files;
- unique employee code retained;
- soft deletion selected over hard delete;
- current salary only (no compensation history);
- authentication/RBAC deliberately excluded for the trusted-HR assessment persona.

The implementation change is being performed TDD-first: document the refined one-page PRD, add deletion/seed regression tests, observe failure, then change migration/model/query behavior and rerun the full suite.
