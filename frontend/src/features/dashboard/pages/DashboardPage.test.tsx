// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../shared/api/client'
import { getCurrentUser, getSession } from '../../auth/services/auth.service'
import { listStudents } from '../../students/services/student.service'
import { listAcademicClasses } from '../../classes/classes.service'
import { listAcademicYears } from '../../enrollments/enrollment.service'
import { listSubjects } from '../../academic-catalogues/academic-catalogue.service'
import DashboardPage from './DashboardPage'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

vi.mock('../../auth/services/auth.service', () => ({
  getCurrentUser: vi.fn(),
  getSession: vi.fn(),
  linkGoogleIdentity: vi.fn(),
}))

vi.mock('../../students/services/student.service', () => ({
  listStudents: vi.fn(),
}))

vi.mock('../../classes/classes.service', () => ({
  listAcademicClasses: vi.fn(),
}))

vi.mock('../../enrollments/enrollment.service', () => ({
  listAcademicYears: vi.fn(),
}))

vi.mock('../../academic-catalogues/academic-catalogue.service', () => ({
  listSubjects: vi.fn(),
}))

const mockedGetCurrentUser = vi.mocked(getCurrentUser)
const mockedGetSession = vi.mocked(getSession)
const mockedListStudents = vi.mocked(listStudents)
const mockedListAcademicClasses = vi.mocked(listAcademicClasses)
const mockedListAcademicYears = vi.mocked(listAcademicYears)
const mockedListSubjects = vi.mocked(listSubjects)

let root: Root | undefined
let host: HTMLDivElement

function renderPage() {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(
      createElement(MemoryRouter, null, createElement(DashboardPage)),
    )
  })
  return host
}

async function settle() {
  await act(async () => {
    await Promise.resolve()
    await Promise.resolve()
    await Promise.resolve()
  })
}

describe('DashboardPage', () => {
  beforeEach(() => {
    mockedGetSession.mockReturnValue({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      email: 'admin@example.test',
      tenantId: 'tenant-1',
    })

    mockedGetCurrentUser.mockResolvedValue({
      id: 'user-1',
      email: 'admin@example.test',
      role: 'ADMIN',
      is_active: true,
      two_factor_enabled: true,
    })

    mockedListStudents.mockResolvedValue([
      { id: 's-1', firstName: 'Jean', lastName: 'Kabangu', email: 'jean@test.cd', status: 'active' },
      { id: 's-2', firstName: 'Marie', lastName: 'Tshimanga', email: null, status: 'inactive' },
    ])

    mockedListAcademicClasses.mockResolvedValue([
      { id: 'c-1', name: '7e EB', active: true },
      { id: 'c-2', name: '8e EB', active: true },
      { id: 'c-3', name: 'Ancienne Classe', active: false },
    ])

    mockedListAcademicYears.mockResolvedValue([
      {
        id: 'y-1',
        label: '2026-2027',
        start_date: '2026-09-01',
        end_date: '2027-07-02',
        status: 'ACTIVE',
      },
    ])

    mockedListSubjects.mockResolvedValue([
      { id: 'sub-1', name: 'Mathématiques', code: 'MATH', coefficient: 3, active: true },
      { id: 'sub-2', name: 'Physique', code: 'PHYS', coefficient: 2, active: true },
      { id: 'sub-3', name: 'Latin Archivé', code: 'LAT', coefficient: 1, active: false },
    ])
  })

  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.resetAllMocks()
  })

  it('shows the authenticated identity and real business metrics from the API', async () => {
    const page = renderPage()
    expect(page.textContent).toContain('Chargement de votre session...')
    await settle()

    // Session identity
    expect(page.textContent).toContain('Administrateur')
    expect(page.textContent).toContain('admin@example.test')
    expect(page.textContent).toContain('Activés')

    // Real Metrics
    expect(page.textContent).toContain('Élèves inscrits')
    expect(page.textContent).toContain('2') // total students
    expect(page.textContent).toContain('1 actif sur 2')

    expect(page.textContent).toContain('Classes pédagogiques')
    expect(page.textContent).toContain('2') // active classes
    expect(page.textContent).toContain('3 classes configurées')

    expect(page.textContent).toContain('Matières enseignées')
    expect(page.textContent).toContain('2') // active subjects

    expect(page.textContent).toContain('Année scolaire active')
    expect(page.textContent).toContain('2026-2027')
    expect(page.textContent).toContain('Du 2026-09-01 au 2027-07-02')

    // No warning banner when active year exists
    expect(page.textContent).not.toContain('aucune année scolaire n’est actuellement active')
  })

  it('renders a warning banner and "Aucune active" when no year is ACTIVE', async () => {
    mockedListAcademicYears.mockResolvedValue([
      {
        id: 'y-draft',
        label: '2026-2027 (Brouillon)',
        start_date: '2026-09-01',
        end_date: '2027-07-02',
        status: 'DRAFT',
      },
    ])

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Aucune active')
    expect(page.textContent).toContain('Aucune année avec le statut ACTIVE')
    expect(page.textContent).toContain('Attention : aucune année scolaire n’est actuellement active.')
    expect(page.textContent).toContain('Gérer les années scolaires →')
  })

  it('renders verified quick links to valid application routes', async () => {
    const page = renderPage()
    await settle()

    const links = Array.from(page.querySelectorAll<HTMLAnchorElement>('a.quick-link-card'))
    const hrefs = links.map((a) => a.getAttribute('href'))

    expect(hrefs).toContain('/app/enrollments')
    expect(hrefs).toContain('/app/classes')
    expect(hrefs).toContain('/app/students')
    expect(hrefs).toContain('/app/academic-catalogues')
    expect(hrefs).toContain('/app/attendance')
  })

  it('gracefully handles metric failure without unmounting user session or inventing fictitious metrics', async () => {
    mockedListStudents.mockRejectedValue(new ApiError(500, 'database error'))

    const page = renderPage()
    await settle()

    // Session remains intact
    expect(page.textContent).toContain('Administrateur')
    expect(page.textContent).toContain('admin@example.test')

    // Metric failure is shown
    expect(page.textContent).toContain('Indicateurs indisponibles')
    expect(page.textContent).toContain('Impossible de charger les indicateurs de pilotage.')

    // No fictitious metrics
    expect(page.querySelector('[data-testid="dashboard-metrics-grid"]')).toBeNull()
  })

  it('does not render fictitious metrics when the identity request fails', async () => {
    mockedGetCurrentUser.mockRejectedValue(new ApiError(500, 'internal'))

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Espace indisponible')
    expect(page.textContent).not.toContain('Élèves inscrits')
    expect(page.querySelector('[role="alert"]')).not.toBeNull()
  })

  it('renders a safe empty-session error when no session exists', async () => {
    mockedGetSession.mockReturnValue(null)

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Votre session est indisponible')
    expect(mockedGetCurrentUser).not.toHaveBeenCalled()
  })
})
