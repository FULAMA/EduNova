// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../shared/api/client'
import { listAcademicClasses } from '../classes/classes.service'
import { getStudentDeliberation, listEligibleStudentPeriods, listStudents } from '../students/services/student.service'
import {
  activateAcademicYear,
  changeStudentAssignmentStatus,
  listAcademicYears,
  listStudentAssignments,
  promoteStudent,
  type AcademicYear,
  type StudentAssignment,
} from './enrollment.service'
import type { Student } from '../students/types/student.types'
import EnrollmentsPage from './EnrollmentsPage'

vi.mock('../classes/classes.service', () => ({
  listAcademicClasses: vi.fn(),
}))

vi.mock('../students/services/student.service', () => ({
  getStudentDeliberation: vi.fn(),
  listEligibleStudentPeriods: vi.fn(),
  listStudents: vi.fn(),
}))

vi.mock('./enrollment.service', () => ({
  activateAcademicYear: vi.fn(),
  changeStudentAssignmentStatus: vi.fn(),
  createAcademicYear: vi.fn(),
  createStudentAssignment: vi.fn(),
  listAcademicYears: vi.fn(),
  listStudentAssignments: vi.fn(),
  promoteStudent: vi.fn(),
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const mockListClasses = vi.mocked(listAcademicClasses)
const mockListStudents = vi.mocked(listStudents)
const mockListPeriods = vi.mocked(listEligibleStudentPeriods)
const mockGetDeliberation = vi.mocked(getStudentDeliberation)
const mockListYears = vi.mocked(listAcademicYears)
const mockListAssignments = vi.mocked(listStudentAssignments)
const mockChangeStatus = vi.mocked(changeStudentAssignmentStatus)
const mockActivateYear = vi.mocked(activateAcademicYear)
const mockPromoteStudent = vi.mocked(promoteStudent)

let root: Root
let host: HTMLDivElement

async function settle() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
    await Promise.resolve()
  })
}

const defaultYears: AcademicYear[] = [
  { id: 'y1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-07-31', status: 'ACTIVE' },
]

const defaultStudents: Student[] = [
  { id: 's1', firstName: 'Marie', lastName: 'Curie', status: 'active' },
]

const defaultClasses = [
  { id: 'c1', name: 'Terminale S', active: true },
]

describe('EnrollmentsPage', () => {
  beforeEach(() => {
    mockListYears.mockResolvedValue(defaultYears)
    mockListStudents.mockResolvedValue(defaultStudents)
    mockListPeriods.mockResolvedValue([])
    mockGetDeliberation.mockRejectedValue(new ApiError(404, 'missing'))
    mockListClasses.mockResolvedValue(defaultClasses)
    mockListAssignments.mockResolvedValue([])

    host = document.createElement('div')
    document.body.append(host)
    root = createRoot(host)
  })

  afterEach(() => {
    act(() => root.unmount())
    host.remove()
    vi.resetAllMocks()
  })

  it('shows contextual empty states after successful empty year and assignment responses', async () => {
    mockListYears.mockResolvedValue([])
    mockListAssignments.mockResolvedValue([])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    expect(host.querySelector('main.enrollments-page')).not.toBeNull()
    expect(host.querySelectorAll('.enrollments-page__section')).toHaveLength(2)
    expect(host.querySelectorAll('.enrollments-page__form')).toHaveLength(2)
    expect(host.textContent).toContain('Aucune année scolaire n’est configurée.')
    expect(host.textContent).toContain('Aucune affectation n’est enregistrée pour cet élève.')
    expect(host.querySelector('[role="alert"]')).toBeNull()
  })

  it('shows a loading status before showing an empty assignment result', async () => {
    let resolveAssignments!: (assignments: StudentAssignment[]) => void
    mockListAssignments.mockReturnValue(new Promise((resolve) => {
      resolveAssignments = resolve
    }))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    expect(host.textContent).toContain('Chargement des affectations de cet élève…')
    expect(host.textContent).not.toContain('Aucune affectation n’est enregistrée pour cet élève.')

    await act(async () => {
      resolveAssignments([])
      await Promise.resolve()
    })

    expect(host.textContent).toContain('Aucune affectation n’est enregistrée pour cet élève.')
  })

  it('hides the previous student assignments as soon as the selection changes', async () => {
    const previous: StudentAssignment = { id: 'old-a', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' }
    const current: StudentAssignment = { ...previous, id: 'new-a', student_id: 's2', status: 'ACTIVE' }
    let resolveCurrent!: (rows: StudentAssignment[]) => void
    mockListStudents.mockResolvedValue([
      ...defaultStudents,
      { id: 's2', firstName: 'Ada', lastName: 'Lovelace', status: 'active' },
    ])
    mockListAssignments.mockResolvedValueOnce([previous]).mockReturnValueOnce(new Promise((resolve) => { resolveCurrent = resolve }))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()
    expect(host.textContent).toContain('Affectation old-a: DRAFT')

    const studentSelect = host.querySelector('section[aria-labelledby="assignment-title"] select') as HTMLSelectElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set
      setter?.call(studentSelect, 's2')
      studentSelect.dispatchEvent(new Event('change', { bubbles: true }))
    })
    expect(host.textContent).not.toContain('Affectation old-a: DRAFT')
    expect(host.textContent).toContain('Chargement des affectations de cet élève…')

    await act(async () => { resolveCurrent([current]); await Promise.resolve() })
    expect(host.textContent).toContain('Affectation new-a: ACTIVE')
  })

  it('offers a working retry after assignment loading fails for the newly selected student', async () => {
    const previous: StudentAssignment = { id: 'old-a', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' }
    const current: StudentAssignment = { ...previous, id: 'new-a', student_id: 's2', status: 'ACTIVE' }
    mockListStudents.mockResolvedValue([
      ...defaultStudents,
      { id: 's2', firstName: 'Ada', lastName: 'Lovelace', status: 'active' },
    ])
    mockListAssignments.mockResolvedValueOnce([previous])
      .mockRejectedValueOnce(new ApiError(503, 'unavailable'))
      .mockResolvedValueOnce([current])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()
    const studentSelect = host.querySelector('section[aria-labelledby="assignment-title"] select') as HTMLSelectElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set
      setter?.call(studentSelect, 's2')
      studentSelect.dispatchEvent(new Event('change', { bubbles: true }))
    })
    await settle()

    const assignmentSection = host.querySelector('section[aria-labelledby="assignment-title"]')!
    expect(assignmentSection.querySelector('[role="alert"]')?.textContent).toContain('Les donnees d inscription ne peuvent pas etre chargees.')
    expect(assignmentSection.textContent).not.toContain('Affectation old-a: DRAFT')
    const retry = assignmentSection.querySelector('[role="alert"] button') as HTMLButtonElement
    await act(async () => { retry.click(); await Promise.resolve(); await Promise.resolve() })
    await settle()

    expect(mockListAssignments.mock.calls.map(([id]) => id)).toEqual(['s1', 's2', 's2'])
    expect(assignmentSection.textContent).toContain('Affectation new-a: ACTIVE')
    expect(assignmentSection.querySelector('[role="alert"]')).toBeNull()
  })

  it('ignores a late assignment response for the previously selected student', async () => {
    let resolveFirst!: (rows: StudentAssignment[]) => void
    let resolveSecond!: (rows: StudentAssignment[]) => void
    const first: StudentAssignment = { id: 'old-a', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' }
    const second: StudentAssignment = { ...first, id: 'new-a', student_id: 's2', status: 'ACTIVE' }
    mockListStudents.mockResolvedValue([
      ...defaultStudents,
      { id: 's2', firstName: 'Ada', lastName: 'Lovelace', status: 'active' },
    ])
    mockListAssignments.mockImplementation((id) => id === 's1'
      ? new Promise((resolve) => { resolveFirst = resolve })
      : new Promise((resolve) => { resolveSecond = resolve }))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()
    const studentSelect = host.querySelector('section[aria-labelledby="assignment-title"] select') as HTMLSelectElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set
      setter?.call(studentSelect, 's2')
      studentSelect.dispatchEvent(new Event('change', { bubbles: true }))
    })
    await settle()

    await act(async () => { resolveSecond([second]); await Promise.resolve() })
    expect(host.textContent).toContain('Affectation new-a: ACTIVE')
    await act(async () => { resolveFirst([first]); await Promise.resolve() })
    expect(host.textContent).toContain('Affectation new-a: ACTIVE')
    expect(host.textContent).not.toContain('Affectation old-a: DRAFT')
  })

  it('explains when there are no available students or classes for an assignment', async () => {
    mockListStudents.mockResolvedValue([])
    mockListClasses.mockResolvedValue([])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    expect(host.textContent).toContain('Aucun élève n’est disponible pour préparer une affectation.')
    expect(host.textContent).toContain('Aucune classe n’est disponible pour préparer une affectation.')
  })

  it('does not describe an assignment API error as an empty assignment list', async () => {
    mockListAssignments.mockRejectedValue(new ApiError(503, 'unavailable'))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    expect(host.querySelector('[role="alert"]')?.textContent).toContain('Les donnees d inscription ne peuvent pas etre chargees.')
    expect(host.textContent).not.toContain('Aucune affectation n’est enregistrée pour cet élève.')
  })

  it('does not describe a failed year request as an empty year list', async () => {
    mockListYears.mockRejectedValue(new ApiError(503, 'unavailable'))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    expect(host.querySelector('[role="alert"]')?.textContent).toBe('Les donnees d inscription ne peuvent pas etre chargees.')
    expect(host.textContent).not.toContain('Aucune année scolaire n’est configurée.')
  })

  it('renders actions according to assignment status (DRAFT shows Activer & Annuler, ACTIVE shows Cloturer, terminal shows no actions)', async () => {
    const assignments: StudentAssignment[] = [
      { id: 'a-draft', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
      { id: 'a-active', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'ACTIVE' },
      { id: 'a-closed', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'CLOSED' },
      { id: 'a-cancelled', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'CANCELLED' },
    ]
    mockListAssignments.mockResolvedValue(assignments)

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const listItems = host.querySelectorAll('section[aria-labelledby="assignment-title"] ul li')
    expect(listItems).toHaveLength(4)

    // a-draft: buttons Activer & Annuler
    const draftItem = listItems[0]
    expect(draftItem.textContent).toContain('Affectation a-draft: DRAFT')
    const draftButtons = draftItem.querySelectorAll('button')
    expect(draftButtons).toHaveLength(2)
    expect(draftButtons[0].textContent).toBe('Activer')
    expect(draftButtons[1].textContent).toBe('Annuler')

    // a-active: button Cloturer
    const activeItem = listItems[1]
    expect(activeItem.textContent).toContain('Affectation a-active: ACTIVE')
    const activeButtons = activeItem.querySelectorAll('button')
    expect(activeButtons).toHaveLength(1)
    expect(activeButtons[0].textContent).toBe('Cloturer')

    // a-closed: no buttons
    const closedItem = listItems[2]
    expect(closedItem.textContent).toContain('Affectation a-closed: CLOSED')
    expect(closedItem.querySelectorAll('button')).toHaveLength(0)

    // a-cancelled: no buttons
    const cancelledItem = listItems[3]
    expect(cancelledItem.textContent).toContain('Affectation a-cancelled: CANCELLED')
    expect(cancelledItem.querySelectorAll('button')).toHaveLength(0)
  })

  it('successfully activates a draft assignment and reloads the list', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
    ]
    const updatedAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'ACTIVE' },
    ]
    mockListAssignments.mockResolvedValueOnce(initialAssignments).mockResolvedValueOnce(updatedAssignments)
    mockChangeStatus.mockResolvedValue(updatedAssignments[0])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const activateBtn = host.querySelector('section[aria-labelledby="assignment-title"] ul li button') as HTMLButtonElement
    expect(activateBtn.textContent).toBe('Activer')

    await act(async () => {
      activateBtn.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(mockChangeStatus).toHaveBeenCalledWith('a1', 'activate')
    expect(mockListAssignments).toHaveBeenCalledTimes(2)
    await settle()
    expect(host.textContent).toContain('Affectation a1: ACTIVE')
  })

  it('successfully cancels a draft assignment', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
    ]
    const updatedAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'CANCELLED' },
    ]
    mockListAssignments.mockResolvedValueOnce(initialAssignments).mockResolvedValueOnce(updatedAssignments)
    mockChangeStatus.mockResolvedValue(updatedAssignments[0])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const buttons = host.querySelectorAll('section[aria-labelledby="assignment-title"] ul li button')
    const cancelBtn = buttons[1] as HTMLButtonElement
    expect(cancelBtn.textContent).toBe('Annuler')

    await act(async () => {
      cancelBtn.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(mockChangeStatus).toHaveBeenCalledWith('a1', 'cancel')
    expect(mockListAssignments).toHaveBeenCalledTimes(2)
    await settle()
    expect(host.textContent).toContain('Affectation a1: CANCELLED')
  })

  it('successfully closes an active assignment', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'ACTIVE' },
    ]
    const updatedAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'CLOSED' },
    ]
    mockListAssignments.mockResolvedValueOnce(initialAssignments).mockResolvedValueOnce(updatedAssignments)
    mockChangeStatus.mockResolvedValue(updatedAssignments[0])

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const closeBtn = host.querySelector('section[aria-labelledby="assignment-title"] ul li button') as HTMLButtonElement
    expect(closeBtn.textContent).toBe('Cloturer')

    await act(async () => {
      closeBtn.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(mockChangeStatus).toHaveBeenCalledWith('a1', 'close')
    expect(mockListAssignments).toHaveBeenCalledTimes(2)
    await settle()
    expect(host.textContent).toContain('Affectation a1: CLOSED')
  })

  it('displays HTTP 409 conflict detail message properly', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
    ]
    mockListAssignments.mockResolvedValue(initialAssignments)
    mockChangeStatus.mockRejectedValue(new ApiError(409, 'Une affectation active existe deja pour cet eleve et cette annee.'))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const activateBtn = host.querySelector('section[aria-labelledby="assignment-title"] ul li button') as HTMLButtonElement

    await act(async () => {
      activateBtn.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    await settle()
    const alert = host.querySelector('p[role="alert"]')
    expect(alert).not.toBeNull()
    expect(alert?.textContent).toBe('Une affectation active existe deja pour cet eleve et cette annee.')
  })

  it('displays a generic error message on network or server error', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
    ]
    mockListAssignments.mockResolvedValue(initialAssignments)
    mockChangeStatus.mockRejectedValue(new Error('Network failure'))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const activateBtn = host.querySelector('section[aria-labelledby="assignment-title"] ul li button') as HTMLButtonElement

    await act(async () => {
      activateBtn.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    await settle()
    const alert = host.querySelector('p[role="alert"]')
    expect(alert?.textContent).toBe('Les donnees d inscription ne peuvent pas etre chargees.')
  })

  it('displays activation errors instead of creating an unhandled rejection', async () => {
    mockListYears.mockResolvedValue([{ ...defaultYears[0], status: 'DRAFT' }])
    mockActivateYear.mockRejectedValue(new ApiError(409, 'Une autre annee est deja active dans cet etablissement.'))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const activateButton = host.querySelector('section[aria-labelledby="academic-year-title"] ul button') as HTMLButtonElement
    await act(async () => {
      activateButton.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(host.querySelector('p[role="alert"]')?.textContent).toBe('Une autre annee est deja active dans cet etablissement.')
  })

  it('disables the button and prevents double submissions while an action is in progress', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
    ]
    mockListAssignments.mockResolvedValue(initialAssignments)

    let resolveAction!: (val: StudentAssignment) => void
    const pendingPromise = new Promise<StudentAssignment>((resolve) => {
      resolveAction = resolve
    })
    mockChangeStatus.mockReturnValue(pendingPromise)

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const activateBtn = host.querySelector('section[aria-labelledby="assignment-title"] ul li button') as HTMLButtonElement
    expect(activateBtn.disabled).toBe(false)

    // Trigger action without awaiting completion immediately
    await act(async () => {
      activateBtn.click()
    })

    // Button should now be disabled with in-progress label
    expect(activateBtn.disabled).toBe(true)
    expect(activateBtn.textContent).toBe('Activation...')

    // Clicking while in progress does not call the service again
    activateBtn.click()
    expect(mockChangeStatus).toHaveBeenCalledTimes(1)

    // Complete the action
    await act(async () => {
      resolveAction({ ...initialAssignments[0], status: 'ACTIVE' })
      await Promise.resolve()
      await Promise.resolve()
    })
  })

  it('disables actions on other assignments while one status change is pending', async () => {
    const initialAssignments: StudentAssignment[] = [
      { id: 'a1', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c1', academic_option_id: null, status: 'DRAFT' },
      { id: 'a2', student_id: 's1', academic_year_id: 'y1', academic_class_id: 'c2', academic_option_id: null, status: 'DRAFT' },
    ]
    mockListAssignments.mockResolvedValue(initialAssignments)

    let resolveAction!: (val: StudentAssignment) => void
    mockChangeStatus.mockReturnValue(new Promise<StudentAssignment>((resolve) => {
      resolveAction = resolve
    }))

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const actionButtons = Array.from(
      host.querySelectorAll('section[aria-labelledby="assignment-title"] ul li button'),
    ) as HTMLButtonElement[]
    expect(actionButtons).toHaveLength(4)

    await act(async () => {
      actionButtons[0].click()
    })

    expect(mockChangeStatus).toHaveBeenCalledTimes(1)
    expect(actionButtons.every((button) => button.disabled)).toBe(true)

    await act(async () => {
      resolveAction({ ...initialAssignments[0], status: 'ACTIVE' })
      await Promise.resolve()
      await Promise.resolve()
    })
  })

  it('promotes only an admitted validated deliberation with API identifiers', async () => {
    const activeAssignment: StudentAssignment = {
      id: 'source-1',
      student_id: 's1',
      academic_year_id: 'y0',
      academic_class_id: 'c1',
      academic_option_id: null,
      status: 'ACTIVE',
    }
    mockListAssignments.mockResolvedValue([activeAssignment])
    mockListPeriods.mockResolvedValue([{
      id: 'period-1',
      name: 'Trimestre 1',
      academic_year_id: 'y1',
      academic_year_label: '2026-2027',
    }])
    mockGetDeliberation.mockResolvedValue({
      student_id: 's1',
      academic_period_id: 'period-1',
      record_version: 2,
      average: 14,
      failed_subjects: 0,
      decision: 'ADMITTED',
      deliberation_id: 'deliberation-1',
      deliberation_status: 'VALIDATED',
      deliberation_version: 2,
    })
    mockPromoteStudent.mockResolvedValue({ ...activeAssignment, id: 'target-1', academic_year_id: 'y2', academic_class_id: 'c1' })

    act(() => root.render(createElement(EnrollmentsPage)))
    await settle()

    const promotionButton = Array.from(host.querySelectorAll('button')).find((button) => button.textContent?.includes('Confirmer le passage')) as HTMLButtonElement
    expect(promotionButton).not.toBeNull()
    await act(async () => {
      promotionButton.click()
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(mockPromoteStudent).toHaveBeenCalledWith({
      source_assignment_id: 'source-1',
      deliberation_id: 'deliberation-1',
      target_year_id: 'y1',
      target_class_id: 'c1',
    })
    expect(host.textContent).toContain('Passage de classe enregistré')
  })
})
