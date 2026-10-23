import { afterEach, describe, expect, it, vi } from 'vitest'

import { apiRequest } from '../../shared/api/client'
import { createCharge, getBillingSummary, recordPayment } from './finance.service'

vi.mock('../../shared/api/client', () => ({ apiRequest: vi.fn() }))
const mockedRequest = vi.mocked(apiRequest)

describe('finance.service', () => {
  afterEach(() => vi.resetAllMocks())

  it('uses authenticated requests and keeps the currency explicit', async () => {
    mockedRequest.mockResolvedValueOnce({ charges: [], payments: [] })
      .mockResolvedValueOnce({ id: 'charge-1' })
      .mockResolvedValueOnce({ id: 'payment-1', currency: 'CDF' })

    await getBillingSummary('student/1')
    await createCharge({ student_id: 'student-1', description: 'Frais', amount: '10.00', currency: 'USD' })
    await recordPayment({ charge_id: 'charge-1', amount: '10.00', currency: 'CDF', idempotency_key: 'payment-1' })

    expect(mockedRequest.mock.calls[0][1]).toEqual({ authenticated: true })
    expect(mockedRequest.mock.calls[1][1]).toMatchObject({ method: 'POST', authenticated: true })
    expect(JSON.parse(String(mockedRequest.mock.calls[2][1]?.body))).toMatchObject({ currency: 'CDF' })
  })
})

