// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../../shared/api/client'
import { getCurrentUser, getSession } from '../../auth/services/auth.service'
import { getDirectionDashboard } from '../services/dashboard.service'
import type { DirectionDashboardData } from '../types/dashboard.types'
import DashboardPage from './DashboardPage'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

vi.mock('../../auth/services/auth.service', () => ({
  getCurrentUser: vi.fn(),
  getSession: vi.fn(),
  linkGoogleIdentity: vi.fn(),
}))

vi.mock('../services/dashboard.service', () => ({
  getDirectionDashboard: vi.fn(),
}))

const mockedGetCurrentUser = vi.mocked(getCurrentUser)
const mockedGetSession = vi.mocked(getSession)
const mockedGetDirectionDashboard = vi.mocked(getDirectionDashboard)

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

const mockDashboardData: DirectionDashboardData = {
  active_students: 42,
  headcount_by_class: [
    { class_id: 'c-1', class_name: '7e EB A', active_students: 25 },
    { class_id: 'c-2', class_name: '8e EB B', active_students: 17 },
  ],
  expected_amounts: [
    { currency: 'USD', amount: '5000.00' },
    { currency: 'CDF', amount: '1200000.00' },
  ],
  paid_amounts: [
    { currency: 'USD', amount: '3500.00' },
    { currency: 'CDF', amount: '600000.00' },
  ],
  remaining_amounts: [
    { currency: 'USD', amount: '1500.00' },
    { currency: 'CDF', amount: '600000.00' },
  ],
  recovery_rates: [
    { currency: 'USD', rate_percent: '70.00' },
    { currency: 'CDF', rate_percent: '50.00' },
  ],
  financial_by_class: [
    {
      class_id: 'c-1',
      class_name: '7e EB A',
      expected: [{ currency: 'USD', amount: '3000.00' }],
      paid: [{ currency: 'USD', amount: '2000.00' }],
      remaining: [{ currency: 'USD', amount: '1000.00' }],
    },
    {
      class_id: 'c-2',
      class_name: '8e EB B',
      expected: [{ currency: 'CDF', amount: '1200000.00' }],
      paid: [{ currency: 'CDF', amount: '600000.00' }],
      remaining: [{ currency: 'CDF', amount: '600000.00' }],
    },
  ],
}

describe('DashboardPage', () => {
  beforeEach(() => {
    mockedGetSession.mockReturnValue({
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
      email: 'directeur@example.test',
      tenantId: 'tenant-1',
    })

    mockedGetCurrentUser.mockResolvedValue({
      id: 'user-dir-1',
      email: 'directeur@example.test',
      role: 'DIRECTION',
      is_active: true,
      two_factor_enabled: true,
    })

    mockedGetDirectionDashboard.mockResolvedValue(mockDashboardData)
  })

  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.resetAllMocks()
  })

  it('shows the authenticated DIRECTION identity and real business metrics from GET /dashboard/direction', async () => {
    const page = renderPage()
    expect(page.textContent).toContain('Chargement de votre session...')
    await settle()

    // Identity check
    expect(page.textContent).toContain('Direction')
    expect(page.textContent).toContain('directeur@example.test')

    // Real Key Indicators
    expect(page.textContent).toContain('Élèves actifs')
    expect(page.textContent).toContain('42')
    expect(page.textContent).toContain('42 élèves actifs dans l’établissement')

    expect(page.textContent).toContain('Classes avec effectifs')
    expect(page.textContent).toContain('2')

    // Multi-currency recovery rates (USD & CDF separated per Decision 19 & 23)
    expect(page.textContent).toContain('Recouvrement (USD)')
    expect(page.textContent).toContain('70.00 %')
    expect(page.textContent).toContain('Recouvrement (CDF)')
    expect(page.textContent).toContain('50.00 %')

    // Table of class headcounts
    expect(page.textContent).toContain('Effectifs par classe')
    expect(page.textContent).toContain('7e EB A')
    expect(page.textContent).toContain('25')
    expect(page.textContent).toContain('8e EB B')
    expect(page.textContent).toContain('17')

    // Financial breakdown by class
    expect(page.textContent).toContain('Situation financière par classe')
    expect(page.textContent).toContain('1 000,00 USD')
    expect(page.textContent).toContain('600 000,00 CDF')
  })

  it('restricts quick links for DIRECTION role to authorized modules only (students, classes, finance)', async () => {
    const page = renderPage()
    await settle()

    const links = Array.from(page.querySelectorAll<HTMLAnchorElement>('a.quick-link-card'))
    const hrefs = links.map((a) => a.getAttribute('href'))

    // DIRECTION authorized modules
    expect(hrefs).toContain('/app/students')
    expect(hrefs).toContain('/app/classes')
    expect(hrefs).toContain('/app/finance')

    // ADMIN exclusive modules MUST NOT be shown to DIRECTION
    expect(hrefs).not.toContain('/app/enrollments')
    expect(hrefs).not.toContain('/app/academic-catalogues')
    expect(hrefs).not.toContain('/app/attendance')
  })

  it('renders ADMIN exclusive quick links when user is ADMIN', async () => {
    mockedGetCurrentUser.mockResolvedValue({
      id: 'admin-1',
      email: 'admin@example.test',
      role: 'ADMIN',
      is_active: true,
      two_factor_enabled: false,
    })

    const page = renderPage()
    await settle()

    const links = Array.from(page.querySelectorAll<HTMLAnchorElement>('a.quick-link-card'))
    const hrefs = links.map((a) => a.getAttribute('href'))

    expect(hrefs).toContain('/app/enrollments')
    expect(hrefs).toContain('/app/classes')
    expect(hrefs).toContain('/app/students')
    expect(hrefs).toContain('/app/academic-catalogues')
    expect(hrefs).toContain('/app/attendance')
    expect(hrefs).toContain('/app/finance')
  })

  it('handles empty dashboard data without crashes and with clear empty states', async () => {
    mockedGetDirectionDashboard.mockResolvedValue({
      active_students: 0,
      headcount_by_class: [],
      expected_amounts: [],
      paid_amounts: [],
      remaining_amounts: [],
      recovery_rates: [],
      financial_by_class: [],
    })

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Élèves actifs')
    expect(page.textContent).toContain('0')
    expect(page.textContent).toContain('Aucun frais ouvert enregistré pour le moment')
    expect(page.textContent).toContain('Aucune classe avec élèves actifs pour le moment.')
    expect(page.textContent).toContain('Aucune obligation financière enregistrée par classe.')
  })

  it('gracefully handles dashboard API failure without unmounting user session or inventing fictitious metrics', async () => {
    mockedGetDirectionDashboard.mockRejectedValue(new ApiError(500, 'database error'))

    const page = renderPage()
    await settle()

    // Session remains intact
    expect(page.textContent).toContain('Direction')
    expect(page.textContent).toContain('directeur@example.test')

    // Metric failure is shown
    expect(page.textContent).toContain('Indicateurs indisponibles')
    expect(page.textContent).toContain('Impossible de charger les indicateurs de pilotage de l’établissement.')

    // No fictitious metrics
    expect(page.querySelector('[data-testid="dashboard-metrics-grid"]')).toBeNull()
  })

  it('does not render fictitious metrics when the identity request fails', async () => {
    mockedGetCurrentUser.mockRejectedValue(new ApiError(500, 'internal'))

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Espace indisponible')
    expect(page.textContent).not.toContain('Élèves actifs')
    expect(page.querySelector('[role="alert"]')).not.toBeNull()
  })

  it('renders a safe empty-session error when no session exists', async () => {
    mockedGetSession.mockReturnValue(null)

    const page = renderPage()
    await settle()

    expect(page.textContent).toContain('Votre session est indisponible')
    expect(mockedGetCurrentUser).not.toHaveBeenCalled()
    expect(mockedGetDirectionDashboard).not.toHaveBeenCalled()
  })
})
