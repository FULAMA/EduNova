import pytest
from datetime import date
from uuid import uuid4

from src.academic.domain.entities.academic_period import AcademicPeriod


def test_academic_period_can_be_created():

    period = AcademicPeriod(
        id=uuid4(),
        name="Semestre 1",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 1, 31),
    )

    assert period.name == "Semestre 1"


def test_period_end_date_must_be_after_start_date():

    with pytest.raises(ValueError):

        AcademicPeriod(
            id=uuid4(),
            name="Semestre 1",
            start_date=date(2027, 1, 31),
            end_date=date(2026, 9, 1),
        )


def test_period_name_cannot_be_empty():

    with pytest.raises(ValueError):

        AcademicPeriod(
            id=uuid4(),
            name="   ",
            start_date=date(2026, 9, 1),
            end_date=date(2027, 1, 31),
        )


def test_period_contains_date():

    period = AcademicPeriod(
        id=uuid4(),
        name="Semestre 1",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 1, 31),
    )

    assert period.contains(date(2026, 10, 15)) is True


def test_period_does_not_contain_date_outside_range():

    period = AcademicPeriod(
        id=uuid4(),
        name="Semestre 1",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 1, 31),
    )

    assert period.contains(date(2027, 2, 1)) is False
