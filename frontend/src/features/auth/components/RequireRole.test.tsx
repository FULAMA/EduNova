// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'

import type { AuthenticatedUser } from '../services/auth.service'
import { CurrentUserContext } from './current-user.context'
import { RequireRole } from './RequireRole'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement | undefined

function renderAs(role: string): HTMLDivElement {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  const user = { role } as unknown as AuthenticatedUser
  act(() => {
    root?.render(
      createElement(
        MemoryRouter,
        null,
        createElement(
          CurrentUserContext.Provider,
          { value: user },
          createElement(RequireRole, { module: 'students', children: createElement('p', null, 'Contenu protégé') }),
        ),
      ),
    )
  })
  return host
}

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  host = undefined
})

describe('RequireRole', () => {
  it('renders the page for an allowed role', () => {
    expect(renderAs('ADMIN').textContent).toContain('Contenu protégé')
  })

  it('shows an explicit denial for a forbidden role', () => {
    const page = renderAs('STUDENT')
    expect(page.textContent).not.toContain('Contenu protégé')
    expect(page.textContent).toContain('Accès non autorisé')
  })
})