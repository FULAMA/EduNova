from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.academic.domain.entities.student_assignment import (
    StudentAssignment,
    StudentAssignmentStatus,
)
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import get_apply_student_promotion_use_case
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


class RecordingPromotionUseCase:
    def __init__(self, error: str | None = None):
        self.error = error
        self.calls: list[tuple[UUID, UUID, UUID, UUID, UUID, UUID]] = []

    def execute(
        self,
        tenant_id: UUID,
        source_assignment_id: UUID,
        deliberation_id: UUID,
        target_year_id: UUID,
        target_class_id: UUID,
        actor_id: UUID,
    ) -> StudentAssignment:
        self.calls.append(
            (
                tenant_id,
                source_assignment_id,
                deliberation_id,
                target_year_id,
                target_class_id,
                actor_id,
            )
        )
        if self.error is not None:
            raise ValueError(self.error)
        now = datetime.now(timezone.utc)
        return StudentAssignment(
            id=uuid4(),
            tenant_id=tenant_id,
            student_id=uuid4(),
            academic_year_id=target_year_id,
            academic_class_id=target_class_id,
            academic_option_id=None,
            status=StudentAssignmentStatus.ACTIVE,
            created_by=actor_id,
            created_at=now,
            updated_at=now,
        )


def make_client(use_case: RecordingPromotionUseCase, role: str = "ADMIN") -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_apply_student_promotion_use_case] = lambda: use_case
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


def promotion_payload() -> dict[str, str]:
    return {
        "source_assignment_id": str(uuid4()),
        "deliberation_id": str(uuid4()),
        "target_year_id": str(uuid4()),
        "target_class_id": str(uuid4()),
    }


def test_promotion_http_uses_authenticated_tenant_and_actor() -> None:
    use_case = RecordingPromotionUseCase()
    client = make_client(use_case)
    payload = promotion_payload()

    response = client.post(
        "/student-assignments/promote",
        json={**payload, "tenant_id": str(uuid4())},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "ACTIVE"
    assert use_case.calls == [
        (
            TENANT_ID,
            UUID(payload["source_assignment_id"]),
            UUID(payload["deliberation_id"]),
            UUID(payload["target_year_id"]),
            UUID(payload["target_class_id"]),
            USER_ID,
        )
    ]


def test_promotion_http_rejects_non_admin_before_use_case() -> None:
    use_case = RecordingPromotionUseCase()
    client = make_client(use_case, role="TEACHER")

    response = client.post("/student-assignments/promote", json=promotion_payload())

    assert response.status_code == 403
    assert use_case.calls == []


def test_promotion_http_maps_business_conflict() -> None:
    use_case = RecordingPromotionUseCase(
        error="La deliberation ne permet pas ce passage."
    )
    client = make_client(use_case)

    response = client.post("/student-assignments/promote", json=promotion_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "La deliberation ne permet pas ce passage."


def test_promotion_http_rejects_malformed_identifiers() -> None:
    use_case = RecordingPromotionUseCase()
    client = make_client(use_case)

    response = client.post(
        "/student-assignments/promote",
        json={
            "source_assignment_id": "not-a-uuid",
            "deliberation_id": str(uuid4()),
            "target_year_id": str(uuid4()),
            "target_class_id": str(uuid4()),
        },
    )

    assert response.status_code == 422
    assert use_case.calls == []
