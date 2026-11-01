from fastapi import APIRouter, Depends, HTTPException, status

from src.presentation.api.dependencies import (
    get_school_profile_use_case,
    update_school_profile_use_case,
)
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_role
from src.presentation.api.schemas.school_profile import SchoolProfileInput, SchoolProfileResponse
from src.shared.application.context.tenant_context import TenantContext
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.school.application.use_cases.get_school_profile import GetSchoolProfile
from src.school.application.use_cases.update_school_profile import UpdateSchoolProfile


router = APIRouter(prefix="/school-profile", tags=["School Profile"])


@router.get(
    "", response_model=SchoolProfileResponse | None,
    dependencies=[Depends(require_role("ADMIN", "DIRECTION"))],
)
def get_school_profile(
    use_case: GetSchoolProfile = Depends(get_school_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute(tenant.tenant_id)


@router.put(
    "", response_model=SchoolProfileResponse,
    dependencies=[Depends(require_role("ADMIN", "DIRECTION"))],
)
def put_school_profile(
    data: SchoolProfileInput,
    use_case: UpdateSchoolProfile = Depends(update_school_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    actor: AuthenticatedUser = Depends(get_current_user),
) -> SchoolProfileResponse:
    try:
        profile = use_case.execute(
            tenant.tenant_id, actor.id, **data.model_dump()
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return SchoolProfileResponse.model_validate(profile)
