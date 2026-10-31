import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from src.academic.application.use_cases.create_academic_calendar import (
    CreateAcademicCalendar,
)
from src.academic.application.use_cases.list_academic_calendars import (
    ListAcademicCalendars,
)
from src.presentation.api.dependencies import (
    get_create_academic_calendar_use_case,
    get_list_academic_calendars_use_case,
)
from src.presentation.api.dependencies.auth import get_tenant_context, require_role
from src.presentation.api.schemas.academic_calendar import (
    AcademicCalendarInput,
    AcademicCalendarResponse,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/academic-calendars", tags=["Academic Calendars"])


@router.get(
    "",
    response_model=list[AcademicCalendarResponse],
    dependencies=[Depends(require_role("ADMIN"))],
)
def list_academic_calendars(
    use_case: ListAcademicCalendars = Depends(get_list_academic_calendars_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[AcademicCalendarResponse]:
    return [
        AcademicCalendarResponse(**calendar.__dict__)
        for calendar in use_case.execute(tenant.tenant_id)
    ]


@router.post(
    "",
    response_model=AcademicCalendarResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def create_academic_calendar(
    data: AcademicCalendarInput,
    use_case: CreateAcademicCalendar = Depends(get_create_academic_calendar_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AcademicCalendarResponse:
    try:
        calendar = use_case.execute(
            tenant.tenant_id, data.name, data.description
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un calendrier portant ce nom existe deja dans cet etablissement.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return AcademicCalendarResponse(**calendar.__dict__)
