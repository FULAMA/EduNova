from uuid import uuid4

import pytest

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.application.use_cases.create_student import CreateStudent
from src.academic.domain.entities.student import Student


class FakeStudentRepository(StudentRepository):
    def __init__(self) -> None:
        self.saved: list[Student] = []

    def list_by_tenant(self, tenant_id):
        return ()

    def get_by_id_and_tenant(self, student_id, tenant_id):
        return None

    def save(self, student: Student) -> None:
        self.saved.append(student)

    def update(self, student: Student) -> None:
        self.saved.append(student)

    def find_by_registration_number(self, tenant_id, registration_number):
        for s in self.saved:
            if s.tenant_id == tenant_id and s.registration_number == registration_number:
                return None
        return None

    def find_potential_duplicates(self, tenant_id, first_name, last_name, exclude_id=None):
        return ()


def test_create_student_persists_trimmed_fields():
    repository = FakeStudentRepository()
    tenant_id = uuid4()

    created = CreateStudent(repository).execute(
        tenant_id,
        first_name="  Ada ",
        last_name=" Lovelace",
        email=" ada@example.test ",
        phone=" ",
    )

    assert created.first_name == "Ada"
    assert created.last_name == "Lovelace"
    assert created.email == "ada@example.test"
    assert created.active is True
    assert repository.saved[0].tenant_id == tenant_id
    assert repository.saved[0].phone is None


def test_create_student_rejects_blank_name():
    with pytest.raises(ValueError, match="prenom"):
        CreateStudent(FakeStudentRepository()).execute(
            uuid4(),
            first_name="   ",
            last_name="Lovelace",
        )


def test_create_student_keeps_creation_non_blocking_and_returns_duplicate_candidates():
    repository = FakeStudentRepository()
    tenant_id = uuid4()
    existing = StudentSummary(
        id=uuid4(), first_name="Ada", last_name="Lovelace", email=None,
        active=True,
    )
    repository.find_potential_duplicates = lambda *_args, **_kwargs: (existing,)

    created = CreateStudent(repository).execute(
        tenant_id, first_name="Ada", last_name="Lovelace"
    )

    assert len(repository.saved) == 1
    assert created.id != existing.id
    assert created.potential_duplicates[0].id == existing.id
