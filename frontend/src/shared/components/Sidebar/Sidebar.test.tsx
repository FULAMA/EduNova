// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'

import { Sidebar } from './Sidebar'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderSidebar(initialEntries = ['/app']) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => root?.render(createElement(MemoryRouter, { initialEntries }, createElement(Sidebar))))
  return host
}

describe('Sidebar', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
  })

  it('keeps every navigation link named and labeled in compact viewport layouts', () => {
    const page = renderSidebar()
    const links = Array.from(page.querySelectorAll('nav a'))

    expect(links).toHaveLength(7)
    expect(links.map((link) => link.getAttribute('aria-label'))).toEqual([
      'Tableau de bord',
      'Élèves',
      'Classes',
      'Inscriptions',
      'Presences',
      'Finances',
      'Configuration scolaire',
    ])
    expect(links.every((link) => link.textContent?.includes(link.getAttribute('aria-label') ?? ''))).toBe(true)
    expect(links.map((link) => link.getAttribute('href'))).toEqual([
      '/app',
      '/app/students',
      '/app/classes',
      '/app/enrollments',
      '/app/attendance',
      '/app/finance',
      '/app/academic-catalogues',
    ])
  })

  it('exposes the active navigation page to assistive technology', () => {
    const page = renderSidebar(['/app/classes'])
    const activeLink = page.querySelector('nav a[aria-current="page"]')

    expect(activeLink?.getAttribute('href')).toBe('/app/classes')
    expect(activeLink?.textContent).toContain('Classes')
  })
})
