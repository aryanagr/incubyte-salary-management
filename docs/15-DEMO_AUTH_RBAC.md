# Demo Authentication & RBAC — Product + Technical Decision Record

## Why this was added
The recruiter clarification explicitly said authentication/authorization could be treated as out of scope for the assessment because the intended environment may be considered a single trusted HR-user context. The core product was therefore designed and completed without making enterprise IAM a prerequisite.

After the core scope was working, a lightweight login and role model was added as a **demo/product enhancement**. The intent is to make the deployed application feel closer to a real HR product and demonstrate authorization thinking, while keeping the implementation proportional to a take-home assignment.

This is intentionally **not** presented as production identity management.

## Product model
Two demo personas are sufficient to demonstrate meaningful permission boundaries:

| Capability | HR Manager | HR Staff |
| --- | --- | --- |
| Sign in / sign out | Yes | Yes |
| View employee directory | Yes | Yes |
| Search/filter/sort employees | Yes | Yes |
| View salary analytics | Yes | Yes |
| View employee details | Yes | Yes |
| Add employee | Yes | No |
| Edit employee | Yes | No |
| Soft-delete employee | Yes | No |

### Why these two roles
Salary management commonly separates people who can consume HR/compensation information from people authorized to change employee records. For the assessment, two roles demonstrate the permission boundary without inventing a complex organization/permission matrix that the brief did not request.

### Why HR Staff can still see salary analytics
The product is fundamentally a salary-management workspace. Removing all compensation visibility from the second persona would turn the role into a generic employee-directory user and would not exercise the central product use case. The meaningful distinction for this demo is therefore **read vs write**, not compensation-visible vs compensation-hidden.

If a production requirement later specified field-level compensation confidentiality, that should become an explicit permission such as `compensation:read` rather than being inferred from a broad role name.

## Demo credentials
The login page intentionally presents both demo accounts so reviewers can switch roles quickly:

- HR Manager: `manager@salary.demo` / `Manager@123`
- HR Staff: `hr@salary.demo` / `Hr@123`

These credentials are intentionally public test fixtures. They are not database-backed production credentials and should never be reused outside this demonstration.

## Technical implementation
### Session model
The backend issues an HMAC-signed session token in the `salary_demo_session` cookie.

Cookie properties in Vercel:
- `HttpOnly` — browser JavaScript cannot read the token.
- `Secure` — transmitted over HTTPS only in the deployed environment.
- `SameSite=Lax` — reduces cross-site request exposure while remaining simple for this same-origin app.
- 8-hour expiry — suitable for a demo HR session without implementing refresh-token machinery.

The signature key is supplied through the server-side `AUTH_SECRET` Vercel environment variable and is not included in source control or exposed to the frontend.

### Authorization enforcement
Authorization is enforced in FastAPI dependencies:

- `current_user` verifies the signed session for authenticated read endpoints.
- `require_manager` wraps `current_user` and returns `403 Forbidden` unless the role is `hr_manager`.

Mutation endpoints (`POST`, `PATCH`, `DELETE` employee operations) require `require_manager`. Directory/reference/analytics reads require an authenticated user.

This matters because hiding UI controls alone is not security. HR Staff requests are rejected by the backend even if a user manually calls the API.

### Frontend behavior
The Next.js application calls `/api/v1/auth/me` before rendering the compensation console:

- unauthenticated users are redirected to `/login`;
- the current user and role are displayed in the session bar;
- HR Staff receives a visibly read-only workspace and mutation controls are hidden;
- logout clears the server-issued session cookie and returns to the login page.

The API remains the source of truth for authorization.

## Why not use NextAuth/Auth.js, Clerk, Auth0 or Cognito?
Those are legitimate production options, but introducing an external identity provider for this assignment would create configuration, callback, secret-management and account-lifecycle scope unrelated to the salary-management requirements. It would also make reviewers depend on a third-party account setup to run the submission.

The lightweight signed-cookie approach demonstrates the important architectural property — server-enforced authorization — without pretending to solve enterprise identity.

## Why not store users/passwords in PostgreSQL?
A production password system would require password hashing, password policy, reset/recovery, lockouts, email verification, MFA considerations and account administration. Adding only a users table plus plaintext/demo passwords would be worse engineering because it would look more production-like while omitting the security controls that make it safe.

For this assessment, explicit hard-coded **demo identities** plus a signed server-side session is more honest and easier to review.

## Tests added
The auth/RBAC test suite covers:
- HR Manager login and role identity;
- invalid credential rejection;
- authentication requirement on protected APIs;
- HR Staff read access;
- HR Staff mutation rejection with `403`;
- HR Manager mutation access;
- logout/session invalidation.

Existing API tests authenticate as the HR Manager so the original domain behavior remains regression-covered after introducing permissions.

## Demo data / production initialization
The existing deterministic seed was reused rather than creating frontend-only mock rows. Production Neon was initialized through a one-time Git-triggered Vercel backend build that ran:

```text
alembic upgrade head
python -m app.seed --count 10000
```

The deployment reached `READY`, so both commands completed successfully. The one-time build hook and temporary HTTP bootstrap surface were then removed from `master`. Normal deployments are side-effect free again.

This keeps one data model and one source of truth across local development, tests and the deployed app.

## What would change for a real production system
A production implementation would typically replace demo auth with organizational SSO/OIDC and explicit permissions, for example:

- `employee:read`
- `employee:write`
- `compensation:read`
- `compensation:write`
- `analytics:read`
- `audit:read`

It would also add centralized user lifecycle management, MFA/conditional access as appropriate, audit events for compensation changes, session revocation, secret rotation and security monitoring.

Those extensions are deliberately not implemented because they would exceed the clarified assessment scope.
