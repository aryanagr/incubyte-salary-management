from __future__ import annotations

import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import Session

from .auth import DemoUser
from .models import Employee, ExportJob
from .services import SORT_COLUMNS

MAX_EXPORT_ATTEMPTS = 3


def create_export_job(
    db: Session,
    *,
    user: DemoUser,
    recipient_email: str,
    search: str | None,
    country_code: str | None,
    job_title_id: int | None,
    department: str | None,
    employment_status: str | None,
    sort_by: str,
    sort_dir: str,
) -> ExportJob:
    job = ExportJob(
        requested_by_email=user.email,
        recipient_email=recipient_email.strip().lower(),
        search=search.strip() if search else None,
        country_code=country_code.strip().upper() if country_code else None,
        job_title_id=job_title_id,
        department=department.strip() if department else None,
        employment_status=employment_status.strip().lower() if employment_status else None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_export_job(db: Session, *, job_id: int, user: DemoUser) -> ExportJob | None:
    return db.scalar(
        select(ExportJob).where(
            ExportJob.id == job_id,
            ExportJob.requested_by_email == user.email,
        )
    )


def _employee_query(job: ExportJob):
    filters = [Employee.deleted_at.is_(None)]
    if job.search:
        term = f"%{job.search.strip()}%"
        filters.append(or_(Employee.full_name.ilike(term), Employee.employee_code.ilike(term)))
    if job.country_code:
        filters.append(Employee.country_code == job.country_code.strip().upper())
    if job.job_title_id:
        filters.append(Employee.job_title_id == job.job_title_id)
    if job.department:
        filters.append(Employee.department == job.department.strip())
    if job.employment_status:
        filters.append(Employee.employment_status == job.employment_status.strip().lower())

    sort_column = SORT_COLUMNS.get(job.sort_by, Employee.full_name)
    sort_clause = desc(sort_column) if job.sort_dir == "desc" else asc(sort_column)
    return select(Employee).where(*filters).order_by(sort_clause, Employee.id.asc())


def build_export_workbook(db: Session, job: ExportJob) -> tuple[bytes, int]:
    employees = db.scalars(_employee_query(job)).all()

    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet("Employees")
    sheet.append(
        [
            "Employee Code",
            "Full Name",
            "Job Title",
            "Department",
            "Country",
            "Currency",
            "Annual Salary",
            "Employment Status",
            "Hire Date",
        ]
    )
    for employee in employees:
        sheet.append(
            [
                employee.employee_code,
                employee.full_name,
                employee.job_title.name,
                employee.department,
                employee.country.name,
                employee.country.currency_code,
                float(employee.salary),
                employee.employment_status,
                employee.hired_at.isoformat() if employee.hired_at else "",
            ]
        )

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue(), len(employees)


def _smtp_settings() -> tuple[str, int, str | None, str | None, str, bool]:
    host = os.getenv("SMTP_HOST", "").strip()
    sender = os.getenv("SMTP_FROM", "").strip()
    if not host or not sender:
        raise RuntimeError("Email delivery is not configured: SMTP_HOST and SMTP_FROM are required")

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME") or None
    password = os.getenv("SMTP_PASSWORD") or None
    use_tls = os.getenv("SMTP_USE_TLS", "1").strip().lower() not in {"0", "false", "no"}
    return host, port, username, password, sender, use_tls


def send_export_email(*, recipient_email: str, xlsx_bytes: bytes, row_count: int, filename: str) -> None:
    host, port, username, password, sender, use_tls = _smtp_settings()

    message = EmailMessage()
    message["Subject"] = f"Employee directory export ({row_count:,} rows)"
    message["From"] = sender
    message["To"] = recipient_email
    message.set_content(
        "Your requested employee-directory export is attached. "
        "The spreadsheet reflects the search, filters and sort order active when the export was queued."
    )
    message.add_attachment(
        xlsx_bytes,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )

    with smtplib.SMTP(host, port, timeout=20) as smtp:
        if use_tls:
            smtp.starttls()
        if username:
            smtp.login(username, password or "")
        smtp.send_message(message)


def process_export_job(db: Session, job: ExportJob) -> str:
    """Process one queued export and persist its terminal/retry state.

    Returns one of: sent, retried, failed, skipped.
    """
    if job.status != "queued" or job.attempts >= MAX_EXPORT_ATTEMPTS:
        return "skipped"

    job.status = "processing"
    job.attempts += 1
    job.started_at = datetime.now(timezone.utc)
    job.last_error = None
    db.commit()

    try:
        xlsx_bytes, row_count = build_export_workbook(db, job)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"employee-export-{timestamp}.xlsx"
        send_export_email(
            recipient_email=job.recipient_email,
            xlsx_bytes=xlsx_bytes,
            row_count=row_count,
            filename=filename,
        )
        job.status = "sent"
        job.row_count = row_count
        job.completed_at = datetime.now(timezone.utc)
        result = "sent"
    except Exception as exc:  # worker boundary: persist failure instead of losing the job
        job.last_error = str(exc)[:2000]
        if job.attempts < MAX_EXPORT_ATTEMPTS:
            job.status = "queued"
            result = "retried"
        else:
            job.status = "failed"
            job.completed_at = datetime.now(timezone.utc)
            result = "failed"
    finally:
        db.commit()
        db.refresh(job)

    return result


def process_export_jobs(db: Session, *, limit: int = 3) -> dict[str, int]:
    jobs = db.scalars(
        select(ExportJob)
        .where(ExportJob.status == "queued", ExportJob.attempts < MAX_EXPORT_ATTEMPTS)
        .order_by(ExportJob.created_at.asc(), ExportJob.id.asc())
        .limit(limit)
    ).all()

    sent = 0
    failed = 0
    retried = 0

    for job in jobs:
        result = process_export_job(db, job)
        if result == "sent":
            sent += 1
        elif result == "failed":
            failed += 1
        elif result == "retried":
            retried += 1

    return {"processed": len(jobs), "sent": sent, "retried": retried, "failed": failed}
