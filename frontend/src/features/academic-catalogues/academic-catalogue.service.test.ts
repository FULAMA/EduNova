import { afterEach, describe, expect, it, vi } from 'vitest'

import { clearSession, saveSession } from '../auth/services/auth.storage'
import { createAcademicPeriod, createSubject, listAcademicPeriods, listSubjects, updateSubject } from './academic-catalogue.service'

describe('academic catalogue service', () => {
  afterEach(() => { vi.restoreAllMocks(); clearSession() })

  it('reads tenant catalogues and passes an encoded search term', async () => {
    saveSession({ accessToken: 'token', refreshToken: 'refresh', email: 'admin@test', tenantId: 'tenant' })
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify([{ id: 's1', name: 'Mathématiques', code: 'MATH', coefficient: 2, active: true }]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 }))
    await expect(listSubjects('math & sciences')).resolves.toHaveLength(1)
    await expect(listAcademicPeriods()).resolves.toEqual([])
    expect(String(fetchMock.mock.calls[0][0])).toContain('search=math%20%26%20sciences')
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer token')
  })

  it('creates and updates persisted subjects through authenticated API contracts', async () => {
    saveSession({ accessToken: 'token', refreshToken: 'refresh', email: 'admin@test', tenantId: 'tenant' })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ id: 's1', name: 'Maths', code: 'MATH', coefficient: 2, active: true }), { status: 200 }))
    await createSubject({ name: 'Maths', code: 'MATH', coefficient: 2 })
    await updateSubject('s1', { name: 'Mathématiques', code: 'MATH' })
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: 'POST' })
    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: 'PUT' })
  })

  it('creates periods with an explicit school year and tenant authentication', async () => {
    saveSession({ accessToken: 'token', refreshToken: 'refresh', email: 'admin@test', tenantId: 'tenant' })
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({
      id: 'p1', name: 'Trimestre 1', academic_year_id: 'year-1', start_date: '2026-09-01', end_date: '2026-12-20',
    }), { status: 201 }))
    await expect(createAcademicPeriod({
      academic_year_id: 'year-1', name: 'Trimestre 1', start_date: '2026-09-01', end_date: '2026-12-20',
    })).resolves.toMatchObject({ academic_year_id: 'year-1' })
    expect(fetchMock.mock.calls[0][0]).toContain('/academic-catalogues/periods')
    expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toMatchObject({ academic_year_id: 'year-1' })
  })
})
