"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, getCurrentUser, logout } from "@/lib/api";
import type { AuthUser } from "@/lib/types";
import SalaryManagementWorkspace from "@/components/SalaryManagementWorkspace";

export default function AuthenticatedApp() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [workspaceError, setWorkspaceError] = useState("");

  const checkSession = useCallback(async () => {
    setChecking(true);
    setWorkspaceError("");
    try {
      setUser(await getCurrentUser());
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        router.replace("/login");
        return;
      }
      setWorkspaceError("We could not reach the HR workspace. Your session has not been discarded.");
    } finally {
      setChecking(false);
    }
  }, [router]);

  useEffect(() => {
    void checkSession();
  }, [checkSession]);

  async function signOut() {
    try {
      await logout();
    } finally {
      router.replace("/login");
      router.refresh();
    }
  }

  if (checking) {
    return <main className="auth-loading"><div className="auth-spinner" /><p>Checking your HR workspace…</p></main>;
  }

  if (workspaceError || !user) {
    return (
      <main className="auth-loading workspace-error" role="alert">
        <h1>Workspace temporarily unavailable</h1>
        <p>{workspaceError || "We could not verify your session."}</p>
        <button className="button primary" onClick={() => void checkSession()}>Try again</button>
      </main>
    );
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
      <SalaryManagementWorkspace canManage={user.role === "hr_manager"} />
    </>
  );
}
