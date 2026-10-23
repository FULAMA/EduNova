import { useEffect, useState } from 'react'

import { ApiError } from '../../../../shared/api/client'
import {
  getMyAcademicPeriods,
  getMyAcademicRecord,
  getMyAttendance,
  getMyReportCards,
  downloadMyReportCardPdf,
  getMyStudentProfile,
  type StudentAcademicPeriod,
  type StudentAcademicRecord,
  type StudentAttendanceResponse,
  type StudentReportCard,
  type StudentPortalProfile,
} from '../../services/student-portal.service'

function errorMessage(reason: unknown): string {
  if (reason instanceof ApiError && reason.status === 401) {
    return 'Votre session a expire. Veuillez vous reconnecter.'
  }
  if (reason instanceof ApiError && reason.status === 404) {
    return 'Aucun dossier eleve n est associe a ce compte. Contactez votre etablissement.'
  }
  if (reason instanceof ApiError && reason.status === 403) {
    return 'Ce compte ne dispose pas des droits eleve necessaires.'
  }
  return 'Le portail eleve est temporairement indisponible.'
}

export default function StudentPortalPage() {
  const [profile, setProfile] = useState<StudentPortalProfile | null>(null)
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState('')
  const [periods, setPeriods] = useState<StudentAcademicPeriod[]>([])
  const [selectedPeriodId, setSelectedPeriodId] = useState('')
  const [record, setRecord] = useState<StudentAcademicRecord | null>(null)
  const [recordStatus, setRecordStatus] = useState<'idle' | 'loading' | 'success' | 'empty' | 'error'>('idle')
  const [recordError, setRecordError] = useState('')
  const [attendance, setAttendance] = useState<StudentAttendanceResponse | null>(null)
  const [attendanceStatus, setAttendanceStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [reportCards, setReportCards] = useState<StudentReportCard[]>([])
  const [reportCardsStatus, setReportCardsStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [reportCardDownloadError, setReportCardDownloadError] = useState('')

  const downloadReportCard = async (reportCardId: string) => {
    setReportCardDownloadError('')
    try {
      const blob = await downloadMyReportCardPdf(reportCardId)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `bulletin-${reportCardId}.pdf`
      anchor.click()
      URL.revokeObjectURL(url)
    } catch {
      setReportCardDownloadError('Le téléchargement du bulletin est temporairement indisponible.')
    }
  }

  const loadRecord = (periodId: string) => {
    setSelectedPeriodId(periodId)
    setRecord(null)
    setRecordError('')
    setRecordStatus('loading')
    setAttendance(null)
    setAttendanceStatus('loading')
    void getMyAcademicRecord(periodId)
      .then((loaded) => {
        setRecord(loaded)
        setRecordStatus('success')
      })
      .catch((reason: unknown) => {
        if (reason instanceof ApiError && reason.status === 404) {
          setRecordStatus('empty')
          return
        }
        setRecordError('Les resultats de cette periode sont temporairement indisponibles.')
        setRecordStatus('error')
      })
    void getMyAttendance(periodId)
      .then((loaded) => {
        setAttendance(loaded)
        setAttendanceStatus('success')
      })
      .catch(() => {
        setAttendanceStatus('error')
      })
  }

  const load = (reset = true) => {
    if (reset) {
      setStatus('loading')
      setError('')
      setPeriods([])
      setSelectedPeriodId('')
      setRecord(null)
      setRecordStatus('idle')
    }
    void Promise.all([getMyStudentProfile(), getMyAcademicPeriods(), getMyReportCards()])
      .then(([loaded, availablePeriods, availableReportCards]) => {
        setProfile(loaded)
        setPeriods(availablePeriods)
        setReportCards(availableReportCards)
        setReportCardsStatus('success')
        setStatus('success')
        if (availablePeriods[0]) loadRecord(availablePeriods[0].id)
      })
      .catch((reason: unknown) => {
        setProfile(null)
        setError(errorMessage(reason))
        setReportCardsStatus('error')
        setStatus('error')
      })
  }

  useEffect(() => {
    void Promise.all([getMyStudentProfile(), getMyAcademicPeriods(), getMyReportCards()])
      .then(([loaded, availablePeriods, availableReportCards]) => {
        setProfile(loaded)
        setPeriods(availablePeriods)
        setReportCards(availableReportCards)
        setReportCardsStatus('success')
        setStatus('success')
        if (availablePeriods[0]) loadRecord(availablePeriods[0].id)
      })
      .catch((reason: unknown) => {
        setError(errorMessage(reason))
        setReportCardsStatus('error')
        setStatus('error')
      })
  }, [])

  if (status === 'loading') {
    return <main aria-busy="true">Chargement de votre espace eleve...</main>
  }

  if (status === 'error') {
    return (
      <main role="alert">
        <h1>Espace eleve indisponible</h1>
        <p>{error}</p>
        <button type="button" onClick={() => load()}>Reessayer</button>
      </main>
    )
  }

  if (!profile) return null

  return (
    <section aria-labelledby="student-portal-title">
      <p>Espace eleve</p>
      <h1 id="student-portal-title">
        {profile.student.first_name} {profile.student.last_name}
      </h1>
      <p>{profile.student.email ?? 'Adresse e-mail non renseignee'}</p>
      <section aria-labelledby="student-school-title">
        <h2 id="student-school-title">Scolarite</h2>
        {profile.assignment && profile.academic_year ? (
          <p>
            Affectation active pour l annee {profile.academic_year.label}.
          </p>
        ) : (
          <p>Aucune affectation active n est disponible.</p>
        )}
      </section>
      <section aria-labelledby="student-data-title">
        <h2 id="student-data-title">Donnees disponibles</h2>
        {periods.length === 0 ? (
          <p>Aucun resultat academique disponible.</p>
        ) : (
          <>
            <label htmlFor="student-period">Periode academique</label>
            <select
              id="student-period"
              value={selectedPeriodId}
              onChange={(event) => loadRecord(event.target.value)}
            >
              {periods.map((period) => (
                <option key={period.id} value={period.id}>
                  {period.name ?? period.id}
                </option>
              ))}
            </select>
            {recordStatus === 'loading' && <p aria-busy="true">Chargement des resultats...</p>}
            {recordStatus === 'empty' && <p>Aucun dossier academique pour cette periode.</p>}
            {recordStatus === 'error' && <p role="alert">{recordError}</p>}
            {recordStatus === 'success' && record && (
              <dl>
                <div><dt>Moyenne generale</dt><dd>{record.general_average}</dd></div>
                <div><dt>Matieres echouees</dt><dd>{record.failed_subjects}</dd></div>
                <div><dt>Credits obtenus</dt><dd>{record.credits_obtained} / {record.total_credits}</dd></div>
              </dl>
            )}
            {recordStatus === 'success' && record && record.subject_results.length > 0 && (
              <table>
                <caption>Resultats par matiere</caption>
                <thead>
                  <tr><th>Matiere</th><th>Moyenne</th><th>Coefficient</th></tr>
                </thead>
                <tbody>
                  {record.subject_results.map((subject) => (
                    <tr key={subject.subject_id}>
                      <td>{subject.subject_name ?? subject.subject_id}</td>
                      <td>{subject.average}</td>
                      <td>{subject.coefficient}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <section aria-labelledby="student-attendance-title">
              <h3 id="student-attendance-title">Presences et absences</h3>
              {attendanceStatus === 'loading' && <p aria-busy="true">Chargement des presences...</p>}
              {attendanceStatus === 'error' && <p role="alert">Les presences sont temporairement indisponibles.</p>}
              {attendanceStatus === 'success' && attendance && (
                attendance.records.length === 0 ? (
                  <p>Aucun releve de presence pour cette periode.</p>
                ) : (
                  <>
                    <p>
                      {attendance.statistics.absences} absence(s), {attendance.statistics.lates} retard(s).
                    </p>
                    <table>
                      <caption>Releves de presence</caption>
                      <thead><tr><th>Date</th><th>Statut</th><th>Justifie</th></tr></thead>
                      <tbody>
                        {attendance.records.map((entry) => (
                          <tr key={entry.id}>
                            <td>{entry.attendance_date}</td>
                            <td>{entry.status}</td>
                            <td>{entry.justified ? 'Oui' : 'Non'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                )
              )}
            </section>
          </>
        )}
      </section>
      <section aria-labelledby="student-report-cards-title">
        <h2 id="student-report-cards-title">Bulletins officiels</h2>
        {reportCardsStatus === 'loading' && <p aria-busy="true">Chargement des bulletins...</p>}
        {reportCardsStatus === 'error' && <p role="alert">Les bulletins sont temporairement indisponibles.</p>}
        {reportCardsStatus === 'success' && reportCards.length === 0 && (
          <p>Aucun bulletin officiel disponible.</p>
        )}
        {reportCardsStatus === 'success' && reportCards.length > 0 && (
          <ul>
            {reportCards.map((reportCard) => (
              <li key={reportCard.id}>
                Version {reportCard.report_version} - {reportCard.issued_at ?? 'Date non disponible'}{' '}
                <button type="button" onClick={() => void downloadReportCard(reportCard.id)}>
                  Télécharger le PDF
                </button>
              </li>
            ))}
          </ul>
        )}
        {reportCardDownloadError && <p role="alert">{reportCardDownloadError}</p>}
      </section>
    </section>
  )
}

