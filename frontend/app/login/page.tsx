"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, login } from "@/lib/api";

const DEMO_ACCOUNTS = [
  {
    role: "HR Manager",
    email: "manager@salary.demo",
    password: "Manager@123",
    access: "Full access: add, edit, delete, directory and salary insights",
  },
  {
    role: "HR Staff",
    email: "hr@salary.demo",
    password: "Hr@123",
    access: "Read-only access: directory and salary insights",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState(DEMO_ACCOUNTS[0].email);
  const [password, setPassword] = useState(DEMO_ACCOUNTS[0].password);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getCurrentUser().then(() => router.replace("/")).catch(() => undefined);
  }, [router]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
      router.replace("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  function useDemoAccount(account: (typeof DEMO_ACCOUNTS)[number]) {
    setEmail(account.email);
    setPassword(account.password);
    setError("");
  }

  return (
    <main className="login-shell">
      <section className="login-hero">
        <p className="brand-kicker">People Operations</p>
        <h1>Compensation Console</h1>
        <p>Explore employee compensation, role benchmarks and salary ranges through a focused HR workspace.</p>
        <div className="permission-summary">
          <div><strong>HR Manager</strong><span>Full salary-management access</span></div>
          <div><strong>HR Staff</strong><span>Read-only salary visibility</span></div>
        </div>
      </section>

      <section className="login-card" aria-labelledby="login-title">
        <div>
          <p className="eyebrow">Demo workspace</p>
          <h2 id="login-title">Sign in</h2>
          <p className="login-copy">Choose either demo role to review the permission model.</p>
        </div>

        <form className="login-form" onSubmit={submit}>
          <label>Email<input type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          <label>Password<input type="password" required value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button primary login-submit" disabled={submitting} type="submit">
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="demo-account-list">
          <p className="demo-label">Demo accounts</p>
          {DEMO_ACCOUNTS.map((account) => (
            <button type="button" className="demo-account" key={account.email} onClick={() => useDemoAccount(account)}>
              <span><strong>{account.role}</strong><small>{account.access}</small></span>
              <code>{account.email}</code>
            </button>
          ))}
        </div>

        <p className="demo-note">This is intentionally a demo authentication layer for the assessment. Production SSO/IAM remains outside the assignment scope.</p>
      </section>
    </main>
  );
}
