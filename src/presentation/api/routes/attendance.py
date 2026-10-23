import sqlite3
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.use_cases.get_attendance_statistics import GetAttendanceStatistics
from src.academic.application.use_cases.list_class_attendance import ListClassAttendance
from src.academic.application.use_cases.record_attendance import RecordAttendance
from src.academic.application.use_cases.correct_attendance import CorrectAttendance
from src.academic.application.use_cases.list_student_attendance import ListStudentAttendance
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_get_attendance_statistics_use_case,
    get_list_class_attendance_use_case,
    get_record_attendance_use_case,
    get_correct_attendance_use_case,
    get_list_student_attendance_use_case,
)
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_role
from src.presentation.api.schemas.attendance import (
    AttendanceInput, AttendanceResponse, AttendanceRosterEntryResponse, AttendanceStatisticsResponse,
    AttendanceCorrectionInput,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/attendance", tags=["Attendance"])
_admin = [Depends(require_role("ADMIN"))]


@router.get("/roster", response_model=list[AttendanceRosterEntryResponse], dependencies=_admin)
def attendance_roster(
    academic_class_id: UUID,
    academic_period_id: UUID,
    attendance_date: date,
    use_case: ListClassAttendance = Depends(get_list_class_attendance_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        rows = use_case.execute(tenant.tenant_id, academic_class_id, academic_period_id, attendance_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [AttendanceRosterEntryResponse(**row.__dict__) for row in rows]


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED, dependencies=_admin)
def record_attendance(
    data: AttendanceInput,
    use_case: RecordAttendance = Depends(get_record_attendance_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        result = use_case.execute(
            tenant.tenant_id, data.student_id, data.academic_class_id,
            data.academic_year_id, data.academic_period_id, data.attendance_date,
            data.status, data.justified, current_user.id,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Un relevé existe déjà pour cet élève et cette date.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AttendanceResponse(**result.__dict__)


@router.get("/students/{student_id}/statistics", response_model=AttendanceStatisticsResponse, dependencies=_admin)
def attendance_statistics(
    student_id: UUID,
    academic_period_id: UUID = Query(...),
    use_case: GetAttendanceStatistics = Depends(get_get_attendance_statistics_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute(tenant.tenant_id, student_id, academic_period_id)


@router.get("/students/{student_id}/records", response_model=list[AttendanceResponse], dependencies=_admin)
def student_attendance_records(
    student_id: UUID,
    academic_period_id: UUID = Query(...),
    use_case: ListStudentAttendance = Depends(get_list_student_attendance_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return [
        AttendanceResponse(**entry.__dict__)
        for entry in use_case.execute(tenant.tenant_id, student_id, academic_period_id)
    ]


@router.put("/{attendance_id}", response_model=AttendanceResponse, dependencies=_admin)
def correct_attendance(
    attendance_id: UUID,
    data: AttendanceCorrectionInput,
    use_case: CorrectAttendance = Depends(get_correct_attendance_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        result = use_case.execute(
            tenant.tenant_id, attendance_id, data.status, data.justified,
            data.expected_version, current_user.id,
        )
    except ValueError as exc:
        detail = str(exc)
        code = 409 if "modifi" in detail else 400
        raise HTTPException(status_code=code, detail=detail) from exc
    return AttendanceResponse(**result.__dict__)
