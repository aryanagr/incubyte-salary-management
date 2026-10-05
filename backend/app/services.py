from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Country, Employee, JobTitle
from .schemas import EmployeeCreate, EmployeeUpdate




def _as_money(value) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"))

SORT_COLUMNS = {
    "full_name": Employee.full_name,
    "salary": Employee.salary,
    "hired_at": Employee.hired_at,
    "updated_at": Employee.updated_at,
    "employee_code": Employee.employee_code,
}


def _require_country(db: Session, code: str) -> Country:
    country = db.get(Country, code)
    if not country:
        raise HTTPException(status_code=422, detail={"field": "country_code", "message": "Unknown country"})
    return country


def _require_job_title(db: Session, job_title_id: int) -> JobTitle:
    job_title = db.get(JobTitle, job_title_id)
    if not job_title:
        raise HTTPException(status_code=422, detail={"field": "job_title_id", "message": "Unknown job title"})
    return job_title


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    _require_country(db, data.country_code)
    _require_job_title(db, data.job_title_id)
    employee = Employee(**data.model_dump())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee code already exists") from exc
    db.refresh(employee)
    return employee


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = db.scalar(
        select(Employee).where(Employee.id == employee_id, Employee.deleted_at.is_(None))
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    employee = get_employee(db, employee_id)
    changes = data.model_dump(exclude_unset=True)
    if "country_code" in changes:
        _require_country(db, changes["country_code"])
    if "job_title_id" in changes:
        _require_job_title(db, changes["job_title_id"])
    for field, value in changes.items():
        setattr(employee, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Employee code already exists") from exc
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int) -> None:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee.deleted_at is None:
        employee.deleted_at = datetime.now(timezone.utc)
        db.commit()


def list_employees(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: str | None,
    country_code: str | None,
    job_title_id: int | None,
    department: str | None,
    employment_status: str | None,
    sort_by: str,
    sort_dir: str,
) -> dict:
    filters = [Employee.deleted_at.is_(None)]
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Employee.full_name.ilike(term), Employee.employee_code.ilike(term)))
    if country_code:
        filters.append(Employee.country_code == country_code.strip().upper())
    if job_title_id:
        filters.append(Employee.job_title_id == job_title_id)
    if department:
        filters.append(Employee.department == department.strip())
    if employment_status:
        filters.append(Employee.employment_status == employment_status.strip().lower())

    total_stmt = select(func.count()).select_from(Employee).where(*filters)
    total = int(db.scalar(total_stmt) or 0)

    sort_column = SORT_COLUMNS.get(sort_by, Employee.full_name)
    sort_clause = desc(sort_column) if sort_dir == "desc" else asc(sort_column)
    rows = db.scalars(
        select(Employee)
        .where(*filters)
        .order_by(sort_clause, Employee.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }


def _employee_summary(employee: Employee | None) -> dict | None:
    if not employee:
        return None
    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "full_name": employee.full_name,
        "salary": employee.salary,
    }


def country_insights(db: Session, country_code: str) -> dict:
    country = _require_country(db, country_code.strip().upper())
    aggregate = db.execute(
        select(
            func.count(Employee.id),
            func.min(Employee.salary),
            func.max(Employee.salary),
            func.avg(Employee.salary),
            func.coalesce(func.sum(Employee.salary), 0),
        ).where(Employee.country_code == country.code, Employee.deleted_at.is_(None))
    ).one()
    count, minimum, maximum, average, total = aggregate

    highest = db.scalar(
        select(Employee)
        .where(Employee.country_code == country.code, Employee.deleted_at.is_(None))
        .order_by(Employee.salary.desc(), Employee.id.asc())
        .limit(1)
    )
    lowest = db.scalar(
        select(Employee)
        .where(Employee.country_code == country.code, Employee.deleted_at.is_(None))
        .order_by(Employee.salary.asc(), Employee.id.asc())
        .limit(1)
    )

    breakdown_rows = db.execute(
        select(JobTitle, func.count(Employee.id), func.avg(Employee.salary))
        .join(Employee, Employee.job_title_id == JobTitle.id)
        .where(Employee.country_code == country.code, Employee.deleted_at.is_(None))
        .group_by(JobTitle.id, JobTitle.name)
        .order_by(JobTitle.name.asc())
    ).all()
    return {
        "country": country,
        "employee_count": int(count or 0),
        "min_salary": _as_money(minimum),
        "max_salary": _as_money(maximum),
        "average_salary": _as_money(average),
        "total_payroll": _as_money(total) or Decimal("0.00"),
        "highest_paid_employee": _employee_summary(highest),
        "lowest_paid_employee": _employee_summary(lowest),
        "job_titles": [
            {
                "job_title": job_title,
                "employee_count": int(title_count),
                "average_salary": _as_money(title_average),
            }
            for job_title, title_count, title_average in breakdown_rows
        ],
    }


def job_title_country_insights(db: Session, country_code: str, job_title_id: int) -> dict:
    country = _require_country(db, country_code.strip().upper())
    job_title = _require_job_title(db, job_title_id)
    count, minimum, maximum, average = db.execute(
        select(
            func.count(Employee.id),
            func.min(Employee.salary),
            func.max(Employee.salary),
            func.avg(Employee.salary),
        ).where(
            Employee.country_code == country.code,
            Employee.job_title_id == job_title.id,
            Employee.deleted_at.is_(None),
        )
    ).one()
    return {
        "country": country,
        "job_title": job_title,
        "employee_count": int(count or 0),
        "min_salary": _as_money(minimum),
        "max_salary": _as_money(maximum),
        "average_salary": _as_money(average),
    }
