from uuid import uuid4

import pytest

from src.academic.domain.entities.deliberation import (
    Deliberation,
    DeliberationDecision,
)


def test_deliberation_can_be_created():
    deliberation = Deliberation(
        student_id=uuid4(),
        average=12,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
    )

    assert deliberation.average == 12
    assert deliberation.failed_subjects == 0


def test_deliberation_rejects_negative_average():
    with pytest.raises(ValueError, match="moyenne"):
        Deliberation(
            student_id=uuid4(),
            average=-1,
            failed_subjects=0,
            decision=DeliberationDecision.FAILED,
        )


def test_deliberation_rejects_negative_failed_subjects():
    with pytest.raises(ValueError, match="matières échouées"):
        Deliberation(
            student_id=uuid4(),
            average=8,
            failed_subjects=-1,
            decision=DeliberationDecision.FAILED,
        )
