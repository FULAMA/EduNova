import { describe, expect, it, vi } from 'vitest'

import { apiRequest } from '../../shared/api/client'
import { listAcademicClasses } from './classes.service'

vi.mock('../../shared/api/client', () => ({
  apiRequest: vi.fn(),
}))

describe('classes service', () => {
  it('uses the authenticated classes endpoint', async () => {
    vi.mocked(apiRequest).mockResolvedValue([])

    await listAcademicClasses()

    expect(apiRequest).toHaveBeenCalledWith('/classes', { authenticated: true })
  })

  it('posts assignment to /classes/:id/subjects with authenticated client', async () => {
    const mockCreated = {
      id: 'cs-1',
      academic_class_id: 'class-1',
      subject_id: 'subj-1',
      coefficient: 3,
      academic_option_id: null,
      active: true,
    }
    vi.mocked(apiRequest).mockResolvedValue(mockCreated)

    const { assignSubjectToClass } = await import('./classes.service')
    const result = await assignSubjectToClass('class-1', {
      subject_id: 'subj-1',
      coefficient: 3,
    })

    expect(result).toEqual(mockCreated)
    expect(apiRequest).toHaveBeenCalledWith('/classes/class-1/subjects', {
      method: 'POST',
      authenticated: true,
      body: JSON.stringify({ subject_id: 'subj-1', coefficient: 3 }),
    })
  })
})
