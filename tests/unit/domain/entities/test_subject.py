from uuid import uuid4

import pytest

from src.domain.entities.subject import Subject


TENANT_ID = uuid4()


def test_subject_can_be_created():
    subject_id = uuid4()

    subject = Subject(
        id=subject_id,
        tenant_id=TENANT_ID,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
    )

    assert subject.id == subject_id
    assert subject.tenant_id == TENANT_ID
    assert subject.name == "Mathématiques"
    assert subject.code == "MATH"
    assert subject.coefficient == 3
    assert subject.active is True


def test_subject_name_cannot_be_empty():
    with pytest.raises(
        ValueError,
        match="Le nom de la matière ne peut pas être vide",
    ):
        Subject(
            id=uuid4(),
            tenant_id=TENANT_ID,
            name="   ",
            code="MATH",
            coefficient=3,
        )


def test_subject_code_cannot_be_empty():
    with pytest.raises(
        ValueError,
        match="Le code de la matière ne peut pas être vide",
    ):
        Subject(
            id=uuid4(),
            tenant_id=TENANT_ID,
            name="Mathématiques",
            code="   ",
            coefficient=3,
        )


def test_subject_coefficient_must_be_positive():
    with pytest.raises(
        ValueError,
        match="Le coefficient doit être supérieur à zéro",
    ):
        Subject(
            id=uuid4(),
            tenant_id=TENANT_ID,
            name="Mathématiques",
            code="MATH",
            coefficient=0,
        )


def test_subject_can_be_deactivated():
    subject = Subject(
        id=uuid4(),
        tenant_id=TENANT_ID,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        active=False,
    )

    assert subject.active is False
