from fastapi import APIRouter, Depends

from src.academic.application.use_cases.get_direction_dashboard import (
    GetDirectionDashboard,
)
from src.billing.domain.money import Currency
from src.presentation.api.dependencies import get_direction_dashboard_use_case
from src.presentation.api.dependencies.auth import get_tenant_context, require_role
from src.presentation.api.schemas.dashboard import (
    ClassFinancialSituation,
    ClassHeadcount,
    CurrencyAmount,
    DirectionDashboardResponse,
    RecoveryRate,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/direction",
    response_model=DirectionDashboardResponse,
    dependencies=[Depends(require_role("ADMIN", "DIRECTION"))],
)
def get_direction_dashboard(
    use_case: GetDirectionDashboard = Depends(get_direction_dashboard_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DirectionDashboardResponse:
    view = use_case.execute(tenant.tenant_id)
    return DirectionDashboardResponse(
        active_students=view.active_students,
        headcount_by_class=[
            ClassHeadcount(
                class_id=item.class_id,
                class_name=item.class_name,
                active_students=item.active_students,
            )
            for item in view.headcount_by_class
        ],
        expected_amounts=[
            CurrencyAmount(currency=Currency(item.currency), amount=item.amount)
            for item in view.expected_amounts
        ],
        paid_amounts=[
            CurrencyAmount(currency=Currency(item.currency), amount=item.amount)
            for item in view.paid_amounts
        ],
        remaining_amounts=[
            CurrencyAmount(currency=Currency(item.currency), amount=item.amount)
            for item in view.remaining_amounts
        ],
        recovery_rates=[
            RecoveryRate(
                currency=Currency(item.currency),
                rate_percent=item.rate_percent,
            )
            for item in view.recovery_rates
        ],
        financial_by_class=[
            ClassFinancialSituation(
                class_id=item.class_id,
                class_name=item.class_name,
                expected=[
                    CurrencyAmount(currency=Currency(entry.currency), amount=entry.amount)
                    for entry in item.expected
                ],
                paid=[
                    CurrencyAmount(currency=Currency(entry.currency), amount=entry.amount)
                    for entry in item.paid
                ],
                remaining=[
                    CurrencyAmount(currency=Currency(entry.currency), amount=entry.amount)
                    for entry in item.remaining
                ],
            )
            for item in view.financial_by_class
        ],
    )
