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
from src.presentation.api.dependencies.auth import get_tenant_context
from src.shared.application.context.tenant_context import TenantContext
from src.academic.application.dto.assign_subject_to_class_request import (
    AssignSubjectToClassRequest,
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
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> AssignSubjectToClassResponseSchema:

    try:
        result = use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=tenant_context.tenant_id,
                academic_class_id=class_id,
                subject_id=data.subject_id,
                coefficient=data.coefficient,
                academic_option_id=data.academic_option_id,
            )
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

        if message == "La matière est déjà assignée à cette classe":
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