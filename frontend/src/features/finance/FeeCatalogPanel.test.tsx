// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import FeeCatalogPanel from './FeeCatalogPanel'
import { assignFeeType, listFeeTypes, type FeeType } from './finance.service'

vi.mock('./finance.service', () => ({
  listFeeTypes: vi.fn(),
  createFeeType: vi.fn(),
  updateFeeTypeStatus: vi.fn(),
  assignFeeType: vi.fn(),
}))
vi.mock('../students/services/student.service', () => ({ listStudents: vi.fn() }))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const published = {
  id: 'f1', name: 'Minerval', category: 'Scolaire', amount: '100.00', currency: 'USD', status: 'PUBLISHED',
} as unknown as FeeType

let root: Root | undefined
let host: HTMLDivElement

async function flush() {
  await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)) })
}

async function renderPanel(props: { canManage: boolean; onAssigned?: (id: string) => void }) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => { root?.render(createElement(FeeCatalogPanel, props)) })
  await flush()
}

function button(label: string): HTMLButtonElement | undefined {
  return [...host.querySelectorAll('button')].find((item) => item.textContent?.trim() === label)
}

beforeEach(() => {
  vi.mocked(listFeeTypes).mockResolvedValue([published])
  vi.mocked(listStudents).mockResolvedValue([
    { id: 's1', firstName: 'Marie', lastName: 'Kabila' } as unknown as Student,
  ])
})

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  vi.clearAllMocks()
})

describe('FeeCatalogPanel', () => {
  it('is read-only for roles that cannot manage the catalogue', async () => {
    await renderPanel({ canManage: false })

    expect(host.textContent).toContain('Minerval')
    expect(host.textContent).toContain('100,00\u00a0USD')
    expect(host.querySelector('form')).toBeNull()
    expect(button('Attribuer')).toBeUndefined()
    expect(button('Archiver')).toBeUndefined()
    expect(listStudents).not.toHaveBeenCalled()
  })

  it('asks for confirmation before assigning and reports the backend result', async () => {
    vi.mocked(assignFeeType).mockResolvedValue({ amount: '100.00', currency: 'USD' } as never)
    const onAssigned = vi.fn()
    await renderPanel({ canManage: true, onAssigned })

    const select = [...host.querySelectorAll('select')].find((item) => item.textContent?.includes('Choisir un élève')) as HTMLSelectElement
    act(() => {
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')!.set!.call(select, 's1')
      select.dispatchEvent(new Event('change', { bubbles: true }))
    })
    act(() => button('Attribuer')!.click())

    expect(assignFeeType).not.toHaveBeenCalled()
    expect(host.textContent).toContain('Attribuer à Marie Kabila ?')

    await act(async () => button('Confirmer')!.click())
    await flush()

    expect(assignFeeType).toHaveBeenCalledWith('f1', 's1')
    expect(onAssigned).toHaveBeenCalledWith('s1')
    expect(host.textContent).toContain('100,00\u00a0USD')
  })
})