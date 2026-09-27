from uuid import uuid4

import pytest

from src.academic.domain.entities.academic_class import AcademicClass


TENANT_ID = uuid4()


def test_academic_class_can_be_created():
    class_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        tenant_id=TENANT_ID,
        name="6e Scientifique",
    )

    assert academic_class.id == class_id
    assert academic_class.tenant_id == TENANT_ID
    assert academic_class.name == "6e Scientifique"
    assert academic_class.active is True


def test_academic_class_name_cannot_be_empty():
    with pytest.raises(
        ValueError,
        match="Le nom de la classe ne peut pas être vide",
    ):
        AcademicClass(
            id=uuid4(),
            tenant_id=TENANT_ID,
            name="   ",
        )


def test_academic_class_can_be_deactivated():
    academic_class = AcademicClass(
        id=uuid4(),
        tenant_id=TENANT_ID,
        name="6e Scientifique",
        active=False,
    )

    assert academic_class.active is False
