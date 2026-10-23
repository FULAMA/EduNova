import { Link } from 'react-router-dom'

import type { Student } from '../../types/student.types'

import './StudentTable.css'

type StudentTableProps = {
  students: Student[]
}

function getStudentFullName(student: Student): string {
  return `${student.firstName} ${student.lastName}`
}

function getStatusLabel(status: Student['status']): string {
  return status === 'active' ? 'Actif' : 'Inactif'
}

export function StudentTable({ students }: StudentTableProps) {
  return (
    <div className="student-table">
      <div className="student-table__scroll">
        <table>
          <thead>
            <tr>
              <th scope="col">Élève</th>
              <th scope="col">Identifiant</th>
              <th scope="col">E-mail</th>
              <th scope="col">Statut</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id}>
                <td>
                  <Link
                    to={`/app/students/${encodeURIComponent(student.id)}`}
                    className="student-table__student-link"
                  >
                    <strong>{getStudentFullName(student)}</strong>
                  </Link>
                </td>
                <td>{student.id}</td>
                <td>{student.email ?? 'Non renseigné'}</td>
                <td>
                  <span className={`student-table__status student-table__status--${student.status}`}>
                    {getStatusLabel(student.status)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
