from datetime import datetime, timezone

from sqlalchemy import func, select

from app.models import Employee
from app.seed import seed_employees


def test_seed_is_deterministic_and_idempotent(db, tmp_path):
    first_names = tmp_path / "first_names.txt"
    last_names = tmp_path / "last_names.txt"
    first_names.write_text("Asha\nRavi\nMaya\n", encoding="utf-8")
    last_names.write_text("Rao\nShah\nPatel\n", encoding="utf-8")

    first = seed_employees(db, count=8, first_names_path=first_names, last_names_path=last_names, batch_size=3)
    second = seed_employees(db, count=8, first_names_path=first_names, last_names_path=last_names, batch_size=3)

    assert first.processed == 8
    assert second.processed == 8
    assert db.scalar(select(func.count()).select_from(Employee)) == 8
    names = db.scalars(select(Employee.full_name).order_by(Employee.employee_code)).all()
    assert names[:3] == ["Asha Rao", "Asha Shah", "Asha Patel"]


def test_seed_can_generate_the_assessment_scale(db, tmp_path):
    first_names = tmp_path / "first_names.txt"
    last_names = tmp_path / "last_names.txt"
    first_names.write_text("\n".join(f"First{i}" for i in range(100)), encoding="utf-8")
    last_names.write_text("\n".join(f"Last{i}" for i in range(100)), encoding="utf-8")

    result = seed_employees(db, count=10_000, first_names_path=first_names, last_names_path=last_names, batch_size=1_000)

    assert result.processed == 10_000
    assert db.scalar(select(func.count()).select_from(Employee)) == 10_000


def test_seed_rerun_restores_soft_deleted_seed_identity(db, tmp_path):
    first_names = tmp_path / "first_names.txt"
    last_names = tmp_path / "last_names.txt"
    first_names.write_text("Asha\n", encoding="utf-8")
    last_names.write_text("Rao\n", encoding="utf-8")

    seed_employees(db, count=1, first_names_path=first_names, last_names_path=last_names)
    employee = db.scalar(select(Employee).where(Employee.employee_code == "EMP-00001"))
    employee.deleted_at = datetime.now(timezone.utc)
    db.commit()

    seed_employees(db, count=1, first_names_path=first_names, last_names_path=last_names)
    restored = db.scalar(select(Employee).where(Employee.employee_code == "EMP-00001"))

    assert db.scalar(select(func.count()).select_from(Employee)) == 1
    assert restored.deleted_at is None
