from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


EMPLOYMENT_STATUSES = {"active", "leave", "terminated"}


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    currency_code: str


class JobTitleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class EmployeeBase(BaseModel):
    employee_code: str = Field(min_length=1, max_length=24)
    full_name: str = Field(min_length=1, max_length=160)
    job_title_id: int = Field(gt=0)
    country_code: str = Field(min_length=2, max_length=2)
    salary: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    department: str = Field(min_length=1, max_length=100)
    employment_status: str = "active"
    hired_at: date | None = None

    @field_validator("employee_code", mode="before")
    @classmethod
    def normalize_employee_code(cls, value: str) -> str:
        return normalize_text(value).upper()

    @field_validator("full_name", "department", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return normalize_text(value)

    @field_validator("country_code", mode="before")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("employment_status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in EMPLOYMENT_STATUSES:
            raise ValueError(f"employment_status must be one of {sorted(EMPLOYMENT_STATUSES)}")
        return normalized

    @field_validator("salary")
    @classmethod
    def normalize_salary(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: str | None = Field(default=None, min_length=1, max_length=24)
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    job_title_id: int | None = Field(default=None, gt=0)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    salary: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    department: str | None = Field(default=None, min_length=1, max_length=100)
    employment_status: str | None = None
    hired_at: date | None = None

    @field_validator("employee_code", mode="before")
    @classmethod
    def normalize_optional_employee_code(cls, value: str | None) -> str | None:
        return None if value is None else normalize_text(value).upper()

    @field_validator("full_name", "department", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        return None if value is None else normalize_text(value)

    @field_validator("country_code", mode="before")
    @classmethod
    def normalize_optional_country(cls, value: str | None) -> str | None:
        return None if value is None else value.strip().upper()

    @field_validator("employment_status")
    @classmethod
    def validate_optional_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in EMPLOYMENT_STATUSES:
            raise ValueError(f"employment_status must be one of {sorted(EMPLOYMENT_STATUSES)}")
        return normalized

    @field_validator("salary")
    @classmethod
    def normalize_optional_salary(cls, value: Decimal | None) -> Decimal | None:
        return None if value is None else value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        nullable_only = {"hired_at"}
        for field_name in self.model_fields_set:
            if field_name not in nullable_only and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    full_name: str
    country: CountryOut
    job_title: JobTitleOut
    salary: Decimal
    department: str
    employment_status: str
    hired_at: date | None
    created_at: datetime
    updated_at: datetime


class PaginatedEmployees(BaseModel):
    items: list[EmployeeOut]
    total: int
    page: int
    page_size: int
    pages: int


class ReferenceDataOut(BaseModel):
    countries: list[CountryOut]
    job_titles: list[JobTitleOut]
    employment_statuses: list[str]


class EmployeeSummary(BaseModel):
    id: int
    employee_code: str
    full_name: str
    salary: Decimal


class JobTitleInsight(BaseModel):
    job_title: JobTitleOut
    employee_count: int
    average_salary: Decimal | None


class CountryInsight(BaseModel):
    country: CountryOut
    employee_count: int
    min_salary: Decimal | None
    max_salary: Decimal | None
    average_salary: Decimal | None
    total_payroll: Decimal
    highest_paid_employee: EmployeeSummary | None
    lowest_paid_employee: EmployeeSummary | None
    job_titles: list[JobTitleInsight]


class JobTitleCountryInsight(BaseModel):
    country: CountryOut
    job_title: JobTitleOut
    employee_count: int
    min_salary: Decimal | None
    max_salary: Decimal | None
    average_salary: Decimal | None


SortDirection = Literal["asc", "desc"]
