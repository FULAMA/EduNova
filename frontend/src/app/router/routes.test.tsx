// @vitest-environment jsdom
import { act, createElement, isValidElement, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { createMemoryRouter, MemoryRouter, RouterProvider } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { routes } from './routes'
import { RequireAuth } from '../../features/auth/components/RequireAuth'
import { Sidebar } from '../../shared/components/Sidebar/Sidebar'

vi.mock('../../features/auth/components/RequireAuth', () => ({
  RequireAuth: ({ children }: { children: ReactNode }) => children,
}))

vi.mock('../../shared/components/Topbar/Topbar', () => ({
  Topbar: () => null,
}))

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderAt(path: string) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  act(() => {
    root?.render(createElement(RouterProvider, { router }))
  })
  return host
}

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
})

describe('frontend routes', () => {
  it('shows a fallback for unknown URLs', () => {
    const page = renderAt('/unknown-page')

    expect(page.textContent).toContain('Page introuvable')
    expect(page.querySelector('a[href="/app"]')?.textContent).toContain('Retour au tableau de bord')
  })

  it('shows a fallback for unknown paths inside the protected app shell', () => {
    const page = renderAt('/app/unknown-page')

    expect(page.textContent).toContain('Page introuvable')
  })

  it('keeps login and protected app route declarations', () => {
    const loginRoute = routes.find((route) => route.path === '/login')
    const appRoute = routes.find((route) => route.path === '/app')

    expect(loginRoute).toBeDefined()
    expect(appRoute && isValidElement(appRoute.element) && appRoute.element.type).toBe(RequireAuth)
  })

  it('only displays sidebar links that resolve to declared app routes', () => {
    host = document.createElement('div')
    document.body.append(host)
    root = createRoot(host)
    act(() => {
      root?.render(createElement(
        MemoryRouter,
        null,
        createElement(Sidebar),
      ))
    })

    const appRoute = routes.find((route) => route.path === '/app')
    const registeredPaths = new Set([
      '/app',
      ...(appRoute?.children ?? [])
        .filter((route) => route.path && route.path !== '*')
        .map((route) => `/app/${route.path}`),
    ])
    const sidebarLinks = [...host.querySelectorAll<HTMLAnchorElement>('nav a, .sidebar__footer a')]

    expect(sidebarLinks.length).toBeGreaterThan(0)
    expect(sidebarLinks.every((link) => registeredPaths.has(link.getAttribute('href') ?? ''))).toBe(true)
    expect(host.textContent).not.toContain('Enseignants')
    expect(host.textContent).not.toContain('Évaluations')
    expect(host.textContent).not.toContain('Bulletins')
    expect(host.textContent).not.toContain('Paramètres')
  })
})
