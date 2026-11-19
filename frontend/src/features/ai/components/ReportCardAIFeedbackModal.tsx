import { useEffect, useState } from 'react'

import { getReportCardAIFeedback, type ReportCardAIFeedback } from '../ai.service'
import './ReportCardAIFeedbackModal.css'

type ReportCardAIFeedbackModalProps = {
  reportCardId: string
  onClose: () => void
  onApply?: (feedback: string) => void
}

export function ReportCardAIFeedbackModal({
  reportCardId,
  onClose,
  onApply,
}: ReportCardAIFeedbackModalProps) {
  const [data, setData] = useState<ReportCardAIFeedback | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    getReportCardAIFeedback(reportCardId)
      .then((res) => {
        if (!active) return
        setData(res)
        setLoading(false)
      })
      .catch(() => {
        if (!active) return
        setError('Impossible de générer les suggestions d’appréciations pour ce bulletin.')
        setLoading(false)
      })
    return () => {
      active = false
    }
  }, [reportCardId])

  const copyToClipboard = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedKey(key)
      setTimeout(() => setCopiedKey(null), 2000)
    } catch {
      // Fallback
    }
  }

  return (
    <div className="ai-feedback-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="ai-feedback-title">
      <div className="ai-feedback-modal">
        <div className="ai-feedback-modal__header">
          <h3 id="ai-feedback-title">
            <span>✨</span> Copilote IA — Appréciations de Bulletin
          </h3>
          <button type="button" className="ai-feedback-modal__close" onClick={onClose} aria-label="Fermer">
            ×
          </button>
        </div>

        <div className="ai-feedback-modal__body">
          {loading && <p>Génération de 3 variantes personnalisées en cours…</p>}
          {error && <p role="alert" style={{ color: '#c53030' }}>{error}</p>}

          {data && (
            <>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', color: '#4a5568' }}>
                Élève : <strong>{data.student_name}</strong>
              </p>

              <div className="ai-feedback-modal__card">
                <h4 className="ai-feedback-modal__card-title">🌟 Variante Encourageante & Bienveillante</h4>
                <div className="ai-feedback-modal__card-text">{data.encouraging}</div>
                <div className="ai-feedback-modal__actions">
                  <button
                    type="button"
                    className="ai-feedback-modal__copy-btn"
                    onClick={() => void copyToClipboard(data.encouraging, 'encouraging')}
                  >
                    {copiedKey === 'encouraging' ? '✓ Copié !' : 'Copier'}
                  </button>
                  {onApply && (
                    <button
                      type="button"
                      className="ai-feedback-modal__copy-btn"
                      onClick={() => {
                        onApply(data.encouraging)
                        onClose()
                      }}
                    >
                      Insérer
                    </button>
                  )}
                </div>
              </div>

              <div className="ai-feedback-modal__card">
                <h4 className="ai-feedback-modal__card-title">⚖️ Variante Analytique & Équilibrée</h4>
                <div className="ai-feedback-modal__card-text">{data.analytical}</div>
                <div className="ai-feedback-modal__actions">
                  <button
                    type="button"
                    className="ai-feedback-modal__copy-btn"
                    onClick={() => void copyToClipboard(data.analytical, 'analytical')}
                  >
                    {copiedKey === 'analytical' ? '✓ Copié !' : 'Copier'}
                  </button>
                  {onApply && (
                    <button
                      type="button"
                      className="ai-feedback-modal__copy-btn"
                      onClick={() => {
                        onApply(data.analytical)
                        onClose()
                      }}
                    >
                      Insérer
                    </button>
                  )}
                </div>
              </div>

              <div className="ai-feedback-modal__card">
                <h4 className="ai-feedback-modal__card-title">🎯 Variante Exigeante & Rigueur</h4>
                <div className="ai-feedback-modal__card-text">{data.demanding}</div>
                <div className="ai-feedback-modal__actions">
                  <button
                    type="button"
                    className="ai-feedback-modal__copy-btn"
                    onClick={() => void copyToClipboard(data.demanding, 'demanding')}
                  >
                    {copiedKey === 'demanding' ? '✓ Copié !' : 'Copier'}
                  </button>
                  {onApply && (
                    <button
                      type="button"
                      className="ai-feedback-modal__copy-btn"
                      onClick={() => {
                        onApply(data.demanding)
                        onClose()
                      }}
                    >
                      Insérer
                    </button>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
