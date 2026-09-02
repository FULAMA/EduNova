from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.presentation.api.dependencies import (
    get_assign_subject_to_class_use_case,
)
from src.presentation.api.schemas.assign_subject_to_class import (
    AssignSubjectToClassRequestSchema,
)
from src.presentation.api.schemas.assign_subject_to_class_response import (
    AssignSubjectToClassResponseSchema,
)


router = APIRouter(
    prefix="/classes",
    tags=["Classes"],
)


@router.post(
    "/{class_id}/subjects",
    response_model=AssignSubjectToClassResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def assign_subject_to_class(
    class_id: UUID,
    data: AssignSubjectToClassRequestSchema,
    use_case=Depends(get_assign_subject_to_class_use_case),
) -> AssignSubjectToClassResponseSchema:

    try:
        result = use_case.execute(
            academic_class_id=class_id,
            subject_id=data.subject_id,
            coefficient=data.coefficient,
            academic_option_id=data.academic_option_id,
        )

    except ValueError as exc:
        message = str(exc)

        if (
            message == "La classe académique n'existe pas"
            or message == "La matière n'existe pas"
            or message == "L'option académique n'appartient pas à cette classe"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        if (
            message == "La matière est déjà assignée à cette classe"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc

    return AssignSubjectToClassResponseSchema(
        id=result.id,
        academic_class_id=result.academic_class_id,
        subject_id=result.subject_id,
        coefficient=result.coefficient,
        academic_option_id=result.academic_option_id,
        active=result.active,
    )
