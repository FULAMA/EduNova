from uuid import uuid4

from src.domain.entities.class_subject import ClassSubject


class FakeClassSubjectRepository:
    def __init__(self):
        self.items = {}

    def save(self, class_subject: ClassSubject) -> None:
        self.items[class_subject.id] = class_subject

    def find_by_id(self, class_subject_id):
        return self.items.get(class_subject_id)

    def find_by_class(self, academic_class_id):
        return [
            item
            for item in self.items.values()
            if item.academic_class_id == academic_class_id
        ]

    def find_by_class_and_option(
        self,
        academic_class_id,
        academic_option_id,
    ):
        return [
            item
            for item in self.items.values()
            if (
                item.academic_class_id == academic_class_id
                and item.academic_option_id == academic_option_id
            )
        ]


def test_save_and_find_by_id():
    repository = FakeClassSubjectRepository()

    class_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=uuid4(),
        subject_id=uuid4(),
        coefficient=3,
    )

    repository.save(class_subject)

    assert repository.find_by_id(class_subject.id) == class_subject


def test_find_by_class_returns_only_subjects_of_class():
    repository = FakeClassSubjectRepository()

    class_id = uuid4()
    other_class_id = uuid4()

    subject_1 = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=uuid4(),
        coefficient=3,
    )

    subject_2 = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=uuid4(),
        coefficient=2,
    )

    other_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=other_class_id,
        subject_id=uuid4(),
        coefficient=4,
    )

    repository.save(subject_1)
    repository.save(subject_2)
    repository.save(other_subject)

    result = repository.find_by_class(class_id)

    assert result == [subject_1, subject_2]


def test_find_by_class_and_option_returns_only_option_subjects():
    repository = FakeClassSubjectRepository()

    class_id = uuid4()
    option_info_id = uuid4()
    option_math_id = uuid4()

    info_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=uuid4(),
        coefficient=4,
        academic_option_id=option_info_id,
    )

    math_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=uuid4(),
        coefficient=3,
        academic_option_id=option_math_id,
    )

    common_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=uuid4(),
        coefficient=2,
    )

    repository.save(info_subject)
    repository.save(math_subject)
    repository.save(common_subject)

    result = repository.find_by_class_and_option(
        class_id,
        option_info_id,
    )

    assert result == [info_subject]
