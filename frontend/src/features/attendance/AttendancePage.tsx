import { useEffect, useRef, useState } from 'react'
import './AttendancePage.css'

import { ApiError } from '../../shared/api/client'
import { listAcademicClasses, type AcademicClass } from '../classes/classes.service'
import { listAcademicPeriods, type AcademicPeriod } from '../academic-catalogues/academic-catalogue.service'
import { listAcademicYears, type AcademicYear } from '../enrollments/enrollment.service'
import { listStudents } from '../students/services/student.service'
import type { Student } from '../students/types/student.types'
import {
  getAttendanceStatistics,
  getStudentAcademicRisk,
  listStudentAttendance,
  correctAttendance,
  recordAttendance,
  type AttendanceRecord,
  type AcademicRisk,
  type AttendanceStatistics,
  type AttendanceStatus,
} from './attendance.service'

const emptyStats: AttendanceStatistics = {
  total_sessions: 0,
  absences: 0,
  justified_absences: 0,
  unjustified_absences: 0,
  lates: 0,
  attendance_rate: null,
}

function errorText(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) return 'Votre session a expire. Reconnectez-vous.'
  if (error instanceof ApiError && error.status === 403) return 'Votre compte ne peut pas gerer les presences.'
  if (error instanceof ApiError && error.status === 404) return 'Eleve, periode ou releve introuvable dans votre etablissement.'
  if (error instanceof ApiError && error.status === 409) return 'Ce pointage existe deja ou est en conflit.'
  if (error instanceof ApiError && error.status >= 500) return 'Le serveur ne repond pas correctement. Reessayez dans un instant.'
  return 'Les donnees de presence ne peuvent pas etre chargees.'
}

function statusLabel(status: AttendanceStatus): string {
  return status === 'PRESENT' ? 'Present' : status === 'ABSENT' ? 'Absent' : 'En retard'
}

export default function AttendancePage() {
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<AcademicClass[]>([])
  const [years, setYears] = useState<AcademicYear[]>([])
  const [periods, setPeriods] = useState<AcademicPeriod[]>([])
  const [studentId, setStudentId] = useState('')
  const [classId, setClassId] = useState('')
  const [yearId, setYearId] = useState('')
  const [periodId, setPeriodId] = useState('')
  const [attendanceDate, setAttendanceDate] = useState('')
  const [status, setStatus] = useState<AttendanceStatus>('PRESENT')
  const [stats, setStats] = useState<AttendanceStatistics>(emptyStats)
  const [risk, setRisk] = useState<AcademicRisk | null>(null)
  const [riskLoading, setRiskLoading] = useState(false)
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [correctingId, setCorrectingId] = useState<string | null>(null)
  const correctingIdRef = useRef<string | null>(null)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [loadedStudents, loadedClasses, loadedYears, loadedPeriods] = await Promise.all([
        listStudents(), listAcademicClasses(), listAcademicYears(), listAcademicPeriods(),
      ])
      setStudents(loadedStudents)
      setClasses(loadedClasses)
      setYears(loadedYears)
      setPeriods(loadedPeriods)
      setStudentId((current) => current || loadedStudents[0]?.id || '')
      setClassId((current) => current || loadedClasses[0]?.id || '')
      const initialYearId = loadedYears.find((year) => year.status === 'ACTIVE')?.id || loadedYears[0]?.id || ''
      const initialPeriod = loadedPeriods.find(
        (period) => !period.academic_year_id || period.academic_year_id === initialYearId,
      )
      setYearId((current) => current || initialYearId)
      setPeriodId((current) => current || initialPeriod?.id || '')
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { queueMicrotask(() => void load()) }, [])
  useEffect(() => {
    queueMicrotask(() => {
      if (!studentId || !periodId) {
        setStats(emptyStats)
        setRisk(null)
        return
      }
      void getAttendanceStatistics(studentId, periodId)
        .then(setStats)
        .catch((reason: unknown) => setError(errorText(reason)))
      void listStudentAttendance(studentId, periodId)
        .then(setRecords)
        .catch((reason: unknown) => setError(errorText(reason)))
      setRiskLoading(true)
      void getStudentAcademicRisk(studentId, periodId)
        .then(setRisk)
        .catch(() => setRisk(null))
        .finally(() => setRiskLoading(false))
    })
  }, [studentId, periodId])

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await recordAttendance({
        student_id: studentId, academic_class_id: classId, academic_year_id: yearId,
        academic_period_id: periodId, attendance_date: attendanceDate, status,
      })
      if (studentId && periodId) {
        setStats(await getAttendanceStatistics(studentId, periodId))
        setRecords(await listStudentAttendance(studentId, periodId))
        setRisk(await getStudentAcademicRisk(studentId, periodId))
      }
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setSubmitting(false)
    }
  }

  const correct = async (record: AttendanceRecord) => {
    if (correctingIdRef.current) return
    correctingIdRef.current = record.id
    setCorrectingId(record.id)
    setError('')
    try {
      await correctAttendance(record.id, record.status, record.justified ?? false, record.version)
      setRecords(await listStudentAttendance(studentId, periodId))
      setStats(await getAttendanceStatistics(studentId, periodId))
      setRisk(await getStudentAcademicRisk(studentId, periodId))
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      correctingIdRef.current = null
      setCorrectingId(null)
    }
  }

  return (
    <main className="attendance-page">
      <header><p>Etablissement</p><h1>Presences et absences</h1><p>Les taux sont recalcules par l API a partir des releves persistés.</p></header>
      {loading ? <p className="attendance-page__status" role="status" aria-busy="true">Chargement des donnees...</p> : null}
      {error ? <div className="attendance-page__alert" role="alert"><span>{error}</span><button type="button" onClick={() => void load()}>Reessayer</button></div> : null}
      <section className="attendance-page__section attendance-page__section--form" aria-labelledby="attendance-form-title">
        <h2 id="attendance-form-title">Enregistrer un releve</h2>
        <p className="attendance-page__section-intro">Selectionnez le contexte avant de saisir la presence du jour.</p>
        <form className="attendance-page__form" onSubmit={submit}>
          <label className="attendance-page__field"><span>Eleve</span><select required value={studentId} onChange={(event) => setStudentId(event.target.value)}>{students.map((student) => <option key={student.id} value={student.id}>{student.firstName} {student.lastName}</option>)}</select></label>
          <label className="attendance-page__field"><span>Classe</span><select required value={classId} onChange={(event) => setClassId(event.target.value)}>{classes.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label className="attendance-page__field"><span>Annee scolaire</span><select required value={yearId} onChange={(event) => { const nextYearId = event.target.value; setYearId(nextYearId); const nextPeriod = periods.find((period) => !period.academic_year_id || period.academic_year_id === nextYearId); setPeriodId(nextPeriod?.id || '') }}>{years.map((year) => <option key={year.id} value={year.id}>{year.label} ({year.status})</option>)}</select></label>
          <label className="attendance-page__field"><span>Periode</span><select required value={periodId} onChange={(event) => setPeriodId(event.target.value)}>{periods.filter((period) => !period.academic_year_id || period.academic_year_id === yearId).map((period) => <option key={period.id} value={period.id}>{period.name}</option>)}</select></label>
          <label className="attendance-page__field"><span>Date</span><input required type="date" value={attendanceDate} onChange={(event) => setAttendanceDate(event.target.value)} /></label>
          <label className="attendance-page__field"><span>Statut</span><select value={status} onChange={(event) => setStatus(event.target.value as AttendanceStatus)}><option value="PRESENT">Present</option><option value="ABSENT">Absent</option><option value="LATE">En retard</option></select></label>
          <button className="attendance-page__submit" type="submit" disabled={submitting || !studentId || !classId || !yearId || !periodId}>{submitting ? 'Enregistrement...' : 'Enregistrer la presence'}</button>
        </form>
      </section>
      <section className="attendance-page__section" aria-labelledby="attendance-stats-title">
        <h2 id="attendance-stats-title">Statistiques de l eleve</h2>
        <div className="attendance-page__stats-grid"><div><span>Total releves</span><strong>{stats.total_sessions}</strong></div><div><span>Absences</span><strong>{stats.absences}</strong></div><div><span>Justifiees</span><strong>{stats.justified_absences}</strong></div><div><span>Retards</span><strong>{stats.lates}</strong></div><div className="attendance-page__stat--highlight"><span>Taux de presence</span><strong>{stats.attendance_rate === null ? '--' : `${stats.attendance_rate}%`}</strong></div></div>
      </section>
      <section className="attendance-page__section" aria-labelledby="academic-risk-title">
        <h2 id="academic-risk-title">Risque académique</h2>
        {riskLoading ? <p role="status" aria-busy="true">Calcul du risque…</p> : null}
        {!riskLoading && risk ? (
          <>
            <div className="attendance-page__risk-summary"><strong>{risk.level}</strong><span>Score {risk.score}</span></div>
            <ul>{risk.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
          </>
        ) : null}
        {!riskLoading && !risk ? <p>Risque indisponible pour cette période.</p> : null}
      </section>
      <section className="attendance-page__section" aria-labelledby="attendance-history-title">
        <h2 id="attendance-history-title">Releves corrigibles</h2>
        <p className="attendance-page__section-intro">Les corrections utilisent la version actuelle du releve pour detecter les conflits.</p>
        {records.length === 0 ? <p>Aucun releve pour cette periode.</p> : (
          <ul className="attendance-page__records">
            {records.map((record) => (
              <li key={record.id}>
                <div className="attendance-page__record-meta"><strong>{record.attendance_date}</strong><span>Version {record.version}</span><span className={`attendance-page__status attendance-page__status--${record.status.toLowerCase()}`}>{statusLabel(record.status)}</span></div>
                <select
                  aria-label={`Statut du releve du ${record.attendance_date}`}
                  value={record.status}
                  disabled={correctingId === record.id}
                  onChange={(event) => {
                    const nextStatus = event.target.value as AttendanceStatus
                    void correct({
                      ...record,
                      status: nextStatus,
                      justified: nextStatus === 'PRESENT' ? false : record.justified,
                    })
                  }}
                >
                  <option value="PRESENT">Present</option>
                  <option value="ABSENT">Absent</option>
                  <option value="LATE">En retard</option>
                </select>
                <label className="attendance-page__checkbox">
                  <input
                    type="checkbox"
                    aria-label={`Absence justifiee du ${record.attendance_date}`}
                    checked={record.justified ?? false}
                    disabled={record.status === 'PRESENT' || correctingId === record.id}
                    onChange={(event) => void correct({ ...record, justified: event.target.checked })}
                  />
                  Justifiee
                </label>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  )
}
