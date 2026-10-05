from __future__ import annotations

from fastapi import Depends, FastAPI, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Country, JobTitle
from .schemas import (
    CountryInsight,
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    JobTitleCountryInsight,
    PaginatedEmployees,
    ReferenceDataOut,
)
from .services import (
    country_insights,
    create_employee,
    delete_employee,
    get_employee,
    job_title_country_insights,
    list_employees,
    update_employee,
)

app = FastAPI(title="Salary Management API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/reference-data", response_model=ReferenceDataOut)
def reference_data(db: Session = Depends(get_db)) -> dict:
    return {
        "countries": db.scalars(select(Country).order_by(Country.name)).all(),
        "job_titles": db.scalars(select(JobTitle).order_by(JobTitle.name)).all(),
        "employment_statuses": ["active", "leave", "terminated"],
    }


@app.post("/api/v1/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(data: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, data)


@app.get("/api/v1/employees", response_model=PaginatedEmployees)
def list_employees_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=500),
    search: str | None = Query(None, max_length=160),
    country_code: str | None = Query(None, min_length=2, max_length=2),
    job_title_id: int | None = Query(None, gt=0),
    department: str | None = Query(None, max_length=100),
    employment_status: str | None = Query(None, max_length=20),
    sort_by: str = Query("full_name", pattern="^(full_name|salary|hired_at|updated_at|employee_code)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    return list_employees(
        db,
        page=page,
        page_size=page_size,
        search=search,
        country_code=country_code,
        job_title_id=job_title_id,
        department=department,
        employment_status=employment_status,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@app.get("/api/v1/employees/{employee_id}", response_model=EmployeeOut)
def get_employee_endpoint(employee_id: int, db: Session = Depends(get_db)):
    return get_employee(db, employee_id)


@app.patch("/api/v1/employees/{employee_id}", response_model=EmployeeOut)
def update_employee_endpoint(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    return update_employee(db, employee_id, data)


@app.delete("/api/v1/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_endpoint(employee_id: int, db: Session = Depends(get_db)) -> Response:
    delete_employee(db, employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/insights/countries/{country_code}", response_model=CountryInsight)
def country_insights_endpoint(country_code: str, db: Session = Depends(get_db)):
    return country_insights(db, country_code)


@app.get(
    "/api/v1/insights/countries/{country_code}/job-titles/{job_title_id}",
    response_model=JobTitleCountryInsight,
)
def job_title_country_insights_endpoint(country_code: str, job_title_id: int, db: Session = Depends(get_db)):
    return job_title_country_insights(db, country_code, job_title_id)
