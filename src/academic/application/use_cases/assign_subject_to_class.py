from uuid import uuid4

from src.academic.application.dto.assign_subject_to_class_request import (
    AssignSubjectToClassRequest,
)
from src.academic.application.dto.assign_subject_to_class_response import (
    AssignSubjectToClassResponse,
)
from src.academic.application.interfaces.academic_class_repository import (
    AcademicClassRepository,
)
from src.academic.application.interfaces.class_option_repository import (
    ClassOptionRepository,
)
from src.academic.application.interfaces.class_subject_repository import (
    ClassSubjectRepository,
)
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.class_subject import ClassSubject


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

    def execute(self, request: AssignSubjectToClassRequest) -> AssignSubjectToClassResponse:
        academic_class = self.academic_class_repository.find_by_id(
            request.academic_class_id,
            request.tenant_id,
        )

        if academic_class is None:
            raise ValueError("La classe académique n'existe pas")

        subject = self.subject_repository.find_by_id(
            request.subject_id,
            request.tenant_id,
        )

        if subject is None:
            raise ValueError("La matière n'existe pas")

        if request.coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à zéro")

        if request.academic_option_id is not None:
            class_option = (
                self.class_option_repository.find_by_class_and_option(
                    request.academic_class_id,
                    request.academic_option_id,
                    request.tenant_id,
                )
            )

            if class_option is None:
                raise ValueError(
                    "L'option académique n'appartient pas à cette classe"
                )

        existing_subjects = (
            self.class_subject_repository.find_by_class_and_option(
                request.academic_class_id,
                request.academic_option_id,
                request.tenant_id,
            )
        )

        for existing in existing_subjects:
            if existing.subject_id == request.subject_id:
                raise ValueError(
                    "La matière est déjà assignée à cette classe"
                )

        class_subject = ClassSubject(
            id=uuid4(),
            tenant_id=request.tenant_id,
            academic_class_id=request.academic_class_id,
            subject_id=request.subject_id,
            coefficient=request.coefficient,
            academic_option_id=request.academic_option_id,
        )

        self.class_subject_repository.save(class_subject)

        return AssignSubjectToClassResponse(
            id=class_subject.id,
            academic_class_id=class_subject.academic_class_id,
            subject_id=class_subject.subject_id,
            coefficient=class_subject.coefficient,
            academic_option_id=class_subject.academic_option_id,
            active=class_subject.active,
        )
