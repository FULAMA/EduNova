// @vitest-environment jsdom
import { createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { act } from 'react'
import { afterEach, describe, expect, it } from 'vitest'

import { Badge } from './Badge'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderBadge(props: Parameters<typeof Badge>[0]) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(Badge, props))
  })
  return host
}

describe('Badge (Panda CSS pilot component)', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
  })

  it('renders children with default variant and Panda atomic styles', () => {
    const el = renderBadge({ children: 'Actif' })
    const badge = el.querySelector('span')

    expect(badge).not.toBeNull()
    expect(badge?.textContent).toBe('Actif')
    expect(badge?.className).toContain('display_inline-flex')
    expect(badge?.className).toContain('font-weight_600')
    expect(badge?.className).toContain('background-color_var(--colors-surface-subtle)')
    expect(badge?.className).toContain('border-radius_var(--radii-sm)')
    expect(badge?.className).toContain('font-size_var(--font-sizes-xs)')
  })

  it('applies variant styling classes correctly', () => {
    const el = renderBadge({ variant: 'success', children: 'Validé' })
    const badge = el.querySelector('span')

    expect(badge?.textContent).toBe('Validé')
    expect(badge?.className).toContain('color_var(--colors-status-success)')
  })

  it('preserves additional HTML attributes and custom className', () => {
    const el = renderBadge({
      variant: 'danger',
      children: 'Erreur',
      className: 'custom-class',
      'aria-label': 'Statut d’erreur',
    })
    const badge = el.querySelector('span')

    expect(badge?.getAttribute('aria-label')).toBe('Statut d’erreur')
    expect(badge?.className).toContain('custom-class')
    expect(badge?.className).toContain('color_var(--colors-status-danger)')
  })
})
