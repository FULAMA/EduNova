import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.academic.application.exceptions import ActiveConflictError
from src.academic.application.use_cases.change_academic_year_status import ChangeAcademicYearStatus
from src.academic.application.use_cases.create_academic_year import CreateAcademicYear
from src.academic.application.use_cases.list_academic_years import ListAcademicYears
from src.presentation.api.dependencies import (
    get_change_academic_year_status_use_case,
    get_create_academic_year_use_case,
    get_list_academic_years_use_case,
)
from src.presentation.api.dependencies.auth import get_tenant_context, require_role
from src.presentation.api.schemas.academic_year import AcademicYearInput, AcademicYearResponse
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/academic-years", tags=["Academic Years"])


@router.get("", response_model=list[AcademicYearResponse], dependencies=[Depends(require_role("ADMIN"))])
def list_academic_years(
    use_case: ListAcademicYears = Depends(get_list_academic_years_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[AcademicYearResponse]:
    return [AcademicYearResponse(**year.__dict__) for year in use_case.execute(tenant.tenant_id)]


@router.post("", response_model=AcademicYearResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("ADMIN"))])
def create_academic_year(
    data: AcademicYearInput,
    use_case: CreateAcademicYear = Depends(get_create_academic_year_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AcademicYearResponse:
    try:
        year = use_case.execute(tenant.tenant_id, data.label, data.start_date, data.end_date)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Cette annee scolaire existe deja dans l'etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AcademicYearResponse(**year.__dict__)


@router.post("/{year_id}/activate", response_model=AcademicYearResponse, dependencies=[Depends(require_role("ADMIN"))])
def activate_academic_year(
    year_id: UUID,
    use_case: ChangeAcademicYearStatus = Depends(get_change_academic_year_status_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AcademicYearResponse:
    try:
        year = use_case.activate(year_id, tenant.tenant_id)
    except ActiveConflictError as exc:
        raise HTTPException(status_code=409, detail="Une autre annee est deja active dans cet etablissement.") from exc
    except sqlite3.IntegrityError as exc:
        err_str = str(exc)
        if "academic_years.tenant_id" in err_str or "uq_academic_year_active" in err_str:
            raise HTTPException(status_code=409, detail="Une autre annee est deja active dans cet etablissement.") from exc
        raise HTTPException(status_code=400, detail="Erreur d'integrite des donnees.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AcademicYearResponse(**year.__dict__)
