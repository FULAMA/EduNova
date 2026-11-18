import { useCallback, useEffect, useState } from 'react'

import { ApiError } from '../../shared/api/client'
import { getMyTeacherAssignments, type TeacherAssignment } from './teacher-portal.service'

import './TeacherPortalPage.css'

export default function TeacherPortalPage() {
  const [assignments, setAssignments] = useState<TeacherAssignment[]>([])
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  const requestAssignments = useCallback(() => {
    void getMyTeacherAssignments()
      .then((rows) => {
        setAssignments(rows)
        setStatus('ready')
      })
      .catch((reason: unknown) => {
        setStatus('error')
        setErrorMessage(reason instanceof ApiError && reason.status === 401
          ? 'Votre session a expiré. Reconnectez-vous.'
          : 'Les affectations ne sont pas disponibles. Vérifiez votre connexion ou contactez la direction.')
      })
  }, [])

  useEffect(() => { requestAssignments() }, [requestAssignments])

  function retry() {
    setStatus('loading')
    requestAssignments()
  }

  return (
    <section className="teacher-portal" aria-labelledby="teacher-portal-title">
      <p className="teacher-portal__eyebrow">EduNova · Équipe pédagogique</p>
      <h1 id="teacher-portal-title">Espace enseignant</h1>
      <p>Vos affectations dans l’établissement actif.</p>
      {status === 'loading' ? <p aria-busy="true">Chargement des affectations…</p> : null}
      {status === 'error' ? (
        <div role="alert">
          <p>{errorMessage}</p>
          <button type="button" onClick={retry}>Réessayer</button>
        </div>
      ) : null}
      {status === 'ready' && assignments.length === 0 ? (
        <p role="status">Aucune affectation active n’est enregistrée pour votre compte.</p>
      ) : null}
      {status === 'ready' && assignments.length > 0 ? (
        <>
          <p>{assignments.length} affectation{assignments.length === 1 ? '' : 's'} enregistrée{assignments.length === 1 ? '' : 's'}.</p>
          <ul className="teacher-portal__list">
            {assignments.map((assignment) => (
              <li className="teacher-portal__card" key={`${assignment.academic_year_id}-${assignment.academic_class_id}-${assignment.subject_id}`}>
                <h2>{assignment.subject_label ?? 'Matière indisponible'}</h2>
                <p>Classe : {assignment.academic_class_label ?? 'Libellé indisponible'}</p>
                <p>Année scolaire : {assignment.academic_year_label ?? 'Libellé indisponible'}</p>
                <p>Attribuée le {new Date(assignment.assigned_at).toLocaleDateString('fr-FR')}</p>
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  )
}
