from uuid import UUID, uuid4

import pytest

from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.infrastructure.repositories.in_memory_student_academic_record_repository import (
    InMemoryStudentAcademicRecordRepository,
)


def test_in_memory_repository_implements_repository_contract():
    repository = InMemoryStudentAcademicRecordRepository()

    assert isinstance(
        repository,
        StudentAcademicRecordRepository,
    )


def test_repository_contract_requires_save():
    assert "save" in StudentAcademicRecordRepository.__abstractmethods__


def test_repository_contract_requires_find_by_student():
    assert (
        "find_by_student"
        in StudentAcademicRecordRepository.__abstractmethods__
    )


def test_repository_contract_requires_find_by_student_and_period():
    assert (
        "find_by_student_and_period"
        in StudentAcademicRecordRepository.__abstractmethods__
    )


def test_repository_contract_is_abstract():
    with pytest.raises(TypeError):
        StudentAcademicRecordRepository()


def test_repository_methods_have_expected_signatures():
    save = StudentAcademicRecordRepository.save
    find_by_student = StudentAcademicRecordRepository.find_by_student
    find_by_student_and_period = (
        StudentAcademicRecordRepository.find_by_student_and_period
    )

    assert save.__annotations__["record"] is not None
    assert find_by_student.__annotations__["student_id"] is UUID
    assert find_by_student_and_period.__annotations__["student_id"] is UUID
    assert (
        find_by_student_and_period.__annotations__["academic_period_id"]
        is UUID
    )
