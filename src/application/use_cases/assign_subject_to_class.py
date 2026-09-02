from uuid import UUID, uuid4

from src.application.interfaces.academic_class_repository import (
    AcademicClassRepository,
)
from src.application.interfaces.class_option_repository import (
    ClassOptionRepository,
)
from src.application.interfaces.class_subject_repository import (
    ClassSubjectRepository,
)
from src.application.interfaces.subject_repository import (
    SubjectRepository,
)
from src.domain.entities.class_subject import ClassSubject


class AssignSubjectToClass:

    def __init__(
        self,
        academic_class_repository: AcademicClassRepository,
        subject_repository: SubjectRepository,
        class_subject_repository: ClassSubjectRepository,
        class_option_repository: ClassOptionRepository,
    ):
        self.academic_class_repository = academic_class_repository
        self.subject_repository = subject_repository
        self.class_subject_repository = class_subject_repository
        self.class_option_repository = class_option_repository

    def execute(
        self,
        academic_class_id: UUID,
        subject_id: UUID,
        coefficient: float,
        academic_option_id: UUID | None = None,
    ) -> ClassSubject:

        academic_class = self.academic_class_repository.find_by_id(
            academic_class_id
        )

        if academic_class is None:
            raise ValueError(
                "La classe académique n'existe pas"
            )

        subject = self.subject_repository.find_by_id(subject_id)

        if subject is None:
            raise ValueError(
                "La matière n'existe pas"
            )

        if coefficient <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro"
            )

        if academic_option_id is not None:
            class_option = (
                self.class_option_repository.find_by_class_and_option(
                    academic_class_id,
                    academic_option_id,
                )
            )

            if class_option is None:
                raise ValueError(
                    "L'option académique n'appartient pas à cette classe"
                )

        existing_subjects = (
            self.class_subject_repository.find_by_class_and_option(
                academic_class_id,
                academic_option_id,
            )
        )

        for existing in existing_subjects:
            if existing.subject_id == subject_id:
                raise ValueError(
                    "La matière est déjà assignée à cette classe"
                )

        class_subject = ClassSubject(
            id=uuid4(),
            academic_class_id=academic_class_id,
            subject_id=subject_id,
            coefficient=coefficient,
            academic_option_id=academic_option_id,
        )

        self.class_subject_repository.save(class_subject)

        return class_subject
