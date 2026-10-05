from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Employee
from app.seed import seed_employees


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory) / "benchmark.db"
        engine = create_engine(f"sqlite+pysqlite:///{db_path}")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
        data_dir = Path(__file__).resolve().parents[1] / "data"
        with SessionLocal() as db:
            first = seed_employees(
                db,
                count=10_000,
                first_names_path=data_dir / "first_names.txt",
                last_names_path=data_dir / "last_names.txt",
                batch_size=1_000,
            )
            second = seed_employees(
                db,
                count=10_000,
                first_names_path=data_dir / "first_names.txt",
                last_names_path=data_dir / "last_names.txt",
                batch_size=1_000,
            )
            total = db.scalar(select(func.count()).select_from(Employee))
        print(f"first_run_seconds={first.elapsed_seconds:.3f}")
        print(f"second_run_seconds={second.elapsed_seconds:.3f}")
        print(f"employee_count_after_rerun={total}")


if __name__ == "__main__":
    main()
