from uuid import uuid4

import pytest

from src.academic.domain.entities.student import Student


def test_student_can_be_created():
    student_id = uuid4()
    tenant_id = uuid4()

    student = Student(
        id=student_id,
        tenant_id=tenant_id,
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
    )

    assert student.id == student_id
    assert student.tenant_id == tenant_id
    assert student.active is True


def test_student_names_cannot_be_blank():
    with pytest.raises(ValueError, match="prenom"):
        Student(id=uuid4(), tenant_id=uuid4(), first_name="  ", last_name="Lovelace")

    with pytest.raises(ValueError, match="nom"):
        Student(id=uuid4(), tenant_id=uuid4(), first_name="Ada", last_name=" ")
