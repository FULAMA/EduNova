from uuid import uuid4

import pytest

from src.domain.entities.subject import Subject


def test_subject_can_be_created():

    subject = Subject(
        id=uuid4(),
        code="MAT-101",
        name="Mathématiques",
        coefficient=4,
        credits=5,
    )

    assert subject.code == "MAT-101"
    assert subject.name == "Mathématiques"
    assert subject.coefficient == 4
    assert subject.credits == 5
    assert subject.is_active is True


def test_subject_can_be_created_without_credits():

    subject = Subject(
        id=uuid4(),
        code="INF-101",
        name="Programmation",
        coefficient=3,
    )

    assert subject.credits == 0


def test_subject_code_cannot_be_empty():

    with pytest.raises(ValueError):
        Subject(
            id=uuid4(),
            code="",
            name="Mathématiques",
            coefficient=4,
        )


def test_subject_name_cannot_be_empty():

    with pytest.raises(ValueError):
        Subject(
            id=uuid4(),
            code="MAT-101",
            name="",
            coefficient=4,
        )


def test_subject_code_is_normalized():

    subject = Subject(
        id=uuid4(),
        code=" mat-101 ",
        name="Mathématiques",
        coefficient=4,
    )

    assert subject.code == "MAT-101"


def test_subject_name_is_normalized():

    subject = Subject(
        id=uuid4(),
        code="MAT-101",
        name="  Mathématiques  ",
        coefficient=4,
    )

    assert subject.name == "Mathématiques"


def test_coefficient_must_be_positive():

    with pytest.raises(ValueError):
        Subject(
            id=uuid4(),
            code="MAT-101",
            name="Mathématiques",
            coefficient=0,
        )


def test_negative_coefficient_is_rejected():

    with pytest.raises(ValueError):
        Subject(
            id=uuid4(),
            code="MAT-101",
            name="Mathématiques",
            coefficient=-2,
        )


def test_credits_cannot_be_negative():

    with pytest.raises(ValueError):
        Subject(
            id=uuid4(),
            code="MAT-101",
            name="Mathématiques",
            coefficient=4,
            credits=-1,
        )


def test_subject_can_be_deactivated():

    subject = Subject(
        id=uuid4(),
        code="MAT-101",
        name="Mathématiques",
        coefficient=4,
    )

    subject.deactivate()

    assert subject.is_active is False


def test_subject_can_be_reactivated():

    subject = Subject(
        id=uuid4(),
        code="MAT-101",
        name="Mathématiques",
        coefficient=4,
    )

    subject.deactivate()
    subject.activate()

    assert subject.is_active is True