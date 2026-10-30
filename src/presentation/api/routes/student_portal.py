import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.identity.application.use_cases.get_student_portal_profile import GetStudentPortalProfile
from src.identity.application.use_cases.link_student_account import LinkStudentAccount
from src.academic.application.dto.analyze_student_academic_record_request import AnalyzeStudentAcademicRecordRequest
from src.academic.application.use_cases.analyze_student_academic_record import AnalyzeStudentAcademicRecord
from src.academic.application.use_cases.list_student_academic_periods import ListStudentAcademicPeriods
from src.academic.application.use_cases.list_student_attendance import ListStudentAttendance
from src.academic.application.use_cases.get_attendance_statistics import GetAttendanceStatistics
from src.presentation.api.dependencies import (
    get_link_student_account_use_case,
    get_student_portal_profile_use_case,
    get_analyze_student_academic_record_use_case,
    get_list_student_academic_periods_use_case,
    get_list_student_attendance_use_case,
    get_get_attendance_statistics_use_case,
)
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_role
from src.presentation.api.schemas.student_portal import (
    LinkStudentAccountInput,
    StudentPortalResponse,
    StudentPortalAttendanceResponse,
    StudentPortalStudent,
    StudentPortalAssignment,
    StudentPortalYear,
)
from src.presentation.api.schemas.academic_record import AcademicRecordResponse, SubjectResultResponse
from src.presentation.api.schemas.attendance import AttendanceResponse, AttendanceStatisticsResponse
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(tags=["Student Portal"])


@router.post(
    "/student-links",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def link_student_account(
    data: LinkStudentAccountInput,
    use_case: LinkStudentAccount = Depends(get_link_student_account_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, str]:
    try:
        use_case.execute(tenant.tenant_id, data.user_id, data.student_id, current_user.id)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Ce compte ou cet eleve est deja associe.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "linked"}


@router.get(
    "/me/student",
    response_model=StudentPortalResponse,
    dependencies=[Depends(require_role("STUDENT"))],
)
def get_my_student_profile(
    use_case: GetStudentPortalProfile = Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> StudentPortalResponse:
    try:
        profile = use_case.execute(current_user.id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    assignment = profile.assignment
    year = profile.academic_year
    return StudentPortalResponse(
        student=StudentPortalStudent(
            id=profile.student.id,
            first_name=profile.student.first_name,
            last_name=profile.student.last_name,
            email=profile.student.email,
            active=profile.student.active,
        ),
        assignment=StudentPortalAssignment(
            id=assignment.id,
            academic_year_id=assignment.academic_year_id,
            academic_class_id=assignment.academic_class_id,
            status=assignment.status,
            created_at=assignment.created_at,
        ) if assignment else None,
        academic_year=StudentPortalYear(
            id=year.id,
            label=year.label,
            start_date=year.start_date,
            end_date=year.end_date,
            status=year.status,
        ) if year else None,
    )


@router.get(
    "/me/student/academic-periods",
    response_model=list[dict[str, str | None]],
    dependencies=[Depends(require_role("STUDENT"))],
)
def list_my_academic_periods(
    use_case: ListStudentAcademicPeriods = Depends(get_list_student_academic_periods_use_case),
    profile_use_case: GetStudentPortalProfile = Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[dict[str, str | None]]:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [
        {"id": str(period["id"]), "name": str(period["name"]) if period["name"] is not None else None}
        for period in use_case.execute_detailed(profile.student.id, tenant.tenant_id)
    ]


@router.get(
    "/me/student/academic-records/{academic_period_id}",
    response_model=AcademicRecordResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(require_role("STUDENT"))],
)
def get_my_academic_record(
    academic_period_id: UUID,
    use_case: AnalyzeStudentAcademicRecord = Depends(get_analyze_student_academic_record_use_case),
    profile_use_case: GetStudentPortalProfile = Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AcademicRecordResponse:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
        response = use_case.execute(AnalyzeStudentAcademicRecordRequest(
            tenant_id=tenant.tenant_id,
            student_id=profile.student.id,
            academic_period_id=academic_period_id,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AcademicRecordResponse(
        student_id=response.student_id,
        academic_period_id=response.academic_period_id,
        general_average=response.general_average,
        failed_subjects=response.failed_subjects,
        credits_obtained=response.credits_obtained,
        total_credits=response.total_credits,
        subject_results=[
            SubjectResultResponse(
                subject_id=result.subject_id,
                subject_name=(response.subject_names or {}).get(result.subject_id),
                average=result.average,
                coefficient=result.coefficient,
            )
            for result in response.subject_results
        ],
        status=response.status,
        version=response.version,
        academic_period_name=response.academic_period_name,
    )


@router.get(
    "/me/student/attendance/{academic_period_id}",
    response_model=StudentPortalAttendanceResponse,
    dependencies=[Depends(require_role("STUDENT"))],
)
def get_my_attendance(
    academic_period_id: UUID,
    records_use_case: ListStudentAttendance = Depends(get_list_student_attendance_use_case),
    statistics_use_case: GetAttendanceStatistics = Depends(get_get_attendance_statistics_use_case),
    profile_use_case: GetStudentPortalProfile = Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> StudentPortalAttendanceResponse:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    records = records_use_case.execute(
        tenant.tenant_id,
        profile.student.id,
        academic_period_id,
    )
    statistics = statistics_use_case.execute(
        tenant.tenant_id,
        profile.student.id,
        academic_period_id,
    )
    return StudentPortalAttendanceResponse(
        records=[AttendanceResponse(**record.__dict__) for record in records],
        statistics=AttendanceStatisticsResponse(
            total_sessions=int(statistics["total_sessions"]),
            absences=int(statistics["absences"]),
            justified_absences=int(statistics["justified_absences"]),
            unjustified_absences=int(statistics["unjustified_absences"]),
            lates=int(statistics["lates"]),
            attendance_rate=(
                float(statistics["attendance_rate"])
                if statistics["attendance_rate"] is not None else None
            ),
        ),
    )
