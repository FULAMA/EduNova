import { useCallback, useEffect, useEffectEvent, useMemo, useState } from 'react'

import { ApiError } from '../../../../shared/api/client'
import { StudentFilters } from '../../components/StudentFilters/StudentFilters'
import type { StudentFiltersValue } from '../../components/StudentFilters/StudentFilters.types'
import { StudentTable } from '../../components/StudentTable/StudentTable'
import { listStudents } from '../../services/student.service'
import type { Student } from '../../types/student.types'

import './StudentsPage.css'

const initialFilters: StudentFiltersValue = { search: '', status: 'all' }

function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [filters, setFilters] = useState(initialFilters)
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
