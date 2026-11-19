import { useState } from 'react'

import { getParentPortalAISummary, type ParentPortalAISummary } from '../ai.service'
import './ParentAISummaryCard.css'

type ParentAISummaryCardProps = {
  studentId: string
  reportCardId: string
}

export function ParentAISummaryCard({ studentId, reportCardId }: ParentAISummaryCardProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [summary, setSummary] = useState<ParentPortalAISummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleToggle = async () => {
    if (isOpen) {
      setIsOpen(false)
      return
    }

    setIsOpen(true)
    if (summary) return

    setLoading(true)
    setError(null)
    try {
      const data = await getParentPortalAISummary(studentId, reportCardId)
      setSummary(data)
    } catch {
      setError('Impossible de générer la synthèse explicative pour le moment.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="parent-ai-summary">
      <button
        type="button"
        className="parent-ai-summary__toggle"
        onClick={() => void handleToggle()}
        aria-expanded={isOpen}
      >
        <span>💡</span> {isOpen ? 'Masquer la synthèse IA' : 'Synthèse & conseils pédagogiques (IA)'}
      </button>

      {isOpen && (
        <div className="parent-ai-summary__content" role="region" aria-label="Synthèse pédagogique IA">
          {loading && <p className="parent-ai-summary__loading">Analyse pédagogique en cours…</p>}
          {error && <p className="parent-ai-summary__error" role="alert">{error}</p>}
          {summary && (
            <>
              <span className="parent-ai-summary__badge">EduNova IA Pédagogique</span>
              <h4 className="parent-ai-summary__headline">{summary.headline}</h4>
              <p className="parent-ai-summary__text">{summary.summary}</p>

              {summary.tips_for_home.length > 0 && (
                <>
                  <h5 className="parent-ai-summary__tips-title">Conseils pour la maison :</h5>
                  <ul className="parent-ai-summary__tips-list">
                    {summary.tips_for_home.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
