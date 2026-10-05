# Independent Code Review

This review was intentionally performed after the initial backend and frontend implementation. Findings are recorded before fixes to make the AI-assisted review process auditable.

## Findings

### CR-01 — Analytics and directory country state were coupled
**Severity:** High (product correctness)

The frontend used one `country` state variable for both the salary-insight country selector and the employee-table country filter. This meant changing the analytical context silently changed the directory filter, and the initial page showed only the first country rather than the full employee directory.

**Fix:** Split into `insightCountry` and `filterCountry` state.

### CR-02 — Salary update could leave analytics stale
**Severity:** High (correctness)

The insight refresh depended on employee `total`. Editing salary does not change headcount, so average/min/max/total payroll could remain stale after a successful edit.

**Fix:** Introduce a mutation/data version that invalidates insight data after create/update/delete.

### CR-03 — Test database engines leaked resources
**Severity:** Medium (test quality)

Coverage runs emitted SQLite `ResourceWarning` messages because fixture engines were not explicitly disposed.

**Fix:** Dispose the engine after each database fixture lifecycle.

### CR-04 — Seed salaries ignored local-currency scale
**Severity:** Medium (product realism)

The first deterministic seed used the same nominal salary range for every country, even though values were interpreted in local currencies. This made the dataset misleading for demonstrations.

**Fix:** Keep analytics country-scoped and generate deterministic country-specific local-currency salary ranges.

### CR-05 — Python bytecode entered an implementation commit
**Severity:** Low (repository hygiene)

`__pycache__` files were included in a commit.

**Fix:** Add root `.gitignore` and explicitly remove tracked generated files in the following commit. The history remains visible rather than rewritten.

### CR-06 — Production DB URLs may contain percent-encoded credentials
**Severity:** Medium (deployment reliability)

Alembic's ConfigParser path can misinterpret `%` in database URLs.

**Fix:** Escape percent characters when injecting `DATABASE_URL` into Alembic config.

### CR-07 — Bulk upsert left ORM identity state stale after fixture restoration
**Severity:** Medium (correctness/test reliability)

The clarified soft-delete design requires a seed rerun to clear `deleted_at` on canonical fixture identities. The SQL upsert did this correctly in storage, but SQLAlchemy could return a previously loaded object with the old `deleted_at` value from the session identity map.

**Fix:** expire ORM state after the bulk seed completes so subsequent reads observe database state. A regression test deletes a seeded identity, reruns seed and asserts it is current again without increasing row count.

### CR-08 — Frontend framework pins were behind current security releases
**Severity:** High (dependency security)

The initial frontend used Next.js 16.0.1 and React 19.2.0. By October 2026, Next.js had published multiple security releases and React Server Components had received security fixes.

**Fix:** Update submission pins to Next.js 16.3.8 and React/React DOM 19.3.0, and document dependency security as part of final release review.

### CR-09 — Directory search generated a request for every keystroke
**Severity:** Low (UX/performance)

The initial controlled search field changed the API query immediately on every input event. This is acceptable at 10k rows but creates avoidable request churn.

**Fix:** Add a 250ms debounce while keeping page reset immediate.

### CR-10 — Modal/search accessibility polish
**Severity:** Low (UX/accessibility)

The search field relied only on placeholder text and dialogs did not support Escape-to-close.

**Fix:** Add an accessible search label and Escape keyboard handling for form/detail dialogs.

## Clarification-driven follow-up
Recruiter guidance on 2026-10-05 resolved the earlier scope questions:
- Authentication/RBAC is explicitly not required for the assessment; production requirement remains documented.
- Current salary is sufficient; salary history remains deliberately out of scope.
- Deletion semantics are a product decision; hard delete was replaced with tested soft deletion.
- Controlled Country/JobTitle reference values and deterministic idempotent seed behavior are retained as documented design choices.

## Remaining deliberate gaps
- Full audit/event ledger and restore workflow are not implemented.
- FX normalization/cross-country comparison is intentionally excluded.
- Frontend dependency build verification remains a CI/deployment release gate when package installation is unavailable locally.
