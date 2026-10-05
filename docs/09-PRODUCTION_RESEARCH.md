# Production Compensation-System Research

The goal of this research is not to copy enterprise HR suites. It is to identify domain patterns that should influence a small, well-crafted assessment solution.

## Patterns observed

### Effective-dated compensation
Workday models compensation changes using effective dates and explicitly supports out-of-order future changes. That is strong evidence that a real compensation domain should preserve time rather than simply overwrite values.

Reference: https://doc.workday.com/admin-guide/en-us/human-capital-management/compensation/manage-compensation/meq1649709028535.html

**Assessment decision:** recruiter confirmed current salary is sufficient. Keep current salary in the MVP and document effective-dated history as a future extension.

### Canonical job architecture and geography
Pave's compensation methodology maps people into job families, career tracks, job levels and locations before benchmarking. Stable dimensions are important because compensation analytics are only trustworthy when equivalent roles/locations group consistently.

Reference: https://www.pave.com/products/market-data-methodology

**Assessment decision:** normalize Country and Job Title rather than allowing uncontrolled strings to fragment required aggregates.

### Currency, access control and auditability
Deel describes global-currency support, sensitive compensation-data access controls, pay-distribution reporting and auditable compensation review cycles.

Reference: https://www.deel.com/solutions/compensation/

**Assessment decision:** represent each country with an explicit currency code and keep analytics country-scoped. Recruiter confirmed auth/RBAC is not required for the assessment, while SSO/RBAC and an audit ledger remain documented production requirements.

### Salary/pay bands
Pave describes salary bands as structured role/location ranges used for consistency, transparency and budgeting.

Reference: https://www.pave.com/blog-posts/salary-bands

**Assessment decision:** do not add salary-band CRUD to this assignment. It is a sensible future capability, but the required product is employee salary management + descriptive insights, not market benchmarking.

## What we deliberately do not copy
Enterprise suites carry workflows for approvals, taxes, bonus/stock plans, payroll execution, legal entities, benefits and global compliance. Implementing those would reduce focus and make the assessment harder to reason about. The architecture preserves extension seams without shipping speculative product scope.
