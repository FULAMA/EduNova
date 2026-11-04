import { describe, expect, it } from 'vitest'

import { canAccess } from './permissions'

describe('canAccess', () => {
  it('lets ADMIN open every module', () => {
    for (const m of ['students', 'classes', 'enrollments', 'attendance', 'finance', 'academic-catalogues'] as const) {
      expect(canAccess('ADMIN', m)).toBe(true)
    }
  })

  it('limits STUDENT to the dashboard (student portal)', () => {
    expect(canAccess('STUDENT', 'dashboard')).toBe(true)
    expect(canAccess('STUDENT', 'students')).toBe(false)
    expect(canAccess('STUDENT', 'finance')).toBe(false)
  })

  it('gives cashiers and accountants finance without the student directory', () => {
    for (const role of ['ACCOUNTANT', 'CASHIER']) {
      expect(canAccess(role, 'finance')).toBe(true)
      expect(canAccess(role, 'students')).toBe(false)
    }
  })

  it('lets DIRECTION open students and finance', () => {
    expect(canAccess('DIRECTION', 'students')).toBe(true)
    expect(canAccess('DIRECTION', 'finance')).toBe(true)
    expect(canAccess('DIRECTION', 'classes')).toBe(false)
  })

  it('denies unknown or missing roles', () => {
    expect(canAccess(undefined, 'dashboard')).toBe(false)
    expect(canAccess('PARENT', 'dashboard')).toBe(false)
  })
})