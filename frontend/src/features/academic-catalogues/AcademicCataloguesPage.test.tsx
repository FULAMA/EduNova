// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createAcademicCalendar, createAcademicPeriod, createSubject, listAcademicCalendars, listAcademicPeriods, listSubjects, updateSubject } from './academic-catalogue.service'
import { activateAcademicYear, closeAcademicYear, createAcademicYear, listAcademicYears } from '../enrollments/enrollment.service'
import AcademicCataloguesPage from './AcademicCataloguesPage'

vi.mock('./academic-catalogue.service', () => ({
  createAcademicCalendar: vi.fn(), createAcademicPeriod: vi.fn(), createSubject: vi.fn(), listAcademicCalendars: vi.fn(), listAcademicPeriods: vi.fn(), listSubjects: vi.fn(), updateSubject: vi.fn(),
}))
vi.mock('../enrollments/enrollment.service', () => ({ activateAcademicYear: vi.fn(), closeAcademicYear: vi.fn(), createAcademicYear: vi.fn(), listAcademicYears: vi.fn() }))
;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true
const subjectList = vi.mocked(listSubjects)
const periodCreate = vi.mocked(createAcademicPeriod)
const calendarCreate = vi.mocked(createAcademicCalendar)
const calendarList = vi.mocked(listAcademicCalendars)
const periodList = vi.mocked(listAcademicPeriods)
const subjectCreate = vi.mocked(createSubject)
const subjectUpdate = vi.mocked(updateSubject)
const yearCreate = vi.mocked(createAcademicYear)
const yearActivate = vi.mocked(activateAcademicYear)
const yearClose = vi.mocked(closeAcademicYear)
let root: Root
let host: HTMLDivElement

async function settle() { await act(async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve() }) }

describe('AcademicCataloguesPage', () => {
  beforeEach(() => {
    subjectList.mockResolvedValue([])
    calendarCreate.mockResolvedValue({ id: 'c2', tenant_id: 'tenant-1', name: 'Secondaire', description: null, is_active: true })
    calendarList.mockResolvedValue([{ id: 'c1', tenant_id: 'tenant-1', name: 'Primaire', description: null, is_active: true }])
    periodCreate.mockResolvedValue({ id: 'p2', name: 'Trimestre 2', start_date: '2027-01-01', end_date: '2027-03-31', academic_year_id: 'y1', academic_calendar_id: 'c1' })
    periodList.mockResolvedValue([{ id: 'p1', name: 'Trimestre 1', start_date: '2026-09-01', end_date: '2026-12-20', academic_calendar_id: 'c1' }])
    vi.mocked(listAcademicYears).mockResolvedValue([{ id: 'y1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-06-30', status: 'ACTIVE' }])
    yearCreate.mockResolvedValue({ id: 'y2', label: '2027-2028', start_date: '2027-09-01', end_date: '2028-06-30', status: 'DRAFT' })
    yearActivate.mockResolvedValue({ id: 'y2', label: '2027-2028', start_date: '2027-09-01', end_date: '2028-06-30', status: 'ACTIVE' })
    yearClose.mockResolvedValue({ id: 'y1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-06-30', status: 'CLOSED' })
    subjectCreate.mockResolvedValue({ id: 's1', name: 'Biologie', code: 'BIO', coefficient: 2, active: true })
    subjectUpdate.mockResolvedValue({ id: 's1', name: 'Biologie', code: 'BIO', coefficient: 2, active: true })
    host = document.createElement('div'); document.body.append(host); root = createRoot(host)
  })
  afterEach(() => { act(() => root.unmount()); host.remove(); vi.resetAllMocks() })

  it('shows empty catalogue states and persisted period labels', async () => {
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    expect(host.textContent).toContain('Aucune matière')
    expect(host.textContent).toContain('Trimestre 1')
    expect(host.querySelectorAll('.catalogues-card')).toHaveLength(4)
    expect(host.querySelector('.catalogues-form')).not.toBeNull()
  })

  it('distinguishes an empty catalogue from an empty search result and empty periods', async () => {
    periodList.mockResolvedValue([])
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    expect(host.textContent).toContain('Aucune matière n’est enregistrée dans le catalogue.')
    expect(host.textContent).toContain('Aucune période n’est enregistrée.')

    const search = host.querySelector('input[type="search"]') as HTMLInputElement
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      setter?.call(search, 'inconnue')
      search.dispatchEvent(new Event('input', { bubbles: true }))
      await Promise.resolve()
      await Promise.resolve()
    })
    await settle()
    expect(host.textContent).toContain('Aucune matière ne correspond à la recherche.')
  })

  it('does not show empty catalogue messages after a failed initial load and retries successfully', async () => {
    subjectList.mockRejectedValueOnce(new Error('Network failure'))
      .mockResolvedValueOnce([{ id: 's1', name: 'Biologie', code: 'BIO', coefficient: 2, active: true }])
    periodList.mockRejectedValueOnce(new Error('Network failure'))
      .mockResolvedValueOnce([])
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()

    expect(host.querySelector('[role="alert"]')?.textContent).toContain('Réessayer')
    expect(host.textContent).not.toContain('Aucune matière n’est enregistrée dans le catalogue.')
    expect(host.textContent).not.toContain('Aucune période n’est enregistrée.')

    const retry = host.querySelector('[role="alert"] button') as HTMLButtonElement
    await act(async () => { retry.click(); await Promise.resolve(); await Promise.resolve() })
    await settle()

    expect(subjectList).toHaveBeenCalledTimes(2)
    expect(periodList).toHaveBeenCalledTimes(2)
    expect(host.textContent).toContain('Biologie')
    expect(host.textContent).toContain('Aucune période n’est enregistrée.')
    expect(host.querySelector('[role="alert"]')).toBeNull()
  })

  it('submits a subject and reloads the API catalogue', async () => {
    subjectList.mockResolvedValueOnce([]).mockResolvedValueOnce([{ id: 's1', name: 'Biologie', code: 'BIO', coefficient: 2, active: true }])
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    const inputs = host.querySelectorAll('input')
    await act(async () => {
      for (const [input, value] of [[inputs[1], 'Biologie'], [inputs[2], 'BIO'], [inputs[3], '2']] as const) {
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
        setter?.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true }))
      }
    })
    const form = host.querySelector('form')!
    await act(async () => { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    expect(subjectCreate).toHaveBeenCalledWith({ name: 'Biologie', code: 'BIO', coefficient: 2 })
    expect(subjectList).toHaveBeenCalledTimes(2)
  })

  it('creates a period linked to the selected school year', async () => {
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    const periodForm = host.querySelector('[aria-labelledby="periods-title"] form') as HTMLFormElement
    const inputs = periodForm.querySelectorAll('input')
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      for (const [input, value] of [[inputs[0], 'Trimestre 2'], [inputs[1], '2027-01-01'], [inputs[2], '2027-03-31']] as const) {
        setter?.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true }))
      }
      await Promise.resolve()
    })
    await act(async () => { periodForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    expect(periodCreate).toHaveBeenCalledWith({ academic_year_id: 'y1', academic_calendar_id: 'c1', name: 'Trimestre 2', start_date: '2027-01-01', end_date: '2027-03-31' })
  })

  it('creates a calendar and refreshes the persisted calendar list', async () => {
    calendarList.mockResolvedValueOnce([]).mockResolvedValueOnce([{ id: 'c2', tenant_id: 'tenant-1', name: 'Secondaire', description: null, is_active: true }])
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    const calendarForm = host.querySelector('[aria-labelledby="calendars-title"] form') as HTMLFormElement
    const inputs = calendarForm.querySelectorAll('input')
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      setter?.call(inputs[0], 'Secondaire'); inputs[0].dispatchEvent(new Event('input', { bubbles: true }))
      setter?.call(inputs[1], 'Cycle du secondaire'); inputs[1].dispatchEvent(new Event('input', { bubbles: true }))
      await Promise.resolve()
    })
    await act(async () => { calendarForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    expect(calendarCreate).toHaveBeenCalledWith({ name: 'Secondaire', description: 'Cycle du secondaire' })
    expect(calendarList).toHaveBeenCalledTimes(2)
  })

  it('creates a draft school year from the configuration form', async () => {
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    const form = host.querySelector('[aria-labelledby="years-title"] form') as HTMLFormElement
    const inputs = form.querySelectorAll('input')
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      for (const [input, value] of [[inputs[0], '2027-2028'], [inputs[1], '2027-09-01'], [inputs[2], '2028-06-30']] as const) {
        setter?.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true }))
      }
      await Promise.resolve()
    })
    await act(async () => { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    expect(yearCreate).toHaveBeenCalledWith({ label: '2027-2028', start_date: '2027-09-01', end_date: '2028-06-30' })
  })

  it('exposes explicit activation and closure actions for years', async () => {
    vi.mocked(listAcademicYears).mockResolvedValue([
      { id: 'y1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-06-30', status: 'ACTIVE' },
      { id: 'y2', label: '2027-2028', start_date: '2027-09-01', end_date: '2028-06-30', status: 'DRAFT' },
    ])
    act(() => root.render(createElement(AcademicCataloguesPage)))
    await settle()
    const yearSection = host.querySelector('[aria-labelledby="years-title"]')!
    const buttons = [...yearSection.querySelectorAll<HTMLButtonElement>('tbody button')]
    expect(buttons.map((button) => button.textContent)).toEqual(['Clôturer', 'Activer'])
    await act(async () => { buttons[1].click(); await Promise.resolve(); await Promise.resolve() })
    expect(yearActivate).toHaveBeenCalledWith('y2')
    await act(async () => { buttons[0].click(); await Promise.resolve(); await Promise.resolve() })
    expect(yearClose).toHaveBeenCalledWith('y1')
  })
})
