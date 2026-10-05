"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  createEmployee,
  deleteEmployee,
  getCountryInsight,
  getEmployees,
  getReferenceData,
  updateEmployee,
} from "@/lib/api";
import type { CountryInsight, Employee, EmployeeInput, ReferenceData } from "@/lib/types";

const PAGE_SIZE = 20;
const EMPTY_FORM: EmployeeInput = {
  employee_code: "",
  full_name: "",
  job_title_id: 0,
  country_code: "",
  salary: "",
  department: "",
  employment_status: "active",
  hired_at: null,
};

function money(value: string | null, currency: string) {
  if (value === null) return "—";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return value;
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${currency} ${amount.toLocaleString()}`;
  }
}

function EmployeeForm({
  reference,
  initial,
  onClose,
  onSaved,
}: {
  reference: ReferenceData;
  initial?: Employee;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<EmployeeInput>(() =>
    initial
      ? {
          employee_code: initial.employee_code,
          full_name: initial.full_name,
          job_title_id: initial.job_title.id,
          country_code: initial.country.code,
          salary: initial.salary,
          department: initial.department,
          employment_status: initial.employment_status,
          hired_at: initial.hired_at,
        }
      : {
          ...EMPTY_FORM,
          job_title_id: reference.job_titles[0]?.id ?? 0,
          country_code: reference.countries[0]?.code ?? "",
        },
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (initial) await updateEmployee(initial.id, form);
      else await createEmployee(form);
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save employee");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="employee-form-title" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow">Employee record</p>
            <h2 id="employee-form-title">{initial ? "Edit employee" : "Add employee"}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close">×</button>
        </div>
        <form className="form-grid" onSubmit={submit}>
          <label>
            Employee code
            <input required maxLength={24} value={form.employee_code} onChange={(e) => setForm({ ...form, employee_code: e.target.value })} />
          </label>
          <label>
            Full name
            <input required maxLength={160} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          </label>
          <label>
            Country
            <select required value={form.country_code} onChange={(e) => setForm({ ...form, country_code: e.target.value })}>
              {reference.countries.map((country) => <option key={country.code} value={country.code}>{country.name}</option>)}
            </select>
          </label>
          <label>
            Job title
            <select required value={form.job_title_id} onChange={(e) => setForm({ ...form, job_title_id: Number(e.target.value) })}>
              {reference.job_titles.map((title) => <option key={title.id} value={title.id}>{title.name}</option>)}
            </select>
          </label>
          <label>
            Annual salary
            <input required min="0.01" step="0.01" type="number" value={form.salary} onChange={(e) => setForm({ ...form, salary: e.target.value })} />
          </label>
          <label>
            Department
            <input required maxLength={100} value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
          </label>
          <label>
            Employment status
            <select value={form.employment_status} onChange={(e) => setForm({ ...form, employment_status: e.target.value })}>
              {reference.employment_statuses.map((status) => <option key={status} value={status}>{status}</option>)}
            </select>
          </label>
          <label>
            Hire date
            <input type="date" value={form.hired_at ?? ""} onChange={(e) => setForm({ ...form, hired_at: e.target.value || null })} />
          </label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="form-actions">
            <button type="button" className="button secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="button primary" disabled={saving}>{saving ? "Saving…" : initial ? "Save changes" : "Add employee"}</button>
          </div>
        </form>
      </section>
    </div>
  );
}

function EmployeeDetail({ employee, onClose }: { employee: Employee; onClose: () => void }) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal detail-modal" role="dialog" aria-modal="true" aria-labelledby="employee-detail-title" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div><p className="eyebrow">{employee.employee_code}</p><h2 id="employee-detail-title">{employee.full_name}</h2></div>
          <button className="icon-button" onClick={onClose} aria-label="Close">×</button>
        </div>
        <dl className="detail-grid">
          <div><dt>Role</dt><dd>{employee.job_title.name}</dd></div>
          <div><dt>Department</dt><dd>{employee.department}</dd></div>
          <div><dt>Country</dt><dd>{employee.country.name}</dd></div>
          <div><dt>Annual salary</dt><dd>{money(employee.salary, employee.country.currency_code)}</dd></div>
          <div><dt>Status</dt><dd className="capitalize">{employee.employment_status}</dd></div>
          <div><dt>Hire date</dt><dd>{employee.hired_at ?? "—"}</dd></div>
        </dl>
      </section>
    </div>
  );
}

export default function SalaryManagementApp() {
  const [reference, setReference] = useState<ReferenceData | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [insightCountry, setInsightCountry] = useState("");
  const [filterCountry, setFilterCountry] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [insight, setInsight] = useState<CountryInsight | null>(null);
  const [formEmployee, setFormEmployee] = useState<Employee | "new" | null>(null);
  const [detailEmployee, setDetailEmployee] = useState<Employee | null>(null);
  const [dataVersion, setDataVersion] = useState(0);

  const loadEmployees = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await getEmployees({
        page,
        page_size: PAGE_SIZE,
        search: debouncedSearch,
        country_code: filterCountry,
        job_title_id: jobTitle || undefined,
        sort_by: "full_name",
        sort_dir: sortDir,
      });
      setEmployees(result.items);
      setTotal(result.total);
      setPages(result.pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load employees");
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, filterCountry, jobTitle, page, sortDir]);

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedSearch(search.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [search]);

  useEffect(() => {
    getReferenceData()
      .then((data) => {
        setReference(data);
        setInsightCountry(data.countries[0]?.code ?? "");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Could not load reference data");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (reference) void loadEmployees();
  }, [reference, loadEmployees]);

  useEffect(() => {
    if (!insightCountry) return;
    getCountryInsight(insightCountry).then(setInsight).catch(() => setInsight(null));
  }, [insightCountry, dataVersion]);

  const selectedCurrency = useMemo(
    () => reference?.countries.find((item) => item.code === insightCountry)?.currency_code ?? "USD",
    [insightCountry, reference],
  );

  function refreshAfterMutation() {
    setFormEmployee(null);
    setDataVersion((value) => value + 1);
    void loadEmployees();
  }

  async function remove(employee: Employee) {
    if (!window.confirm(`Remove ${employee.full_name} from the current directory? The record will be retained for traceability.`)) return;
    try {
      await deleteEmployee(employee.id);
      setDataVersion((value) => value + 1);
      if (employees.length === 1 && page > 1) setPage((value) => value - 1);
      else void loadEmployees();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete employee");
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand-kicker">People Operations</p>
          <h1>Compensation Console</h1>
          <p className="subtitle">Manage employee records and inspect compensation patterns without spreadsheet exports.</p>
        </div>
        <button className="button primary" onClick={() => setFormEmployee("new")} disabled={!reference}>+ Add employee</button>
      </header>

      <section className="insights-section" aria-labelledby="insights-title">
        <div className="section-heading">
          <div><p className="eyebrow">Salary insights</p><h2 id="insights-title">Country overview</h2></div>
          <label className="compact-label">Country
            <select value={insightCountry} onChange={(e) => setInsightCountry(e.target.value)}>
              {reference?.countries.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}
            </select>
          </label>
        </div>
        <div className="metric-grid">
          <article className="metric-card"><span>Employees</span><strong>{insight?.employee_count.toLocaleString() ?? "—"}</strong></article>
          <article className="metric-card"><span>Average salary</span><strong>{money(insight?.average_salary ?? null, selectedCurrency)}</strong></article>
          <article className="metric-card"><span>Salary range</span><strong className="metric-small">{money(insight?.min_salary ?? null, selectedCurrency)} – {money(insight?.max_salary ?? null, selectedCurrency)}</strong></article>
          <article className="metric-card"><span>Total payroll</span><strong>{money(insight?.total_payroll ?? null, selectedCurrency)}</strong></article>
        </div>
        <div className="insight-panels">
          <article className="panel">
            <div className="panel-header"><h3>Role benchmarks</h3><span>{insight?.job_titles.length ?? 0} roles</span></div>
            <div className="benchmark-list">
              {insight?.job_titles.slice(0, 6).map((row) => (
                <div className="benchmark-row" key={row.job_title.id}>
                  <div><strong>{row.job_title.name}</strong><span>{row.employee_count} employees</span></div>
                  <b>{money(row.average_salary, selectedCurrency)}</b>
                </div>
              ))}
              {insight && insight.job_titles.length === 0 && <p className="empty-copy">No salary data for this country yet.</p>}
            </div>
          </article>
          <article className="panel outliers-panel">
            <div className="panel-header"><h3>Range context</h3><span>Current data</span></div>
            <div className="outlier-item"><span>Highest paid</span><strong>{insight?.highest_paid_employee?.full_name ?? "—"}</strong><b>{money(insight?.highest_paid_employee?.salary ?? null, selectedCurrency)}</b></div>
            <div className="outlier-item"><span>Lowest paid</span><strong>{insight?.lowest_paid_employee?.full_name ?? "—"}</strong><b>{money(insight?.lowest_paid_employee?.salary ?? null, selectedCurrency)}</b></div>
          </article>
        </div>
      </section>

      <section className="employees-section" aria-labelledby="employees-title">
        <div className="section-heading">
          <div><p className="eyebrow">Directory</p><h2 id="employees-title">Employees <span className="count-badge">{total.toLocaleString()}</span></h2></div>
        </div>
        <div className="toolbar">
          <input className="search-input" aria-label="Search employees" placeholder="Search name or employee code" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
          <select aria-label="Filter country" value={filterCountry} onChange={(e) => { setFilterCountry(e.target.value); setPage(1); }}>
            <option value="">All countries</option>
            {reference?.countries.map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}
          </select>
          <select aria-label="Filter job title" value={jobTitle} onChange={(e) => { setJobTitle(e.target.value); setPage(1); }}>
            <option value="">All job titles</option>
            {reference?.job_titles.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
          <button className="button secondary" onClick={() => setSortDir((current) => current === "asc" ? "desc" : "asc")}>Name {sortDir === "asc" ? "↑" : "↓"}</button>
        </div>

        {error && <div className="error-banner" role="alert">{error}<button onClick={() => void loadEmployees()}>Retry</button></div>}
        <div className="table-wrap">
          <table>
            <thead><tr><th>Employee</th><th>Role</th><th>Country</th><th>Salary</th><th>Status</th><th><span className="sr-only">Actions</span></th></tr></thead>
            <tbody>
              {!loading && employees.map((employee) => (
                <tr key={employee.id}>
                  <td><button className="employee-link" onClick={() => setDetailEmployee(employee)}><strong>{employee.full_name}</strong><span>{employee.employee_code}</span></button></td>
                  <td><strong>{employee.job_title.name}</strong><span className="table-sub">{employee.department}</span></td>
                  <td>{employee.country.name}</td>
                  <td className="salary-cell">{money(employee.salary, employee.country.currency_code)}</td>
                  <td><span className={`status-chip ${employee.employment_status}`}>{employee.employment_status}</span></td>
                  <td><div className="row-actions"><button onClick={() => setFormEmployee(employee)}>Edit</button><button className="danger-link" onClick={() => void remove(employee)}>Delete</button></div></td>
                </tr>
              ))}
              {loading && <tr><td colSpan={6} className="state-cell">Loading employees…</td></tr>}
              {!loading && employees.length === 0 && <tr><td colSpan={6} className="state-cell">No employees match these filters.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="pagination">
          <span>Page {pages === 0 ? 0 : page} of {pages}</span>
          <div><button className="button secondary" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Previous</button><button className="button secondary" disabled={page >= pages} onClick={() => setPage((value) => value + 1)}>Next</button></div>
        </div>
      </section>

      {reference && formEmployee && (
        <EmployeeForm
          reference={reference}
          initial={formEmployee === "new" ? undefined : formEmployee}
          onClose={() => setFormEmployee(null)}
          onSaved={refreshAfterMutation}
        />
      )}
      {detailEmployee && <EmployeeDetail employee={detailEmployee} onClose={() => setDetailEmployee(null)} />}
    </main>
  );
}
