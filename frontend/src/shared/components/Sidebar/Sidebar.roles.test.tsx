// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'

import { Sidebar } from './Sidebar'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement | undefined

function hrefsFor(role: string): string[] {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(MemoryRouter, null, createElement(Sidebar, { role })))
  })
  return [...host.querySelectorAll<HTMLAnchorElement>('nav a')].map(
    (link) => link.getAttribute('href') ?? '',
  )
}

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  host = undefined
})

describe('Sidebar by role', () => {
  it('shows every module to ADMIN', () => {
    expect(hrefsFor('ADMIN')).toHaveLength(7)
  })

  it('opens the student portal from the dashboard entry', () => {
    expect(hrefsFor('STUDENT')).toEqual(['/app'])
  })

  it('shows only the parent area to PARENT', () => {
    expect(hrefsFor('PARENT')).toEqual(['/app/parent-portal'])
  })

  it('shows only the teacher area to canonical and legacy teacher roles', () => {
    expect(hrefsFor('PROF')).toEqual(['/app/teacher-portal'])
    expect(hrefsFor('TEACHER')).toEqual(['/app/teacher-portal'])
  })

  it('shows dashboard and finance to a cashier', () => {
    expect(hrefsFor('CASHIER')).toEqual(['/app', '/app/finance'])
  })

  it('shows dashboard, students, classes and finance to direction', () => {
    expect(hrefsFor('DIRECTION')).toEqual(['/app', '/app/students', '/app/classes', '/app/finance'])
  })
})
