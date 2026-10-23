from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.academic.domain.entities.student_assignment import (
    StudentAssignment,
    StudentAssignmentStatus,
)
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import get_change_student_assignment_status_use_case
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_membership_repository,
    get_tenant_context,
)
from src.presentation.api.routes.student_assignments import router
from src.shared.application.context.tenant_context import TenantContext


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_ID = UUID("00000000-0000-0000-0000-000000000002")


class FakeMembership:
    def __init__(self, role: str):
        self.role = role
        self.active = True


class FakeMembershipRepository:
    def __init__(self, role: str):
        self._membership = FakeMembership(role)

    def find_by_user_and_tenant(self, user_id: UUID, tenant_id: UUID) -> FakeMembership:
        return self._membership


class RecordingCloseUseCase:
    def __init__(self, result: StudentAssignment | None = None, error: str | None = None):
        self.result = result
        self.error = error
        self.calls: list[tuple[UUID, UUID]] = []

    def close(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment:
        self.calls.append((assignment_id, tenant_id))
        if self.error is not None:
            raise ValueError(self.error)
        assert self.result is not None
        return self.result


def assignment(status: StudentAssignmentStatus = StudentAssignmentStatus.CLOSED) -> StudentAssignment:
    now = datetime.now(timezone.utc)
    return StudentAssignment(
        id=uuid4(),
        tenant_id=TENANT_ID,
        student_id=uuid4(),
        academic_year_id=uuid4(),
        academic_class_id=uuid4(),
        academic_option_id=None,
        status=status,
        created_by=USER_ID,
        created_at=now,
        updated_at=now,
        closed_at=now if status is StudentAssignmentStatus.CLOSED else None,
    )


def test_domain_rejects_second_close_without_mutating_closed_entity() -> None:
    current = assignment(StudentAssignmentStatus.ACTIVE)
    closed = current.close()

    assert current.status is StudentAssignmentStatus.ACTIVE
    assert closed.status is StudentAssignmentStatus.CLOSED
    assert closed.closed_at is not None

    with pytest.raises(ValueError, match="Seule une affectation active"):
        closed.close()

    assert closed.status is StudentAssignmentStatus.CLOSED
    assert closed.closed_at is not None


def make_client(use_case: RecordingCloseUseCase, role: str = "ADMIN") -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_change_student_assignment_status_use_case] = lambda: use_case
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id=USER_ID,
        email="isolated@example.test",
        role=role,
        is_active=True,
        two_factor_enabled=False,
    )
    app.dependency_overrides[get_tenant_context] = lambda: TenantContext(TENANT_ID)
    app.dependency_overrides[get_membership_repository] = lambda: FakeMembershipRepository(role)
    return TestClient(app)


def test_close_http_uses_real_route_and_authorized_tenant() -> None:
    result = assignment()
    use_case = RecordingCloseUseCase(result=result)
    client = make_client(use_case)

    response = client.post(f"/student-assignments/{result.id}/close")

    assert response.status_code == 200
    assert response.json()["status"] == "CLOSED"
    assert use_case.calls == [(result.id, TENANT_ID)]


def test_close_http_rejects_teacher_without_reaching_use_case() -> None:
    result = assignment()
    use_case = RecordingCloseUseCase(result=result)
    client = make_client(use_case, role="TEACHER")

    response = client.post(f"/student-assignments/{result.id}/close")

    assert response.status_code == 403
    assert use_case.calls == []


def test_close_http_validates_uuid_and_maps_domain_error() -> None:
    use_case = RecordingCloseUseCase(error="Affectation introuvable.")
    client = make_client(use_case)

    malformed = client.post("/student-assignments/not-a-uuid/close")
    missing_id = uuid4()
    missing = client.post(f"/student-assignments/{missing_id}/close")

    assert malformed.status_code == 422
    assert missing.status_code == 400
    assert use_case.calls == [(missing_id, TENANT_ID)]


def test_close_http_never_accepts_a_client_tenant() -> None:
    result = assignment()
    use_case = RecordingCloseUseCase(result=result)
    client = make_client(use_case)

    response = client.post(
        f"/student-assignments/{result.id}/close",
        json={"tenant_id": str(uuid4())},
    )

    assert response.status_code == 200
    assert use_case.calls == [(result.id, TENANT_ID)]
