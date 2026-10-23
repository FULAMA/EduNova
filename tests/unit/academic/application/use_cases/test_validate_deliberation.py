from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.academic.application.exceptions import DeliberationConcurrencyError
from src.academic.application.use_cases.validate_deliberation import ValidateDeliberation
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeRecords:
    def __init__(self, record):
        self.record = record

    def find_by_student_and_period(self, student_id, academic_period_id, tenant_id):
        return self.record if tenant_id == TENANT_ID else None


class FakeDeliberations:
    def __init__(self, deliberation):
        self.deliberation = deliberation
        self.validated = None

    def find_by_id(self, deliberation_id, tenant_id):
        return self.deliberation if tenant_id == TENANT_ID else None

    def validate(self, deliberation_id, tenant_id, expected_version, actor_id):
        self.validated = (deliberation_id, tenant_id, expected_version, actor_id)
        return Deliberation(
            **{
                **self.deliberation.__dict__,
                "status": "VALIDATED",
                "version": self.deliberation.version + 1,
                "validated_by": actor_id,
                "validated_at": datetime.now(timezone.utc),
            }
        )


def make_record(student_id, period_id, version=3):
    return type("Record", (), {
        "student_id": student_id,
        "academic_period_id": period_id,
        "status": AcademicRecordStatus.VALIDATED,
        "version": version,
    })()


def make_deliberation(student_id, period_id, record_version=3):
    return Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TENANT_ID,
        academic_period_id=period_id,
        record_version=record_version,
        id=uuid4(),
    )


def test_validate_deliberation_records_actor_and_increments_version():
    student_id, period_id, actor_id = uuid4(), uuid4(), uuid4()
    deliberations = FakeDeliberations(make_deliberation(student_id, period_id))
    result = ValidateDeliberation(
        deliberations, FakeRecords(make_record(student_id, period_id))
    ).execute(TENANT_ID, deliberations.deliberation.id, 1, actor_id)

    assert result.status == "VALIDATED"
    assert result.version == 2
    assert result.validated_by == actor_id
    assert deliberations.validated == (
        deliberations.deliberation.id, TENANT_ID, 1, actor_id
    )


def test_validate_deliberation_rejects_stale_record():
    student_id, period_id = uuid4(), uuid4()
    deliberations = FakeDeliberations(make_deliberation(student_id, period_id, 2))

    with pytest.raises(DeliberationConcurrencyError):
        ValidateDeliberation(
            deliberations, FakeRecords(make_record(student_id, period_id, 3))
        ).execute(TENANT_ID, deliberations.deliberation.id, 1, uuid4())
