// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../../shared/api/client'
import { addStudentSubjectResult, createStudentAcademicRecord, getStudent, getStudentAcademicHistory, getStudentAcademicRecord, getStudentDeliberation, listEligibleStudentPeriods, listEligibleStudentSubjects, listStudents, validateStudentAcademicRecord, validateStudentDeliberation } from '../../services/student.service'
import StudentsPage from '../StudentsPage/StudentsPage'
import StudentDetailPage from './StudentDetailPage'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true
vi.mock('../../services/student.service', () => ({ addStudentSubjectResult: vi.fn(), correctStudentAcademicRecord: vi.fn(), createStudentAcademicRecord: vi.fn(), getStudent: vi.fn(), getStudentAcademicHistory: vi.fn(), getStudentAcademicRecord: vi.fn(), getStudentDeliberation: vi.fn(), listEligibleStudentPeriods: vi.fn(), listEligibleStudentSubjects: vi.fn(), listStudents: vi.fn(), validateStudentAcademicRecord: vi.fn(), validateStudentDeliberation: vi.fn() }))
const mockGetStudent = vi.mocked(getStudent)
const mockListStudents = vi.mocked(listStudents)
const mockListPeriods = vi.mocked(listEligibleStudentPeriods)
const mockGetRecord = vi.mocked(getStudentAcademicRecord)
const mockGetDeliberation = vi.mocked(getStudentDeliberation)
const mockGetHistory = vi.mocked(getStudentAcademicHistory)
const mockListSubjects = vi.mocked(listEligibleStudentSubjects)
const mockCreateRecord = vi.mocked(createStudentAcademicRecord)
const mockAddResult = vi.mocked(addStudentSubjectResult)
const mockValidateRecord = vi.mocked(validateStudentAcademicRecord)
const mockValidateDeliberation = vi.mocked(validateStudentDeliberation)
let root: Root
let host: HTMLDivElement

function renderAt(path: string) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => root.render(createElement(MemoryRouter, { initialEntries: [path] },
    createElement(Routes, null,
      createElement(Route, { path: '/app/students', element: createElement(StudentsPage) }),
      createElement(Route, { path: '/app/students/:studentId', element: createElement(StudentDetailPage) }),
    ),
  )))
  return host
}

async function settle() {
  await act(async () => { await Promise.resolve(); await Promise.resolve() })
}

describe('Student detail route', () => {
  beforeEach(() => {
    mockListPeriods.mockResolvedValue([])
    mockListSubjects.mockResolvedValue([])
    mockCreateRecord.mockResolvedValue({})
    mockAddResult.mockResolvedValue({})
    mockGetDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 1, average: 12, failed_subjects: 0, decision: 'ADMITTED' })
    mockGetHistory.mockResolvedValue([])
  })

  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.resetAllMocks()
  })

  it('navigates from the real list link and renders the API detail', async () => {
    mockListStudents.mockResolvedValue([{ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' }])
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', academic_period_name: 'Trimestre 1', general_average: 14.5, failed_subjects: 1, credits_obtained: 12, total_credits: 24, status: 'DRAFT', version: 1, subject_results: [{ subject_id: 'subject-1', subject_name: 'Mathématiques', average: 14.5, coefficient: 2 }] })
    const page = renderAt('/app/students')
    await settle()
    const link = page.querySelector('a[href="/app/students/student-1"]') as HTMLAnchorElement
    expect(link).not.toBeNull()
    act(() => link.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })))
    await settle()
    expect(mockGetStudent).toHaveBeenCalledWith('student-1')
    expect(mockListPeriods).toHaveBeenCalledWith('student-1')
    expect(mockGetRecord).toHaveBeenCalledWith('student-1', 'period-1')
    expect(page.textContent).toContain('Informations générales')
    expect(page.textContent).toContain('Non renseigné')
    expect(page.querySelector('a[href="/app/students"]')?.textContent).toContain('Retour aux élèves')
  })

  it('shows an explicit empty state when no academic records exist', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([])
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.textContent).toContain('Aucune période liée à une affectation active')
  })

  it('creates the first dossier and adds a result using the persisted coefficient', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1', has_record: false }])
    mockListSubjects.mockResolvedValue([{ id: 'subject-1', name: 'Mathématiques', coefficient: 3 }])
    mockGetRecord.mockRejectedValueOnce(new ApiError(404, 'missing')).mockResolvedValueOnce({
      student_id: 'student-1', academic_period_id: 'period-1', general_average: 0, failed_subjects: 0,
      credits_obtained: 0, total_credits: 24, status: 'DRAFT', version: 1, subject_results: [],
    }).mockResolvedValueOnce({
      student_id: 'student-1', academic_period_id: 'period-1', general_average: 15, failed_subjects: 0,
      credits_obtained: 0, total_credits: 24, status: 'DRAFT', version: 2,
      subject_results: [{ subject_id: 'subject-1', subject_name: 'Mathématiques', average: 15, coefficient: 3 }],
    })
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.textContent).toContain('Créer le dossier académique')

    const totalCredits = page.querySelector('#record-total-credits') as HTMLInputElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      setter?.call(totalCredits, '24'); totalCredits.dispatchEvent(new Event('input', { bubbles: true }))
    })
    const createForm = totalCredits.closest('form')!
    await act(async () => { createForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    await settle()
    expect(mockCreateRecord).toHaveBeenCalledWith('student-1', 'period-1', 24)
    expect(page.textContent).toContain('Saisir un résultat')
    expect(page.textContent).toContain('coefficient 3')

    const average = page.querySelector('#result-average') as HTMLInputElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      setter?.call(average, '15'); average.dispatchEvent(new Event('input', { bubbles: true }))
    })
    const resultForm = average.closest('form')!
    await act(async () => { resultForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    await settle()
    expect(mockAddResult).toHaveBeenCalledWith('student-1', 'period-1', 'subject-1', 15)
    expect(page.textContent).toContain('Mathématiques')
    expect(page.textContent).toContain('15 / 20')
  })

  it('loads the selected academic period record and displays its results', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Semestre 1' }, { id: 'period-2', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Semestre 2' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 16, failed_subjects: 0, credits_obtained: 24, total_credits: 24, status: 'VALIDATED', version: 1, subject_results: [
      { subject_id: 'subject-1', subject_name: 'Chimie', average: 16, coefficient: 3 },
      { subject_id: 'subject-2', subject_name: 'Histoire', average: 12.5, coefficient: 2 },
    ] })
    mockGetHistory.mockResolvedValue([{ version: 1, status: 'VALIDATED', operation: 'CORRECTED', recorded_at: '2026-10-20T00:00:00Z', actor_id: 'admin-1', reason: 'Correction de test', snapshot: {} }])
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.textContent).toContain('16 / 20')
    expect(page.textContent).toContain('Chimie')
    expect(page.textContent).toContain('Histoire')
    expect(page.textContent).toContain('12.5 / 20')
    expect(page.textContent).toContain('Correction de test')
    expect(page.textContent).toContain('admin-1')
    expect(page.textContent).toContain('2026-10-20T00:00:00Z')
    expect(page.querySelector('[role="img"][aria-label*="Chimie : 16 sur 20"]')?.getAttribute('aria-label')).toContain('Histoire : 12,5 sur 20')
    expect(mockGetRecord).toHaveBeenCalledTimes(1)
    expect(mockListPeriods).toHaveBeenCalledTimes(1)
  })

  it('does not display a deliberation from an older record version', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 16, failed_subjects: 0, credits_obtained: 24, total_credits: 24, status: 'VALIDATED', version: 3, subject_results: [] })
    mockGetDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 2, average: 16, failed_subjects: 0, decision: 'ADMITTED' })

    const page = renderAt('/app/students/student-1')
    await settle()

    expect(page.textContent).not.toContain('Délibération serveur')
  })

  it('refreshes history and deliberation after validating a record', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 14, failed_subjects: 0, credits_obtained: 0, total_credits: 24, status: 'DRAFT', version: 1, subject_results: [] })
    mockValidateRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 14, failed_subjects: 0, credits_obtained: 0, total_credits: 24, status: 'VALIDATED', version: 2, subject_results: [] })
    mockGetDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 2, average: 14, failed_subjects: 0, decision: 'ADMITTED' })
    mockGetHistory.mockResolvedValue([{ version: 2, status: 'VALIDATED', operation: 'VALIDATED', recorded_at: '2026-10-20T00:00:00Z', actor_id: 'admin-1', reason: null, snapshot: {} }])

    const page = renderAt('/app/students/student-1')
    await settle()
    act(() => Array.from(page.querySelectorAll('button')).find((button) => button.textContent?.includes('Valider le dossier'))?.click())
    await settle()

    expect(mockValidateRecord).toHaveBeenCalledWith('student-1', 'period-1', 1)
    expect(mockGetHistory).toHaveBeenCalledWith('student-1', 'period-1')
    expect(page.textContent).toContain('Historique du dossier')
    expect(page.textContent).toContain('Délibération serveur')
    expect(page.textContent).toContain('Calculée sur la version 2 du dossier.')
  })

  it('explains why a prepared deliberation cannot trigger promotion', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 14, failed_subjects: 0, credits_obtained: 0, total_credits: 24, status: 'VALIDATED', version: 1, subject_results: [] })
    mockGetDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 1, average: 14, failed_subjects: 0, decision: 'ADMITTED', deliberation_status: 'PREPARED' })

    const page = renderAt('/app/students/student-1')
    await settle()

    expect(page.textContent).toContain('Le passage reste bloqué tant que la délibération n\'est pas validée.')
  })

  it('validates a prepared deliberation through the authenticated API contract', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 14, failed_subjects: 0, credits_obtained: 0, total_credits: 24, status: 'VALIDATED', version: 1, subject_results: [] })
    mockGetDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 1, average: 14, failed_subjects: 0, decision: 'ADMITTED', deliberation_id: 'delib-1', deliberation_status: 'PREPARED', deliberation_version: 1 })
    mockValidateDeliberation.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', record_version: 1, average: 14, failed_subjects: 0, decision: 'ADMITTED', deliberation_id: 'delib-1', deliberation_status: 'VALIDATED', deliberation_version: 2 })

    const page = renderAt('/app/students/student-1')
    await settle()
    const button = Array.from(page.querySelectorAll('button')).find((item) => item.textContent?.includes('Valider la délibération')) as HTMLButtonElement
    await act(async () => { button.click(); await Promise.resolve(); await Promise.resolve() })

    expect(mockValidateDeliberation).toHaveBeenCalledWith('delib-1', 1)
    expect(page.textContent).toContain('Statut : VALIDATED')
    expect(page.textContent).not.toContain('Le passage reste bloqué')
  })

  it('does not render a chart when a record contains no subject results', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 0, failed_subjects: 0, credits_obtained: 0, total_credits: 0, status: 'DRAFT', version: 1, subject_results: [] })
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.textContent).toContain('Aucun résultat par matière n’est enregistré pour cette période.')
    expect(page.querySelector('[role="img"]')).toBeNull()
  })

  it('omits invalid averages from the chart without converting them to zero', async () => {
    mockGetStudent.mockResolvedValue({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    mockListPeriods.mockResolvedValue([{ id: 'period-1', academic_year_id: 'year-1', academic_year_label: '2026-2027', name: 'Trimestre 1' }])
    mockGetRecord.mockResolvedValue({ student_id: 'student-1', academic_period_id: 'period-1', general_average: 10, failed_subjects: 0, credits_obtained: 0, total_credits: 0, status: 'DRAFT', version: 1, subject_results: [
      { subject_id: 'valid', subject_name: 'Mathématiques', average: 10, coefficient: 1 },
      { subject_id: 'invalid', subject_name: 'Physique', average: Number.NaN, coefficient: 1 },
    ] })
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.querySelector('[role="img"]')?.getAttribute('aria-label')).toContain('Mathématiques : 10 sur 20')
    expect(page.querySelector('[role="img"]')?.getAttribute('aria-label')).not.toContain('Physique')
    expect(page.textContent).toContain('1 résultat avec une moyenne invalide n’est pas représenté')
    expect(page.textContent).toContain('NaN / 20')
  })

  it('shows loading while the detail request is pending', async () => {
    let finishRequest: ((student: Awaited<ReturnType<typeof getStudent>>) => void) | undefined
    mockGetStudent.mockReturnValue(new Promise((resolve) => { finishRequest = resolve }))
    const page = renderAt('/app/students/student-1')
    expect(page.textContent).toContain('Chargement de la fiche élève')
    await act(async () => {
      finishRequest?.({ id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' })
    })
  })

  it.each([
    [401, 'Votre session a expiré. Veuillez vous reconnecter.'],
    [403, 'Votre compte ne peut pas consulter les élèves de cet établissement.'],
    [404, 'Aucun élève ne correspond à cet identifiant.'],
    [0, 'Impossible de charger cet élève pour le moment.'],
  ])('shows the expected error state for status %i', async (status, message) => {
    mockGetStudent.mockRejectedValue(new ApiError(status, 'internal'))
    const page = renderAt('/app/students/student-1')
    await settle()
    expect(page.textContent).toContain(message)
    expect(page.querySelector('a[href="/app/students"]')).not.toBeNull()
    expect(page.querySelector('button')?.textContent).toContain('Réessayer')
  })

  it('retries the detail request after an error', async () => {
    mockGetStudent.mockRejectedValueOnce(new ApiError(0, 'network')).mockResolvedValueOnce({
      id: 'student-1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active',
    })
    const page = renderAt('/app/students/student-1')
    await settle()
    act(() => page.querySelector('button')?.dispatchEvent(new MouseEvent('click', { bubbles: true })))
    await settle()
    expect(page.textContent).toContain('Ada Lovelace')
    expect(mockGetStudent).toHaveBeenCalledTimes(2)
  })
})
