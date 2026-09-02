from uuid import uuid4

import pytest

from src.domain.entities.academic_option import AcademicOption


def test_academic_option_can_be_created():
    option_id = uuid4()

    option = AcademicOption(
        id=option_id,
        name="Informatique",
        code="INFO",
    )

    assert option.id == option_id
    assert option.name == "Informatique"
    assert option.code == "INFO"
    assert option.active is True


def test_academic_option_name_cannot_be_empty():
    with pytest.raises(
        ValueError,
        match="Le nom de l'option ne peut pas être vide",
    ):
        AcademicOption(
            id=uuid4(),
            name="   ",
            code="INFO",
        )


def test_academic_option_code_cannot_be_empty():
    with pytest.raises(
        ValueError,
        match="Le code de l'option ne peut pas être vide",
    ):
        AcademicOption(
            id=uuid4(),
            name="Informatique",
            code="   ",
        )


def test_academic_option_can_be_deactivated():
    option = AcademicOption(
        id=uuid4(),
        name="Informatique",
        code="INFO",
        active=False,
    )

    assert option.active is False
