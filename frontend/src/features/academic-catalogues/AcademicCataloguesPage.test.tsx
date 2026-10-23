// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createAcademicPeriod, createSubject, listAcademicPeriods, listSubjects, updateSubject } from './academic-catalogue.service'
import { listAcademicYears } from '../enrollments/enrollment.service'
import AcademicCataloguesPage from './AcademicCataloguesPage'

vi.mock('./academic-catalogue.service', () => ({
  createAcademicPeriod: vi.fn(), createSubject: vi.fn(), listAcademicPeriods: vi.fn(), listSubjects: vi.fn(), updateSubject: vi.fn(),
}))
vi.mock('../enrollments/enrollment.service', () => ({ listAcademicYears: vi.fn() }))
;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true
const subjectList = vi.mocked(listSubjects)
const periodCreate = vi.mocked(createAcademicPeriod)
const periodList = vi.mocked(listAcademicPeriods)
const subjectCreate = vi.mocked(createSubject)
const subjectUpdate = vi.mocked(updateSubject)
let root: Root
let host: HTMLDivElement

async function settle() { await act(async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve() }) }

describe('AcademicCataloguesPage', () => {
  beforeEach(() => {
    subjectList.mockResolvedValue([])
    periodCreate.mockResolvedValue({ id: 'p2', name: 'Trimestre 2', start_date: '2027-01-01', end_date: '2027-03-31', academic_year_id: 'y1' })
    periodList.mockResolvedValue([{ id: 'p1', name: 'Trimestre 1', start_date: '2026-09-01', end_date: '2026-12-20' }])
    vi.mocked(listAcademicYears).mockResolvedValue([{ id: 'y1', label: '2026-2027', start_date: '2026-09-01', end_date: '2027-06-30', status: 'ACTIVE' }])
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
    expect(host.querySelectorAll('.catalogues-card')).toHaveLength(2)
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
    const periodForm = host.querySelectorAll('form')[1]
    const inputs = periodForm.querySelectorAll('input')
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
      for (const [input, value] of [[inputs[0], 'Trimestre 2'], [inputs[1], '2027-01-01'], [inputs[2], '2027-03-31']] as const) {
        setter?.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true }))
      }
      await Promise.resolve()
    })
    await act(async () => { periodForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await Promise.resolve(); await Promise.resolve() })
    expect(periodCreate).toHaveBeenCalledWith({ academic_year_id: 'y1', name: 'Trimestre 2', start_date: '2027-01-01', end_date: '2027-03-31' })
  })
})
