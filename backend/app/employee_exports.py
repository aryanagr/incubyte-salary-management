from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import DemoUser
from .db import SessionLocal
from .email_delivery import send_employee_export_email
from .models import Employee, EmployeeExportJob
from .schemas import EmployeeExportRequest
from .services import employee_filter_clauses, employee_sort_clause

MAX_EXPORT_ROWS = 25_000


def create_export_job(db: Session, data: EmployeeExportRequest, user: DemoUser) -> EmployeeExportJob:
    job = EmployeeExportJob(
        id=str(uuid.uuid4()),
        requested_by_email=user.email,
        recipient_email=str(data.recipient_email),
        filters=data.filter_snapshot(),
        status="queued",
        attempt_count=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_export_job(db: Session, job_id: str, user: DemoUser) -> EmployeeExportJob:
    job = db.get(EmployeeExportJob, job_id)
    if not job or job.requested_by_email != user.email:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


def mark_export_enqueue_failure(db: Session, job: EmployeeExportJob) -> None:
    job.status = "failed"
    job.error_message = "The export could not be queued. Please try again."
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)


def _export_rows(db: Session, filters: dict) -> list[Employee]:
    clauses = employee_filter_clauses(
        search=filters.get("search"),
        country_code=filters.get("country_code"),
        job_title_id=filters.get("job_title_id"),
    )
    rows = db.scalars(
        select(Employee)
        .where(*clauses)
        .order_by(
            employee_sort_clause(filters.get("sort_by") or "full_name", filters.get("sort_dir") or "asc"),
            Employee.id.asc(),
        )
        .limit(MAX_EXPORT_ROWS + 1)
    ).all()
    if len(rows) > MAX_EXPORT_ROWS:
        raise RuntimeError(f"Export exceeds the {MAX_EXPORT_ROWS:,}-row safety limit")
    return rows


def build_employee_export_csv(db: Session, job: EmployeeExportJob) -> tuple[bytes, int]:
    rows = _export_rows(db, job.filters)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "employee_code",
            "full_name",
            "job_title",
            "country",
            "currency",
            "annual_salary",
            "department",
            "employment_status",
            "hired_at",
        ]
    )
    for employee in rows:
        writer.writerow(
            [
                employee.employee_code,
                employee.full_name,
                employee.job_title.name,
                employee.country.name,
                employee.country.currency_code,
                f"{employee.salary:.2f}",
                employee.department,
                employee.employment_status,
                employee.hired_at.isoformat() if employee.hired_at else "",
            ]
        )
    # UTF-8 BOM improves Excel's handling of non-ASCII names while remaining
    # valid UTF-8 for other spreadsheet tools.
    return ("\ufeff" + buffer.getvalue()).encode("utf-8"), len(rows)


def process_export_job(job_id: str) -> None:
    with SessionLocal() as db:
        job = db.get(EmployeeExportJob, job_id)
        if not job:
            # A deleted/nonexistent job is not retryable queue work.
            return
        if job.status == "sent":
            # Vercel Queues is at-least-once. Sent jobs are idempotent no-ops.
            return

        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        job.completed_at = None
        job.error_message = None
        job.attempt_count += 1
        db.commit()

        try:
            csv_bytes, row_count = build_employee_export_csv(db, job)
            provider_message_id = send_employee_export_email(
                job_id=job.id,
                recipient_email=job.recipient_email,
                csv_bytes=csv_bytes,
                row_count=row_count,
            )
        except Exception as exc:
            db.rollback()
            failed = db.get(EmployeeExportJob, job_id)
            if failed:
                failed.status = "failed"
                # Do not persist provider payloads, credentials or stack traces.
                failed.error_message = str(exc)[:500]
                failed.completed_at = datetime.now(timezone.utc)
                db.commit()
            raise

        delivered = db.get(EmployeeExportJob, job_id)
        if delivered:
            delivered.status = "sent"
            delivered.row_count = row_count
            delivered.provider_message_id = provider_message_id
            delivered.error_message = None
            delivered.completed_at = datetime.now(timezone.utc)
            db.commit()
