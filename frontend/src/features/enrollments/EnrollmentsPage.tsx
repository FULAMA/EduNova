import { useCallback, useEffect, useRef, useState } from 'react'

import { ApiError } from '../../shared/api/client'
import { listAcademicClasses, type AcademicClass } from '../classes/classes.service'
import { getStudentDeliberation, listEligibleStudentPeriods, listStudents, type EligibleAcademicPeriod } from '../students/services/student.service'
import type { Deliberation } from '../students/types/student-detail.types'
import type { Student } from '../students/types/student.types'
import {
  activateAcademicYear,
  changeStudentAssignmentStatus,
  createAcademicYear,
  createStudentAssignment,
  listAcademicYears,
  listStudentAssignments,
  promoteStudent,
  type AcademicYear,
  type StudentAssignment,
} from './enrollment.service'
import './EnrollmentsPage.css'

function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return 'Votre session a expire. Reconnectez-vous.'
    if (error.status === 403) return 'Votre compte ne peut pas gerer les inscriptions.'
    if (error.status === 409) {
      return error.message || 'Cette operation entre en conflit avec une regle existante.'
    }
    if (error.status === 400) {
      return error.message || 'La requete est invalide.'
    }
  }
  return 'Les donnees d inscription ne peuvent pas etre chargees.'
}

export default function EnrollmentsPage() {
  const [years, setYears] = useState<AcademicYear[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<AcademicClass[]>([])
  const [assignments, setAssignments] = useState<StudentAssignment[]>([])
  const [assignmentsStudentId, setAssignmentsStudentId] = useState('')
  const [assignmentsStatusStudentId, setAssignmentsStatusStudentId] = useState('')
  const [studentId, setStudentId] = useState('')
  const [yearId, setYearId] = useState('')
  const [classId, setClassId] = useState('')
  const [label, setLabel] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [promotionPeriods, setPromotionPeriods] = useState<EligibleAcademicPeriod[]>([])
  const [promotionPeriodId, setPromotionPeriodId] = useState('')
  const [promotionYearId, setPromotionYearId] = useState('')
  const [promotionClassId, setPromotionClassId] = useState('')
  const [promotionDeliberation, setPromotionDeliberation] = useState<Deliberation>()
  const [promotionLoading, setPromotionLoading] = useState(false)
  const [promotionSubmitting, setPromotionSubmitting] = useState(false)
  const [promotionError, setPromotionError] = useState('')
  const [loading, setLoading] = useState(true)
  const [resourcesFailed, setResourcesFailed] = useState(false)
  const [assignmentsStatus, setAssignmentsStatus] = useState<'loading' | 'loaded' | 'error'>('loading')
  const [assignmentsError, setAssignmentsError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [actionInProgressId, setActionInProgressId] = useState<string | null>(null)
  const [yearActionInProgressId, setYearActionInProgressId] = useState<string | null>(null)
  const assignmentsRequestId = useRef(0)

  const load = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const [loadedYears, loadedStudents, loadedClasses] = await Promise.all([
        listAcademicYears(),
        listStudents(),
        listAcademicClasses(),
      ])
      setYears(loadedYears)
      setStudents(loadedStudents)
      setClasses(loadedClasses)
      setResourcesFailed(false)
      setStudentId((current) => current || loadedStudents[0]?.id || '')
      setYearId((current) => current || loadedYears.find((year) => year.status === 'ACTIVE')?.id || loadedYears[0]?.id || '')
      setClassId((current) => current || loadedClasses[0]?.id || '')
    } catch (reason) {
      setResourcesFailed(true)
      setError(errorText(reason))
    } finally {
      setLoading(false)
    }
  }

  const loadAssignments = async (selectedStudentId: string) => {
    const requestId = ++assignmentsRequestId.current
    setAssignmentsStatusStudentId(selectedStudentId)
    setAssignmentsStatus('loading')
    setAssignmentsError('')
    if (!selectedStudentId) {
      setAssignments([])
      setAssignmentsStudentId('')
      setAssignmentsStatus('loaded')
      return
    }
    try {
      const loadedAssignments = await listStudentAssignments(selectedStudentId)
      if (requestId !== assignmentsRequestId.current) return
      setAssignments(loadedAssignments)
      setAssignmentsStudentId(selectedStudentId)
      setAssignmentsStatus('loaded')
    } catch (reason) {
      if (requestId !== assignmentsRequestId.current) return
      setAssignmentsStatus('error')
      setAssignmentsError(errorText(reason))
    }
  }

  const loadPromotionPeriods = async (selectedStudentId: string) => {
    setPromotionPeriods([])
    setPromotionPeriodId('')
    setPromotionDeliberation(undefined)
    setPromotionError('')
    if (!selectedStudentId) return
    try {
      const periods = await listEligibleStudentPeriods(selectedStudentId)
      setPromotionPeriods(periods)
      setPromotionPeriodId(periods[0]?.id ?? '')
    } catch {
      setPromotionError('Les périodes de délibération ne peuvent pas être chargées.')
    }
  }

  const loadPromotionDeliberation = useCallback(async (periodId: string) => {
    setPromotionDeliberation(undefined)
    if (!periodId) return
    setPromotionLoading(true)
    setPromotionError('')
    try {
      setPromotionDeliberation(await getStudentDeliberation(studentId, periodId))
    } catch (reason) {
      setPromotionError(reason instanceof ApiError && reason.status === 404
        ? 'Aucune délibération disponible pour cette période.'
        : 'La délibération ne peut pas être chargée.')
    } finally {
      setPromotionLoading(false)
    }
  }, [studentId])

  useEffect(() => {
    queueMicrotask(() => void load())
  }, [])

  useEffect(() => {
    queueMicrotask(() => void loadAssignments(studentId))
    queueMicrotask(() => void loadPromotionPeriods(studentId))
  }, [studentId])

  useEffect(() => {
    queueMicrotask(() => void loadPromotionDeliberation(promotionPeriodId))
  }, [loadPromotionDeliberation, promotionPeriodId])

  const activeSource = assignments.find((assignment) => assignment.status === 'ACTIVE')
  const promotionYears = years.filter((year) => year.id !== activeSource?.academic_year_id)
  const promotionTargetYearId = promotionYears.some((year) => year.id === promotionYearId)
    ? promotionYearId
    : promotionYears.find((year) => year.status === 'ACTIVE')?.id ?? promotionYears[0]?.id ?? ''
  const promotionTargetClassId = classes.some((academicClass) => academicClass.id === promotionClassId)
    ? promotionClassId
    : classes[0]?.id ?? ''

  const submitYear = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await createAcademicYear({ label, start_date: startDate, end_date: endDate })
      setLabel('')
      setStartDate('')
      setEndDate('')
      await load()
      setSuccess('Année scolaire créée. Elle doit être activée avant toute affectation active.')
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setSubmitting(false)
    }
  }

  const submitAssignment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setSuccess('')
    try {
      await createStudentAssignment({
        student_id: studentId,
        academic_year_id: yearId,
        academic_class_id: classId,
      })
      await loadAssignments(studentId)
      setSuccess('Affectation préparée. Elle reste en brouillon jusqu’à son activation explicite.')
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setSubmitting(false)
    }
  }

  const handleAssignmentStatusChange = async (assignmentId: string, action: 'activate' | 'cancel' | 'close') => {
    if (actionInProgressId) return
    setActionInProgressId(assignmentId)
    setError('')
    setSuccess('')
    try {
      await changeStudentAssignmentStatus(assignmentId, action)
      await loadAssignments(studentId)
      setSuccess(action === 'activate'
        ? 'Affectation activée avec succès.'
        : action === 'close'
          ? 'Affectation clôturée et conservée dans l’historique.'
          : 'Affectation annulée.')
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setActionInProgressId(null)
    }
  }

  const handleYearActivation = async (yearId: string) => {
    if (yearActionInProgressId) return
    setYearActionInProgressId(yearId)
    setError('')
    setSuccess('')
    try {
      await activateAcademicYear(yearId)
      await load()
      setSuccess('Année scolaire activée.')
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setYearActionInProgressId(null)
    }
  }

  const promote = async (sourceAssignment: StudentAssignment) => {
    if (!promotionDeliberation?.deliberation_id
      || promotionDeliberation.deliberation_status !== 'VALIDATED'
      || promotionDeliberation.decision !== 'ADMITTED'
      || promotionSubmitting) return
    setPromotionSubmitting(true)
    setPromotionError('')
    setSuccess('')
    try {
      await promoteStudent({
        source_assignment_id: sourceAssignment.id,
        deliberation_id: promotionDeliberation.deliberation_id,
        target_year_id: promotionTargetYearId,
        target_class_id: promotionTargetClassId,
      })
      await loadAssignments(studentId)
      setSuccess('Passage de classe enregistré. L’affectation précédente reste conservée dans l’historique.')
    } catch (reason) {
      setPromotionError(errorText(reason))
    } finally {
      setPromotionSubmitting(false)
    }
  }

  const visibleAssignments = assignmentsStudentId === studentId ? assignments : []
  const visibleAssignmentsStatus = assignmentsStatusStudentId === studentId
    ? assignmentsStatus
    : studentId ? 'loading' : 'loaded'

  return (
    <main className="enrollments-page">
      <header className="enrollments-page__header">
        <p>Etablissement</p>
        <h1>Annees et inscriptions</h1>
        <p>Preparez des affectations en brouillon. Les controles de securite restent cote API.</p>
      </header>
      {loading ? <p role="status" aria-busy="true">Chargement...</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {success ? <p role="status">{success}</p> : null}

      <section className="enrollments-page__section" aria-labelledby="academic-year-title">
        <h2 id="academic-year-title">Creer une annee scolaire</h2>
        <form className="enrollments-page__form" onSubmit={submitYear}>
          <label>Libelle<input required value={label} onChange={(event) => setLabel(event.target.value)} placeholder="2026-2027" /></label>
          <label>Debut<input required type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label>
          <label>Fin<input required type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label>
          <button className="enrollments-page__primary-action" type="submit" disabled={submitting}>Creer</button>
        </form>
        <ul className="enrollments-page__list enrollments-page__year-list">
          {years.map((year) => (
            <li key={year.id}>
              {year.label} - {year.status}
              {year.status === 'DRAFT' ? (
                <button
                  className="enrollments-page__list-action"
                  type="button"
                  disabled={yearActionInProgressId !== null}
                  onClick={() => void handleYearActivation(year.id)}
                >
                  {yearActionInProgressId === year.id ? 'Activation...' : 'Activer'}
                </button>
              ) : null}
            </li>
          ))}
        </ul>
        {!loading && !resourcesFailed && years.length === 0 ? (
          <p role="status">Aucune année scolaire n’est configurée. Créez-en une avec le formulaire ci-dessus.</p>
        ) : null}
      </section>

      <section className="enrollments-page__section" aria-labelledby="assignment-title">
        <h2 id="assignment-title">Preparer une affectation</h2>
        {!loading && !resourcesFailed && students.length === 0 ? (
          <p role="status">Aucun élève n’est disponible pour préparer une affectation.</p>
        ) : null}
        {!loading && !resourcesFailed && classes.length === 0 ? (
          <p role="status">Aucune classe n’est disponible pour préparer une affectation.</p>
        ) : null}
        <form className="enrollments-page__form" onSubmit={submitAssignment}>
          <label>Eleve<select required value={studentId} onChange={(event) => setStudentId(event.target.value)}>{students.map((student) => <option key={student.id} value={student.id}>{student.firstName} {student.lastName}</option>)}</select></label>
          <label>Annee<select required value={yearId} onChange={(event) => setYearId(event.target.value)}>{years.map((year) => <option key={year.id} value={year.id}>{year.label} ({year.status})</option>)}</select></label>
          <label>Classe<select required value={classId} onChange={(event) => setClassId(event.target.value)}>{classes.map((academicClass) => <option key={academicClass.id} value={academicClass.id}>{academicClass.name}</option>)}</select></label>
          <button className="enrollments-page__primary-action" type="submit" disabled={submitting || !studentId || !yearId || !classId}>Creer le brouillon</button>
        </form>
        {visibleAssignmentsStatus === 'loading' && studentId ? (
          <p role="status" aria-busy="true">Chargement des affectations de cet élève…</p>
        ) : null}
        {visibleAssignmentsStatus === 'error' ? (
          <div role="alert">
            <p>{assignmentsError}</p>
            <button type="button" onClick={() => void loadAssignments(studentId)}>Réessayer</button>
          </div>
        ) : null}
        {visibleAssignmentsStatus === 'loaded' && studentId && visibleAssignments.length === 0 ? (
          <p role="status">Aucune affectation n’est enregistrée pour cet élève.</p>
        ) : null}
        <ul className="enrollments-page__list enrollments-page__assignment-list">
          {visibleAssignments.map((assignment) => {
            const isProcessing = actionInProgressId === assignment.id
            return (
              <li key={assignment.id}>
                <span>Affectation {assignment.id}: {assignment.status}</span>
                {assignment.status === 'DRAFT' ? (
                  <>
                    <button
                      className="enrollments-page__list-action"
                      type="button"
                      disabled={actionInProgressId !== null}
                      onClick={() => void handleAssignmentStatusChange(assignment.id, 'activate')}
                    >
                      {isProcessing ? 'Activation...' : 'Activer'}
                    </button>
                    <button
                      className="enrollments-page__list-action enrollments-page__list-action--danger"
                      type="button"
                      disabled={actionInProgressId !== null}
                      onClick={() => void handleAssignmentStatusChange(assignment.id, 'cancel')}
                    >
                      {isProcessing ? 'Annulation...' : 'Annuler'}
                    </button>
                  </>
                ) : null}
                {assignment.status === 'ACTIVE' ? (
                  <button
                    className="enrollments-page__list-action"
                    type="button"
                    disabled={actionInProgressId !== null}
                    onClick={() => void handleAssignmentStatusChange(assignment.id, 'close')}
                  >
                    {isProcessing ? 'Cloture...' : 'Cloturer'}
                  </button>
                ) : null}
              </li>
            )
          })}
        </ul>
        {visibleAssignments.some((assignment) => assignment.status === 'ACTIVE') ? (
          <section aria-labelledby="promotion-title">
            <h3 id="promotion-title">Passage de classe</h3>
            <label>Période de délibération
              <select required value={promotionPeriodId} onChange={(event) => setPromotionPeriodId(event.target.value)}>
                {promotionPeriods.map((period) => (
                  <option key={period.id} value={period.id}>{period.academic_year_label} · {period.name}</option>
                ))}
              </select>
            </label>
            {promotionLoading ? <p role="status" aria-busy="true">Chargement de la délibération…</p> : null}
            {promotionError ? <p role="alert">{promotionError}</p> : null}
            {promotionDeliberation && promotionDeliberation.deliberation_status !== 'VALIDATED' ? (
              <p role="status">La délibération doit être validée avant tout passage.</p>
            ) : null}
            {promotionDeliberation && promotionDeliberation.decision !== 'ADMITTED' ? (
              <p role="status">La décision {promotionDeliberation.decision} ne permet pas un passage automatique.</p>
            ) : null}
            <label>Année cible
              <select required value={promotionTargetYearId} onChange={(event) => setPromotionYearId(event.target.value)}>
                {promotionYears.map((year) => (
                  <option key={year.id} value={year.id}>{year.label} ({year.status})</option>
                ))}
              </select>
            </label>
            <label>Classe cible
              <select required value={promotionTargetClassId} onChange={(event) => setPromotionClassId(event.target.value)}>
                {classes.map((academicClass) => (
                  <option key={academicClass.id} value={academicClass.id}>{academicClass.name}</option>
                ))}
              </select>
            </label>
            {promotionDeliberation?.deliberation_status === 'VALIDATED'
              && promotionDeliberation.decision === 'ADMITTED' ? (
              <button
                type="button"
                disabled={promotionSubmitting || !promotionTargetYearId || !promotionTargetClassId}
                onClick={() => {
                  const source = visibleAssignments.find((assignment) => assignment.status === 'ACTIVE')
                  if (source) void promote(source)
                }}
              >
                {promotionSubmitting ? 'Passage en cours…' : 'Confirmer le passage'}
              </button>
            ) : null}
          </section>
        ) : null}
      </section>
    </main>
  )
}
