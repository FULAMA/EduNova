import { describe, expect, it } from 'vitest'

import { canManageFeeCatalog, canManageStudents } from './permissions'

describe('canManageFeeCatalog', () => {
  it('allows ADMIN and DIRECTION only', () => {
    expect(canManageFeeCatalog('ADMIN')).toBe(true)
    expect(canManageFeeCatalog('DIRECTION')).toBe(true)
    for (const role of ['ACCOUNTANT', 'CASHIER', 'STUDENT', undefined]) {
      expect(canManageFeeCatalog(role)).toBe(false)
    }
  })
})

describe('canManageStudents', () => {
  it('allows ADMIN and DIRECTION only', () => {
    expect(canManageStudents('ADMIN')).toBe(true)
    expect(canManageStudents('DIRECTION')).toBe(true)
    for (const role of ['ACCOUNTANT', 'CASHIER', 'STUDENT', undefined]) {
      expect(canManageStudents(role)).toBe(false)
    }
  })
})