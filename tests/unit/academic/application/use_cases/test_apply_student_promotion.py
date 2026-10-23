from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from src.academic.application.use_cases.apply_student_promotion import ApplyStudentPromotion
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeAssignments:
    def __init__(self, assignment):
        self.assignment = assignment

    def find_by_id(self, assignment_id, tenant_id):
        return self.assignment if tenant_id == TENANT_ID else None


class FakeDeliberations:
    def __init__(self, deliberation):
        self.deliberation = deliberation

    def find_by_id(self, deliberation_id, tenant_id):
        return self.deliberation if tenant_id == TENANT_ID else None


def test_prepared_deliberation_cannot_trigger_promotion():
    student_id = uuid4()
    source = SimpleNamespace(student_id=student_id, status=StudentAssignmentStatus.ACTIVE)
    deliberation = Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TENANT_ID,
        status="PREPARED",
    )

    use_case = ApplyStudentPromotion(
        FakeAssignments(source),
        FakeDeliberations(deliberation),
        years=SimpleNamespace(),
        classes=SimpleNamespace(),
    )

    with pytest.raises(ValueError, match="ne permet pas"):
        use_case.execute(
            TENANT_ID,
            uuid4(),
            uuid4(),
            uuid4(),
            uuid4(),
            uuid4(),
        )


def test_promotion_rejects_a_deliberation_for_an_obsolete_record():
    student_id = uuid4()
    source = SimpleNamespace(student_id=student_id, status=StudentAssignmentStatus.ACTIVE)
    deliberation = Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TENANT_ID,
        record_version=2,
        status="VALIDATED",
    )
    records = SimpleNamespace(
        find_by_student_and_period=lambda student, period, tenant: SimpleNamespace(version=3)
    )
    use_case = ApplyStudentPromotion(
        FakeAssignments(source),
        FakeDeliberations(deliberation),
        years=SimpleNamespace(),
        classes=SimpleNamespace(),
        records=records,
    )

    with pytest.raises(ValueError, match="change"):
        use_case.execute(TENANT_ID, uuid4(), uuid4(), uuid4(), uuid4(), uuid4())


def test_promotion_rejects_the_source_year_as_target():
    student_id = uuid4()
    year_id = uuid4()
    source = SimpleNamespace(
        student_id=student_id,
        academic_year_id=year_id,
        status=StudentAssignmentStatus.ACTIVE,
    )
    deliberation = Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TENANT_ID,
        status="VALIDATED",
    )
    use_case = ApplyStudentPromotion(
        FakeAssignments(source),
        FakeDeliberations(deliberation),
        years=SimpleNamespace(),
        classes=SimpleNamespace(),
    )

    with pytest.raises(ValueError, match="differente"):
        use_case.execute(TENANT_ID, uuid4(), uuid4(), year_id, uuid4(), uuid4())


def test_promotion_requires_an_active_source_assignment():
    student_id = uuid4()
    source = SimpleNamespace(
        student_id=student_id,
        academic_year_id=uuid4(),
        status=StudentAssignmentStatus.CLOSED,
    )
    deliberation = Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TENANT_ID,
        status="VALIDATED",
    )
    use_case = ApplyStudentPromotion(
        FakeAssignments(source),
        FakeDeliberations(deliberation),
        years=SimpleNamespace(),
        classes=SimpleNamespace(),
    )

    with pytest.raises(ValueError, match="active"):
        use_case.execute(TENANT_ID, uuid4(), uuid4(), uuid4(), uuid4(), uuid4())
