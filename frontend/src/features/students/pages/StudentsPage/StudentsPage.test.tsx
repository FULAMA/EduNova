// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../../../shared/api/client'
import { createStudent, listStudents } from '../../services/student.service'
import StudentsPage from './StudentsPage'
import { MemoryRouter } from 'react-router-dom'
import { createRoot, type Root } from 'react-dom/client'
import { act, createElement } from 'react'
import type { AuthenticatedUser } from '../../../auth/services/auth.service'
import { CurrentUserContext } from '../../../auth/components/current-user.context'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

vi.mock('../../services/student.service', () => ({ createStudent: vi.fn(), listStudents: vi.fn() }))
const mockedListStudents = vi.mocked(listStudents)
const mockedCreateStudent = vi.mocked(createStudent)
let root: Root
let host: HTMLDivElement

const adminUser: AuthenticatedUser = {
  id: 'u1', email: 'admin@example.test', role: 'ADMIN', is_active: true, two_factor_enabled: false,
}

function renderPage() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => root.render(
    createElement(MemoryRouter, null,
      createElement(CurrentUserContext.Provider, { value: adminUser },
        createElement(StudentsPage)
      )
    )
  ))
  return host
}

async function settle() {
  await act(async () => { await Promise.resolve(); await Promise.resolve() })
}

describe('StudentsPage', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.resetAllMocks()
  })

  it('shows loading then API data and filters by name', async () => {
    let resolveRequest: ((students: Awaited<ReturnType<typeof listStudents>>) => void) | undefined
    mockedListStudents.mockReturnValue(new Promise((resolve) => { resolveRequest = resolve }))
    const page = renderPage()
    expect(page.textContent).toContain('Chargement des élèves...')
    await act(async () => {
      resolveRequest?.([{ id: '1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' }])
    })
    expect(page.textContent).toContain('Ada Lovelace')
    const search = page.querySelector('input[type="search"]')!
    act(() => {
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set?.call(search, 'Grace')
      search.dispatchEvent(new Event('input', { bubbles: true }))
    })
    expect(page.textContent).toContain('Aucun élève trouvé')
  })

  it('shows genuine empty state', async () => {
    mockedListStudents.mockResolvedValue([])
    const page = renderPage()
    await settle()
    expect(page.textContent).toContain('Cet établissement ne possède encore aucun élève.')
  })

  it('shows a non-blocking duplicate warning after creating a same-name student', async () => {
    mockedListStudents.mockResolvedValue([])
    mockedCreateStudent.mockResolvedValue({
      id: 'new-id', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active',
      potentialDuplicates: [{ id: 'existing-id', firstName: 'Ada', lastName: 'Lovelace' }],
    })
    const page = renderPage()
    await settle()

    const inputs = page.querySelectorAll('form input')
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
    act(() => {
      setter?.call(inputs[0], 'Ada')
      inputs[0].dispatchEvent(new Event('input', { bubbles: true }))
      setter?.call(inputs[1], 'Lovelace')
      inputs[1].dispatchEvent(new Event('input', { bubbles: true }))
    })
    await act(async () => {
      page.querySelector('form')?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
      await Promise.resolve()
      await Promise.resolve()
    })

    expect(page.textContent).toContain('Vérifiez manuellement les dossiers')
    expect(page.textContent).toContain('aucune fusion')
  })

  it.each([
    [401, 'Votre session a expiré. Veuillez vous reconnecter.'],
    [403, 'Votre compte ne peut pas consulter les élèves de cet établissement.'],
    [0, 'Impossible de charger les élèves pour le moment.'],
  ])('shows safe error text for status %i', async (status, message) => {
    mockedListStudents.mockRejectedValue(new ApiError(status, 'internal'))
    const page = renderPage()
    await settle()
    expect(page.textContent).toContain(message)
    expect(page.querySelector('[role="alert"]')).not.toBeNull()
  })

  it('retries a failed API request', async () => {
    mockedListStudents.mockRejectedValueOnce(new ApiError(0, 'internal'))
      .mockResolvedValueOnce([{ id: '1', firstName: 'Ada', lastName: 'Lovelace', email: null, status: 'active' }])
    const page = renderPage()
    await settle()
    const retryButton = page.querySelector('[role="alert"] button')!
    act(() => retryButton.dispatchEvent(new MouseEvent('click', { bubbles: true })))
    await settle()
    expect(page.textContent).toContain('Ada Lovelace')
  })
})
