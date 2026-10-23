from datetime import date
import sqlite3
from uuid import uuid4

import pytest

from src.academic.domain.entities.subject import Subject
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.infrastructure.repositories.sqlite_academic_year_repository import SQLiteAcademicYearRepository
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_period_repository import (
    SQLiteAcademicPeriodRepository,
)
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)


def test_subject_catalogue_is_tenant_scoped_searchable_and_persistent(tmp_path):
    database = SQLiteDatabase(tmp_path / "catalogue.db")
    database.initialize()
    repository = SQLiteSubjectRepository(database)
    tenant, other_tenant = uuid4(), uuid4()
    subject = Subject(uuid4(), tenant, "Mathématiques", "MATH", 2)
    repository.save(subject)
    repository.save(Subject(uuid4(), other_tenant, "Mathématiques", "MATH", 1))

    assert repository.list_by_tenant(tenant, "math") == [subject]
    assert repository.list_by_tenant(tenant, "physique") == []
    assert repository.find_many_by_ids({subject.id}, other_tenant) == {}

    changed = Subject(subject.id, tenant, "Maths", "MATH", 3)
    repository.update(changed)
    assert SQLiteSubjectRepository(database).find_by_id(subject.id, tenant) == changed


def test_academic_period_catalogue_is_scoped_by_tenant(tmp_path):
    database = SQLiteDatabase(tmp_path / "periods.db")
    database.initialize()
    tenant, other_tenant, period_id = uuid4(), uuid4(), uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (str(period_id), str(tenant), "Trimestre 1", "2026-09-01", "2026-12-20"),
        )
    repository = SQLiteAcademicPeriodRepository(database)
    assert repository.find_by_id(period_id, tenant).name == "Trimestre 1"
    assert repository.find_by_id(period_id, other_tenant) is None
    assert repository.list_by_tenant(other_tenant) == []


def test_academic_period_roundtrips_school_year_without_rewriting_historical_rows(tmp_path):
    database = SQLiteDatabase(tmp_path / "period-year.db")
    database.initialize()
    tenant, year_id = uuid4(), uuid4()
    SQLiteAcademicYearRepository(database).save(AcademicYear(
        year_id, tenant, "2026-2027", date(2026, 9, 1), date(2027, 6, 30), AcademicYearStatus.DRAFT,
    ))
    historical_id = uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (str(historical_id), str(tenant), "Historique", "2025-09-01", "2025-12-20"),
        )
    period = AcademicPeriod(uuid4(), tenant, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20), year_id)
    repository = SQLiteAcademicPeriodRepository(database)
    repository.save(period)

    assert repository.find_by_id(period.id, tenant) == period
    with database.connect() as connection:
        historical = connection.execute(
            "SELECT academic_year_id FROM academic_periods WHERE id = ?", (str(historical_id),)
        ).fetchone()
    assert historical[0] is None

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(AcademicPeriod(uuid4(), uuid4(), "Wrong tenant", date(2026, 9, 1), date(2026, 12, 20), year_id))
