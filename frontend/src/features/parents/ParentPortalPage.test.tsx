// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, expect, it, vi } from 'vitest'

import ParentPortalPage from './ParentPortalPage'
import { getChildReportCards, getParentChildren } from './parent-portal.service'

vi.mock('./parent-portal.service', () => ({
  getChildReportCards: vi.fn(),
  getParentChildren: vi.fn(),
  downloadChildReportCardPdf: vi.fn(),
}))

const mockChildren = vi.mocked(getParentChildren)
const mockCards = vi.mocked(getChildReportCards)
let root: Root | undefined
let host: HTMLDivElement

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  vi.clearAllMocks()
})

it('shows only official bulletins for linked children', async () => {
  mockChildren.mockResolvedValue([{
    student: {
      id: 'student-1', first_name: 'Amina', last_name: 'Kabila',
      email: null, registration_number: null, active: true,
    },
    relationship_type: 'LEGAL_GUARDIAN',
  }])
  mockCards.mockResolvedValue([{
    id: 'report-1', academic_period_id: 'period-1', report_version: 2,
    status: 'ISSUED', issued_at: '2026-06-20T12:00:00Z',
  }])
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)

  await act(async () => root?.render(createElement(ParentPortalPage)))

  expect(host.textContent).toContain('Amina Kabila')
  expect(host.textContent).toContain('Association enregistrée par l’établissement')
  expect(host.textContent).toContain('Bulletin officiel · version 2')
  expect(host.textContent).not.toContain('Factures')
  expect(host.textContent).not.toContain('Présences')
  expect(mockCards).toHaveBeenCalledWith('student-1')
})

it('explains when no student is officially associated with the parent account', async () => {
  mockChildren.mockResolvedValue([])
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)

  await act(async () => root?.render(createElement(ParentPortalPage)))

  expect(host.textContent).toContain('Aucun élève n’est associé')
  expect(mockCards).not.toHaveBeenCalled()
})
