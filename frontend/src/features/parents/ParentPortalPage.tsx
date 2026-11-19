import { useEffect, useState } from 'react'

import { ApiError } from '../../shared/api/client'
import { PageHeader } from '../../shared/components/PageHeader/PageHeader'
import { ParentAISummaryCard } from '../ai/components/ParentAISummaryCard'
import {
  downloadChildReportCardPdf,
  getChildReportCards,
  getParentChildren,
  type ParentChild,
  type ParentReportCard,
} from './parent-portal.service'

import './ParentPortalPage.css'
import '../../shared/styles/portals.css'

function accessError(error: unknown): string {
  if (error instanceof ApiError && error.status === 0) {
    return 'Connexion indisponible. Les données des élèves ne sont pas conservées hors ligne.'
  }
  if (error instanceof ApiError && error.status === 401) {
    return 'Votre session a expiré. Reconnectez-vous pour consulter cet espace.'
  }
  if (error instanceof ApiError && error.status === 403) {
    return 'Cet espace est réservé aux responsables associés par votre établissement.'
  }
  return 'Le portail famille est temporairement indisponible.'
}

function relationshipLabel(value: string): string {
  void value
  return 'Association enregistrée par l’établissement'
}

function savePdf(blob: Blob, reportCardId: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `bulletin-${reportCardId}.pdf`
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
}

export default function ParentPortalPage() {
  const [children, setChildren] = useState<ParentChild[]>([])
  const [selectedStudentId, setSelectedStudentId] = useState('')
  const [cards, setCards] = useState<ParentReportCard[]>([])
  const [childrenStatus, setChildrenStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [cardsStatus, setCardsStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle')
  const [error, setError] = useState('')
  const [downloadError, setDownloadError] = useState('')

  useEffect(() => {
    let active = true
    void getParentChildren()
      .then((loaded) => {
        if (!active) return
        setChildren(loaded)
        setSelectedStudentId(loaded[0]?.student.id ?? '')
        setCardsStatus(loaded.length > 0 ? 'loading' : 'idle')
        setChildrenStatus('ready')
      })
      .catch((reason: unknown) => {
        if (!active) return
        setError(accessError(reason))
        setChildrenStatus('error')
      })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (!selectedStudentId) return
    let active = true
    void getChildReportCards(selectedStudentId)
      .then((loaded) => {
        if (!active) return
        setCards(loaded)
        setCardsStatus('ready')
      })
      .catch((reason: unknown) => {
        if (!active) return
        setError(accessError(reason))
        setCardsStatus('error')
      })
    return () => { active = false }
  }, [selectedStudentId])

  async function download(reportCardId: string) {
    setDownloadError('')
    try {
      savePdf(await downloadChildReportCardPdf(selectedStudentId, reportCardId), reportCardId)
    } catch {
      setDownloadError('Le téléchargement du bulletin est temporairement indisponible.')
    }
  }

  if (childrenStatus === 'loading') {
    return <section aria-busy="true" className="portal-content"><PageHeader eyebrow="Famille - EduNova" title="Chargement de votre espace" description="Recuperation des bulletins associes a votre compte." /><p role="status">Chargement de votre espace famille...</p></section>
  }

  if (childrenStatus === 'error') {
    return (
      <section className="portal-content"><PageHeader eyebrow="Famille - EduNova" title="Portail famille indisponible" description="Votre espace n'a pas pu etre charge." /><div className="portal-content__state" role="alert"><p>{error}</p></div></section>
    )
  }

  return (
    <section className="portal-content" aria-labelledby="parent-portal-title">
      <PageHeader titleId="parent-portal-title" eyebrow="Famille - EduNova" title="Espace parent" description="Consultez les bulletins officiels des eleves associes a votre compte." />

      {children.length === 0 ? (
        <p role="status">Aucun élève n’est associé à votre compte. Contactez votre établissement.</p>
      ) : (
        <>
          <label className="role-portal__field" htmlFor="parent-child">
            Élève
            <select
              id="parent-child"
              value={selectedStudentId}
              onChange={(event) => {
                setSelectedStudentId(event.target.value)
                setCards([])
                setCardsStatus('loading')
                setError('')
              }}
            >
              {children.map(({ student, relationship_type }) => (
                <option key={student.id} value={student.id}>
                  {student.first_name} {student.last_name} · {relationshipLabel(relationship_type)}
                </option>
              ))}
            </select>
          </label>

          <section className="portal-content__section" aria-labelledby="parent-report-cards-title">
            <h2 id="parent-report-cards-title">Bulletins officiels</h2>
            {cardsStatus === 'loading' ? <p aria-busy="true">Chargement des bulletins…</p> : null}
            {cardsStatus === 'error' ? <p role="alert">{error}</p> : null}
            {cardsStatus === 'ready' && cards.length === 0 ? (
              <p>Aucun bulletin officiel n’est encore publié pour cet élève.</p>
            ) : null}
            {cardsStatus === 'ready' && cards.length > 0 ? (
              <ul className="portal-content__list">
                {cards.map((card) => (
                  <li className="portal-content__item" key={card.id}>
                    <div>
                      <h3>Bulletin officiel · version {card.report_version}</h3>
                      <p>{card.issued_at ? new Date(card.issued_at).toLocaleDateString('fr-FR') : 'Date de publication non renseignée'}</p>
                    </div>
                    <button type="button" onClick={() => void download(card.id)}>
                      Télécharger le PDF
                    </button>
                    <ParentAISummaryCard studentId={selectedStudentId} reportCardId={card.id} />
                  </li>
                ))}
              </ul>
            ) : null}
            {downloadError ? <p role="alert">{downloadError}</p> : null}
          </section>
        </>
      )}
    </section>
  )
}
