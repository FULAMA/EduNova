import { useCallback, useEffect, useEffectEvent, useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import { ApiError } from '../../../../shared/api/client'
import { useCurrentUser } from '../../../auth/components/useCurrentUser'
import { canManageStudents } from '../../../auth/permissions'
import { StudentFilters } from '../../components/StudentFilters/StudentFilters'
import type { StudentFiltersValue } from '../../components/StudentFilters/StudentFilters.types'
import { StudentTable } from '../../components/StudentTable/StudentTable'
import { createStudent, listStudents } from '../../services/student.service'
import { describeStudentError } from '../../student.errors'
import type { Student } from '../../types/student.types'

import './StudentsPage.css'

const initialFilters: StudentFiltersValue = { search: '', status: 'all' }

function StudentsPage() {
  const user = useCurrentUser()
  const canCreate = canManageStudents(user.role)
  const [students, setStudents] = useState<Student[]>([])
  const [filters, setFilters] = useState(initialFilters)
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')

  const loadStudents = useCallback(async (isCurrent: () => boolean = () => true) => {
    try {
      setStudents(await listStudents())
    } catch (reason: unknown) {
      if (!isCurrent()) return
      if (reason instanceof ApiError && reason.status === 403) {
        setError('Votre compte ne peut pas consulter les élèves de cet établissement.')
      } else if (reason instanceof ApiError && reason.status === 401) {
        setError('Votre session a expiré. Veuillez vous reconnecter.')
      } else {
        setError('Impossible de charger les élèves pour le moment.')
      }
    } finally {
      if (isCurrent()) setCompleted(true)
    }
  }, [])

  const loadStudentsFromEffect = useEffectEvent(loadStudents)

  useEffect(() => {
    let active = true
    queueMicrotask(() => {
      if (active) void loadStudentsFromEffect(() => active)
    })
    return () => {
      active = false
    }
  }, [])

  const isLoading = !completed

  const filteredStudents = useMemo(() => {
    const normalizedSearch = filters.search.trim().toLocaleLowerCase()
    return students.filter((student) => {
      const matchesSearch =
        normalizedSearch === '' ||
        (student.firstName + ' ' + student.lastName)
          .toLocaleLowerCase()
          .includes(normalizedSearch) ||
        student.id.toLocaleLowerCase().includes(normalizedSearch) ||
        student.email?.toLocaleLowerCase().includes(normalizedSearch) === true
      const matchesStatus =
        filters.status === 'all' || student.status === filters.status
      return matchesSearch && matchesStatus
    })
  }, [filters, students])

  async function submitStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    setNotice(null)
    setSubmitting(true)
    try {
      const created = await createStudent({
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        email: email.trim() || undefined,
      })
      setStudents((current) =>
        [...current, created].sort((left, right) =>
          `${left.lastName} ${left.firstName}`.localeCompare(
            `${right.lastName} ${right.firstName}`,
            'fr',
          ),
        ),
      )
      setFirstName('')
      setLastName('')
      setEmail('')
      setNotice(`${created.firstName} ${created.lastName} a été ajouté.`)
    } catch (reason: unknown) {
      setFormError(describeStudentError(reason, 'Impossible de créer cet élève pour le moment.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="students-page">
      <header className="students-page__header">
        <div>
          <p className="students-page__eyebrow">Administration</p>
          <h1 className="students-page__title">Élèves</h1>
          <p className="students-page__description">
            Consultez les élèves autorisés de votre établissement.
          </p>
        </div>
        {!isLoading && !error ? (
          <p className="students-page__count">
            {filteredStudents.length} sur {students.length} élèves
          </p>
        ) : null}
      </header>

      {canCreate ? (
        <form className="students-page__form" onSubmit={(event) => void submitStudent(event)}>
          <h2>Ajouter un élève</h2>
          <label>
            Prénom
            <input
              required
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
              autoComplete="given-name"
            />
          </label>
          <label>
            Nom
            <input
              required
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              autoComplete="family-name"
            />
          </label>
          <label>
            E-mail (optionnel)
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
            />
          </label>
          <div className="students-page__form-actions">
            <button type="submit" disabled={submitting}>
              {submitting ? 'Enregistrement…' : 'Créer l’élève'}
            </button>
          </div>
          {formError ? <p role="alert">{formError}</p> : null}
          {notice ? <p role="status">{notice}</p> : null}
        </form>
      ) : null}

      {!isLoading && !error ? (
        <StudentFilters value={filters} onChange={setFilters} />
      ) : null}

      {isLoading ? (
        <div className="students-page__empty" aria-busy="true">
          <h2>Chargement des élèves...</h2>
          <p>Récupération des données de votre établissement.</p>
        </div>
      ) : error ? (
        <div className="students-page__empty" role="alert">
          <h2>Liste indisponible</h2>
          <p>{error}</p>
          <button type="button" onClick={() => {
            setCompleted(false)
            setError(null)
            void loadStudents()
          }}>
            Réessayer
          </button>
        </div>
      ) : filteredStudents.length > 0 ? (
        <StudentTable students={filteredStudents} />
      ) : (
        <div className="students-page__empty">
          <h2>{students.length === 0 ? 'Aucun élève' : 'Aucun élève trouvé'}</h2>
          <p>
            {students.length === 0
              ? 'Cet établissement ne possède encore aucun élève.'
              : 'Aucun élève ne correspond aux critères de recherche.'}
          </p>
        </div>
      )}
    </section>
  )
}

export default StudentsPage
