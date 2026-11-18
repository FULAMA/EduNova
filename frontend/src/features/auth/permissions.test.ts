import { describe, expect, it } from 'vitest'

import { canAccess, canManageClassSubjects } from './permissions'

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

  it('lets DIRECTION open students, classes and finance', () => {
    expect(canAccess('DIRECTION', 'students')).toBe(true)
    expect(canAccess('DIRECTION', 'finance')).toBe(true)
    expect(canAccess('DIRECTION', 'classes')).toBe(true)
    // Refuses ADMIN exclusive modules for DIRECTION
    expect(canAccess('DIRECTION', 'enrollments')).toBe(false)
    expect(canAccess('DIRECTION', 'attendance')).toBe(false)
    expect(canAccess('DIRECTION', 'academic-catalogues')).toBe(false)
  })

  it('reserves class subject assignment to ADMIN only', () => {
    expect(canManageClassSubjects('ADMIN')).toBe(true)
    expect(canManageClassSubjects('DIRECTION')).toBe(false)
    expect(canManageClassSubjects('ACCOUNTANT')).toBe(false)
    expect(canManageClassSubjects('CASHIER')).toBe(false)
    expect(canManageClassSubjects(undefined)).toBe(false)
  })

  it('denies unknown or missing roles', () => {
    expect(canAccess(undefined, 'dashboard')).toBe(false)
    expect(canAccess('PARENT', 'dashboard')).toBe(false)
  })

  it('keeps parent, student and teacher PWA spaces role-scoped', () => {
    expect(canAccess('PARENT', 'parent-portal')).toBe(true)
    expect(canAccess('PARENT', 'student-portal')).toBe(false)
    expect(canAccess('STUDENT', 'student-portal')).toBe(true)
    expect(canAccess('STUDENT', 'parent-portal')).toBe(false)
    expect(canAccess('PROF', 'teacher-portal')).toBe(true)
    expect(canAccess('TEACHER', 'teacher-portal')).toBe(true)
    expect(canAccess('PROF', 'students')).toBe(false)
  })
})
