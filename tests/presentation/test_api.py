from uuid import uuid4

from fastapi.testclient import TestClient

from src.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from src.presentation.api.dependencies import get_analyze_student_academic_record_use_case
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-development-secret-key-32-bytes-minimum-change-in-production"

container = ApplicationContainer(database_path=":memory:")
app = create_app(container)
client = TestClient(app)


def authenticate_test_client():
    user = User(
        id=uuid4(),
        email=f"presentation-admin-{uuid4()}@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container._user_repository().save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
    )

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    client.headers.update(
        {
            "Authorization": f"Bearer {token}",
        }
    )


class FakeAcademicRecordRepository(StudentAcademicRecordRepository):
    def __init__(self):
        self.records = {}

    def save(self, record):
        key = (
            record.tenant_id,
            record.student_id,
            record.academic_period_id,
        )
        self.records[key] = record

    def find_by_student(self, student_id, tenant_id):
        for (
            stored_tenant_id,
            stored_student_id,
            _,
        ), record in self.records.items():
            if (
                stored_tenant_id == tenant_id
                and stored_student_id == student_id
            ):
                return record

        return None

    def find_by_student_and_period(
        self,
        student_id,
        academic_period_id,
        tenant_id,
    ):
        return self.records.get(
            (
                tenant_id,
                student_id,
                academic_period_id,
            )
        )

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200


def test_unknown_route_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_academic_record_returns_404_when_record_does_not_exist():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()
    use_case = AnalyzeStudentAcademicRecord(repository)

    app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    student_id = uuid4()
    academic_period_id = uuid4()

    try:
        response = client.get(
            f"/academic-records/{student_id}/{academic_period_id}"
        )

        assert response.status_code == 404
        assert "Aucun dossier academique trouve pour cet etudiant et cette periode." in response.json()["detail"]

    finally:
        app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)


def test_academic_record_returns_existing_record():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=15.5,
        failed_subjects=1,
        credits_obtained=24,
        total_credits=30,
    )

    repository.save(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    try:
        response = client.get(
            f"/academic-records/{student_id}/{academic_period_id}"
        )

        assert response.status_code == 200

        assert response.json() == {
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "general_average": 15.5,
            "failed_subjects": 1,
            "credits_obtained": 24,
            "total_credits": 30,
            "subject_results": [],
        }

    finally:
        app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)

def test_academic_record_returns_subject_results():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()
    subject_id = uuid4()

    subject_result = SubjectResult(
        subject_id=subject_id,
        average=16.5,
        coefficient=3,
    )

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(subject_result,),
        general_average=16.5,
        failed_subjects=0,
        credits_obtained=30,
        total_credits=30,
    )

    repository.save(record)

    use_case = AnalyzeStudentAcademicRecord(repository)

    app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    try:
        response = client.get(
            f"/academic-records/{student_id}/{academic_period_id}"
        )

        assert response.status_code == 200

        assert response.json() == {
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "general_average": 16.5,
            "failed_subjects": 0,
            "credits_obtained": 30,
            "total_credits": 30,
            "subject_results": [
                {
                    "subject_id": str(subject_id),
                    "average": 16.5,
                    "coefficient": 3,
                }
            ],
        }
    finally:
        app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)


def test_add_subject_result_returns_created_result():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()
    subject_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(subject_id),
                "average": 16,
                "coefficient": 3,
            },
        )

        assert response.status_code == 201

        assert response.json() == {
            "subject_id": str(subject_id),
            "average": 16,
            "coefficient": 3,
        }

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_returns_404_when_record_does_not_exist():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()
    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    student_id = uuid4()
    academic_period_id = uuid4()

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
                "coefficient": 2,
            },
        )

        assert response.status_code == 404
        assert "Aucun dossier académique trouvé pour cet étudiant et cette période." in response.json()["detail"]

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_average():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 25,
                "coefficient": 2,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_coefficient():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
                "coefficient": 0,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_returns_created_result():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()
    subject_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(subject_id),
                "average": 16,
                "coefficient": 3,
            },
        )

        assert response.status_code == 201

        assert response.json() == {
            "subject_id": str(subject_id),
            "average": 16,
            "coefficient": 3,
        }

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_returns_404_when_record_does_not_exist():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()
    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    student_id = uuid4()
    academic_period_id = uuid4()

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
                "coefficient": 2,
            },
        )

        assert response.status_code == 404
        assert "Aucun dossier académique trouvé pour cet étudiant et cette période." in response.json()["detail"]

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_average():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 25,
                "coefficient": 2,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_coefficient():
    authenticate_test_client()
    repository = FakeAcademicRecordRepository()

    student_id = uuid4()
    academic_period_id = uuid4()

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(),
        general_average=0,
        failed_subjects=0,
        credits_obtained=0,
        total_credits=30,
    )

    repository.save(record)

    use_case = AddSubjectResult(repository)

    app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
                "coefficient": 0,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_add_subject_result_use_case, None)

from src.application.use_cases.add_subject_result import (
    AddSubjectResult,
)
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
)











