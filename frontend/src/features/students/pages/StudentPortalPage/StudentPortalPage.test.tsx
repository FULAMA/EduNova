// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, expect, it, vi } from 'vitest'

import { ApiError } from '../../../../shared/api/client'
import StudentPortalPage from './StudentPortalPage'
import {
  getMyAcademicPeriods,
  getMyAcademicRecord,
  getMyAttendance,
  getMyReportCards,
  getMyStudentProfile,
} from '../../services/student-portal.service'

vi.mock('../../services/student-portal.service', () => ({
  getMyStudentProfile: vi.fn(),
  getMyAcademicPeriods: vi.fn(),
  getMyAcademicRecord: vi.fn(),
  getMyAttendance: vi.fn(),
  getMyReportCards: vi.fn(),
}))

const mockProfile = vi.mocked(getMyStudentProfile)
const mockPeriods = vi.mocked(getMyAcademicPeriods)
const mockRecord = vi.mocked(getMyAcademicRecord)
const mockAttendance = vi.mocked(getMyAttendance)
const mockReportCards = vi.mocked(getMyReportCards)
let root: Root | undefined
let host: HTMLDivElement

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  vi.clearAllMocks()
})

function setupProfile() {
  mockProfile.mockResolvedValue({
    student: { id: 'student-1', first_name: 'Ada', last_name: 'Lovelace', email: 'ada@example.test', active: true },
    assignment: null,
    academic_year: null,
  })
  mockPeriods.mockResolvedValue([])
  mockAttendance.mockResolvedValue({
    records: [],
    statistics: { total_sessions: 0, absences: 0, justified_absences: 0, unjustified_absences: 0, lates: 0, attendance_rate: null },
  })
  mockReportCards.mockResolvedValue([])
}

it('renders the authenticated student profile and explicit unavailable data state', async () => {
  setupProfile()
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  await act(async () => root?.render(createElement(StudentPortalPage)))

  expect(host.textContent).toContain('Ada Lovelace')
  expect(host.textContent).toContain('Aucune affectation active')
  expect(host.textContent).toContain('Aucun resultat academique')
})

it('loads and renders the authenticated student academic record', async () => {
  setupProfile()
  mockPeriods.mockResolvedValue([{ id: 'period-1', name: 'Trimestre 1' }])
  mockRecord.mockResolvedValue({
    student_id: 'student-1',
    academic_period_id: 'period-1',
    general_average: 13.2,
    failed_subjects: 1,
    credits_obtained: 20,
    total_credits: 30,
    subject_results: [{ subject_id: 'maths', subject_name: 'Mathematiques', average: 14, coefficient: 2 }],
    status: 'VALIDATED',
    version: 1,
    academic_period_name: 'Trimestre 1',
  })
  mockAttendance.mockResolvedValue({
    records: [{
      id: 'attendance-1', student_id: 'student-1', academic_class_id: 'class-1', academic_year_id: 'year-1',
      academic_period_id: 'period-1', attendance_date: '2026-10-20', status: 'ABSENT', justified: true,
      recorded_by: 'admin-1', version: 1,
    }],
    statistics: { total_sessions: 1, absences: 1, justified_absences: 1, unjustified_absences: 0, lates: 0, attendance_rate: 0 },
  })
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  await act(async () => root?.render(createElement(StudentPortalPage)))

  expect(mockRecord).toHaveBeenCalledWith('period-1')
  expect(host.textContent).toContain('Moyenne generale13.2')
  expect(host.textContent).toContain('Credits obtenus20 / 30')
  expect(host.textContent).toContain('Mathematiques')
  expect(host.textContent).toContain('2026-10-20')
  expect(host.textContent).toContain('1 absence(s), 0 retard(s).')
})

it('explains when the authenticated session has expired', async () => {
  mockProfile.mockRejectedValue(new ApiError(401, 'expired'))
  mockPeriods.mockResolvedValue([])
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  await act(async () => root?.render(createElement(StudentPortalPage)))

  expect(host.textContent).toContain('Votre session a expire')
})
