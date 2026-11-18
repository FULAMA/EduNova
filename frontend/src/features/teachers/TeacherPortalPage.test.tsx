// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, expect, it, vi } from 'vitest'

import TeacherPortalPage from './TeacherPortalPage'
import { getMyTeacherAssignments } from './teacher-portal.service'

vi.mock('./teacher-portal.service', () => ({ getMyTeacherAssignments: vi.fn() }))

const mockAssignments = vi.mocked(getMyTeacherAssignments)
let root: Root | undefined
let host: HTMLDivElement

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  vi.clearAllMocks()
})

it('shows the teacher assignment summary without exposing raw identifiers', async () => {
  mockAssignments.mockResolvedValue([{
    tenant_id: 'tenant-id', teacher_user_id: 'teacher-id',
    academic_class_id: 'class-id', academic_class_label: '6e Math-Physique',
    subject_id: 'subject-id', subject_label: 'Physique',
    academic_year_id: 'year-id', academic_year_label: '2026-2027', assigned_by: 'admin-id',
    assigned_at: '2026-06-20T12:00:00Z',
  }])
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)

  await act(async () => root?.render(createElement(TeacherPortalPage)))

  expect(host.textContent).toContain('1 affectation enregistrée')
  expect(host.textContent).toContain('Physique')
  expect(host.textContent).toContain('6e Math-Physique')
  expect(host.textContent).toContain('2026-2027')
  expect(host.textContent).not.toContain('class-id')
  expect(host.textContent).not.toContain('subject-id')
})
