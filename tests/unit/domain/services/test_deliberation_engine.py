from uuid import uuid4

from src.domain.entities.deliberation import (
    DeliberationDecision,
)
from src.domain.policies.academic_policy import AcademicPolicy
from src.domain.services.deliberation_engine import (
    DeliberationEngine,
)


def test_student_is_admitted_with_passing_average():

    student_id = uuid4()

    policy = AcademicPolicy()

    engine = DeliberationEngine(policy)

    result = engine.deliberate(
        student_id=student_id,
        average=12,
        failed_subjects=0,
    )

    assert result.decision == DeliberationDecision.ADMITTED


def test_student_is_failed_with_low_average_and_too_many_failed_subjects():

    student_id = uuid4()

    policy = AcademicPolicy(
        max_failed_subjects=2,
    )

    engine = DeliberationEngine(policy)

    result = engine.deliberate(
        student_id=student_id,
        average=8,
        failed_subjects=3,
    )

    assert result.decision == DeliberationDecision.FAILED


def test_student_can_be_conditional():

    student_id = uuid4()

    policy = AcademicPolicy(
        passing_average=10,
        max_failed_subjects=2,
    )

    engine = DeliberationEngine(policy)

    result = engine.deliberate(
        student_id=student_id,
        average=9,
        failed_subjects=2,
    )

    assert result.decision == DeliberationDecision.CONDITIONAL