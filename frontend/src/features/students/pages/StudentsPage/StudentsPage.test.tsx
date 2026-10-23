// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../../../shared/api/client'
import { listStudents } from '../../services/student.service'
import StudentsPage from './StudentsPage'
import { MemoryRouter } from 'react-router-dom'
import { createRoot, type Root } from 'react-dom/client'
import { act, createElement } from 'react'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

vi.mock('../../services/student.service', () => ({ listStudents: vi.fn() }))
const mockedListStudents = vi.mocked(listStudents)
let root: Root
let host: HTMLDivElement

function renderPage() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => root.render(createElement(MemoryRouter, null, createElement(StudentsPage))))
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
    const button = page.querySelector('button')!
    act(() => button.dispatchEvent(new MouseEvent('click', { bubbles: true })))
    await settle()
    expect(page.textContent).toContain('Ada Lovelace')
  })
})
