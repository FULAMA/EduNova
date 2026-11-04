import { describe, expect, it } from 'vitest'

import { ApiError } from '../../shared/api/client'
import { describeFinanceError } from './finance.errors'

describe('describeFinanceError', () => {
  it('shows the backend message for business and validation errors', () => {
    for (const status of [0, 400, 404, 409, 422]) {
      expect(describeFinanceError(new ApiError(status, 'Message du serveur'), 'Repli')).toBe('Message du serveur')
    }
  })

  it('uses fixed texts for 401 and 403', () => {
    expect(describeFinanceError(new ApiError(401, 'x'), 'Repli')).toContain('session')
    expect(describeFinanceError(new ApiError(403, 'x'), 'Repli')).toContain('rôle')
  })

  it('falls back for server errors and unknown failures', () => {
    expect(describeFinanceError(new ApiError(500, 'interne'), 'Repli')).toBe('Repli')
    expect(describeFinanceError(new Error('boom'), 'Repli')).toBe('Repli')
  })
})