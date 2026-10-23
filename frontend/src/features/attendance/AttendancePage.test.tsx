// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../shared/api/client'
import AttendancePage from './AttendancePage'
import { correctAttendance, getAttendanceStatistics, getStudentAcademicRisk, listStudentAttendance } from './attendance.service'
import { listAcademicClasses } from '../classes/classes.service'
import { listAcademicPeriods } from '../academic-catalogues/academic-catalogue.service'
import { listAcademicYears } from '../enrollments/enrollment.service'
import { listStudents } from '../students/services/student.service'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

vi.mock('../classes/classes.service', () => ({ listAcademicClasses: vi.fn() }))
vi.mock('../academic-catalogues/academic-catalogue.service', () => ({ listAcademicPeriods: vi.fn() }))
vi.mock('../enrollments/enrollment.service', () => ({ listAcademicYears: vi.fn() }))
vi.mock('../students/services/student.service', () => ({ listStudents: vi.fn() }))
vi.mock('./attendance.service', () => ({
  correctAttendance: vi.fn(),
  getAttendanceStatistics: vi.fn(),
  getStudentAcademicRisk: vi.fn(),
  listStudentAttendance: vi.fn(),
  recordAttendance: vi.fn(),
}))

const mockedListClasses = vi.mocked(listAcademicClasses)
const mockedListPeriods = vi.mocked(listAcademicPeriods)
const mockedListYears = vi.mocked(listAcademicYears)
const mockedListStudents = vi.mocked(listStudents)
const mockedStats = vi.mocked(getAttendanceStatistics)
const mockedRisk = vi.mocked(getStudentAcademicRisk)
const mockedRecords = vi.mocked(listStudentAttendance)
const mockedCorrect = vi.mocked(correctAttendance)

let root: Root | undefined
let host: HTMLDivElement | undefined

function renderPage() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => root?.render(createElement(AttendancePage)))
  return host
}

async function settle() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
    await Promise.resolve()
  })
}

function configureSuccess() {
  mockedListStudents.mockResolvedValue([{ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' }])
  mockedListClasses.mockResolvedValue([{ id: 'class-1', name: '6e A', active: true }])
  mockedListYears.mockResolvedValue([{ id: 'year-1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-07-01', status: 'ACTIVE' }])
  mockedListPeriods.mockResolvedValue([{ id: 'period-1', name: 'Trimestre 1', start_date: '2026-09-01', end_date: '2026-12-20', academic_year_id: 'year-1' }])
  mockedStats.mockResolvedValue({ total_sessions: 4, absences: 1, justified_absences: 0, unjustified_absences: 1, lates: 0, attendance_rate: 75 })
  mockedRisk.mockResolvedValue({ level: 'LOW', score: 10, reasons: [] })
  mockedRecords.mockResolvedValue([])
}

describe('AttendancePage', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.resetAllMocks()
  })

  it('affiche les statistiques provenant des services authentifies', async () => {
    configureSuccess()
    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Presences et absences')
    expect(page.textContent).toContain('75%')
    expect(page.textContent).toContain('LOW')
    expect(page.textContent).toContain('Aucun releve pour cette periode.')
  })

  it('affiche une erreur d autorisation sans exposer le message serveur', async () => {
    mockedListStudents.mockRejectedValue(new ApiError(403, 'internal authorization detail'))
    mockedListClasses.mockResolvedValue([])
    mockedListYears.mockResolvedValue([])
    mockedListPeriods.mockResolvedValue([])
    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Votre compte ne peut pas gerer les presences.')
    expect(page.textContent).not.toContain('internal authorization detail')
    expect(page.querySelector('[role="alert"]')).not.toBeNull()
  })

  it('initialise la periode dans l annee active', async () => {
    configureSuccess()
    mockedListYears.mockResolvedValue([
      { id: 'year-old', label: '2025-2026', start_date: '2025-09-01', end_date: '2026-07-01', status: 'CLOSED' },
      { id: 'year-1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-07-01', status: 'ACTIVE' },
    ])
    mockedListPeriods.mockResolvedValue([
      { id: 'period-old', name: 'Trimestre ancien', start_date: '2025-09-01', end_date: '2025-12-20', academic_year_id: 'year-old' },
      { id: 'period-1', name: 'Trimestre actif', start_date: '2026-09-01', end_date: '2026-12-20', academic_year_id: 'year-1' },
    ])
    const page = renderPage()
    await settle()

    const periodSelect = page.querySelectorAll('select')[3] as HTMLSelectElement
    expect(periodSelect.value).toBe('period-1')
  })

  it('verrouille un releve pendant sa correction', async () => {
    configureSuccess()
    mockedRecords.mockResolvedValue([{
      id: 'record-1',
      student_id: 'student-1',
      academic_class_id: 'class-1',
      academic_year_id: 'year-1',
      academic_period_id: 'period-1',
      attendance_date: '2026-10-20',
      status: 'PRESENT',
      justified: false,
      version: 2,
      recorded_by: null,
    }])
    let resolveCorrection: (() => void) | undefined
    mockedCorrect.mockReturnValue(new Promise((resolve) => {
      resolveCorrection = () => resolve({})
    }) as ReturnType<typeof correctAttendance>)
    const page = renderPage()
    await settle()

    const statusSelect = page.querySelector('select[aria-label="Statut du releve du 2026-10-20"]') as HTMLSelectElement
    await act(async () => {
      statusSelect.value = 'ABSENT'
      statusSelect.dispatchEvent(new Event('change', { bubbles: true }))
    })
    expect(mockedCorrect).toHaveBeenCalledTimes(1)
    expect(statusSelect.disabled).toBe(true)
    resolveCorrection?.()
  })
})
