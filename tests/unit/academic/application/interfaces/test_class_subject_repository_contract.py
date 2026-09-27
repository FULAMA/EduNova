from src.academic.application.interfaces.class_subject_repository import (
    ClassSubjectRepository,
)


class FakeClassSubjectRepository(ClassSubjectRepository):
    def save(self, class_subject):
        pass

    def find_by_id(self, class_subject_id):
        return None

    def find_by_class(self, academic_class_id):
        return []

    def find_by_class_and_option(
        self,
        academic_class_id,
        academic_option_id,
    ):
        return []


def test_fake_repository_implements_contract():
    repository = FakeClassSubjectRepository()

    assert isinstance(repository, ClassSubjectRepository)
