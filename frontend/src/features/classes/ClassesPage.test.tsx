// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../shared/api/client'
import { listSubjects, type Subject } from '../academic-catalogues/academic-catalogue.service'
import { assignSubjectToClass, listAcademicClasses, type AcademicClass, type ClassSubject } from './classes.service'
import ClassesPage from './ClassesPage'

vi.mock('./classes.service', () => ({
  assignSubjectToClass: vi.fn(),
  listAcademicClasses: vi.fn(),
}))

vi.mock('../academic-catalogues/academic-catalogue.service', () => ({
  listSubjects: vi.fn(),
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const mockListClasses = vi.mocked(listAcademicClasses)
const mockListSubjects = vi.mocked(listSubjects)
const mockAssignSubject = vi.mocked(assignSubjectToClass)

let root: Root
let host: HTMLDivElement

async function settle() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
    await Promise.resolve()
  })
}

const defaultClasses: AcademicClass[] = [
  { id: 'c1', name: 'Terminale S', active: true },
  { id: 'c2', name: 'Premiere L', active: true },
]

const defaultSubjects: Subject[] = [
  { id: 's1', name: 'Mathematiques', code: 'MATH', coefficient: 4, active: true },
  { id: 's2', name: 'Physique', code: 'PHYS', coefficient: 3, active: true },
]

describe('ClassesPage', () => {
  beforeEach(() => {
    mockListClasses.mockResolvedValue(defaultClasses)
    mockListSubjects.mockResolvedValue(defaultSubjects)

    host = document.createElement('div')
    document.body.append(host)
    root = createRoot(host)
  })

  afterEach(() => {
    act(() => root.unmount())
    host.remove()
    vi.resetAllMocks()
  })

  it('renders classes list and assign subject form', async () => {
    act(() => root.render(createElement(ClassesPage)))
    await settle()

    expect(host.textContent).toContain('Liste des classes')
    expect(host.querySelector('main.classes-page')).not.toBeNull()
    expect(host.querySelector('.classes-page__form')).not.toBeNull()
    expect(host.querySelector('.classes-page__table-scroll')).not.toBeNull()
    expect(host.textContent).toContain('Terminale S')
    expect(host.textContent).toContain('Premiere L')
    expect(host.textContent).toContain('Assigner une matière à une classe')

    const tableHeaders = host.querySelectorAll('section[aria-labelledby="classes-list-title"] th')
    expect(tableHeaders).toHaveLength(2)
    expect([...tableHeaders].every((header) => header.getAttribute('scope') === 'col')).toBe(true)

    const classSelect = host.querySelector('select') as HTMLSelectElement
    expect(classSelect).not.toBeNull()
    expect(classSelect.querySelectorAll('option')).toHaveLength(3)

    const selects = host.querySelectorAll('select')
    expect(selects).toHaveLength(2)
    const subjectSelect = selects[1] as HTMLSelectElement
    expect(subjectSelect.querySelectorAll('option')).toHaveLength(3)
  })

  it('does not show an empty class list after an initial loading failure', async () => {
    mockListClasses.mockRejectedValue(new ApiError(503, 'unavailable'))
    act(() => root.render(createElement(ClassesPage)))
    await settle()

    expect(host.querySelector('[role="alert"]')?.textContent).toContain('Réessayer')
    expect(host.textContent).not.toContain("Aucune classe n'est disponible.")
  })

  it('retries a failed class load and shows empty only after a successful empty response', async () => {
    mockListClasses.mockRejectedValueOnce(new ApiError(503, 'unavailable'))
      .mockResolvedValueOnce([])
    act(() => root.render(createElement(ClassesPage)))
    await settle()

    expect(host.textContent).not.toContain("Aucune classe n'est disponible.")
    const retry = host.querySelector('[role="alert"] button') as HTMLButtonElement
    await act(async () => { retry.click(); await Promise.resolve(); await Promise.resolve() })
    await settle()

    expect(mockListClasses).toHaveBeenCalledTimes(2)
    expect(host.textContent).toContain("Aucune classe n'est disponible.")
    expect(host.querySelector('[role="alert"]')).toBeNull()
  })

  it('populates default selection and auto-fills coefficient from subject', async () => {
    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const selects = host.querySelectorAll('select')
    const classSelect = selects[0] as HTMLSelectElement
    const subjectSelect = selects[1] as HTMLSelectElement
    const coefInput = host.querySelector('input[type="number"]') as HTMLInputElement

    expect(classSelect.value).toBe('c1')
    expect(subjectSelect.value).toBe('s1')

    // Change subject selection to s2 (Physique, coeff 3)
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set
      setter?.call(subjectSelect, 's2')
      subjectSelect.dispatchEvent(new Event('change', { bubbles: true }))
    })

    await settle()
    expect(coefInput.value).toBe('3')
  })

  it('submits valid assignment with exact API contract and shows confirmation notice and recent list', async () => {
    const mockCreated: ClassSubject = {
      id: 'cs1',
      academic_class_id: 'c1',
      subject_id: 's1',
      coefficient: 4,
      academic_option_id: null,
      active: true,
    }
    mockAssignSubject.mockResolvedValue(mockCreated)

    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const form = host.querySelector('form')!
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(mockAssignSubject).toHaveBeenCalledWith('c1', {
      subject_id: 's1',
      coefficient: 4,
    })

    await settle()
    expect(host.textContent).toContain('Matière "Mathematiques" assignée avec succès à la classe "Terminale S"')
    expect(host.textContent).toContain('Assignations effectuées durant la session')
    expect(host.textContent).toContain('Mathematiques assignée à Terminale S (coeff. 4)')
  })

  it('handles HTTP 409 conflict when subject is already assigned', async () => {
    mockAssignSubject.mockRejectedValue(new ApiError(409, 'La matière est déjà assignée à cette classe'))

    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const form = host.querySelector('form')!
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
      await Promise.resolve()
    })

    await settle()
    const alert = host.querySelector('div[role="alert"]')
    expect(alert).not.toBeNull()
    expect(alert?.textContent).toContain('La matière est déjà assignée à cette classe')
  })

  it('handles network or server errors during assignment', async () => {
    mockAssignSubject.mockRejectedValue(new ApiError(0, 'Le serveur API est inaccessible.'))

    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const form = host.querySelector('form')!
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
      await Promise.resolve()
    })

    await settle()
    const alert = host.querySelector('div[role="alert"]')
    expect(alert).not.toBeNull()
    expect(alert?.textContent).toContain('Le serveur API est inaccessible.')
  })

  it('prevents double submissions while an assignment is in progress', async () => {
    let resolveAction!: (val: ClassSubject) => void
    const pendingPromise = new Promise<ClassSubject>((resolve) => {
      resolveAction = resolve
    })
    mockAssignSubject.mockReturnValue(pendingPromise)

    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const submitBtn = host.querySelector('form button[type="submit"]') as HTMLButtonElement
    expect(submitBtn.disabled).toBe(false)

    // Trigger submit
    await act(async () => {
      submitBtn.click()
    })

    // Button should now be disabled and show loading label
    expect(submitBtn.disabled).toBe(true)
    expect(submitBtn.textContent).toBe('Assignation en cours…')

    // Further clicks do not trigger mock again
    submitBtn.click()
    expect(mockAssignSubject).toHaveBeenCalledTimes(1)

    // Resolve
    await act(async () => {
      resolveAction({
        id: 'cs1',
        academic_class_id: 'c1',
        subject_id: 's1',
        coefficient: 4,
        academic_option_id: null,
        active: true,
      })
      await Promise.resolve()
      await Promise.resolve()
    })
  })

  it.each([
    ['', 'Le coefficient est obligatoire.'],
    ['0', 'Le coefficient doit être strictement supérieur à zéro.'],
    ['-2', 'Le coefficient doit être strictement supérieur à zéro.'],
    ['abc', 'Le coefficient est obligatoire.'],
  ])('rejects invalid coefficient %s with a field error', async (value, message) => {
    act(() => root.render(createElement(ClassesPage)))
    await settle()

    const coefInput = host.querySelector('input[type="number"]') as HTMLInputElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      setter?.call(coefInput, value)
      coefInput.dispatchEvent(new Event('input', { bubbles: true }))
    })

    const form = host.querySelector('form')!
    await act(async () => {
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    })

    await settle()
    expect(mockAssignSubject).not.toHaveBeenCalled()
    expect(host.textContent).toContain(message)
    expect(coefInput.getAttribute('aria-invalid')).toBe('true')
    expect(coefInput.getAttribute('aria-describedby')).toBe('assignment-coefficient-error')
    expect(host.querySelector('label[for="assignment-coefficient"]')).not.toBeNull()
    expect(host.querySelector('#assignment-coefficient-error')?.textContent).toBe(message)
  })

  it.each(['class', 'subject'])('requires a selected %s', async (field) => {
    act(() => root.render(createElement(ClassesPage)))
    await settle()
    const select = host.querySelector(`#assignment-${field}`) as HTMLSelectElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')?.set
      setter?.call(select, '')
      select.dispatchEvent(new Event('change', { bubbles: true }))
    })
    await act(async () => {
      host.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
    })
    await settle()
    expect(mockAssignSubject).not.toHaveBeenCalled()
    expect(select.getAttribute('aria-invalid')).toBe('true')
    expect(select.getAttribute('aria-describedby')).toBe(`assignment-${field}-error`)
    expect(host.querySelector(`label[for="assignment-${field}"]`)).not.toBeNull()
    expect(host.querySelector(`#assignment-${field}-error`)?.textContent).toBeTruthy()
  })
})

