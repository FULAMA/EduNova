import { describe, expect, it } from 'vitest'

import { formatDate, formatDateTime, formatMoney } from './format'

describe('formatMoney', () => {
  it('groups thousands and keeps two decimals', () => {
    expect(formatMoney('1250.5', 'USD')).toBe('1\u202f250,50\u00a0USD')
    expect(formatMoney('100', 'CDF')).toBe('100,00\u00a0CDF')
  })

  it('stays exact on very large amounts (no float arithmetic)', () => {
    expect(formatMoney('12345678901234567.89', 'CDF')).toBe(
      '12\u202f345\u202f678\u202f901\u202f234\u202f567,89\u00a0CDF',
    )
  })

  it('always keeps the currency code, never merging USD and CDF', () => {
    expect(formatMoney('10.00', 'USD')).not.toBe(formatMoney('10.00', 'CDF'))
  })

  it('returns the raw value when it is not a decimal', () => {
    expect(formatMoney('abc', 'USD')).toBe('abc USD')
  })
})

describe('dates', () => {
  it('formats an ISO date without timezone shift', () => {
    expect(formatDate('2026-10-31')).toBe('31/10/2026')
    expect(formatDate('n/a')).toBe('n/a')
  })

  it('formats a datetime and keeps invalid input as is', () => {
    expect(formatDateTime('2026-10-20T12:00:00Z')).toMatch(/2026/)
    expect(formatDateTime('invalid')).toBe('invalid')
  })
})