from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)

    employees: Mapped[list[Employee]] = relationship(back_populates="country")


class JobTitle(Base):
    __tablename__ = "job_titles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)

    employees: Mapped[list[Employee]] = relationship(back_populates="job_title")


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary > 0", name="ck_employee_salary_positive"),
        Index("ix_employees_country_job_title", "country_code", "job_title_id"),
        Index("ix_employees_country_salary", "country_code", "salary"),
        Index("ix_employees_department", "department"),
        Index("ix_employees_status", "employment_status"),
        Index("ix_employees_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    job_title_id: Mapped[int] = mapped_column(ForeignKey("job_titles.id", ondelete="RESTRICT"), nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code", ondelete="RESTRICT"), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    country: Mapped[Country] = relationship(back_populates="employees", lazy="joined")
    job_title: Mapped[JobTitle] = relationship(back_populates="employees", lazy="joined")
