// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as aiService from '../ai.service'
import { ReportCardAIFeedbackModal } from './ReportCardAIFeedbackModal'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderModal(
  reportCardId = 'rc-1',
  onClose = vi.fn(),
  onApply = vi.fn(),
) {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(ReportCardAIFeedbackModal, { reportCardId, onClose, onApply }))
  })
  return host
}

describe('ReportCardAIFeedbackModal', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.restoreAllMocks()
  })

  it('renders the 3 variants and triggers onApply when Insérer is clicked', async () => {
    const mockFeedback: aiService.ReportCardAIFeedback = {
      report_card_id: 'rc-1',
      student_name: 'Ephraim Kasongo',
      encouraging: 'Bravo pour cet engagement soutenu.',
      analytical: 'Moyenne de 14.5 avec régularité.',
      demanding: 'Peut viser l’excellence en approfondissant.',
    }

    vi.spyOn(aiService, 'getReportCardAIFeedback').mockResolvedValue(mockFeedback)
    const onApply = vi.fn()
    const onClose = vi.fn()

    const page = renderModal('rc-1', onClose, onApply)

    // Allow promise resolution
    await act(async () => {
      await Promise.resolve()
    })

    expect(page.textContent).toContain('Ephraim Kasongo')
    expect(page.textContent).toContain('Bravo pour cet engagement soutenu.')
    expect(page.textContent).toContain('Moyenne de 14.5 avec régularité.')
    expect(page.textContent).toContain('Peut viser l’excellence en approfondissant.')

    const insertButtons = Array.from(page.querySelectorAll('button')).filter((b) =>
      b.textContent?.includes('Insérer'),
    )
    expect(insertButtons.length).toBe(3)

    await act(async () => {
      insertButtons[0]?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    })

    expect(onApply).toHaveBeenCalledWith('Bravo pour cet engagement soutenu.')
    expect(onClose).toHaveBeenCalled()
  })
})
