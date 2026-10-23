from datetime import date
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.academic.domain.entities.attendance import Attendance
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_analyze_student_academic_risk_use_case,
    get_correct_attendance_use_case,
    get_get_attendance_statistics_use_case,
    get_record_attendance_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_membership_repository,
    get_tenant_context,
)
from src.presentation.api.routes.attendance import router
from src.presentation.api.routes.academic_risk import router as risk_router
from src.shared.application.context.tenant_context import TenantContext


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_ID = UUID("00000000-0000-0000-0000-000000000002")


class Membership:
    def __init__(self, role: str):
        self.role = role
        self.active = True


class MembershipRepository:
    def __init__(self, role: str):
        self.membership = Membership(role)

    def find_by_user_and_tenant(self, user_id: UUID, tenant_id: UUID) -> Membership:
        return self.membership


class RecordUseCase:
    def __init__(self):
        self.calls: list[tuple[UUID, UUID]] = []

    def execute(self, tenant_id, student_id, academic_class_id, academic_year_id,
                academic_period_id, attendance_date, status, justified, actor_id):
        self.calls.append((tenant_id, actor_id))
        return Attendance(
            uuid4(), tenant_id, student_id, academic_class_id, academic_year_id,
            academic_period_id, attendance_date, status, justified, actor_id,
        )


class StatisticsUseCase:
    def execute(self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID):
        return {"total_sessions": 1, "absences": 0, "justified_absences": 0,
                "unjustified_absences": 0, "lates": 0, "attendance_rate": 100}


class CorrectionUseCase:
    def execute(self, tenant_id, attendance_id, status, justified, expected_version, changed_by):
        return Attendance(
            attendance_id, tenant_id, uuid4(), uuid4(), uuid4(), uuid4(),
            date(2026, 10, 19), status, justified, uuid4(), expected_version + 1,
        )


class RiskUseCase:
    def execute(self, tenant_id, student_id, academic_period_id):
        from src.academic.application.dto.analyze_academic_risk_response import AnalyzeAcademicRiskResponse
        return AnalyzeAcademicRiskResponse("LOW", 0, ("Calcul serveur",))


def make_client(role: str = "ADMIN") -> tuple[TestClient, RecordUseCase, StatisticsUseCase]:
    app = FastAPI()
    app.include_router(router)
    app.include_router(risk_router)
    record = RecordUseCase()
    statistics = StatisticsUseCase()
    app.dependency_overrides[get_record_attendance_use_case] = lambda: record
    app.dependency_overrides[get_get_attendance_statistics_use_case] = lambda: statistics
    app.dependency_overrides[get_correct_attendance_use_case] = CorrectionUseCase
    app.dependency_overrides[get_analyze_student_academic_risk_use_case] = RiskUseCase
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id=USER_ID, email="attendance@example.test", role=role,
        is_active=True, two_factor_enabled=False,
    )
    app.dependency_overrides[get_tenant_context] = lambda: TenantContext(TENANT_ID)
    app.dependency_overrides[get_membership_repository] = lambda: MembershipRepository(role)
    return TestClient(app), record, statistics


def test_record_attendance_uses_authenticated_tenant_and_actor() -> None:
    client, use_case, _ = make_client()
    response = client.post("/attendance", json={
        "student_id": str(uuid4()), "academic_class_id": str(uuid4()),
        "academic_year_id": str(uuid4()), "academic_period_id": str(uuid4()),
        "attendance_date": "2026-10-19", "status": "ABSENT",
    })

    assert response.status_code == 201
    assert use_case.calls == [(TENANT_ID, USER_ID)]
    assert response.json()["recorded_by"] == str(USER_ID)


def test_attendance_routes_reject_non_admin_without_calling_use_case() -> None:
    client, record, _ = make_client("TEACHER")
    response = client.get(f"/attendance/students/{uuid4()}/statistics?academic_period_id={uuid4()}")

    assert response.status_code == 403
    assert record.calls == []


def test_correction_uses_expected_version_and_authenticated_tenant() -> None:
    client, _, _ = make_client()
    response = client.put(f"/attendance/{uuid4()}", json={
        "status": "PRESENT", "justified": False, "expected_version": 1,
    })

    assert response.status_code == 200
    assert response.json()["version"] == 2


def test_server_risk_route_does_not_accept_client_supplied_attendance_rate() -> None:
    client, _, _ = make_client()
    response = client.get(f"/academic-risk/students/{uuid4()}/periods/{uuid4()}")

    assert response.status_code == 200
    assert response.json()["reasons"] == ["Calcul serveur"]
