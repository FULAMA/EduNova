from uuid import uuid4

import pytest

from src.application.interfaces.class_option_repository import (
    ClassOptionRepository,
)
from src.application.use_cases.assign_subject_to_class import (
    AssignSubjectToClass,
)
from src.domain.entities.academic_class import AcademicClass
from src.domain.entities.class_option import ClassOption
from src.domain.entities.class_subject import ClassSubject
from src.domain.entities.subject import Subject


class FakeClassSubjectRepository:
    def __init__(self):
        self.items = {}

    def save(self, class_subject: ClassSubject) -> None:
        self.items[class_subject.id] = class_subject

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


class FakeAcademicClassRepository:
    def __init__(self):
        self.items = {}

    def add(self, academic_class):
        self.items[academic_class.id] = academic_class

    def find_by_id(self, academic_class_id):
        return self.items.get(academic_class_id)


class FakeSubjectRepository:
    def __init__(self):
        self.items = {}

    def add(self, subject):
        self.items[subject.id] = subject

    def find_by_id(self, subject_id):
        return self.items.get(subject_id)


class FakeClassOptionRepository(ClassOptionRepository):
    def __init__(self):
        self.items = {}

    def save(self, class_option):
        self.items[class_option.id] = class_option

    def find_by_id(self, class_option_id):
        return self.items.get(class_option_id)

    def find_by_class_and_option(
        self,
        academic_class_id,
        academic_option_id,
    ):
        for item in self.items.values():
            if (
                item.academic_class_id == academic_class_id
                and item.academic_option_id == academic_option_id
                and item.active
            ):
                return item

        return None


def build_use_case(
    class_repository,
    subject_repository,
    class_subject_repository,
    class_option_repository,
):
    return AssignSubjectToClass(
        academic_class_repository=class_repository,
        subject_repository=subject_repository,
        class_subject_repository=class_subject_repository,
        class_option_repository=class_option_repository,
    )


def test_assign_subject_to_class_creates_class_subject():
    class_id = uuid4()
    subject_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    result = use_case.execute(
        academic_class_id=class_id,
        subject_id=subject_id,
        coefficient=3,
    )

    assert isinstance(result, ClassSubject)
    assert result.academic_class_id == class_id
    assert result.subject_id == subject_id
    assert result.coefficient == 3
    assert result.academic_option_id is None

    saved = class_subject_repository.find_by_class_and_option(
        class_id,
        None,
    )

    assert saved == [result]


def test_assign_subject_to_class_fails_if_class_does_not_exist():
    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="La classe académique n'existe pas",
    ):
        use_case.execute(
            academic_class_id=uuid4(),
            subject_id=uuid4(),
            coefficient=3,
        )


def test_assign_subject_to_class_fails_if_subject_does_not_exist():
    class_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="La matière n'existe pas",
    ):
        use_case.execute(
            academic_class_id=class_id,
            subject_id=uuid4(),
            coefficient=3,
        )


def test_assign_subject_to_class_rejects_non_positive_coefficient():
    class_id = uuid4()
    subject_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="Le coefficient doit être supérieur à zéro",
    ):
        use_case.execute(
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=0,
        )


def test_assign_subject_to_class_rejects_duplicate_subject():
    class_id = uuid4()
    subject_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)

    existing = ClassSubject(
        id=uuid4(),
        academic_class_id=class_id,
        subject_id=subject_id,
        coefficient=3,
    )

    class_subject_repository.save(existing)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="La matière est déjà assignée à cette classe",
    ):
        use_case.execute(
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=3,
        )


def test_assign_subject_to_class_rejects_option_not_belonging_to_class():
    class_id = uuid4()
    subject_id = uuid4()
    option_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Mathématiques",
        code="MATH",
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="L'option académique n'appartient pas à cette classe",
    ):
        use_case.execute(
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=3,
            academic_option_id=option_id,
        )
def test_assign_subject_to_class_accepts_valid_option():
    class_id = uuid4()
    subject_id = uuid4()
    option_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Programmation",
        code="PROG",
        coefficient=4,
    )

    class_option = ClassOption(
        id=uuid4(),
        academic_class_id=class_id,
        academic_option_id=option_id,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)
    class_option_repository.save(class_option)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    result = use_case.execute(
        academic_class_id=class_id,
        subject_id=subject_id,
        coefficient=4,
        academic_option_id=option_id,
    )

    assert isinstance(result, ClassSubject)
    assert result.academic_class_id == class_id
    assert result.subject_id == subject_id
    assert result.academic_option_id == option_id
    assert result.coefficient == 4
from src.domain.entities.class_option import ClassOption


def test_assign_subject_to_class_rejects_inactive_option():
    class_id = uuid4()
    subject_id = uuid4()
    option_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        name="Programmation",
        code="PROG",
        coefficient=4,
    )

    inactive_class_option = ClassOption(
        id=uuid4(),
        academic_class_id=class_id,
        academic_option_id=option_id,
        active=False,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)
    class_option_repository.save(inactive_class_option)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="L'option académique n'appartient pas à cette classe",
    ):
        use_case.execute(
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=4,
            academic_option_id=option_id,
        )
