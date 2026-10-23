from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership
from tests.integration.test_academic_record_http_sqlite import seed_eligible_context




def test_academic_record_full_http_workflow():
    student_id = uuid4()
    academic_period_id = uuid4()

    container = ApplicationContainer(
        database_path=":memory:"
    )

    app = create_app(container)
    client = TestClient(app)

    # Utilisateur authentifi�
    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container._user_repository().save(user)

    # Membership active dans le tenant de test
    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
    )

    # �tudiant appartenant au m�me tenant
    with container._database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_id),
                str(TEST_TENANT_ID),
                "Test",
                "Student",
                None,
                None,
                1,
            ),
        )

    subjects = seed_eligible_context(container, user.id, student_id, academic_period_id)

    # JWT contenant le tenant actif
    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)

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

    # 1. Cr�ation du dossier acad�mique
    response = client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "total_credits": 30,
        },
    )

    assert response.status_code == 201

    # 2. Ajout de Math�matiques : 16 � coefficient 3
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(subjects[0].id),
            "average": 16,
        },
    )

    assert response.status_code == 201
    assert response.json()["coefficient"] == 2

    # 3. Ajout de Physique : 12 � coefficient 2
    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(subjects[1].id),
            "average": 12,
        },
    )

    assert response.status_code == 201
    assert response.json()["coefficient"] == 3

    # 4. Consultation du dossier
    response = client.get(
        f"/academic-records/{student_id}/{academic_period_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == str(student_id)
    assert data["academic_period_id"] == str(academic_period_id)

    # (16 � 3 + 12 � 2) / (3 + 2) = 14.4
    assert data["general_average"] == 13.6

    assert data["failed_subjects"] == 0
    assert data["total_credits"] == 30

    assert len(data["subject_results"]) == 2

    results = {row["subject_id"]: row for row in data["subject_results"]}
    assert results[str(subjects[0].id)] == {
        "subject_id": str(subjects[0].id), "subject_name": subjects[0].name,
        "average": 16, "coefficient": 2,
    }
    assert results[str(subjects[1].id)] == {
        "subject_id": str(subjects[1].id), "subject_name": subjects[1].name,
        "average": 12, "coefficient": 3,
    }


