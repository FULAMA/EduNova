import sqlite3
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.billing.application.service import BillingService
from src.billing.domain.money import Currency
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_billing_repository import SQLiteBillingRepository


TENANT = UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT = UUID("00000000-0000-0000-0000-000000000002")


def service_with_student(tenant_id: UUID = TENANT):
    database = SQLiteDatabase(":memory:")
    database.initialize()
    student_id = uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_id), str(tenant_id), "Ada", "Lovelace", None),
        )
    return BillingService(SQLiteBillingRepository(database)), student_id


def test_records_usd_payment_once_and_returns_same_result_for_retry():
    service, student_id = service_with_student()
    charge = service.create_charge(TENANT, student_id, "Frais scolaires", Decimal("100.00"), Currency.USD, None)

    first = service.record_payment(TENANT, charge.id, Decimal("40.00"), Currency.USD, "payment-1", uuid4())
    retry = service.record_payment(TENANT, charge.id, Decimal("40"), Currency.USD, "payment-1", uuid4())

    assert first.id == retry.id
    assert first.receipt_number == retry.receipt_number
    assert service.summary(TENANT, student_id).payments == (first,)


def test_rejects_currency_mismatch_and_overpayment():
    service, student_id = service_with_student()
    charge = service.create_charge(TENANT, student_id, "Contribution", Decimal("100.00"), Currency.CDF, None)

    with pytest.raises(ValueError, match="devise"):
        service.record_payment(TENANT, charge.id, Decimal("1.00"), Currency.USD, "usd-1", uuid4())

    with pytest.raises(ValueError, match="solde"):
        service.record_payment(TENANT, charge.id, Decimal("100.01"), Currency.CDF, "cdf-1", uuid4())


def test_rejects_cross_tenant_student_and_charge_access():
    service, student_id = service_with_student()

    with pytest.raises(LookupError):
        service.create_charge(OTHER_TENANT, student_id, "Frais", Decimal("10.00"), Currency.USD, None)



def test_fee_assignment_keeps_immutable_catalogue_snapshot_after_catalogue_change():
    service, student_id = service_with_student()
    actor_id = uuid4()
    fee = service.create_fee_type(
        TENANT, "Travaux", "Travaux pratiques", "ACTIVITY",
        Decimal("75.00"), Currency.CDF, None, "STUDENT", actor_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)

    first = service.assign_fee_type(TENANT, fee.id, student_id, None, actor_id)

    with service._repository._database.connect() as connection:
        connection.execute(
            "UPDATE billing_fee_types SET amount = ?, currency = ?, name = ? WHERE tenant_id = ? AND id = ?",
            ("99.00", "USD", "Travaux modifiés", str(TENANT), str(fee.id)),
        )

    retry = service.assign_fee_type(TENANT, fee.id, student_id, None, actor_id)

    assert first.id == retry.id
    assert retry.amount.amount == Decimal("75.00")
    assert retry.amount.currency is Currency.CDF

    with service._repository._database.connect() as connection:
        snapshot = connection.execute(
            "SELECT snapshot_name, snapshot_description, snapshot_category, "
            "snapshot_applicability, amount, currency FROM billing_fee_assignments "
            "WHERE tenant_id = ? AND id = ?",
            (str(TENANT), str(first.id)),
        ).fetchone()

    assert snapshot["snapshot_name"] == "Travaux"
    assert snapshot["snapshot_description"] == "Travaux pratiques"
    assert snapshot["snapshot_category"] == "ACTIVITY"
    assert snapshot["snapshot_applicability"] == "STUDENT"
    assert snapshot["amount"] == "75.00"
    assert snapshot["currency"] == "CDF"

    with pytest.raises(sqlite3.IntegrityError, match="snapshots are immutable"):
        with service._repository._database.connect() as connection:
            connection.execute(
                "UPDATE billing_fee_assignments SET snapshot_name = ? WHERE tenant_id = ? AND id = ?",
                ("Historique altéré", str(TENANT), str(first.id)),
            )



def test_class_fee_requires_active_assignment_in_target_class_and_preserves_class_snapshot():
    service, student_id = service_with_student()
    database = service._repository._database
    actor_id, year_id, class_id, other_class_id, period_id = (
        uuid4(), uuid4(), uuid4(), uuid4(), uuid4()
    )
    now = "2026-10-30T10:00:00+00:00"
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status) "
            "VALUES (?, ?, ?, ?, ?, 'ACTIVE')",
            (str(year_id), str(TENANT), "2026-2027", "2026-09-01", "2027-07-31"),
        )
        for class_id_value, class_name in ((class_id, "6e primaire"), (other_class_id, "5e primaire")):
            connection.execute(
                "INSERT INTO academic_classes (id, tenant_id, name) VALUES (?, ?, ?)",
                (str(class_id_value), str(TENANT), class_name),
            )
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date, academic_year_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(period_id), str(TENANT), "Trimestre 1", "2026-09-01", "2026-12-20", str(year_id)),
        )
        connection.execute(
            """INSERT INTO student_assignments
            (id, tenant_id, student_id, academic_year_id, academic_class_id,
             academic_option_id, status, created_by, created_at, updated_at, closed_at)
            VALUES (?, ?, ?, ?, ?, NULL, 'ACTIVE', ?, ?, ?, NULL)""",
            (str(uuid4()), str(TENANT), str(student_id), str(year_id), str(class_id),
             str(actor_id), now, now),
        )

    fee = service.create_fee_type(
        TENANT, "Frais de classe", "Frais réservés à une classe", "SCHOOL",
        Decimal("50.00"), Currency.CDF, period_id, "CLASS", actor_id, class_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)
    assignment = service.assign_fee_type(TENANT, fee.id, student_id, period_id, actor_id)

    assert assignment.snapshot_class_id == class_id
    with database.connect() as connection:
        snapshot = connection.execute(
            "SELECT snapshot_class_id FROM billing_fee_assignments WHERE tenant_id = ? AND id = ?",
            (str(TENANT), str(assignment.id)),
        ).fetchone()
    assert snapshot["snapshot_class_id"] == str(class_id)


def test_class_fee_rejects_student_assigned_to_another_class_and_cross_tenant_target():
    service, student_id = service_with_student()
    database = service._repository._database
    actor_id, year_id, target_class_id, actual_class_id, period_id = (
        uuid4(), uuid4(), uuid4(), uuid4(), uuid4()
    )
    now = "2026-10-30T10:00:00+00:00"
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status) "
            "VALUES (?, ?, ?, ?, ?, 'ACTIVE')",
            (str(year_id), str(TENANT), "2026-2027", "2026-09-01", "2027-07-31"),
        )
        for class_id_value, class_name in ((target_class_id, "Classe cible"), (actual_class_id, "Autre classe")):
            connection.execute(
                "INSERT INTO academic_classes (id, tenant_id, name) VALUES (?, ?, ?)",
                (str(class_id_value), str(TENANT), class_name),
            )
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date, academic_year_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(period_id), str(TENANT), "Trimestre 1", "2026-09-01", "2026-12-20", str(year_id)),
        )
        connection.execute(
            """INSERT INTO student_assignments
            (id, tenant_id, student_id, academic_year_id, academic_class_id,
             academic_option_id, status, created_by, created_at, updated_at, closed_at)
            VALUES (?, ?, ?, ?, ?, NULL, 'ACTIVE', ?, ?, ?, NULL)""",
            (str(uuid4()), str(TENANT), str(student_id), str(year_id), str(actual_class_id),
             str(actor_id), now, now),
        )

    fee = service.create_fee_type(
        TENANT, "Frais cible", "Classe précise", "SCHOOL",
        Decimal("30.00"), Currency.CDF, period_id, "CLASS", actor_id, target_class_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)
    with pytest.raises(ValueError, match="affectation active"):
        service.assign_fee_type(TENANT, fee.id, student_id, period_id, actor_id)

    foreign_class_id = uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_classes (id, tenant_id, name) VALUES (?, ?, ?)",
            (str(foreign_class_id), str(OTHER_TENANT), "Classe étrangère"),
        )
    with pytest.raises(LookupError, match="Classe cible"):
        service.create_fee_type(
            TENANT, "Frais invalide", "Classe hors tenant", "SCHOOL",
            Decimal("30.00"), Currency.CDF, period_id, "CLASS", actor_id, foreign_class_id,
        )


def test_establishment_fee_applies_to_active_tenant_student_without_class_target():
    service, student_id = service_with_student()
    actor_id = uuid4()
    fee = service.create_fee_type(
        TENANT, "Frais établissement", "Pour les élèves actifs", "SCHOOL",
        Decimal("20.00"), Currency.USD, None, "ESTABLISHMENT", actor_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)
    assignment = service.assign_fee_type(TENANT, fee.id, student_id, None, actor_id)
    assert assignment.student_id == student_id
    assert assignment.snapshot_class_id is None



def test_class_fee_rejects_period_without_linked_academic_year():
    service, student_id = service_with_student()
    database = service._repository._database
    actor_id, class_id, period_id = uuid4(), uuid4(), uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_classes (id, tenant_id, name) VALUES (?, ?, ?)",
            (str(class_id), str(TENANT), "Classe sans année"),
        )
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) "
            "VALUES (?, ?, ?, ?, ?)",
            (str(period_id), str(TENANT), "Période historique", "2026-09-01", "2026-12-20"),
        )

    fee = service.create_fee_type(
        TENANT, "Frais classe", "Période sans année", "SCHOOL",
        Decimal("25.00"), Currency.CDF, period_id, "CLASS", actor_id, class_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)

    with pytest.raises(ValueError, match="annee scolaire"):
        service.assign_fee_type(TENANT, fee.id, student_id, period_id, actor_id)


def test_fee_assignment_rejects_inactive_student():
    service, student_id = service_with_student()
    actor_id = uuid4()
    fee = service.create_fee_type(
        TENANT, "Frais individuel", "Elève actif uniquement", "SCHOOL",
        Decimal("15.00"), Currency.CDF, None, "STUDENT", actor_id,
    )
    service.change_fee_type_status(TENANT, fee.id, "PUBLISHED", actor_id)
    with service._repository._database.connect() as connection:
        connection.execute(
            "UPDATE students SET active = 0 WHERE tenant_id = ? AND id = ?",
            (str(TENANT), str(student_id)),
        )

    with pytest.raises(LookupError, match="Eleve actif"):
        service.assign_fee_type(TENANT, fee.id, student_id, None, actor_id)



def test_concurrent_cashiers_cannot_overpay_the_same_charge(tmp_path):
    database_path = tmp_path / "billing-concurrency.db"
    database = SQLiteDatabase(database_path)
    database.initialize()
    student_id = uuid4()
    with database.connect() as connection:
        connection.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_id), str(TENANT), "Grace", "Hopper", None),
        )

    charge = BillingService(SQLiteBillingRepository(database)).create_charge(
        TENANT, student_id, "Annual fees", Decimal("100.00"), Currency.USD, None
    )
    services = [
        BillingService(SQLiteBillingRepository(SQLiteDatabase(database_path)))
        for _ in range(2)
    ]

    def submit_payment(index: int) -> str:
        try:
            services[index].record_payment(
                TENANT, charge.id, Decimal("60.00"), Currency.USD,
                f"cashier-payment-{index}", uuid4(),
            )
            return "accepted"
        except ValueError as exc:
            assert "solde" in str(exc)
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(submit_payment, (0, 1)))

    assert sorted(outcomes) == ["accepted", "rejected"]
    with database.connect() as connection:
        total = connection.execute(
            "SELECT SUM(CAST(amount AS NUMERIC)) FROM billing_payments "
            "WHERE tenant_id = ? AND charge_id = ? AND status = 'CONFIRMED'",
            (str(TENANT), str(charge.id)),
        ).fetchone()[0]
    assert Decimal(str(total)) == Decimal("60.00")
