import type { ChangeEvent } from 'react'

import type {
  StudentFiltersProps,
} from './StudentFilters.types'

import './StudentFilters.css'

export function StudentFilters({
  value,
  onChange,
}: StudentFiltersProps) {
  function handleSearchChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    onChange({
      ...value,
      search: event.target.value,
    })
  }

  function handleStatusChange(
    event: ChangeEvent<HTMLSelectElement>,
  ) {
    onChange({
      ...value,
      status: event.target.value as StudentFiltersProps['value']['status'],
    })
  }

  return (
    <div className="student-filters">
      <label className="student-filters__field">
        <span className="student-filters__label">
          Rechercher
        </span>

        <input
          type="search"
          value={value.search}
          onChange={handleSearchChange}
          placeholder="Nom, prénom ou matricule"
        />
      </label>

      <label className="student-filters__field student-filters__field--status">
        <span className="student-filters__label">
          Statut
        </span>

        <select
          value={value.status}
          onChange={handleStatusChange}
        >
          <option value="all">
            Tous
          </option>

          <option value="active">
            Actifs
          </option>

          <option value="inactive">
            Inactifs
          </option>
        </select>
      </label>
    </div>
  )
}
