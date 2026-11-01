import { describe, expect, it, vi } from 'vitest'

import { apiRequest } from '../../shared/api/client'
import { closeAcademicYear, createAcademicYear, listStudentAssignments } from './enrollment.service'

vi.mock('../../shared/api/client', () => ({
  apiRequest: vi.fn(),
}))

describe('enrollment service', () => {
  it('uses the authenticated academic years endpoint', async () => {
    vi.mocked(apiRequest).mockResolvedValue([])

    await createAcademicYear({ label: '2026-2027', start_date: '2026-09-01', end_date: '2027-07-31' })

    expect(apiRequest).toHaveBeenCalledWith('/academic-years', expect.objectContaining({
      method: 'POST',
      authenticated: true,
    }))
  })

  it('scopes assignment reads to the selected student and authenticated client', async () => {
    vi.mocked(apiRequest).mockResolvedValue([])

    await listStudentAssignments('student/1')

    expect(apiRequest).toHaveBeenCalledWith('/student-assignments?student_id=student%2F1', { authenticated: true })
  })

  it('posts status changes to activate, cancel or close an assignment', async () => {
    vi.mocked(apiRequest).mockResolvedValue({ id: 'assign-1', status: 'ACTIVE' })

    const { changeStudentAssignmentStatus } = await import('./enrollment.service')
    await changeStudentAssignmentStatus('assign-1', 'activate')
    expect(apiRequest).toHaveBeenCalledWith('/student-assignments/assign-1/activate', {
      method: 'POST',
      authenticated: true,
    })

    await changeStudentAssignmentStatus('assign-1', 'cancel')
    expect(apiRequest).toHaveBeenCalledWith('/student-assignments/assign-1/cancel', {
      method: 'POST',
      authenticated: true,
    })

    await changeStudentAssignmentStatus('assign-1', 'close')
    expect(apiRequest).toHaveBeenCalledWith('/student-assignments/assign-1/close', {
      method: 'POST',
      authenticated: true,
    })
  })
})


describe('academic year lifecycle client', () => {
  it('posts the explicit close action to the tenant-authenticated API', async () => {
    vi.mocked(apiRequest).mockResolvedValue({ id: 'year-1', status: 'CLOSED' })
    await closeAcademicYear('year/1')
    expect(apiRequest).toHaveBeenCalledWith('/academic-years/year%2F1/close', {
      method: 'POST', authenticated: true,
    })
  })
})
