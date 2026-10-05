"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, getCurrentUser, logout } from "@/lib/api";
import type { AuthUser } from "@/lib/types";
import SalaryManagementApp from "@/components/SalaryManagementApp";

export default function AuthenticatedApp() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((error) => {
        if (error instanceof ApiError && error.status === 401) router.replace("/login");
        else router.replace("/login");
      })
      .finally(() => setChecking(false));
  }, [router]);

  useEffect(() => {
    if (!user) return;
    document.body.classList.toggle("hr-readonly", user.role === "hr");
    return () => document.body.classList.remove("hr-readonly");
  }, [user]);

  async function signOut() {
    try {
      await logout();
    } finally {
      router.replace("/login");
      router.refresh();
    }
  }

  if (checking || !user) {
    return <main className="auth-loading"><div className="auth-spinner" /><p>Checking your HR workspace…</p></main>;
  }

  return (
    <>
      <div className="session-bar">
        <div>
          <strong>{user.name}</strong>
          <span>{user.role === "hr_manager" ? "HR Manager · Full access" : "HR Staff · Read only"}</span>
        </div>
        <button className="button secondary" onClick={signOut}>Log out</button>
      </div>
      <SalaryManagementApp />
    </>
  );
}
