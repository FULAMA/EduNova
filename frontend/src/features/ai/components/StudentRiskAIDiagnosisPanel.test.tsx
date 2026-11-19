// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as aiService from '../ai.service'
import { StudentRiskAIDiagnosisPanel } from './StudentRiskAIDiagnosisPanel'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

let root: Root | undefined
let host: HTMLDivElement

function renderPanel(studentId = 's-1', academicPeriodId = 'p-1') {
  host = document.createElement('div')
  document.body.append(host)
  root = createRoot(host)
  act(() => {
    root?.render(createElement(StudentRiskAIDiagnosisPanel, { studentId, academicPeriodId }))
  })
  return host
}

describe('StudentRiskAIDiagnosisPanel', () => {
  afterEach(() => {
    act(() => root?.unmount())
    host?.remove()
    vi.restoreAllMocks()
  })

  it('renders trigger button and loads risk diagnosis upon click', async () => {
    const mockDiagnosis: aiService.StudentRiskAIDiagnosis = {
      student_id: 's-1',
      student_name: 'Ephraim Kasongo',
      academic_period_id: 'p-1',
      risk_level: 'HIGH',
      risk_score: 75,
      diagnostic_summary: 'Décrochage sévère constaté en Mathématiques et Physique.',
      root_causes: ['Moyenne de 7.5/20', '8 absences injustifiées'],
      action_plan: [
        'Mise en place d’un tutorat hebdomadaire',
        'Entretien avec les parents',
        'Contrat pédagogique individualisé',
      ],
    }

    const spy = vi.spyOn(aiService, 'getStudentRiskAIDiagnosis').mockResolvedValue(mockDiagnosis)

    const page = renderPanel()
    const btn = page.querySelector('button.student-risk-ai-panel__btn')
    expect(btn).not.toBeNull()
    expect(btn?.textContent).toContain('Lancer le diagnostic IA')

    await act(async () => {
      btn?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    })

    expect(spy).toHaveBeenCalledWith('s-1', 'p-1')
    expect(page.textContent).toContain('Risque Élevé')
    expect(page.textContent).toContain('75 / 100')
    expect(page.textContent).toContain('Décrochage sévère constaté en Mathématiques et Physique.')
    expect(page.textContent).toContain('8 absences injustifiées')
    expect(page.textContent).toContain('Mise en place d’un tutorat hebdomadaire')
  })
})
