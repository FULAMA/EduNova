import { Outlet } from 'react-router-dom'
import { Sidebar } from '../../../shared/components/Sidebar/Sidebar'
import { PreviewTopbar } from './PreviewTopbar'
import './PreviewLayout.css'

export function PreviewLayout() {
  return (
    <div className="preview-layout">
      <Sidebar isMobileOpen={false} role="ADMIN" />

      <div className="preview-layout__content">
        <PreviewTopbar />

        <main className="preview-layout__main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
