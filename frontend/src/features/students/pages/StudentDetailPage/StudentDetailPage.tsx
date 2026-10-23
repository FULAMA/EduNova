import { useCallback, useEffect, useEffectEvent, useRef, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { ApiError } from '../../../../shared/api/client'
import {
  getStudent,
  getStudentAcademicRecord,
  listEligibleStudentPeriods,
  listEligibleStudentSubjects,
  createStudentAcademicRecord,
  addStudentSubjectResult,
  validateStudentAcademicRecord,
  correctStudentAcademicRecord,
  getStudentDeliberation,
  validateStudentDeliberation,
  getStudentAcademicHistory,
} from '../../services/student.service'
import type { AcademicPeriod, AcademicRecord, AcademicRecordHistory, Deliberation, EligibleSubject } from '../../types/student-detail.types'
import type { Student } from '../../types/student.types'

import './StudentDetailPage.css'

function messageForError(reason: unknown, resource: 'student' | 'academic' = 'academic'): string {
  if (reason instanceof ApiError) {
    if (reason.status === 401) return 'Votre session a expir\u00e9. Veuillez vous reconnecter.'
    if (reason.status === 403) return resource === 'student'
      ? 'Votre compte ne peut pas consulter les \u00e9l\u00e8ves de cet \u00e9tablissement.'
      : 'Votre compte ne peut pas consulter les donn\u00e9es de cet \u00e9tablissement.'
    if (reason.status === 404) return resource === 'student'
      ? 'Aucun \u00e9l\u00e8ve ne correspond \u00e0 cet identifiant.'
      : 'Aucun dossier ne correspond \u00e0 cette p\u00e9riode.'
  }
  return resource === 'student'
    ? 'Impossible de charger cet \u00e9l\u00e8ve pour le moment.'
    : 'Impossible de charger les donn\u00e9es pour le moment.'
}

function formatAverage(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toLocaleString('fr-FR', { maximumFractionDigits: 2 })
}

function StudentDetailPage() {
  const { studentId = '' } = useParams<{ studentId: string }>()
  const [student, setStudent] = useState<Student>()
  const [completedStudentId, setCompletedStudentId] = useState<string | null>(null)
  const [studentError, setStudentError] = useState<string | null>(null)
  const [periods, setPeriods] = useState<AcademicPeriod[]>([])
  const [periodsCompleted, setPeriodsCompleted] = useState(false)
  const [periodError, setPeriodError] = useState<string | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [record, setRecord] = useState<AcademicRecord>()
  const [deliberation, setDeliberation] = useState<Deliberation>()
  const [history, setHistory] = useState<AcademicRecordHistory[]>([])
  const [recordCompletedPeriod, setRecordCompletedPeriod] = useState<string | null>(null)
  const [recordError, setRecordError] = useState<string | null>(null)
  const [requestVersion, setRequestVersion] = useState(0)
  const [mutationError, setMutationError] = useState<string | null>(null)
  const [mutating, setMutating] = useState(false)
  const [showCorrection, setShowCorrection] = useState(false)
  const [correction, setCorrection] = useState({ general_average: 0, failed_subjects: 0, credits_obtained: 0 })
  const [correctionReason, setCorrectionReason] = useState('')
  const [subjects, setSubjects] = useState<EligibleSubject[]>([])
  const [subjectsLoading, setSubjectsLoading] = useState(false)
  const [subjectsError, setSubjectsError] = useState<string | null>(null)
  const [totalCredits, setTotalCredits] = useState('')
  const [selectedSubjectId, setSelectedSubjectId] = useState('')
  const [subjectAverage, setSubjectAverage] = useState('')
  const [selectedYearId, setSelectedYearId] = useState('')
  const mutationLock = useRef(false)

  const loadStudent = useCallback(async (isCurrent: () => boolean = () => true) => {
    try {
      const result = await getStudent(studentId)
      if (isCurrent()) {
        setStudent(result)
        setStudentError(null)
        setCompletedStudentId(studentId)
      }
    } catch (reason: unknown) {
      if (isCurrent()) {
        setStudentError(messageForError(reason, 'student'))
        setCompletedStudentId(studentId)
      }
    }
  }, [studentId])

  const loadPeriods = useCallback(async (isCurrent: () => boolean = () => true) => {
    try {
      const result = await listEligibleStudentPeriods(studentId)
      if (isCurrent()) {
        setPeriods(result)
        setPeriodError(null)
        setPeriodsCompleted(true)
        const yearIds = [...new Set(result.map((period) => period.academic_year_id).filter((id): id is string => Boolean(id)))]
        const yearId = yearIds.includes(selectedYearId) ? selectedYearId : yearIds[0] ?? ''
        setSelectedYearId(yearId)
        setSelectedPeriod((current) => current && result.some((period) => period.id === current && period.academic_year_id === yearId)
          ? current
          : result.find((period) => period.academic_year_id === yearId)?.id ?? '')
      }
    } catch (reason: unknown) {
      if (isCurrent()) {
        setPeriodError(messageForError(reason))
        setPeriodsCompleted(true)
      }
    }
  }, [selectedYearId, studentId])

  const loadRecord = useCallback(async (isCurrent: () => boolean = () => true) => {
    if (!selectedPeriod) {
      setRecord(undefined)
      return
    }
    try {
      const result = await getStudentAcademicRecord(studentId, selectedPeriod)
      if (isCurrent()) {
        setRecord(result)
        setCorrection({
          general_average: result.general_average,
          failed_subjects: result.failed_subjects,
          credits_obtained: result.credits_obtained,
        })
        setRecordError(null)
        setHistory([])
        setRecordCompletedPeriod(selectedPeriod)
        if (result.status === 'VALIDATED') {
          void getStudentDeliberation(studentId, selectedPeriod)
            .then((decision) => {
              if (!isCurrent()) return
              setDeliberation(decision.record_version === result.version ? decision : undefined)
            })
            .catch(() => { if (isCurrent()) setDeliberation(undefined) })
          void getStudentAcademicHistory(studentId, selectedPeriod)
            .then((entries) => { if (isCurrent()) setHistory(entries) })
            .catch(() => { if (isCurrent()) setHistory([]) })
        } else {
          setDeliberation(undefined)
        }
      }
    } catch (reason: unknown) {
      if (isCurrent()) {
        setRecord(undefined)
        setDeliberation(undefined)
        setHistory([])
        setRecordError(reason instanceof ApiError && reason.status === 404
          ? null
          : messageForError(reason))
        setRecordCompletedPeriod(selectedPeriod)
      }
    }
  }, [selectedPeriod, studentId])

  const loadSubjects = useCallback(async (isCurrent: () => boolean = () => true) => {
    if (!selectedPeriod) { setSubjects([]); return }
    setSubjectsLoading(true)
    try {
      const result = await listEligibleStudentSubjects(studentId, selectedPeriod)
      if (isCurrent()) {
        setSubjects(result)
        setSubjectsError(null)
        setSelectedSubjectId((current) => result.some((subject) => subject.id === current) ? current : result[0]?.id ?? '')
      }
    } catch (reason: unknown) {
      if (isCurrent()) { setSubjects([]); setSubjectsError(messageForError(reason)); }
    } finally {
      if (isCurrent()) setSubjectsLoading(false)
    }
  }, [selectedPeriod, studentId])

  const refreshValidatedMetadata = async (updatedRecord: AcademicRecord) => {
    setDeliberation(undefined)
    setHistory([])
    if (updatedRecord.status !== 'VALIDATED') return

    const [deliberationResult, historyResult] = await Promise.allSettled([
      getStudentDeliberation(studentId, updatedRecord.academic_period_id),
      getStudentAcademicHistory(studentId, updatedRecord.academic_period_id),
    ])

    if (deliberationResult.status === 'fulfilled'
      && deliberationResult.value.record_version === updatedRecord.version) {
      setDeliberation(deliberationResult.value)
    }
    if (historyResult.status === 'fulfilled') setHistory(historyResult.value)
  }

  const loadStudentFromEffect = useEffectEvent(loadStudent)
  const loadPeriodsFromEffect = useEffectEvent(loadPeriods)
  const loadRecordFromEffect = useEffectEvent(loadRecord)
  const loadSubjectsFromEffect = useEffectEvent(loadSubjects)

  useEffect(() => {
    let active = true
    queueMicrotask(() => {
      if (!active) return
      void loadStudentFromEffect(() => active)
      void loadPeriodsFromEffect(() => active)
    })
    return () => { active = false }
  }, [requestVersion, studentId])

  useEffect(() => {
    let active = true
    queueMicrotask(() => {
      if (active) void loadRecordFromEffect(() => active)
    })
    return () => { active = false }
  }, [selectedPeriod, studentId, requestVersion])

  useEffect(() => {
    let active = true
    queueMicrotask(() => { if (active) void loadSubjectsFromEffect(() => active) })
    return () => { active = false }
  }, [selectedPeriod, studentId, requestVersion])

  const isStudentLoading = completedStudentId !== studentId
  const isRecordLoading = Boolean(selectedPeriod) && recordCompletedPeriod !== selectedPeriod
  const subjectChartData = record?.subject_results
    .filter((result) => Number.isFinite(result.average) && result.average >= 0 && result.average <= 20)
    .map((result) => ({
      subject: result.subject_name?.trim() || 'Libellé de matière indisponible',
      average: result.average,
    })) ?? []
  const invalidChartResultCount = (record?.subject_results.length ?? 0) - subjectChartData.length
  const subjectChartSummary = subjectChartData
    .map((result) => `${result.subject} : ${formatAverage(result.average)} sur 20`)
    .join('; ')
  const remainingSubjects = subjects.filter((subject) => !record?.subject_results.some((result) => result.subject_id === subject.id))

  const retry = () => {
    setStudent(undefined)
    setCompletedStudentId(null)
    setStudentError(null)
    setPeriods([])
    setPeriodsCompleted(false)
    setPeriodError(null)
    setRecord(undefined)
    setRecordCompletedPeriod(null)
    setRecordError(null)
    setSubjects([])
    setSubjectsError(null)
    setSubjectsLoading(false)
    setRequestVersion((version) => version + 1)
  }

  const validateRecord = async () => {
    if (!record || mutationLock.current) return
    mutationLock.current = true
    setMutating(true)
    setMutationError(null)
    try {
      const updatedRecord = await validateStudentAcademicRecord(studentId, record.academic_period_id, record.version)
      setRecord(updatedRecord)
      await refreshValidatedMetadata(updatedRecord)
    } catch (reason: unknown) {
      setMutationError(reason instanceof ApiError && reason.status === 409
        ? 'Le dossier a été modifié entre-temps. Rechargez les résultats.'
        : 'Impossible de valider le dossier pour le moment.')
    } finally {
      mutationLock.current = false
      setMutating(false)
    }
  }

  const correctRecord = async () => {
    if (!record || mutationLock.current) return
    mutationLock.current = true
    setMutating(true)
    setMutationError(null)
    try {
      const updatedRecord = await correctStudentAcademicRecord(studentId, record.academic_period_id, {
        expected_version: record.version,
        reason: correctionReason,
        general_average: correction.general_average,
        failed_subjects: correction.failed_subjects,
        credits_obtained: correction.credits_obtained,
      })
      setRecord(updatedRecord)
      await refreshValidatedMetadata(updatedRecord)
    } catch (reason: unknown) {
      setMutationError(reason instanceof ApiError && reason.status === 409
        ? 'Le dossier a été modifié entre-temps. Rechargez les résultats.'
        : 'Impossible de corriger le dossier pour le moment.')
    } finally {
      mutationLock.current = false
      setMutating(false)
    }
  }

  const validateDeliberation = async () => {
    if (!deliberation?.deliberation_id
      || deliberation.deliberation_status !== 'PREPARED'
      || mutationLock.current) return
    mutationLock.current = true
    setMutating(true)
    setMutationError(null)
    try {
      const validated = await validateStudentDeliberation(
        deliberation.deliberation_id,
        deliberation.deliberation_version ?? 1,
      )
      setDeliberation(validated)
    } catch (reason: unknown) {
      setMutationError(reason instanceof ApiError && reason.status === 409
        ? 'La délibération ou le dossier a été modifié entre-temps. Rechargez les résultats.'
        : 'Impossible de valider la délibération pour le moment.')
    } finally {
      mutationLock.current = false
      setMutating(false)
    }
  }

  const createRecord = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const credits = Number(totalCredits)
    if (!Number.isFinite(credits) || credits <= 0 || !selectedPeriod) {
      setMutationError('Saisissez un total de crédits supérieur à zéro.')
      return
    }
    if (mutationLock.current) return
    mutationLock.current = true
    setMutating(true); setMutationError(null)
    try {
      await createStudentAcademicRecord(studentId, selectedPeriod, credits)
      const persisted = await getStudentAcademicRecord(studentId, selectedPeriod)
      setRecord(persisted); setRecordCompletedPeriod(selectedPeriod); setTotalCredits('')
    } catch (reason: unknown) {
      setMutationError(reason instanceof ApiError && reason.status === 409
        ? 'Un dossier existe déjà pour cette période. Actualisez les résultats.'
        : reason instanceof ApiError && reason.status === 403
          ? 'Votre compte ne peut pas créer un dossier pour cet élève.'
          : 'Impossible de créer le dossier pour le moment.')
    } finally { mutationLock.current = false; setMutating(false) }
  }

  const addResult = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const average = Number(subjectAverage)
    const subjectId = remainingSubjects.some((subject) => subject.id === selectedSubjectId)
      ? selectedSubjectId
      : remainingSubjects[0]?.id ?? ''
    if (!subjectId || !Number.isFinite(average) || average < 0 || average > 20 || !record) {
      setMutationError('Sélectionnez une matière et saisissez une moyenne entre 0 et 20.')
      return
    }
    if (mutationLock.current) return
    mutationLock.current = true
    setMutating(true); setMutationError(null)
    try {
      await addStudentSubjectResult(studentId, record.academic_period_id, subjectId, average)
      setRecord(await getStudentAcademicRecord(studentId, record.academic_period_id))
      setSubjectAverage('')
    } catch (reason: unknown) {
      setMutationError(reason instanceof ApiError && reason.status === 409
        ? 'Le dossier a été modifié entre-temps. Rechargez les résultats.'
        : reason instanceof ApiError && reason.status === 403
          ? 'Votre compte ne peut pas saisir des résultats pour cet élève.'
          : reason instanceof ApiError && reason.status === 404
            ? 'Cette matière ou cette affectation n’est plus disponible pour l’élève.'
            : 'Impossible d’enregistrer le résultat pour le moment.')
    } finally { mutationLock.current = false; setMutating(false) }
  }

  if (isStudentLoading) {
    return (
      <section className="student-detail-page" aria-busy="true">
        <Link to="/app/students" className="student-detail-page__back-link">← Retour aux élèves</Link>
        <div className="student-detail-page__card" role="status"><p>Chargement de la fiche élève…</p></div>
      </section>
    )
  }

  if (studentError || !student) {
    return (
      <section className="student-detail-page">
        <Link to="/app/students" className="student-detail-page__back-link">← Retour aux élèves</Link>
        <div className="student-detail-page__card" role="alert">
          <h1 className="student-detail-page__title">Fiche indisponible</h1>
          <p className="student-detail-page__description">{studentError ?? 'Aucun élève ne correspond à cet identifiant.'}</p>
          <button type="button" className="student-detail-page__retry" onClick={retry}>Réessayer</button>
        </div>
      </section>
    )
  }

  return (
    <section className="student-detail-page">
      <header className="student-detail-page__header">
        <div>
          <Link to="/app/students" className="student-detail-page__back-link">← Retour aux élèves</Link>
          <p className="student-detail-page__eyebrow">Élève</p>
          <h1 className="student-detail-page__title">{student.firstName} {student.lastName}</h1>
          <p className="student-detail-page__subtitle">{student.id}</p>
        </div>
      </header>

      <section className="student-detail-page__card">
        <header className="student-detail-page__card-header">
          <div><h2>Informations générales</h2><p>Données disponibles dans le dossier de l’établissement.</p></div>
        </header>
        <dl className="student-detail-page__info-grid">
          <div className="student-detail-page__info-item"><dt>Prénom</dt><dd>{student.firstName}</dd></div>
          <div className="student-detail-page__info-item"><dt>Nom</dt><dd>{student.lastName}</dd></div>
          <div className="student-detail-page__info-item"><dt>Identifiant</dt><dd>{student.id}</dd></div>
          <div className="student-detail-page__info-item"><dt>E-mail</dt><dd>{student.email ?? 'Non renseigné'}</dd></div>
          <div className="student-detail-page__info-item"><dt>Statut</dt><dd><span className={`student-detail-page__status student-detail-page__status--${student.status}`}>{student.status === 'active' ? 'Actif' : 'Inactif'}</span></dd></div>
        </dl>
      </section>

      <section className="student-detail-page__card" aria-labelledby="academic-records-heading">
        <header className="student-detail-page__card-header">
          <div><h2 id="academic-records-heading">Dossiers académiques</h2><p>Résultats enregistrés par période pour cet élève.</p></div>
        </header>
        {periodsCompleted && periods.length > 0 ? (
          <div className="student-detail-page__period-picker">
            <label htmlFor="academic-year">Année scolaire</label>
            <select id="academic-year" value={selectedYearId} onChange={(event) => {
              const yearId = event.target.value
              setSelectedYearId(yearId)
              setSelectedPeriod(periods.find((period) => period.academic_year_id === yearId)?.id ?? '')
              setRecord(undefined)
              setRecordCompletedPeriod(null)
              setRecordError(null)
            }}>
              {[...new Map(periods.map((period) => [period.academic_year_id ?? '', period.academic_year_label ?? 'Année scolaire'])).entries()]
                .filter(([id]) => Boolean(id))
                .map(([id, label]) => <option key={id} value={id}>{label}</option>)}
            </select>
            <label htmlFor="academic-period">Période académique</label>
            <select id="academic-period" value={selectedPeriod} onChange={(event) => {
              setSelectedPeriod(event.target.value)
              setRecord(undefined)
              setRecordCompletedPeriod(null)
              setRecordError(null)
            }}>
              {periods.filter((period) => period.academic_year_id === selectedYearId).map((period) => <option key={period.id} value={period.id}>{period.name ?? 'Période non renseignée'}</option>)}
            </select>
          </div>
        ) : null}
        {periodError ? (
          <div className="student-detail-page__academic-state" role="alert">
            <p>{periodError}</p><button type="button" className="student-detail-page__retry" onClick={retry}>Réessayer</button>
          </div>
        ) : !periodsCompleted ? (
          <p className="student-detail-page__academic-state" role="status" aria-busy="true">Chargement des périodes académiques…</p>
        ) : periods.length === 0 ? (
          <p className="student-detail-page__academic-state">Aucune période liée à une affectation active n’est disponible pour cet élève.</p>
        ) : isRecordLoading ? (
          <p className="student-detail-page__academic-state" role="status" aria-busy="true">Chargement des résultats…</p>
        ) : recordError ? (
          <div className="student-detail-page__academic-state" role="alert">
            <p>{recordError}</p><button type="button" className="student-detail-page__retry" onClick={() => { setRecordCompletedPeriod(null); setRecordError(null); setRequestVersion((version) => version + 1) }}>Réessayer</button>
          </div>
        ) : !record ? (
          <div className="student-detail-page__academic-state">
            <p>Aucun dossier n’existe encore pour cette période.</p>
            <form className="student-detail-page__result-form" onSubmit={(event) => void createRecord(event)}>
              <label htmlFor="record-total-credits">Total des crédits de la période</label>
              <input id="record-total-credits" type="number" min="0.01" step="any" required value={totalCredits} onChange={(event) => setTotalCredits(event.target.value)} />
              <button type="submit" disabled={mutating || !totalCredits}>{mutating ? 'Création…' : 'Créer le dossier académique'}</button>
            </form>
            {mutationError ? <p role="alert">{mutationError}</p> : null}
          </div>
        ) : record ? (
          <div className="student-detail-page__academic-content">
            <dl className="student-detail-page__summary-grid">
              <div><dt>Statut</dt><dd>{record.status === 'VALIDATED' ? 'Validé' : 'Brouillon'}</dd></div>
              <div><dt>Version</dt><dd>{record.version}</dd></div>
              <div><dt>Moyenne générale</dt><dd>{record.general_average} / 20</dd></div>
              <div><dt>Matières échouées</dt><dd>{record.failed_subjects}</dd></div>
              <div><dt>Crédits obtenus</dt><dd>{record.credits_obtained} / {record.total_credits}</dd></div>
            </dl>
            {deliberation ? (
              <aside aria-label="Decision de deliberation">
                <strong>Délibération serveur</strong>
                <p>Décision : {deliberation.decision}</p>
                <p>Statut : {deliberation.deliberation_status ?? 'PREPARED'}</p>
                <p>Calculée sur la version {deliberation.record_version} du dossier.</p>
                {(deliberation.deliberation_status ?? 'PREPARED') === 'PREPARED'
                  && deliberation.deliberation_id ? (
                  <button type="button" disabled={mutating} onClick={() => void validateDeliberation()}>
                    {mutating ? 'Validation…' : 'Valider la délibération'}
                  </button>
                ) : null}
                {(deliberation.deliberation_status ?? 'PREPARED') !== 'VALIDATED' ? (
                  <p>Le passage reste bloqué tant que la délibération n&apos;est pas validée.</p>
                ) : null}
              </aside>
            ) : null}
            {record.status === 'VALIDATED' && history.length > 0 ? (
              <section aria-labelledby="academic-record-history-title">
                <h3 id="academic-record-history-title">Historique du dossier</h3>
                <ul>
                  {history.map((entry) => (
                    <li key={`${entry.operation}-${entry.version}-${entry.recorded_at}`}>
                      Version {entry.version} · {entry.operation}
                      {' · '}{entry.recorded_at}
                      {entry.actor_id ? ` · Auteur : ${entry.actor_id}` : ''}
                      {entry.reason ? ` · ${entry.reason}` : ''}
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}
            <div className="student-detail-page__actions">
              {record.status === 'DRAFT' ? <button type="button" disabled={mutating} onClick={() => void validateRecord()}>{mutating ? 'Validation…' : 'Valider le dossier'}</button> : null}
              {record.status === 'VALIDATED' ? <button type="button" disabled={mutating} onClick={() => setShowCorrection((visible) => !visible)}>Corriger le dossier</button> : null}
            </div>
            {record.status === 'VALIDATED' && showCorrection ? (
              <form className="student-detail-page__correction-form" onSubmit={(event) => { event.preventDefault(); void correctRecord() }}>
                <label>Motif de correction<input required minLength={1} maxLength={500} value={correctionReason} onChange={(event) => setCorrectionReason(event.target.value)} /></label>
                <p>Les agrégats sont recalculés par le serveur à partir des résultats persistés.</p>
                <label>Moyenne générale<input type="number" value={correction.general_average} readOnly aria-readonly="true" /></label>
                <label>Matières échouées<input type="number" value={correction.failed_subjects} readOnly aria-readonly="true" /></label>
                <label>Crédits obtenus<input type="number" value={correction.credits_obtained} readOnly aria-readonly="true" /></label>
                <button type="submit" disabled={mutating}>{mutating ? 'Enregistrement…' : 'Enregistrer la correction'}</button>
              </form>
            ) : null}
            {mutationError ? <p className="student-detail-page__academic-state" role="alert">{mutationError}</p> : null}
            {record.status === 'DRAFT' ? (
              <form className="student-detail-page__result-form" onSubmit={(event) => void addResult(event)}>
                <h3>Saisir un résultat</h3>
                {subjectsLoading ? <p role="status" aria-busy="true">Chargement des matières autorisées…</p> : null}
                {subjectsError ? <p role="alert">{subjectsError}</p> : null}
                {!subjectsLoading && !subjectsError && subjects.length === 0 ? <p>Aucune matière active n’est affectée à la classe de l’élève pour cette période.</p> : null}
                  {subjects.length > 0 ? <>
                  <label htmlFor="result-subject">Matière et coefficient</label>
                  <select id="result-subject" required value={remainingSubjects.some((subject) => subject.id === selectedSubjectId) ? selectedSubjectId : remainingSubjects[0]?.id ?? ''} onChange={(event) => setSelectedSubjectId(event.target.value)}>
                    {remainingSubjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name} — coefficient {subject.coefficient}</option>)}
                  </select>
                  <label htmlFor="result-average">Moyenne sur 20</label>
                  <input id="result-average" type="number" min="0" max="20" step="any" required value={subjectAverage} onChange={(event) => setSubjectAverage(event.target.value)} />
                  <button type="submit" disabled={mutating || remainingSubjects.length === 0}>{mutating ? 'Enregistrement…' : 'Enregistrer le résultat'}</button>
                </> : null}
              </form>
            ) : null}
            {record.subject_results.length === 0 ? (
              <p className="student-detail-page__academic-state">Aucun résultat par matière n’est enregistré pour cette période.</p>
            ) : (
              <>
                <section className="student-detail-page__results-chart" aria-labelledby="subject-results-chart-title">
                  <h3 id="subject-results-chart-title">Moyennes par matière</h3>
                  <p>Chaque barre représente la moyenne de la matière sur 20 pour la période sélectionnée.</p>
                  {subjectChartData.length > 0 ? (
                    <div role="img" aria-label={`Moyennes par matière : ${subjectChartSummary}`}>
                      <div className="student-detail-page__chart" aria-hidden="true" style={{ width: '100%', height: Math.max(240, subjectChartData.length * 44) }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={subjectChartData} layout="vertical" margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
                            <CartesianGrid stroke="#D9DEE3" horizontal={false} />
                            <XAxis type="number" domain={[0, 20]} ticks={[0, 5, 10, 15, 20]} tick={{ fill: '#182126', fontSize: 12 }} tickLine={{ stroke: '#66737A' }} axisLine={{ stroke: '#66737A' }} />
                            <YAxis type="category" dataKey="subject" width={120} tick={{ fill: '#182126', fontSize: 12 }} tickLine={false} axisLine={{ stroke: '#66737A' }} />
                            <Tooltip formatter={(value) => [`${formatAverage(Number(value))} / 20`, 'Moyenne']} />
                            <Bar dataKey="average" name="Moyenne" fill="#276678" maxBarSize={24} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  ) : (
                    <p className="student-detail-page__academic-state">Aucune moyenne valide à représenter dans le graphique pour cette période.</p>
                  )}
                  {invalidChartResultCount > 0 ? <p role="status">{invalidChartResultCount} résultat{invalidChartResultCount > 1 ? 's' : ''} avec une moyenne invalide n’est pas représenté dans le graphique.</p> : null}
                </section>
              <div className="student-detail-page__results-scroll">
                <table className="student-detail-page__results-table">
                  <caption>Résultats par matière — moyenne sur 20 et coefficient</caption>
                  <thead><tr><th scope="col">Matière</th><th scope="col">Moyenne / 20</th><th scope="col">Coefficient</th></tr></thead>
                  <tbody>{record.subject_results.map((result) => <tr key={result.subject_id}><td>{result.subject_name ?? 'Libellé de matière indisponible'}</td><td>{result.average} / 20</td><td>{result.coefficient}</td></tr>)}</tbody>
                </table>
              </div>
              </>
            )}
          </div>
        ) : null}
      </section>
    </section>
  )
}

export default StudentDetailPage
