import pytest
from uuid import uuid4

from src.school.domain.entities.school_profile import SchoolProfile


def test_school_profile_requires_legal_and_display_names():
    with pytest.raises(ValueError):
        SchoolProfile(tenant_id=uuid4(), legal_name=" ", display_name="School")


def test_school_profile_normalizes_optional_blank_values():
    profile = SchoolProfile(
        tenant_id=uuid4(), legal_name="École Exemple",
        display_name="Exemple", address=" ", email="contact@example.org",
    )
    assert profile.address is None
    assert profile.email == "contact@example.org"


def test_school_profile_rejects_invalid_email():
    with pytest.raises(ValueError):
        SchoolProfile(tenant_id=uuid4(), legal_name="École", display_name="École", email="invalid")
