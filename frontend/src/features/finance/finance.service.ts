import { apiRequest } from '../../shared/api/client'

export type Currency = 'USD' | 'CDF'
export type Charge = { id: string; student_id: string; description: string; amount: string; currency: Currency; due_date: string | null; status: string }
export type Payment = { id: string; charge_id: string; student_id: string; amount: string; currency: Currency; status: string; recorded_at: string; receipt_number: string; receipt_status: string }
export type BillingSummary = { charges: Charge[]; payments: Payment[] }
export type FeeType = { id: string; name: string; description: string; category: string; amount: string; currency: Currency; academic_period_id: string | null; applicability: string; status: string; version: number; created_by: string; created_at: string; updated_at: string }

export function getBillingSummary(studentId: string): Promise<BillingSummary> {
  return apiRequest(`/billing/students/${encodeURIComponent(studentId)}/summary`, { authenticated: true })
}

export function createCharge(payload: { student_id: string; description: string; amount: string; currency: Currency; due_date?: string }) {
  return apiRequest<Charge>('/billing/charges', { method: 'POST', authenticated: true, body: JSON.stringify(payload) })
}

export function recordPayment(payload: { charge_id: string; amount: string; currency: Currency; idempotency_key: string }) {
  return apiRequest<Payment>('/billing/payments', { method: 'POST', authenticated: true, body: JSON.stringify(payload) })
}

export function correctPayment(paymentId: string, reason: string) {
  return apiRequest(`/billing/payments/${encodeURIComponent(paymentId)}/correction`, { method: 'POST', authenticated: true, body: JSON.stringify({ reason }) })
}

export function listFeeTypes(): Promise<FeeType[]> {
  return apiRequest('/billing/fee-types', { authenticated: true })
}

export function createFeeType(payload: { name: string; category: string; amount: string; currency: Currency; description?: string }) {
  return apiRequest<FeeType>('/billing/fee-types', { method: 'POST', authenticated: true, body: JSON.stringify(payload) })
}

export function updateFeeTypeStatus(id: string, status: 'PUBLISHED' | 'ARCHIVED') {
  return apiRequest<FeeType>(`/billing/fee-types/${encodeURIComponent(id)}/${status === 'PUBLISHED' ? 'publish' : 'archive'}`, { method: 'POST', authenticated: true })
}

export function assignFeeType(id: string, studentId: string) {
  return apiRequest(`/billing/fee-types/${encodeURIComponent(id)}/assign`, { method: 'POST', authenticated: true, body: JSON.stringify({ student_id: studentId }) })
}

