import { describe, expect, it } from 'vitest'

import { ApiError } from '../../shared/api/client'
import { describeEnrollmentError } from './enrollment.errors'

describe('describeEnrollmentError', () => {
  it('shows the backend message for business, validation and network errors', () => {
    for (const status of [0, 400, 404, 409, 422]) {
      expect(describeEnrollmentError(new ApiError(status, 'Message du serveur'), 'Repli')).toBe('Message du serveur')
    }
  })

  it('uses fixed texts for 401 and 403', () => {
    expect(describeEnrollmentError(new ApiError(401, 'x'), 'Repli')).toContain('session')
    expect(describeEnrollmentError(new ApiError(403, 'x'), 'Repli')).toContain('rôle')
  })

  it('falls back for server errors and unknown failures', () => {
    expect(describeEnrollmentError(new ApiError(500, 'interne'), 'Repli')).toBe('Repli')
    expect(describeEnrollmentError(new Error('boom'), 'Repli')).toBe('Repli')
  })
})