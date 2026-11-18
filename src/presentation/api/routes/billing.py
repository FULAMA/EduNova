from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.billing.application.service import BillingService
from src.presentation.api.dependencies import get_billing_service
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_finance_manager_role, require_finance_role
from src.presentation.api.schemas.billing import (
    ArrearItemResponse,
    ArrearListResponse,
    BillingSummaryResponse,
    ChargeCreateRequest,
    ChargeResponse,
    PaymentCreateRequest,
    PaymentListResponse,
    PaymentResponse,
    CounterEntryResponse,
    PaymentCorrectionRequest,
    FeeTypeCreateRequest,
    FeeTypeResponse,
    FeeAssignmentRequest,
    FeeAssignmentResponse,
    ClassFeeAssignmentRequest,
    ClassFeeAssignmentResponse,
    CreateArrearReminderRequest,
    ArrearReminderResponse,
)
from src.shared.application.context.tenant_context import TenantContext
from src.identity.application.dto.authenticated_user import AuthenticatedUser


router = APIRouter(prefix="/billing", tags=["Billing"])
_finance = [Depends(require_finance_role())]


def _charge_response(charge) -> ChargeResponse:
    return ChargeResponse(id=charge.id, student_id=charge.student_id, description=charge.description,
                          amount=charge.amount.amount, currency=charge.amount.currency,
                          due_date=charge.due_date, status=charge.status)


def _payment_response(payment) -> PaymentResponse:
    return PaymentResponse(id=payment.id, charge_id=payment.charge_id, student_id=payment.student_id,
                           amount=payment.amount.amount, currency=payment.amount.currency,
                           idempotency_key=payment.idempotency_key, status=payment.status,
                           recorded_by=payment.recorded_by, recorded_at=payment.recorded_at,
                           receipt_number=payment.receipt_number, receipt_status=payment.receipt_status)


def _fee_type_response(item) -> FeeTypeResponse:
    return FeeTypeResponse(id=item.id, name=item.name, description=item.description, category=item.category,
                           amount=item.amount.amount, currency=item.amount.currency,
                           academic_period_id=item.academic_period_id, target_class_id=item.target_class_id, applicability=item.applicability,
                           status=item.status, version=item.version, created_by=item.created_by,
                           created_at=item.created_at, updated_at=item.updated_at)


def _fee_assignment_response(item) -> FeeAssignmentResponse:
    return FeeAssignmentResponse(id=item.id, fee_type_id=item.fee_type_id, fee_type_version=item.fee_type_version,
                                 student_id=item.student_id, academic_period_id=item.academic_period_id, snapshot_class_id=item.snapshot_class_id,
                                 charge_id=item.charge_id, amount=item.amount.amount, currency=item.amount.currency,
                                 created_by=item.created_by, created_at=item.created_at)


@router.post("/charges", response_model=ChargeResponse, status_code=status.HTTP_201_CREATED, dependencies=_finance)
def create_charge(data: ChargeCreateRequest, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context)):
    try:
        return _charge_response(service.create_charge(tenant.tenant_id, data.student_id, data.description, data.amount, data.currency, data.due_date))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Eleve introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/payments", response_model=PaymentResponse, dependencies=_finance)
def record_payment(data: PaymentCreateRequest, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _payment_response(service.record_payment(tenant.tenant_id, data.charge_id, data.amount, data.currency, data.idempotency_key, current_user.id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Frais introuvables dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409 if "idempotence" in str(exc) or "solde" in str(exc) or "devise" in str(exc) else 400, detail=str(exc)) from exc


@router.get("/payments", response_model=PaymentListResponse, dependencies=_finance)
def list_payments(
    student_id: UUID | None = Query(default=None),
    class_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status", max_length=40),
    recorded_from: date | None = Query(default=None),
    recorded_to: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: BillingService = Depends(get_billing_service),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PaymentListResponse:
    try:
        page = service.list_payments(
            tenant.tenant_id,
            student_id=student_id,
            class_id=class_id,
            status=status_filter,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            limit=limit,
            offset=offset,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Eleve introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PaymentListResponse(
        items=[_payment_response(item) for item in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/arrears", response_model=ArrearListResponse, dependencies=_finance)
def list_arrears(
    student_id: UUID | None = Query(default=None),
    class_id: UUID | None = Query(default=None),
    as_of: date | None = Query(default=None),
    overdue_only: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: BillingService = Depends(get_billing_service),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ArrearListResponse:
    try:
        page = service.list_arrears(
            tenant.tenant_id,
            student_id=student_id,
            class_id=class_id,
            as_of=as_of,
            overdue_only=overdue_only,
            limit=limit,
            offset=offset,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Eleve introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArrearListResponse(
        items=[
            ArrearItemResponse(
                charge_id=item.charge_id,
                student_id=item.student_id,
                description=item.description,
                currency=item.currency,
                amount_due=item.amount_due,
                amount_paid=item.amount_paid,
                amount_remaining=item.amount_remaining,
                due_date=item.due_date,
                charge_status=item.charge_status,
                overdue=item.overdue,
                class_id=item.class_id,
            )
            for item in page.items
        ],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/students/{student_id}/summary", response_model=BillingSummaryResponse, dependencies=_finance)
def get_billing_summary(student_id: UUID, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context)):
    try:
        summary = service.summary(tenant.tenant_id, student_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Eleve introuvable dans cet etablissement.") from exc
    return BillingSummaryResponse(charges=[_charge_response(item) for item in summary.charges], payments=[_payment_response(item) for item in summary.payments])


@router.get("/fee-types", response_model=list[FeeTypeResponse], dependencies=_finance)
def list_fee_types(service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context)):
    return [_fee_type_response(item) for item in service.list_fee_types(tenant.tenant_id)]


@router.post("/fee-types", response_model=FeeTypeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_finance_manager_role())])
def create_fee_type(data: FeeTypeCreateRequest, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        item = service.create_fee_type(tenant.tenant_id, data.name, data.description, data.category, data.amount, data.currency, data.academic_period_id, data.applicability, current_user.id, data.target_class_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _fee_type_response(item)


@router.post("/fee-types/{fee_type_id}/publish", response_model=FeeTypeResponse, dependencies=[Depends(require_finance_manager_role())])
def publish_fee_type(fee_type_id: UUID, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _fee_type_response(service.change_fee_type_status(tenant.tenant_id, fee_type_id, "PUBLISHED", current_user.id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Type de frais introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/fee-types/{fee_type_id}/archive", response_model=FeeTypeResponse, dependencies=[Depends(require_finance_manager_role())])
def archive_fee_type(fee_type_id: UUID, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _fee_type_response(service.change_fee_type_status(tenant.tenant_id, fee_type_id, "ARCHIVED", current_user.id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Type de frais introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/fee-types/{fee_type_id}/assign", response_model=FeeAssignmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_finance_manager_role())])
def assign_fee_type(fee_type_id: UUID, data: FeeAssignmentRequest, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _fee_assignment_response(service.assign_fee_type(tenant.tenant_id, fee_type_id, data.student_id, data.academic_period_id, current_user.id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc




@router.post(
    "/fee-types/{fee_type_id}/assign-class",
    response_model=ClassFeeAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_finance_manager_role())],
)
def assign_fee_type_to_class(
    fee_type_id: UUID,
    data: ClassFeeAssignmentRequest,
    service: BillingService = Depends(get_billing_service),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        result = service.assign_fee_type_to_class(
            tenant.tenant_id,
            fee_type_id,
            data.class_id,
            data.academic_period_id,
            current_user.id,
        )
        return ClassFeeAssignmentResponse(
            fee_type_id=result.fee_type_id,
            class_id=result.class_id,
            academic_period_id=result.academic_period_id,
            total_eligible_students=result.total_eligible_students,
            assigned_count=result.assigned_count,
            already_assigned_count=result.already_assigned_count,
            assignments=[_fee_assignment_response(item) for item in result.assignments],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409 if "publie" in str(exc) or "cible" in str(exc) else 400, detail=str(exc)) from exc


@router.post("/payments/{payment_id}/correction", response_model=CounterEntryResponse, dependencies=_finance)
def correct_payment(data: PaymentCorrectionRequest, payment_id: UUID, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context), current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        entry = service.reverse_payment(tenant.tenant_id, payment_id, data.reason, current_user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Paiement introuvable dans cet etablissement.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return CounterEntryResponse(id=entry.id, original_payment_id=entry.original_payment_id, amount=entry.amount.amount, currency=entry.amount.currency, reason=entry.reason, recorded_by=entry.recorded_by, recorded_at=entry.recorded_at)


@router.get("/receipts/{receipt_number}/pdf", dependencies=_finance)
def get_receipt_pdf(receipt_number: str, service: BillingService = Depends(get_billing_service), tenant: TenantContext = Depends(get_tenant_context)):
    try:
        row = service.receipt_pdf(tenant.tenant_id, receipt_number)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Recu introuvable dans cet etablissement.") from exc
    text = f"EduNova receipt {row['number']} | {row['amount']} {row['currency']} | {row['status']}"
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 50 760 Td ({escaped}) Tj ET".encode("ascii", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    body = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode())
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    body.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    body.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return Response(content=bytes(body), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="receipt-{receipt_number}.pdf"'})



@router.post(
    "/arrears/{charge_id}/reminders",
    response_model=ArrearReminderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=_finance,
)
def record_arrear_reminder(
    charge_id: UUID,
    data: CreateArrearReminderRequest,
    service: BillingService = Depends(get_billing_service),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        reminder = service.record_arrear_reminder(
            tenant.tenant_id,
            charge_id,
            data.channel,
            data.recipient,
            data.notes,
            current_user.id,
        )
        return ArrearReminderResponse(
            id=reminder.id,
            tenant_id=reminder.tenant_id,
            charge_id=reminder.charge_id,
            student_id=reminder.student_id,
            channel=reminder.channel,
            recipient=reminder.recipient,
            notes=reminder.notes,
            sent_at=reminder.sent_at,
            sent_by=reminder.sent_by,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/arrears/{charge_id}/reminders",
    response_model=list[ArrearReminderResponse],
    dependencies=_finance,
)
def list_arrear_reminders(
    charge_id: UUID,
    service: BillingService = Depends(get_billing_service),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        reminders = service.list_arrear_reminders(tenant.tenant_id, charge_id)
        return [
            ArrearReminderResponse(
                id=r.id,
                tenant_id=r.tenant_id,
                charge_id=r.charge_id,
                student_id=r.student_id,
                channel=r.channel,
                recipient=r.recipient,
                notes=r.notes,
                sent_at=r.sent_at,
                sent_by=r.sent_by,
            )
            for r in reminders
        ]
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
