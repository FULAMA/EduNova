from datetime import date, datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.report_card import ReportCard
from src.academic.domain.entities.report_card import ReportCardStatus
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus, StudentAcademicRecord
from src.academic.application.use_cases.correct_report_card import CorrectReportCard
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
from src.infrastructure.repositories.sqlite_report_card_repository import SQLiteReportCardRepository
from src.infrastructure.persistence.database import SQLiteDatabase
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID


def test_sqlite_report_card_is_tenant_scoped_and_published_only_for_students():
    container = ApplicationContainer(database_path=":memory:")
    tenant_id = TEST_TENANT_ID
    student_id, period_id, deliberation_id, actor_id = uuid4(), uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(tenant_id), "Test", "Student", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, tenant_id, "Periode test", date(2026, 9, 1), date(2026, 12, 20),
    ))
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id, average=14, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=tenant_id,
        academic_period_id=period_id, record_version=1, id=deliberation_id,
        status="VALIDATED", version=3, created_by=actor_id,
        created_at=datetime.now(timezone.utc), validated_by=actor_id,
        validated_at=datetime.now(timezone.utc),
    ))
    card = ReportCard(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        deliberation_id=deliberation.id, deliberation_version=deliberation.version,
        record_version=1, report_version=1, snapshot={"decision": "ADMITTED"},
        snapshot_hash=ReportCard.calculate_snapshot_hash({"decision": "ADMITTED"}), id=uuid4(), created_at=datetime.now(timezone.utc),
    )
    repository = SQLiteReportCardRepository(container._database)
    repository.save(card)
    assert repository.list_published_for_student(tenant_id, student_id) == ()
    published = repository.publish(card.id, tenant_id, actor_id, datetime.now(timezone.utc))
    assert published.status.value == "ISSUED"
    assert repository.list_published_for_student(tenant_id, student_id)[0].snapshot == {"decision": "ADMITTED"}
    assert repository.list_published_for_student(uuid4(), student_id) == ()
    second = ReportCard(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        deliberation_id=deliberation.id, deliberation_version=deliberation.version,
        record_version=1, report_version=2, snapshot={"decision": "ADMITTED"},
        snapshot_hash=ReportCard.calculate_snapshot_hash({"decision": "ADMITTED"}),
        id=uuid4(), created_at=datetime.now(timezone.utc),
    )
    repository.save(second)
    import pytest
    with pytest.raises(ValueError, match="correction"):
        repository.publish(second.id, tenant_id, actor_id, datetime.now(timezone.utc))


def test_correction_atomically_supersedes_previous_version():
    container = ApplicationContainer(database_path=":memory:")
    tenant_id = TEST_TENANT_ID
    student_id, period_id, actor_id = uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(tenant_id), "Test", "Correction", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, tenant_id, "Periode correction", date(2026, 9, 1), date(2026, 12, 20),
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        subject_results=(), general_average=14, failed_subjects=0,
        credits_obtained=20, total_credits=30, status=AcademicRecordStatus.VALIDATED,
    ))
    deliberations = SQLiteDeliberationRepository(container._database)
    first = deliberations.save(Deliberation(
        student_id=student_id, average=14, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=tenant_id,
        academic_period_id=period_id, record_version=1, id=uuid4(),
        status="VALIDATED", version=2, created_by=actor_id,
        created_at=datetime.now(timezone.utc), validated_by=actor_id,
        validated_at=datetime.now(timezone.utc),
    ))
    second = deliberations.save(Deliberation(
        student_id=student_id, average=15, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=tenant_id,
        academic_period_id=period_id, record_version=1, id=uuid4(),
        status="VALIDATED", version=3, created_by=actor_id,
        created_at=datetime.now(timezone.utc), validated_by=actor_id,
        validated_at=datetime.now(timezone.utc),
    ))
    repository = SQLiteReportCardRepository(container._database)
    previous = ReportCard(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        deliberation_id=first.id, deliberation_version=first.version, record_version=1,
        report_version=1, snapshot={"version": 1}, snapshot_hash=ReportCard.calculate_snapshot_hash({"version": 1}), id=uuid4(),
        status=ReportCardStatus.ISSUED, created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc), issued_by=actor_id,
    )
    repository.save(previous)
    corrected = CorrectReportCard(repository, container.prepare_report_card()).execute(
        tenant_id, previous.id, second.id, actor_id,
    )
    assert corrected.status is ReportCardStatus.ISSUED
    assert corrected.report_version == 2
    assert corrected.previous_report_card_id == previous.id
    assert repository.find_by_id(previous.id, tenant_id).status is ReportCardStatus.SUPERSEDED
    assert repository.list_published_for_student(tenant_id, student_id) == (corrected,)


def test_repository_rejects_a_corrupted_snapshot():
    container = ApplicationContainer(database_path=":memory:")
    tenant_id, student_id, period_id, actor_id = TEST_TENANT_ID, uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(tenant_id), "Test", "Integrity", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, tenant_id, "Periode hash", date(2026, 9, 1), date(2026, 12, 20),
    ))
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id, average=14, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=tenant_id,
        academic_period_id=period_id, record_version=1, id=uuid4(),
        status="VALIDATED", version=2, created_by=actor_id,
        created_at=datetime.now(timezone.utc), validated_by=actor_id,
        validated_at=datetime.now(timezone.utc),
    ))
    repository = SQLiteReportCardRepository(container._database)
    card = ReportCard(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        deliberation_id=deliberation.id, deliberation_version=2, record_version=1,
        report_version=1, snapshot={"value": 1},
        snapshot_hash=ReportCard.calculate_snapshot_hash({"value": 1}), id=uuid4(),
        status=ReportCardStatus.ISSUED, created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc), issued_by=actor_id,
    )
    repository.save(card)
    with container._database.connect() as connection:
        connection.execute("UPDATE report_cards SET snapshot_json=? WHERE id=?", ('{"value": 2}', str(card.id)))
    import pytest
    with pytest.raises(ValueError, match="corrompu"):
        repository.find_by_id(card.id, tenant_id)


def test_concurrent_publication_from_two_sqlite_connections_accepts_one(tmp_path):
    database_path = tmp_path / "report-card-concurrency.db"
    container = ApplicationContainer(database_path=str(database_path))
    tenant_id, student_id, period_id, actor_id = TEST_TENANT_ID, uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(tenant_id), "Test", "Concurrent", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, tenant_id, "Periode concurrente", date(2026, 9, 1), date(2026, 12, 20),
    ))
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id, average=14, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=tenant_id,
        academic_period_id=period_id, record_version=1, id=uuid4(),
        status="VALIDATED", version=1, created_by=actor_id,
        created_at=datetime.now(timezone.utc), validated_by=actor_id,
        validated_at=datetime.now(timezone.utc),
    ))
    card = ReportCard(
        tenant_id=tenant_id, student_id=student_id, academic_period_id=period_id,
        deliberation_id=deliberation.id, deliberation_version=1, record_version=1,
        report_version=1, snapshot={"concurrent": True},
        snapshot_hash=ReportCard.calculate_snapshot_hash({"concurrent": True}), id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )
    SQLiteReportCardRepository(container._database).save(card)

    def publish_from_new_connection():
        repository = SQLiteReportCardRepository(SQLiteDatabase(database_path))
        try:
            return repository.publish(card.id, tenant_id, actor_id, datetime.now(timezone.utc))
        except Exception as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: publish_from_new_connection(), (1, 2)))

    assert sum(not isinstance(result, Exception) for result in results) == 1
    assert sum(isinstance(result, ValueError) for result in results) == 1
