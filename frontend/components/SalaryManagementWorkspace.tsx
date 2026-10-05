"use client";

import SalaryManagementApp from "@/components/SalaryManagementApp";

export default function SalaryManagementWorkspace({ canManage }: { canManage: boolean }) {
  return (
    <div className={`role-boundary ${canManage ? "can-manage" : "read-only"}`}>
      {!canManage && <div className="readonly-banner">HR Staff view · read-only access</div>}
      <SalaryManagementApp canManage={canManage} />
    </div>
  );
}
