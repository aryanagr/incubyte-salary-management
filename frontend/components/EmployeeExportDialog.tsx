"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { createEmployeeExport, getEmployeeExport } from "@/lib/api";
import type { EmployeeExportJob } from "@/lib/types";

export type EmployeeExportFilters = {
  search: string;
  countryCode: string;
  countryLabel: string;
  jobTitleId?: number;
  jobTitleLabel: string;
  sortDir: "asc" | "desc";
};

export default function EmployeeExportDialog({
  filters,
  resultCount,
  onClose,
}: {
  filters: EmployeeExportFilters;
  resultCount: number;
  onClose: () => void;
}) {
  const [recipientEmail, setRecipientEmail] = useState("");
  const [job, setJob] = useState<EmployeeExportJob | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    if (!job || (job.status !== "queued" && job.status !== "processing")) return;

    const timer = window.setTimeout(async () => {
      try {
        setJob(await getEmployeeExport(job.id));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not refresh export status");
      }
    }, 1500);

    return () => window.clearTimeout(timer);
  }, [job]);

  const filterSummary = useMemo(() => {
    const active: string[] = [];
    if (filters.search) active.push(`Search: “${filters.search}”`);
    if (filters.countryCode) active.push(`Country: ${filters.countryLabel}`);
    if (filters.jobTitleId) active.push(`Job title: ${filters.jobTitleLabel}`);
    active.push(`Name: ${filters.sortDir === "asc" ? "A → Z" : "Z → A"}`);
    return active;
  }, [filters]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setJob(null);
    try {
      const created = await createEmployeeExport({
        recipient_email: recipientEmail,
        search: filters.search || undefined,
        country_code: filters.countryCode || undefined,
        job_title_id: filters.jobTitleId,
        sort_by: "full_name",
        sort_dir: filters.sortDir,
      });
      setJob(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not queue export");
    } finally {
      setSubmitting(false);
    }
  }

  const busy = submitting || job?.status === "queued" || job?.status === "processing";

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="modal export-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="employee-export-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">Async export</p>
            <h2 id="employee-export-title">Email filtered employee CSV</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close">×</button>
        </div>

        <p className="export-copy">
          The export snapshots the filters currently applied to the employee directory. You can close this dialog after queuing; processing continues asynchronously.
        </p>

        <div className="export-snapshot" aria-label="Export filter snapshot">
          <div><strong>{resultCount.toLocaleString()}</strong><span>matching employees</span></div>
          <ul>
            {filterSummary.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>

        <form className="export-form" onSubmit={submit}>
          <label>
            Send CSV to
            <input
              type="email"
              required
              autoComplete="email"
              placeholder="name@company.com"
              value={recipientEmail}
              onChange={(event) => setRecipientEmail(event.target.value)}
              disabled={busy}
            />
          </label>
          <p className="export-security-note">Salary exports contain sensitive compensation data. Send only to an approved mailbox.</p>

          {error && <p className="form-error" role="alert">{error}</p>}

          {job && (
            <div className={`export-status ${job.status}`} role="status" aria-live="polite">
              <strong>
                {job.status === "queued" && "Export queued"}
                {job.status === "processing" && "Preparing your CSV"}
                {job.status === "sent" && "Export sent"}
                {job.status === "failed" && "Export failed"}
              </strong>
              <span>
                {job.status === "queued" && "A worker will pick up the request shortly."}
                {job.status === "processing" && "Generating the filtered file and delivering it by email."}
                {job.status === "sent" && `${(job.row_count ?? resultCount).toLocaleString()} rows were delivered to ${job.recipient_email}.`}
                {job.status === "failed" && (job.error_message || "The worker could not complete the export. Please retry.")}
              </span>
            </div>
          )}

          <div className="form-actions">
            <button type="button" className="button secondary" onClick={onClose}>Close</button>
            <button type="submit" className="button primary" disabled={busy || job?.status === "sent"}>
              {submitting ? "Queuing…" : busy ? "Processing…" : job?.status === "failed" ? "Retry export" : job?.status === "sent" ? "Sent" : "Queue email export"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
