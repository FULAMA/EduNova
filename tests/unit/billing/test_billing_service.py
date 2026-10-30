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
