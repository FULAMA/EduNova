// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { saveBlob } from '../../shared/utils/download'
import { CurrentUserContext } from '../auth/components/current-user.context'
import type { AuthenticatedUser } from '../auth/services/auth.service'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import FinancePage from './FinancePage'
import { correctPayment, downloadReceiptPdf, getBillingSummary, type BillingSummary } from './finance.service'

vi.mock('./FeeCatalogPanel', () => ({ default: () => null }))
vi.mock('./finance.service', () => ({
  getBillingSummary: vi.fn(),
  createCharge: vi.fn(),
  recordPayment: vi.fn(),
  correctPayment: vi.fn(),
  downloadReceiptPdf: vi.fn(),
}))
vi.mock('../students/services/student.service', () => ({ listStudents: vi.fn() }))
vi.mock('../../shared/utils/download', () => ({ saveBlob: vi.fn() }))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const user: AuthenticatedUser = {
  id: 'u1', email: 'admin@example.test', role: 'ADMIN', is_active: true, two_factor_enabled: false,
}

const summary = {
  charges: [{ id: 'c1', student_id: 's1', description: 'Minerval', amount: '100.00', currency: 'USD', due_date: null, status: 'OPEN' }],
  payments: [{
    id: 'p1', charge_id: 'c1', student_id: 's1', amount: '40.00', currency: 'USD', status: 'RECORDED',
    recorded_at: '2026-10-20T12:00:00Z', receipt_number: 'R-001', receipt_status: 'ISSUED',
  }],
} as unknown as BillingSummary

let root: Root | undefined
let host: HTMLDivElement

async function flush() {
  await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)) })
}

function setValue(element: HTMLInputElement | HTMLSelectElement, value: string) {
  const proto = element instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype
  act(() => {
    Object.getOwnPropertyDescriptor(proto, 'value')!.set!.call(element, value)
    element.dispatchEvent(new Event(element instanceof HTMLSelectElement ? 'change' : 'input', { bubbles: true }))
  })
}

function button(label: string): HTMLButtonElement | undefined {
  return [...host.querySelectorAll('button')].find((item) => item.textContent?.trim() === label)
}

async function renderWithStudent() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(CurrentUserContext.Provider, { value: user }, createElement(FinancePage)))
  })
  await flush()
  setValue(host.querySelector('select') as HTMLSelectElement, 's1')
  await flush()
}

beforeEach(() => {
  vi.mocked(listStudents).mockResolvedValue([
    { id: 's1', firstName: 'Marie', lastName: 'Kabila' } as unknown as Student,
  ])
  vi.mocked(getBillingSummary).mockResolvedValue(summary)
})

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  vi.clearAllMocks()
})

describe('FinancePage', () => {
  it('shows amounts with their currency and downloads a receipt through the API', async () => {
    const blob = new Blob(['%PDF'])
    vi.mocked(downloadReceiptPdf).mockResolvedValue(blob)
    await renderWithStudent()

    expect(host.textContent).toContain('40,00\u00a0USD')
    expect(host.textContent).toContain('R-001')

    await act(async () => button('Reçu PDF')!.click())
    await flush()

    expect(downloadReceiptPdf).toHaveBeenCalledWith('R-001')
    expect(saveBlob).toHaveBeenCalledWith(blob, 'recu-R-001.pdf')
  })

  it('requires an explicit confirmation before recording a correction', async () => {
    vi.mocked(correctPayment).mockResolvedValue({ amount: '40.00', currency: 'USD' } as never)
    await renderWithStudent()

    const form = host.querySelector('form[aria-label="Corriger un paiement"]') as HTMLFormElement
    setValue(form.querySelector('select') as HTMLSelectElement, 'p1')
    setValue(form.querySelector('input') as HTMLInputElement, 'Erreur de saisie')
    act(() => { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })) })

    expect(correctPayment).not.toHaveBeenCalled()
    expect(host.textContent).toContain('Confirmer ?')

    await act(async () => button('Confirmer')!.click())
    await flush()

    expect(correctPayment).toHaveBeenCalledWith('p1', 'Erreur de saisie')
  })
})