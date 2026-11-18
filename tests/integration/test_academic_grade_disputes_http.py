"""
Tests d'intégration HTTP — Contestation de note et cycle de réclamation (Décision 18).

Scénarios vérifiés :
1. Soumission d'une contestation valide (POST /academic/disputes -> 201 SUBMITTED)
2. Rejet si motif manquant ou trop court (422)
3. Rejet si entité référencée introuvable (404)
4. Mise sous examen par la direction (POST /academic/disputes/{id}/review -> UNDER_REVIEW)
5. Résolution avec acceptation motivée (POST /academic/disputes/{id}/resolve -> ACCEPTED)
6. Résolution avec rejet motivé (POST /academic/disputes/{id}/resolve -> REJECTED)
7. Double résolution interdite (400)
8. Règle impérative Décision 18 : la contestation ne modifie jamais automatiquement la note
9. RBAC : un élève ne peut ni mettre sous examen ni résoudre une contestation (403)
10. Isolation multi-tenant stricte (404)
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def _make_academic_client(role: str = "ADMIN", tenant_id=TEST_TENANT_ID):
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}-{uuid4().hex[:6]}@edunova.test", "hashed-pass", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=tenant_id, role=role)

    student_id = uuid4()
    year_id = uuid4()
    period_id = uuid4()
    subject_id = uuid4()

    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, active) VALUES (?, ?, 'Alice', 'Mbuyi', 1)",
            (str(student_id), str(tenant_id)),
        )
        conn.execute(
            """INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status)
               VALUES (?, ?, '2026-2027', '2026-09-01', '2027-06-30', 'ACTIVE')""",
            (str(year_id), str(tenant_id)),
        )
        conn.execute(
            """INSERT INTO academic_periods (id, tenant_id, academic_year_id, name, start_date, end_date)
               VALUES (?, ?, ?, 'Trimestre 1', '2026-09-01', '2026-12-15')""",
            (str(period_id), str(tenant_id), str(year_id)),
        )
        conn.execute(
            """INSERT INTO subjects (id, tenant_id, name, code, coefficient, active)
               VALUES (?, ?, 'Mathematiques', 'MATH101', 3.0, 1)""",
            (str(subject_id), str(tenant_id)),
        )

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container, student_id, period_id, subject_id


def test_submit_grade_dispute_nominal():
    client, _, student_id, period_id, subject_id = _make_academic_client(role="STUDENT")

    resp = client.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Erreur d'addition sur la copie d'examen du premier trimestre.",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["student_id"] == str(student_id)
    assert data["academic_period_id"] == str(period_id)
    assert data["subject_id"] == str(subject_id)
    assert data["status"] == "SUBMITTED"
    assert "submitted_at" in data
    assert data["reviewed_by"] is None


def test_submit_grade_dispute_rejects_missing_reason():
    client, _, student_id, period_id, subject_id = _make_academic_client(role="STUDENT")

    resp = client.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "   ",
        },
    )
    assert resp.status_code == 422


def test_submit_grade_dispute_rejects_unknown_subject():
    client, _, student_id, period_id, _ = _make_academic_client(role="STUDENT")

    resp = client.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(uuid4()),
            "reason": "Contestation sur matiere inexistante.",
        },
    )
    assert resp.status_code == 404
    assert "Matiere introuvable" in resp.json()["detail"]


def test_grade_dispute_workflow_review_and_accepted():
    client_admin, _, student_id, period_id, subject_id = _make_academic_client(role="DIRECTION")

    # 1. Soumission
    submit_resp = client_admin.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Copie physique portant la mention 16/20 saisie comme 06/20.",
        },
    )
    assert submit_resp.status_code == 201
    dispute_id = submit_resp.json()["id"]

    # 2. Passage sous examen
    review_resp = client_admin.post(f"/academic/disputes/{dispute_id}/review")
    assert review_resp.status_code == 200, review_resp.text
    review_data = review_resp.json()
    assert review_data["status"] == "UNDER_REVIEW"
    assert review_data["reviewed_by"] is not None
    assert review_data["reviewed_at"] is not None

    # 3. Résolution ACCEPTED
    resolve_resp = client_admin.post(
        f"/academic/disputes/{dispute_id}/resolve",
        json={
            "decision": "ACCEPTED",
            "resolution_notes": "Apres verification de la souche papier, la note est bien 16/20. Correction autorisee.",
        },
    )
    assert resolve_resp.status_code == 200, resolve_resp.text
    resolve_data = resolve_resp.json()
    assert resolve_data["status"] == "ACCEPTED"
    assert resolve_data["resolution_notes"] is not None
    assert resolve_data["resolved_at"] is not None


def test_grade_dispute_cannot_be_resolved_twice():
    client, _, student_id, period_id, subject_id = _make_academic_client(role="ADMIN")

    sub = client.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Reclamation sur la seconde interrogation.",
        },
    ).json()
    did = sub["id"]

    res1 = client.post(
        f"/academic/disputes/{did}/resolve",
        json={"decision": "REJECTED", "resolution_notes": "Bareme applique sans erreur de calcul."},
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "REJECTED"

    # Tentative de re-résolution -> 400
    res2 = client.post(
        f"/academic/disputes/{did}/resolve",
        json={"decision": "ACCEPTED", "resolution_notes": "Changement d avis."},
    )
    assert res2.status_code == 400
    assert "deja ete resolue" in res2.json()["detail"]


def test_grade_dispute_rbac_student_cannot_review_or_resolve():
    client_student, _, student_id, period_id, subject_id = _make_academic_client(role="STUDENT")

    sub = client_student.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Reclamation etudiant ordinaire.",
        },
    ).json()
    did = sub["id"]

    # Student ne peut ni review ni resolve -> 403 Forbidden
    assert client_student.post(f"/academic/disputes/{did}/review").status_code == 403
    assert client_student.post(
        f"/academic/disputes/{did}/resolve",
        json={"decision": "ACCEPTED", "resolution_notes": "Auto-validation interdite."},
    ).status_code == 403


def test_grade_dispute_cross_tenant_isolation():
    client_a, container, student_id, period_id, subject_id = _make_academic_client(role="ADMIN", tenant_id=TEST_TENANT_ID)

    sub = client_a.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Reclamation etablissement A.",
        },
    ).json()
    did = sub["id"]

    # Client sur tenant B
    other_tenant = uuid4()
    user_b = User(uuid4(), f"admin-{uuid4().hex[:6]}@other.test", "pwd", "ADMIN")
    container._user_repository().save(user_b)
    seed_membership(container, user_b.id, tenant_id=other_tenant, role="ADMIN")
    token_b = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user_b.id, role="ADMIN", tenant_id=other_tenant,
    )
    client_b = TestClient(create_app(container))
    client_b.headers.update({"Authorization": f"Bearer {token_b}"})

    # L'admin du tenant B ne peut ni examiner ni résoudre la contestation du tenant A -> 404
    assert client_b.post(f"/academic/disputes/{did}/review").status_code == 404
    assert client_b.post(
        f"/academic/disputes/{did}/resolve",
        json={"decision": "REJECTED", "resolution_notes": "Autre tenant."},
    ).status_code == 404


def test_grade_dispute_acceptance_does_not_silently_modify_grades():
    client_admin, container, student_id, period_id, subject_id = _make_academic_client(role="DIRECTION")

    # Créer un dossier académique existant avec une note initiale
    with container._database.connect() as conn:
        conn.execute(
            """INSERT INTO student_academic_records
               (tenant_id, student_id, academic_period_id, general_average, failed_subjects, credits_obtained, total_credits, version, status)
               VALUES (?, ?, ?, 10.0, 0, 0.0, 0.0, 1, 'VALIDATED')""",
            (str(TEST_TENANT_ID), str(student_id), str(period_id)),
        )

    # 1. Soumission d'une contestation
    sub = client_admin.post(
        "/academic/disputes",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "subject_id": str(subject_id),
            "reason": "Note contestee de 10.0.",
        },
    ).json()
    did = sub["id"]

    # 2. Résolution ACCEPTED
    res = client_admin.post(
        f"/academic/disputes/{did}/resolve",
        json={
            "decision": "ACCEPTED",
            "resolution_notes": "Reclamation legitime. Doit faire l objet d une correction manuelle tracee.",
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ACCEPTED"

    # 3. Vérification impérative Décision 18 : la note n'a pas été modifiée silencieusement
    with container._database.connect() as conn:
        rec = conn.execute(
            "SELECT general_average, version FROM student_academic_records WHERE student_id = ? AND academic_period_id = ?",
            (str(student_id), str(period_id)),
        ).fetchone()
        assert rec["general_average"] == 10.0
        assert rec["version"] == 1
