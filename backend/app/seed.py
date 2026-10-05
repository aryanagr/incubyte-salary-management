from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Country, Employee, JobTitle


COUNTRIES = [
    ("IN", "India", "INR"),
    ("US", "United States", "USD"),
    ("GB", "United Kingdom", "GBP"),
    ("DE", "Germany", "EUR"),
    ("CA", "Canada", "CAD"),
]
JOB_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Engineering Manager",
    "Product Manager",
    "Data Analyst",
    "QA Engineer",
    "UX Designer",
    "HR Business Partner",
]
DEPARTMENTS = ["Engineering", "Product", "Data", "Quality", "Design", "People"]
SALARY_RANGES = {
    "IN": (Decimal("600000"), Decimal("4200000")),
    "US": (Decimal("55000"), Decimal("220000")),
    "GB": (Decimal("35000"), Decimal("140000")),
    "DE": (Decimal("45000"), Decimal("165000")),
    "CA": (Decimal("50000"), Decimal("180000")),
}


@dataclass(frozen=True)
class SeedResult:
    processed: int
    elapsed_seconds: float


def _read_names(path: Path) -> list[str]:
    names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not names:
        raise ValueError(f"No names found in {path}")
    return names


def ensure_reference_data(db: Session) -> None:
    for code, name, currency in COUNTRIES:
        if not db.get(Country, code):
            db.add(Country(code=code, name=name, currency_code=currency))
    existing_titles = set(db.scalars(select(JobTitle.name)).all())
    for title in JOB_TITLES:
        if title not in existing_titles:
            db.add(JobTitle(name=title))
    db.commit()


def _generate_rows(db: Session, count: int, first_names: list[str], last_names: list[str]) -> list[dict]:
    countries = db.scalars(select(Country).order_by(Country.code)).all()
    job_titles = db.scalars(select(JobTitle).order_by(JobTitle.id)).all()
    if not countries or not job_titles:
        raise ValueError("Reference data must exist before seeding employees")

    combos = len(first_names) * len(last_names)
    rows: list[dict] = []
    for index in range(count):
        first = first_names[(index // len(last_names)) % len(first_names)]
        last = last_names[index % len(last_names)]
        # If count exceeds unique name combinations, identity remains unique via code and a deterministic suffix.
        cycle = index // combos
        full_name = f"{first} {last}" if cycle == 0 else f"{first} {last} {cycle + 1}"
        country = countries[index % len(countries)]
        title = job_titles[index % len(job_titles)]
        salary_min, salary_max = SALARY_RANGES.get(country.code, (Decimal("45000"), Decimal("200000")))
        salary_span = int(salary_max - salary_min)
        annual_salary = (salary_min + Decimal((index * 7919) % max(salary_span, 1))).quantize(Decimal("0.01"))
        rows.append(
            {
                "employee_code": f"EMP-{index + 1:05d}",
                "full_name": full_name,
                "job_title_id": title.id,
                "country_code": country.code,
                "salary": annual_salary,
                "department": DEPARTMENTS[index % len(DEPARTMENTS)],
                "employment_status": "active" if index % 20 else "leave",
                "hired_at": date(2015, 1, 1) + timedelta(days=(index * 17) % 3650),
                "deleted_at": None,
            }
        )
    return rows


def _upsert_batch(db: Session, batch: list[dict]) -> None:
    dialect = db.get_bind().dialect.name
    update_columns = {
        "full_name": "excluded.full_name",
        "job_title_id": "excluded.job_title_id",
        "country_code": "excluded.country_code",
        "salary": "excluded.salary",
        "department": "excluded.department",
        "employment_status": "excluded.employment_status",
        "hired_at": "excluded.hired_at",
        "deleted_at": "excluded.deleted_at",
    }
    if dialect == "sqlite":
        stmt = sqlite_insert(Employee).values(batch)
        excluded = stmt.excluded
        stmt = stmt.on_conflict_do_update(
            index_elements=[Employee.employee_code],
            set_={key: getattr(excluded, key) for key in update_columns},
        )
        db.execute(stmt)
    elif dialect == "postgresql":
        stmt = postgres_insert(Employee).values(batch)
        excluded = stmt.excluded
        stmt = stmt.on_conflict_do_update(
            index_elements=[Employee.employee_code],
            set_={key: getattr(excluded, key) for key in update_columns},
        )
        db.execute(stmt)
    else:
        existing = {
            employee.employee_code: employee
            for employee in db.scalars(
                select(Employee).where(Employee.employee_code.in_([row["employee_code"] for row in batch]))
            ).all()
        }
        for row in batch:
            current = existing.get(row["employee_code"])
            if current:
                for field, value in row.items():
                    if field != "employee_code":
                        setattr(current, field, value)
            else:
                db.add(Employee(**row))


def seed_employees(
    db: Session,
    *,
    count: int = 10_000,
    first_names_path: Path,
    last_names_path: Path,
    batch_size: int = 1_000,
) -> SeedResult:
    if count < 1:
        raise ValueError("count must be positive")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    ensure_reference_data(db)
    first_names = _read_names(first_names_path)
    last_names = _read_names(last_names_path)
    rows = _generate_rows(db, count, first_names, last_names)
    start = time.perf_counter()
    for start_index in range(0, len(rows), batch_size):
        _upsert_batch(db, rows[start_index : start_index + batch_size])
        db.commit()
    db.expire_all()
    elapsed = time.perf_counter() - start
    return SeedResult(processed=count, elapsed_seconds=elapsed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed deterministic salary-management employee data")
    data_dir = Path(__file__).resolve().parents[1] / "data"
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    parser.add_argument("--first-names", type=Path, default=data_dir / "first_names.txt")
    parser.add_argument("--last-names", type=Path, default=data_dir / "last_names.txt")
    args = parser.parse_args()

    with SessionLocal() as db:
        result = seed_employees(
            db,
            count=args.count,
            first_names_path=args.first_names,
            last_names_path=args.last_names,
            batch_size=args.batch_size,
        )
    print(f"Seeded/upserted {result.processed} employees in {result.elapsed_seconds:.3f}s")


if __name__ == "__main__":
    main()
