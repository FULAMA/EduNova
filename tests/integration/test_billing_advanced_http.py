"""
LOT D — Tests financiers avancés — EduNova Mission V1.1

Scénarios vérifiés (Décision 19, 21, 22, FIN-ROLE-01, FIN-COR-01, FIN-REC-01) :
1.  Paiement intégral → solde restant nul
2.  Paiement partiel → arriéré correct
3.  Plusieurs paiements successifs (3 transactions)
4.  Paiement en devise incorrecte → 409
5.  Échéance future → overdue=false
6.  Échéance dépassée → overdue=true
7.  Correction par contre-écriture (reverse_payment)
8.  Double correction → 409
9.  PDF de reçu → Content-Type application/pdf
10. Pagination offset sur arriérés
11. Filtrage combiné student_id + status
12. Idempotence du paiement (même clé, mêmes données → identique)
13. Idempotence conflictuelle (même clé, données différentes → 409)
14. Paiement ne pouvant pas dépasser le solde restant → 400/409

Toutes les bases sont en mémoire (:memory:). Aucune modification de edunova.db.
"""

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


# ─── Helpers ────────────────────────────────────────────────────────────────

def _make_client(role: str = "ADMIN"):
    """Crée un conteneur :memory: avec un utilisateur et un token."""
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}-{uuid4()}@edunova.test", "hashed-pwd", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=TEST_TENANT_ID, role=role)
    student_id = uuid4()
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) "
            "VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_id), str(TEST_TENANT_ID), "Test", "Student", None),
        )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container, student_id


def _create_charge(client, student_id, amount="100.00", currency="USD", due_date=None):
    body = {
        "student_id": str(student_id),
        "description": "Frais test",
        "amount": amount,
        "currency": currency,
    }
    if due_date is not None:
        body["due_date"] = due_date
    r = client.post("/billing/charges", json=body)
    assert r.status_code == 201, f"Charge creation failed: {r.text}"
    return r.json()


def _record_payment(client, charge_id, amount, currency, key):
    r = client.post(
        "/billing/payments",
        json={"charge_id": charge_id, "amount": amount, "currency": currency, "idempotency_key": key},
    )
    return r


# ─── Scénario 1 : paiement intégral ─────────────────────────────────────────

def test_full_payment_clears_arrear():
    """Paiement intégral → solde restant = 0 → aucun arriéré."""
    client, _, student_id = _make_client()
    past = (date.today() - timedelta(days=1)).isoformat()
    charge = _create_charge(client, student_id, "150.00", "USD", due_date=past)

    r = _record_payment(client, charge["id"], "150.00", "USD", "full-pay-1")
    assert r.status_code == 200

    arrears = client.get("/billing/arrears?overdue_only=true")
    assert arrears.status_code == 200
    assert arrears.json()["total"] == 0, "Un paiement intégral ne doit pas laisser d'arriéré"


# ─── Scénario 2 : paiement partiel ──────────────────────────────────────────

def test_partial_payment_leaves_correct_arrear():
    """Paiement de 60 sur 100 → arriéré de 40 (Décision 22)."""
    client, _, student_id = _make_client()
    past = (date.today() - timedelta(days=2)).isoformat()
    charge = _create_charge(client, student_id, "100.00", "USD", due_date=past)

    _record_payment(client, charge["id"], "60.00", "USD", "partial-pay-1")

    arrears = client.get("/billing/arrears?overdue_only=true")
    assert arrears.status_code == 200
    items = arrears.json()["items"]
    assert len(items) == 1
    assert items[0]["amount_due"] == "100.00"
    assert items[0]["amount_paid"] == "60.00"
    assert items[0]["amount_remaining"] == "40.00"
    assert items[0]["overdue"] is True


# ─── Scénario 3 : plusieurs paiements successifs ─────────────────────────────

def test_multiple_payments_on_same_charge():
    """3 paiements cumulés : 100 + 150 + 50 = 300 sur une charge de 300."""
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "300.00", "CDF")

    r1 = _record_payment(client, charge["id"], "100.00", "CDF", "multi-1")
    r2 = _record_payment(client, charge["id"], "150.00", "CDF", "multi-2")
    r3 = _record_payment(client, charge["id"], "50.00", "CDF", "multi-3")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 200

    # La liste doit contenir 3 paiements
    payments = client.get("/billing/payments")
    assert payments.json()["total"] == 3


# ─── Scénario 4 : devise incorrecte → 409 ───────────────────────────────────

def test_payment_wrong_currency_rejected():
    """Un paiement en CDF sur une charge USD est refusé (Décision 19 — devises séparées)."""
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "100.00", "USD")

    r = _record_payment(client, charge["id"], "100.00", "CDF", "wrong-currency-1")
    assert r.status_code == 409, "La devise incorrecte doit être rejetée avec 409"


# ─── Scénario 5 : échéance future → overdue=false ────────────────────────────

def test_future_due_date_not_overdue():
    """Un frais dont l'échéance est dans le futur n'est pas un arriéré (overdue=false)."""
    client, _, student_id = _make_client()
    future = (date.today() + timedelta(days=30)).isoformat()
    charge = _create_charge(client, student_id, "100.00", "USD", due_date=future)

    # Paiement partiel pour qu'il apparaisse dans la liste arriérés sans overdue_only
    _record_payment(client, charge["id"], "10.00", "USD", "future-pay-1")

    arrears_all = client.get("/billing/arrears?overdue_only=false")
    assert arrears_all.status_code == 200
    items = arrears_all.json()["items"]
    # Il doit y avoir 1 arriéré mais overdue=false
    matching = [i for i in items if i["charge_id"] == charge["id"]]
    assert len(matching) == 1
    assert matching[0]["overdue"] is False

    # Avec overdue_only=true, il ne doit pas apparaître
    arrears_overdue = client.get("/billing/arrears?overdue_only=true")
    assert len([i for i in arrears_overdue.json()["items"] if i["charge_id"] == charge["id"]]) == 0


# ─── Scénario 6 : échéance dépassée → overdue=true ───────────────────────────

def test_past_due_date_is_overdue():
    """Un frais dont l'échéance est passée et non soldé est overdue=true (Décision 22)."""
    client, _, student_id = _make_client()
    past = (date.today() - timedelta(days=10)).isoformat()
    charge = _create_charge(client, student_id, "200.00", "USD", due_date=past)

    _record_payment(client, charge["id"], "50.00", "USD", "overdue-pay-1")

    arrears = client.get("/billing/arrears?overdue_only=true")
    items = arrears.json()["items"]
    matching = [i for i in items if i["charge_id"] == charge["id"]]
    assert len(matching) == 1
    assert matching[0]["overdue"] is True
    assert matching[0]["amount_remaining"] == "150.00"


# ─── Scénario 7 : correction par contre-écriture ─────────────────────────────

def test_payment_reversal_restores_arrear():
    """Après correction (counter-entry), le solde est restauré (FIN-COR-01)."""
    client, _, student_id = _make_client()
    past = (date.today() - timedelta(days=5)).isoformat()
    charge = _create_charge(client, student_id, "100.00", "USD", due_date=past)

    pay = _record_payment(client, charge["id"], "100.00", "USD", "reversal-pay-1")
    assert pay.status_code == 200
    payment_id = pay.json()["id"]

    # Avant correction : aucun arriéré (charge soldée)
    arrears_before = client.get("/billing/arrears?overdue_only=true")
    assert arrears_before.json()["total"] == 0

    # Correction par contre-écriture
    correction = client.post(
        f"/billing/payments/{payment_id}/correction",
        json={"reason": "Erreur de saisie - correction test"},
    )
    assert correction.status_code == 200

    # Après correction : arriéré restauré
    arrears_after = client.get("/billing/arrears?overdue_only=true")
    assert arrears_after.json()["total"] == 1
    assert arrears_after.json()["items"][0]["amount_remaining"] == "100.00"


# ─── Scénario 8 : double correction → 409 ────────────────────────────────────

def test_double_reversal_rejected():
    """Une deuxième correction sur le même paiement est refusée (FIN-COR-01 — unicité)."""
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "50.00", "USD")
    pay = _record_payment(client, charge["id"], "50.00", "USD", "double-rev-1")
    payment_id = pay.json()["id"]

    first = client.post(
        f"/billing/payments/{payment_id}/correction",
        json={"reason": "Première correction"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/billing/payments/{payment_id}/correction",
        json={"reason": "Tentative de double correction"},
    )
    assert second.status_code == 409, "La double correction doit être refusée avec 409"


# ─── Scénario 9 : PDF de reçu ────────────────────────────────────────────────

def test_receipt_pdf_content_type():
    """Le endpoint PDF reçu retourne Content-Type: application/pdf (FIN-REC-01)."""
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "80.00", "USD")
    pay = _record_payment(client, charge["id"], "80.00", "USD", "pdf-pay-1")
    receipt_number = pay.json()["receipt_number"]

    pdf_response = client.get(f"/billing/receipts/{receipt_number}/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    # Le PDF doit être non vide
    assert len(pdf_response.content) > 100


# ─── Scénario 10 : pagination offset ─────────────────────────────────────────

def test_arrears_offset_pagination():
    """La pagination offset exclut les premiers éléments (Décision 22)."""
    client, _, student_id = _make_client()
    past = (date.today() - timedelta(days=1)).isoformat()

    # 3 charges avec paiement partiel
    for i in range(3):
        charge = _create_charge(client, student_id, "100.00", "USD", due_date=past)
        _record_payment(client, charge["id"], "10.00", "USD", f"offset-pay-{i}")

    total_resp = client.get("/billing/arrears?overdue_only=true&limit=10&offset=0")
    total = total_resp.json()["total"]
    assert total == 3

    paged = client.get("/billing/arrears?overdue_only=true&limit=1&offset=1")
    assert paged.json()["total"] == 3  # total reste 3
    assert len(paged.json()["items"]) == 1


# ─── Scénario 11 : filtrage combiné ──────────────────────────────────────────

def test_combined_filter_student_id_and_status():
    """Filtrage par student_id + status=CONFIRMED retourne uniquement les paiements confirmés
    pour cet élève (Décision 32 — isolation, Décision 19 — traçabilité).
    """
    client, container, student_a = _make_client()
    student_b = uuid4()
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) "
            "VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_b), str(TEST_TENANT_ID), "Autre", "Eleve", None),
        )

    charge_a = _create_charge(client, student_a, "60.00", "CDF")
    charge_b = _create_charge(client, student_b, "40.00", "CDF")

    _record_payment(client, charge_a["id"], "60.00", "CDF", "filter-a-1")
    _record_payment(client, charge_b["id"], "40.00", "CDF", "filter-b-1")

    result = client.get(f"/billing/payments?student_id={student_a}&status=CONFIRMED")
    assert result.status_code == 200
    assert result.json()["total"] == 1
    assert result.json()["items"][0]["student_id"] == str(student_a)


# ─── Scénario 12 : idempotence OK ────────────────────────────────────────────

def test_payment_idempotency_same_key_same_data():
    """La même clé d'idempotence avec les mêmes données retourne le même paiement
    sans créer de doublon (Décision 19, invariant FIN).
    """
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "100.00", "USD")

    r1 = _record_payment(client, charge["id"], "100.00", "USD", "idempotent-key-1")
    r2 = _record_payment(client, charge["id"], "100.00", "USD", "idempotent-key-1")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"], "Les deux paiements doivent retourner le même ID"

    # Un seul paiement créé
    payments = client.get("/billing/payments")
    assert payments.json()["total"] == 1


# ─── Scénario 13 : idempotence conflictuelle → 409 ───────────────────────────

def test_payment_idempotency_conflict_different_amount():
    """La même clé avec un montant différent est refusée avec 409
    (Décision 19 — IdempotencyKey unique et cohérente).
    """
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "100.00", "USD")

    r1 = _record_payment(client, charge["id"], "50.00", "USD", "conflict-key-1")
    assert r1.status_code == 200

    r2 = _record_payment(client, charge["id"], "60.00", "USD", "conflict-key-1")
    assert r2.status_code == 409, "Une clé d'idempotence réutilisée avec un montant différent doit retourner 409"


# ─── Scénario 14 : dépassement du solde → erreur ─────────────────────────────

def test_payment_exceeding_balance_rejected():
    """Un paiement supérieur au solde restant est refusé.
    (Invariant financier : montant alloué ne dépasse pas le solde disponible)
    """
    client, _, student_id = _make_client()
    charge = _create_charge(client, student_id, "100.00", "USD")

    # Payer 80 d'abord
    _record_payment(client, charge["id"], "80.00", "USD", "exceed-pay-1")

    # Essayer de payer 50 alors qu'il ne reste que 20
    r = _record_payment(client, charge["id"], "50.00", "USD", "exceed-pay-2")
    assert r.status_code in (400, 409), (
        f"Un paiement dépassant le solde doit être refusé (got {r.status_code})"
    )
