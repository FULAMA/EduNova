// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as aiService from '../ai.service'
import { ParentAISummaryCard } from './ParentAISummaryCard'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderCard(studentId = 's-1', reportCardId = 'rc-1') {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(ParentAISummaryCard, { studentId, reportCardId }))
  })
  return host
}

describe('ParentAISummaryCard', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.restoreAllMocks()
  })

  it('renders the toggle button and toggles open to load the AI summary', async () => {
    const mockSummary: aiService.ParentPortalAISummary = {
      student_id: 's-1',
      report_card_id: 'rc-1',
      period_name: 'Trimestre 1',
      headline: 'Excellent travail ce trimestre pour Ephraim',
      summary: 'Chers parents, votre enfant a obtenu 16/20.',
      tips_for_home: [
        'Maintenir les temps de lecture quotidienne',
        'Consolider les acquis en calcul',
      ],
    }

    const spy = vi.spyOn(aiService, 'getParentPortalAISummary').mockResolvedValue(mockSummary)

    const page = renderCard()
    const toggleBtn = page.querySelector('button.parent-ai-summary__toggle')
    expect(toggleBtn).not.toBeNull()
    expect(toggleBtn?.textContent).toContain('Synthèse & conseils pédagogiques (IA)')

    // Click to open
    await act(async () => {
      toggleBtn?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    })

    expect(spy).toHaveBeenCalledWith('s-1', 'rc-1')
    expect(page.textContent).toContain('Excellent travail ce trimestre pour Ephraim')
    expect(page.textContent).toContain('Chers parents, votre enfant a obtenu 16/20.')
    expect(page.textContent).toContain('Maintenir les temps de lecture quotidienne')
  })
})
