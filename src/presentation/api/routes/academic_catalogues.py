from uuid import UUID
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.use_cases.create_subject import CreateSubject
from src.academic.application.use_cases.create_academic_period import CreateAcademicPeriod
from src.academic.application.use_cases.list_academic_periods import ListAcademicPeriods
from src.academic.application.use_cases.list_subjects import ListSubjects
from src.academic.application.use_cases.update_subject import UpdateSubject
from src.presentation.api.dependencies import (
    get_create_subject_use_case,
    get_list_academic_periods_use_case,
    get_list_subjects_use_case,
    get_update_subject_use_case,
    get_create_academic_period_use_case,
)
from src.presentation.api.dependencies.auth import get_tenant_context, require_role
from src.presentation.api.schemas.subject import (
    AcademicPeriodResponse,
    SubjectInput,
    SubjectResponse,
    SubjectUpdateInput,
    AcademicPeriodInput,
)
from src.shared.application.context.tenant_context import TenantContext

router = APIRouter(prefix="/academic-catalogues", tags=["Academic Catalogues"])


@router.get("/subjects", response_model=list[SubjectResponse], dependencies=[Depends(require_role("ADMIN"))])
def list_subjects(
    search: str | None = Query(default=None, max_length=100),
    use_case: ListSubjects = Depends(get_list_subjects_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute(tenant.tenant_id, search)


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("ADMIN"))])
def create_subject(
    data: SubjectInput,
    use_case: CreateSubject = Depends(get_create_subject_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        return use_case.execute(tenant.tenant_id, data.name, data.code, data.coefficient)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Le code de cette matière existe déjà dans l’établissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/subjects/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_role("ADMIN"))])
def update_subject(
    subject_id: UUID,
    data: SubjectUpdateInput,
    use_case: UpdateSubject = Depends(get_update_subject_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        return use_case.execute(tenant.tenant_id, subject_id, data.name, data.code)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Le code de cette matière existe déjà dans l’établissement.") from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Matière introuvable.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/periods", response_model=list[AcademicPeriodResponse], response_model_exclude_none=True, dependencies=[Depends(require_role("ADMIN"))])
def list_periods(
    use_case: ListAcademicPeriods = Depends(get_list_academic_periods_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute(tenant.tenant_id)


@router.post("/periods", response_model=AcademicPeriodResponse, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("ADMIN"))])
def create_period(
    data: AcademicPeriodInput,
    use_case: CreateAcademicPeriod = Depends(get_create_academic_period_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        return use_case.execute(tenant.tenant_id, data.academic_year_id, data.name,
                                data.start_date, data.end_date)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Cette periode existe deja pour cette annee scolaire.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
