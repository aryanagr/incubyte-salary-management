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

## Cycle 2 review findings

### CR-11 — Concurrent export workers could race on the same queued job
**Severity:** High (delivery correctness)

The immediate browser dispatch and scheduled recovery worker could both observe the same queued export before either persisted a `processing` state, creating a risk of duplicate email delivery.

**Fix:** Claim each job through a conditional atomic database update (`queued` -> `processing`) that increments attempts only when exactly one worker wins the claim. A regression test calls processing twice and asserts the email send path executes once.

### CR-12 — Final-attempt worker crash could leave export permanently processing
**Severity:** High (operational correctness)

Stale recovery originally only requeued `processing` jobs when attempts were below the retry ceiling. If the worker died after claiming the third/final attempt, the job no longer qualified for recovery and could remain `processing` indefinitely.

**Fix:** Recovery now inspects every stale processing job. Retryable jobs return to `queued`; jobs that have exhausted the attempt budget transition to terminal `failed` with `completed_at` and an explicit timeout reason. Regression tests cover both branches.

### CR-13 — Final QA evidence drifted behind the implementation
**Severity:** Medium (submission/evidence quality)

The earlier final QA document still described authentication as out of scope and frontend build verification as pending even after role-based demo authentication and CI frontend builds were added.

**Fix:** Refresh final QA evidence from the latest GitHub Actions results and explicitly distinguish automated build verification from browser/E2E UAT.

### CR-14 — Frontend has no automated component/E2E test suite
**Severity:** Medium (test depth)

The frontend release gate currently runs TypeScript type checking and a production Next.js build, but there is no React component test or browser E2E suite.

**Status:** Open, documented rather than hidden. Backend behavior, authorization, export generation, concurrency and API boundaries are automated; browser-level interaction remains a UAT/test-depth follow-up.

## Clarification-driven follow-up
Recruiter guidance on 2026-10-05 resolved the earlier scope questions:
- Authentication/RBAC was not required by the original assessment; a small demo HR Manager/HR Staff role boundary was later added as a production-minded extension.
- Current salary is sufficient; salary history remains deliberately out of scope.
- Deletion semantics are a product decision; hard delete was replaced with tested soft deletion.
- Controlled Country/JobTitle reference values and deterministic idempotent seed behavior are retained as documented design choices.

## Remaining deliberate gaps
- Full audit/event ledger and restore workflow are not implemented.
- FX normalization/cross-country comparison is intentionally excluded.
- Frontend component/E2E automation is not implemented; typecheck/build are enforced in CI.
- Live export-email UAT remains gated on SMTP provider credentials.
