import { useState } from 'react'

import { getStudentRiskAIDiagnosis, type StudentRiskAIDiagnosis } from '../ai.service'
import './StudentRiskAIDiagnosisPanel.css'

type StudentRiskAIDiagnosisPanelProps = {
  studentId: string
  academicPeriodId: string
}

function riskBadgeClass(level: string): string {
  const norm = level.toLowerCase()
  if (norm === 'low' || norm === 'faible') return 'student-risk-ai-panel__level-badge--low'
  if (norm === 'medium' || norm === 'modere' || norm === 'moyen') {
    return 'student-risk-ai-panel__level-badge--medium'
  }
  return 'student-risk-ai-panel__level-badge--high'
}

function riskLabel(level: string): string {
  const norm = level.toLowerCase()
  if (norm === 'low' || norm === 'faible') return 'Risque Faible'
  if (norm === 'medium' || norm === 'modere' || norm === 'moyen') return 'Risque Modéré'
  if (norm === 'high' || norm === 'eleve') return 'Risque Élevé'
  return level
}

export function StudentRiskAIDiagnosisPanel({
  studentId,
  academicPeriodId,
}: StudentRiskAIDiagnosisPanelProps) {
  const [diagnosis, setDiagnosis] = useState<StudentRiskAIDiagnosis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDiagnose = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getStudentRiskAIDiagnosis(studentId, academicPeriodId)
      setDiagnosis(data)
    } catch {
      setError('Impossible de générer le diagnostic de risque pour cette période.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="student-risk-ai-panel" aria-labelledby="ai-diagnosis-title">
      <div className="student-risk-ai-panel__header">
        <h3 id="ai-diagnosis-title" className="student-risk-ai-panel__title">
          <span>🤖</span> Copilote IA — Diagnostic de Risque Précoce
        </h3>
        <button
          type="button"
          className="student-risk-ai-panel__btn"
          disabled={loading || !academicPeriodId}
          onClick={() => void handleDiagnose()}
        >
          {loading ? 'Diagnostic en cours…' : diagnosis ? 'Actualiser le diagnostic' : 'Lancer le diagnostic IA'}
        </button>
      </div>

      {error && <p className="student-risk-ai-panel__error" role="alert">{error}</p>}

      {diagnosis && (
        <div className="student-risk-ai-panel__result">
          <div className="student-risk-ai-panel__badges">
            <span className={`student-risk-ai-panel__level-badge ${riskBadgeClass(diagnosis.risk_level)}`}>
              {riskLabel(diagnosis.risk_level)}
            </span>
            <span className="student-risk-ai-panel__score">
              Score de risque : <strong>{diagnosis.risk_score} / 100</strong>
            </span>
          </div>

          <div className="student-risk-ai-panel__summary">
            {diagnosis.diagnostic_summary}
          </div>

          {diagnosis.root_causes.length > 0 && (
            <>
              <h4 className="student-risk-ai-panel__section-title">Facteurs et causes identifiés :</h4>
              <ul className="student-risk-ai-panel__list">
                {diagnosis.root_causes.map((cause, idx) => (
                  <li key={idx}>{cause}</li>
                ))}
              </ul>
            </>
          )}

          {diagnosis.action_plan.length > 0 && (
            <>
              <h4 className="student-risk-ai-panel__section-title">Plan de remédiation recommandé :</h4>
              <ul className="student-risk-ai-panel__list student-risk-ai-panel__list--action">
                {diagnosis.action_plan.map((action, idx) => (
                  <li key={idx}>✓ {action}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </section>
  )
}
