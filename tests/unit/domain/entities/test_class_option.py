from uuid import uuid4

from src.academic.domain.entities.class_option import ClassOption


TENANT_ID = uuid4()


def test_class_option_can_be_created():
    class_option_id = uuid4()
    class_id = uuid4()
    option_id = uuid4()

    class_option = ClassOption(
        id=class_option_id,
        tenant_id=TENANT_ID,
        academic_class_id=class_id,
        academic_option_id=option_id,
    )

    assert class_option.id == class_option_id
    assert class_option.tenant_id == TENANT_ID
    assert class_option.academic_class_id == class_id
    assert class_option.academic_option_id == option_id
    assert class_option.active is True


def test_class_option_can_be_deactivated():
    class_option = ClassOption(
        id=uuid4(),
        tenant_id=TENANT_ID,
        academic_class_id=uuid4(),
        academic_option_id=uuid4(),
        active=False,
    )

    assert class_option.active is False

