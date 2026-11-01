from uuid import uuid4, UUID


from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.dependencies import get_analyze_student_academic_record_use_case
from src.academic.application.use_cases.add_subject_result import (
    AddSubjectResult,
)
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
)
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership
from tests.support.academic_eligibility import eligible_result_repositories





def authenticate_test_client(container, client, role="ADMIN", tenant_id=TEST_TENANT_ID):
    user = User(
        id=uuid4(),
        email=f"presentation-{role.lower()}-{uuid4()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )

    container._user_repository().save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=tenant_id,
        role=role,
    )

    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role=role,
        tenant_id=tenant_id,
    )

    client.headers.update(
        {
            "Authorization": f"Bearer {token}",
        }
    )
    return user.id


class FakeAcademicRecordRepository(StudentAcademicRecordRepository):
    def __init__(self):
        self.records = {}

    def save(self, record, *, expected_version=None, operation="SAVE"):
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

def test_health_check(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200


def test_unknown_route_returns_404(api_client):
    response = api_client.get("/does-not-exist")

    assert response.status_code == 404


def test_academic_record_returns_404_when_record_does_not_exist(application_container, api_client):
    authenticate_test_client(application_container, api_client)
    repository = FakeAcademicRecordRepository()
    use_case = AnalyzeStudentAcademicRecord(repository)

    api_client.app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    student_id = uuid4()
    academic_period_id = uuid4()

    try:
        response = api_client.get(
            f"/academic-records/{student_id}/{academic_period_id}"
        )

        assert response.status_code == 404
        assert "Aucun dossier académique trouvé pour cet étudiant et cette période." in response.json()["detail"]

    finally:
        api_client.app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)


def test_academic_record_returns_existing_record(application_container, api_client):
    authenticate_test_client(application_container, api_client)
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

    api_client.app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    try:
        response = api_client.get(
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
            "status": "DRAFT",
            "version": 1,
        }

    finally:
        api_client.app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)

def test_academic_record_returns_subject_results(application_container, api_client):
    authenticate_test_client(application_container, api_client)
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

    api_client.app.dependency_overrides[get_analyze_student_academic_record_use_case] = lambda: use_case

    try:
        response = api_client.get(
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
            "status": "DRAFT",
            "version": 1,
        }
    finally:
        api_client.app.dependency_overrides.pop(get_analyze_student_academic_record_use_case, None)


def test_add_subject_result_returns_created_result(application_container, api_client):
    authenticate_test_client(application_container, api_client)
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

    use_case = AddSubjectResult(repository, **eligible_result_repositories([subject_id], coefficient=3))

    api_client.app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = api_client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(subject_id),
                "average": 16,
            },
        )

        assert response.status_code == 201

        assert response.json() == {
            "subject_id": str(subject_id),
            "average": 16,
            "coefficient": 3,
        }

    finally:
        api_client.app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_returns_404_when_record_does_not_exist(application_container, api_client):
    authenticate_test_client(application_container, api_client)
    repository = FakeAcademicRecordRepository()
    use_case = AddSubjectResult(repository, **eligible_result_repositories([uuid4()]))

    api_client.app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    student_id = uuid4()
    academic_period_id = uuid4()

    try:
        response = api_client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
            },
        )

        assert response.status_code == 404
        assert "Aucun dossier académique trouvé pour cet étudiant et cette période." in response.json()["detail"]

    finally:
        api_client.app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_average(application_container, api_client):
    authenticate_test_client(application_container, api_client)
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

    use_case = AddSubjectResult(repository, **eligible_result_repositories([uuid4()]))

    api_client.app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = api_client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 25,
            },
        )

        assert response.status_code == 422

    finally:
        api_client.app.dependency_overrides.pop(get_add_subject_result_use_case, None)


def test_add_subject_result_rejects_invalid_coefficient(application_container, api_client):
    authenticate_test_client(application_container, api_client)
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

    use_case = AddSubjectResult(repository, **eligible_result_repositories([uuid4()]))

    api_client.app.dependency_overrides[get_add_subject_result_use_case] = (
        lambda: use_case
    )

    try:
        response = api_client.post(
            f"/academic-records/{student_id}/{academic_period_id}/subjects",
            json={
                "subject_id": str(uuid4()),
                "average": 15,
                "coefficient": 0,
            },
        )

        assert response.status_code == 422

    finally:
        api_client.app.dependency_overrides.pop(get_add_subject_result_use_case, None)




def test_school_profile_api_records_authenticated_actor_and_tenant_scope(application_container, api_client):
    actor_id = authenticate_test_client(application_container, api_client)
    response = api_client.put(
        "/school-profile",
        json={
            "legal_name": "Établissement Exemple ASBL",
            "display_name": "Établissement Exemple",
            "address": "Kinshasa",
            "phone": "+243000000",
        },
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Établissement Exemple"

    read_response = api_client.get("/school-profile")
    assert read_response.status_code == 200
    assert read_response.json()["legal_name"] == "Établissement Exemple ASBL"

    with application_container._database.connect() as connection:
        audit = connection.execute(
            "SELECT tenant_id, actor_user_id, action, before_state, after_state FROM school_profile_audit"
        ).fetchone()
    assert audit is not None
    assert audit["tenant_id"] == str(TEST_TENANT_ID)
    assert audit["actor_user_id"] == str(actor_id)
    assert audit["action"] == "CREATE"
    assert audit["before_state"] is None
    assert '"display_name": "Établissement Exemple"' in audit["after_state"]



def test_school_profile_rejects_non_authorized_membership_role(application_container, api_client):
    authenticate_test_client(application_container, api_client, role="PROF")
    read_response = api_client.get("/school-profile")
    assert read_response.status_code == 403

    response = api_client.put(
        "/school-profile",
        json={
            "legal_name": "Établissement Non Autorisé",
            "display_name": "Non Autorisé",
        },
    )
    assert response.status_code == 403

    with application_container._database.connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM school_profiles").fetchone()[0]
        audit_count = connection.execute("SELECT COUNT(*) FROM school_profile_audit").fetchone()[0]
    assert count == 0
    assert audit_count == 0



def test_school_profile_api_isolates_profiles_between_tenants(application_container, api_client):
    authenticate_test_client(application_container, api_client, tenant_id=TEST_TENANT_ID)
    tenant_a_response = api_client.put(
        "/school-profile",
        json={
            "legal_name": "École A ASBL",
            "display_name": "École A",
        },
    )
    assert tenant_a_response.status_code == 200

    tenant_b_id = UUID("00000000-0000-0000-0000-000000000002")
    authenticate_test_client(
        application_container, api_client, tenant_id=tenant_b_id
    )

    read_response = api_client.get("/school-profile")
    assert read_response.status_code == 200
    assert read_response.json() is None

    tenant_b_response = api_client.put(
        "/school-profile",
        json={
            "legal_name": "École B ASBL",
            "display_name": "École B",
        },
    )
    assert tenant_b_response.status_code == 200

    with application_container._database.connect() as connection:
        profiles = connection.execute(
            "SELECT tenant_id, display_name FROM school_profiles ORDER BY tenant_id"
        ).fetchall()
        audit_rows = connection.execute(
            "SELECT tenant_id, action FROM school_profile_audit ORDER BY occurred_at, rowid"
        ).fetchall()

    assert [(row["tenant_id"], row["display_name"]) for row in profiles] == [
        (str(TEST_TENANT_ID), "École A"),
        (str(tenant_b_id), "École B"),
    ]
    assert [row["tenant_id"] for row in audit_rows].count(str(TEST_TENANT_ID)) == 1
    assert [row["tenant_id"] for row in audit_rows].count(str(tenant_b_id)) == 1
