import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiRequest } from '../../shared/api/client'
import {
  getParentPortalAISummary,
  getReportCardAIFeedback,
  getStudentRiskAIDiagnosis,
} from './ai.service'

vi.mock('../../shared/api/client', () => ({ apiRequest: vi.fn() }))
const mockedRequest = vi.mocked(apiRequest)

describe('ai.service', () => {
  afterEach(() => vi.resetAllMocks())

  it('calls POST /ai/report-cards/{id}/feedback', async () => {
    const mockResponse = {
      report_card_id: 'rc-1',
      student_name: 'Ephraim Kasongo',
      encouraging: 'Très bon trimestre',
      analytical: 'Moyenne satisfaisante',
      demanding: 'Doit intensifier ses efforts',
    }
    mockedRequest.mockResolvedValueOnce(mockResponse)

    const result = await getReportCardAIFeedback('rc-1')
    expect(result).toEqual(mockResponse)
    expect(mockedRequest).toHaveBeenCalledWith('/ai/report-cards/rc-1/feedback', {
      method: 'POST',
      authenticated: true,
    })
  })

  it('calls POST /ai/students/{id}/risk-diagnosis with academic_period_id query parameter', async () => {
    const mockDiagnosis = {
      student_id: 's-1',
      student_name: 'Ephraim Kasongo',
      academic_period_id: 'p-1',
      risk_level: 'LOW',
      risk_score: 15,
      diagnostic_summary: 'Situation académique stable',
      root_causes: ['Aucun décrochage'],
      action_plan: ['Maintenir le rythme'],
    }
    mockedRequest.mockResolvedValueOnce(mockDiagnosis)

    const result = await getStudentRiskAIDiagnosis('s-1', 'p-1')
    expect(result).toEqual(mockDiagnosis)
    expect(mockedRequest).toHaveBeenCalledWith(
      '/ai/students/s-1/risk-diagnosis?academic_period_id=p-1',
      {
        method: 'POST',
        authenticated: true,
      },
    )
  })

  it('calls GET /parent-portal/students/{sId}/report-cards/{rcId}/ai-summary', async () => {
    const mockSummary = {
      student_id: 's-1',
      report_card_id: 'rc-1',
      period_name: 'Trimestre 1',
      headline: 'Félicitations pour le Trimestre 1',
      summary: 'Chers parents, votre enfant a bien travaillé.',
      tips_for_home: ['Continuer la lecture quotidienne'],
    }
    mockedRequest.mockResolvedValueOnce(mockSummary)

    const result = await getParentPortalAISummary('s-1', 'rc-1')
    expect(result).toEqual(mockSummary)
    expect(mockedRequest).toHaveBeenCalledWith(
      '/parent-portal/students/s-1/report-cards/rc-1/ai-summary',
      {
        method: 'GET',
        authenticated: true,
      },
    )
  })
})
