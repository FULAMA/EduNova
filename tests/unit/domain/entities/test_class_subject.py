from uuid import uuid4

import pytest

from src.domain.entities.class_subject import ClassSubject


TENANT_ID = uuid4()


def test_class_subject_can_be_created():
    class_subject_id = uuid4()
    class_id = uuid4()
    subject_id = uuid4()

    class_subject = ClassSubject(
        id=class_subject_id,
        tenant_id=TENANT_ID,
        academic_class_id=class_id,
        subject_id=subject_id,
        coefficient=3,
    )

    assert class_subject.id == class_subject_id
    assert class_subject.tenant_id == TENANT_ID
    assert class_subject.academic_class_id == class_id
    assert class_subject.subject_id == subject_id
    assert class_subject.coefficient == 3
    assert class_subject.active is True


def test_class_subject_coefficient_must_be_positive():
    with pytest.raises(
        ValueError,
        match="Le coefficient doit être supérieur à zéro",
    ):
        ClassSubject(
            id=uuid4(),
            tenant_id=TENANT_ID,
            academic_class_id=uuid4(),
            subject_id=uuid4(),
            coefficient=0,
        )


def test_class_subject_can_be_deactivated():
    class_subject = ClassSubject(
        id=uuid4(),
        tenant_id=TENANT_ID,
        academic_class_id=uuid4(),
        subject_id=uuid4(),
        coefficient=3,
        active=False,
    )

    assert class_subject.active is False


def test_class_subject_can_be_created_without_option():
    class_subject = ClassSubject(
        id=uuid4(),
        tenant_id=TENANT_ID,
        academic_class_id=uuid4(),
        subject_id=uuid4(),
        coefficient=3,
    )

    assert class_subject.academic_option_id is None


def test_class_subject_can_be_assigned_to_option():
    option_id = uuid4()

    class_subject = ClassSubject(
        id=uuid4(),
        tenant_id=TENANT_ID,
        academic_class_id=uuid4(),
        subject_id=uuid4(),
        coefficient=4,
        academic_option_id=option_id,
    )

    assert class_subject.academic_option_id == option_id
