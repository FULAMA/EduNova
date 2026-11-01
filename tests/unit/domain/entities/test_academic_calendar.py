from uuid import uuid4

import pytest

from src.academic.domain.entities.academic_calendar import AcademicCalendar


def test_academic_calendar_is_tenant_scoped():
    tenant_id = uuid4()
    calendar = AcademicCalendar(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Calendrier primaire",
    )

    assert calendar.tenant_id == tenant_id
    assert calendar.name == "Calendrier primaire"
    assert calendar.is_active is True


def test_academic_calendar_rejects_blank_name():
    with pytest.raises(ValueError, match="nom"):
        AcademicCalendar(id=uuid4(), tenant_id=uuid4(), name="  ")


def test_academic_calendar_rejects_non_uuid_tenant():
    with pytest.raises(TypeError, match="tenant"):
        AcademicCalendar(id=uuid4(), tenant_id="tenant-1", name="Calendrier")
