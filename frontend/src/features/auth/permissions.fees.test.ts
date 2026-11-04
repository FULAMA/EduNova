import { describe, expect, it } from 'vitest'

import { canManageFeeCatalog } from './permissions'

describe('canManageFeeCatalog', () => {
  it('allows ADMIN and DIRECTION only', () => {
    expect(canManageFeeCatalog('ADMIN')).toBe(true)
    expect(canManageFeeCatalog('DIRECTION')).toBe(true)
    for (const role of ['ACCOUNTANT', 'CASHIER', 'STUDENT', undefined]) {
      expect(canManageFeeCatalog(role)).toBe(false)
    }
  })
})