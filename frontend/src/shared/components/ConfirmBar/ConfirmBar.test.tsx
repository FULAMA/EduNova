// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ConfirmBar } from './ConfirmBar'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement | undefined

function renderBar(props: { busy?: boolean; onConfirm?: () => void; onCancel?: () => void } = {}) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(ConfirmBar, {
      message: 'Annuler cette affectation ?',
      confirmLabel: 'Annuler l’affectation',
      cancelLabel: 'Garder',
      busy: props.busy,
      onConfirm: props.onConfirm ?? (() => undefined),
      onCancel: props.onCancel ?? (() => undefined),
    }))
  })
  return host
}

function button(label: string): HTMLButtonElement {
  return [...host!.querySelectorAll('button')].find((item) => item.textContent === label)!
}

afterEach(() => {
  act(() => root?.unmount())
  host?.remove()
  root = undefined
  host = undefined
})

describe('ConfirmBar', () => {
  it('names the dialog with its message and focuses the safe action first', () => {
    const page = renderBar()
    const dialog = page.querySelector('[role="alertdialog"]')!

    expect(page.textContent).toContain('Annuler cette affectation ?')
    expect(dialog.getAttribute('aria-labelledby')).toBeTruthy()
    expect(document.activeElement).toBe(button('Garder'))
  })

  it('calls the right handler for confirm and cancel', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()
    renderBar({ onConfirm, onCancel })

    act(() => button('Annuler l’affectation').click())
    act(() => button('Garder').click())

    expect(onConfirm).toHaveBeenCalledOnce()
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('cancels with Escape', () => {
    const onCancel = vi.fn()
    renderBar({ onCancel })

    act(() => button('Garder').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })))

    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('disables both actions while busy', () => {
    renderBar({ busy: true })

    expect(button('Annuler l’affectation').disabled).toBe(true)
    expect(button('Garder').disabled).toBe(true)
  })
})