from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from src.academic.application.dto.direction_dashboard import (
    ClassFinancialSituationView,
    ClassHeadcountView,
    CurrencyAmountView,
    DirectionDashboardView,
    RecoveryRateView,
)


def _money_map_to_tuple(values: dict[str, Decimal]) -> tuple[CurrencyAmountView, ...]:
    return tuple(
        CurrencyAmountView(currency=currency, amount=amount.quantize(Decimal("0.01")))
        for currency, amount in sorted(values.items())
        if amount != 0
    )


def _add_amount(bucket: dict[str, Decimal], currency: str, amount: Decimal) -> None:
    bucket[currency] = bucket.get(currency, Decimal("0")) + amount


class GetDirectionDashboard:
    def __init__(self, database):
        self._database = database

    def execute(self, tenant_id: UUID) -> DirectionDashboardView:
        with self._database.connect() as connection:
            active_students = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM students
                WHERE tenant_id = ? AND active = 1
                """,
                (str(tenant_id),),
            ).fetchone()["total"]

            headcount_rows = connection.execute(
                """
                SELECT ac.id AS class_id, ac.name AS class_name, COUNT(*) AS active_students
                FROM student_assignments sa
                JOIN academic_classes ac
                  ON ac.tenant_id = sa.tenant_id AND ac.id = sa.academic_class_id
                JOIN students s
                  ON s.tenant_id = sa.tenant_id AND s.id = sa.student_id
                WHERE sa.tenant_id = ?
                  AND sa.status = 'ACTIVE'
                  AND s.active = 1
                GROUP BY ac.id, ac.name
                ORDER BY ac.name, ac.id
                """,
                (str(tenant_id),),
            ).fetchall()

            charge_rows = connection.execute(
                """
                SELECT
                    c.id,
                    c.student_id,
                    c.currency,
                    CAST(c.amount AS DECIMAL) AS amount_due,
                    COALESCE((
                        SELECT SUM(CAST(p.amount AS DECIMAL))
                        FROM billing_payments p
                        WHERE p.tenant_id = c.tenant_id
                          AND p.charge_id = c.id
                          AND p.status = 'CONFIRMED'
                    ), 0) - COALESCE((
                        SELECT SUM(CAST(e.amount AS DECIMAL))
                        FROM billing_counter_entries e
                        JOIN billing_payments p
                          ON p.tenant_id = e.tenant_id AND p.id = e.original_payment_id
                        WHERE e.tenant_id = c.tenant_id
                          AND p.charge_id = c.id
                    ), 0) AS amount_paid,
                    (
                        SELECT sa.academic_class_id
                        FROM student_assignments sa
                        WHERE sa.tenant_id = c.tenant_id
                          AND sa.student_id = c.student_id
                          AND sa.status = 'ACTIVE'
                        ORDER BY sa.updated_at DESC, sa.id DESC
                        LIMIT 1
                    ) AS class_id
                FROM billing_charges c
                WHERE c.tenant_id = ? AND c.status = 'OPEN'
                """,
                (str(tenant_id),),
            ).fetchall()

        class_names = {
            UUID(row["class_id"]): row["class_name"] for row in headcount_rows
        }

        expected: dict[str, Decimal] = {}
        paid: dict[str, Decimal] = {}
        remaining: dict[str, Decimal] = {}
        by_class_expected: dict[UUID | None, dict[str, Decimal]] = defaultdict(dict)
        by_class_paid: dict[UUID | None, dict[str, Decimal]] = defaultdict(dict)
        by_class_remaining: dict[UUID | None, dict[str, Decimal]] = defaultdict(dict)

        for row in charge_rows:
            currency = row["currency"]
            amount_due = Decimal(str(row["amount_due"]))
            amount_paid = Decimal(str(row["amount_paid"]))
            amount_remaining = amount_due - amount_paid
            if amount_remaining < 0:
                amount_remaining = Decimal("0")

            _add_amount(expected, currency, amount_due)
            _add_amount(paid, currency, amount_paid)
            _add_amount(remaining, currency, amount_remaining)

            class_key = UUID(row["class_id"]) if row["class_id"] else None
            _add_amount(by_class_expected[class_key], currency, amount_due)
            _add_amount(by_class_paid[class_key], currency, amount_paid)
            _add_amount(by_class_remaining[class_key], currency, amount_remaining)

        recovery_rates: list[RecoveryRateView] = []
        for currency in sorted(set(expected) | set(paid)):
            due = expected.get(currency, Decimal("0"))
            received = paid.get(currency, Decimal("0"))
            if due == 0:
                rate: Decimal | None = None
            else:
                rate = ((received / due) * Decimal("100")).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            recovery_rates.append(
                RecoveryRateView(currency=currency, rate_percent=rate)
            )

        financial_by_class: list[ClassFinancialSituationView] = []
        class_ids = {
            class_id
            for class_id in (
                set(by_class_expected)
                | set(by_class_paid)
                | set(by_class_remaining)
                | set(class_names)
            )
            if class_id is not None
        }
        for class_id in sorted(
            class_ids, key=lambda value: (class_names.get(value, ""), str(value))
        ):
            financial_by_class.append(
                ClassFinancialSituationView(
                    class_id=class_id,
                    class_name=class_names.get(class_id, "Classe inconnue"),
                    expected=_money_map_to_tuple(by_class_expected.get(class_id, {})),
                    paid=_money_map_to_tuple(by_class_paid.get(class_id, {})),
                    remaining=_money_map_to_tuple(
                        by_class_remaining.get(class_id, {})
                    ),
                )
            )

        return DirectionDashboardView(
            active_students=int(active_students),
            headcount_by_class=tuple(
                ClassHeadcountView(
                    class_id=UUID(row["class_id"]),
                    class_name=row["class_name"],
                    active_students=int(row["active_students"]),
                )
                for row in headcount_rows
            ),
            expected_amounts=_money_map_to_tuple(expected),
            paid_amounts=_money_map_to_tuple(paid),
            remaining_amounts=_money_map_to_tuple(remaining),
            recovery_rates=tuple(recovery_rates),
            financial_by_class=tuple(financial_by_class),
        )
