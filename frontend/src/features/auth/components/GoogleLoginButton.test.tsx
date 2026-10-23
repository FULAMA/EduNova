// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it } from 'vitest'

import { GoogleLoginButton } from './GoogleLoginButton'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement | undefined

describe('GoogleLoginButton', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    root = undefined
    host = undefined
  })

  it('keeps a visible, honest fallback when Google is not configured', () => {
    host = document.createElement('div')
    document.body.append(host)
    root = createRoot(host)

    act(() => root?.render(createElement(GoogleLoginButton, { onCredential: () => undefined })))

    const button = host.querySelector('button') as HTMLButtonElement | null
    expect(button).not.toBeNull()
    expect(button?.disabled).toBe(true)
    expect(button?.getAttribute('aria-label')).toContain('Google')
    expect(button?.textContent).toContain('Continuer avec Google')
    expect(button?.querySelector('svg')).not.toBeNull()
  })
})
