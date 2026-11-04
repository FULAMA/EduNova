import { Link } from 'react-router-dom'
import { DashboardHeader } from '../../dashboard/components/DashboardHeader/DashboardHeader'
import { StatCard } from '../../dashboard/components/StatCard/StatCard'
import { DEMO_METRICS, DEMO_QUICK_LINKS } from '../types/preview.types'
import './PreviewDashboard.css'

export function PreviewDashboard() {
  return (
    <section className="preview-dashboard">
      <DashboardHeader
        title="Tableau de bord de pilotage"
        description="Indicateurs de gestion et pilotage opérationnel de votre établissement scolaire."
      />

      {/* Banner indiquant que c'est une démo */}
      <div className="preview-dashboard__banner" role="status">
        <div className="preview-dashboard__banner-content">
          <strong>Mode démonstration</strong>
          <p>
            Vous visualisez une prévisualisation statique de l&apos;interface EduNova.
            Aucune authentification ni appel API n&apos;est effectué.
          </p>
        </div>
        <Link to="/login" className="preview-dashboard__banner-action">
          Se connecter &rarr;
        </Link>
      </div>

      {/* Indicateurs clés */}
      <section className="preview-dashboard__section" aria-labelledby="preview-metrics-title">
        <h2 id="preview-metrics-title" className="preview-dashboard__section-title">
          Indicateurs clés
        </h2>

        <div className="preview-dashboard__metrics" data-testid="preview-metrics-grid">
          {DEMO_METRICS.map((metric) => (
            <StatCard key={metric.label} metric={metric} />
          ))}
        </div>
      </section>

      {/* Accès rapides aux modules */}
      <section className="preview-dashboard__section" aria-labelledby="preview-quicklinks-title">
        <h2 id="preview-quicklinks-title" className="preview-dashboard__section-title">
          Accès rapides aux modules
        </h2>
        <div className="preview-dashboard__quick-links">
          {DEMO_QUICK_LINKS.map((link) => (
            <div key={link.title} className="preview-quick-link-card">
              <span className="preview-quick-link-card__badge">{link.badge}</span>
              <strong className="preview-quick-link-card__title">{link.title}</strong>
              <p className="preview-quick-link-card__desc">{link.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bloc compte */}
      <section className="preview-dashboard__account" aria-labelledby="preview-account-title">
        <div>
          <p className="preview-dashboard__eyebrow">Session démo</p>
          <h2 id="preview-account-title">Administrateur</h2>
          <p>admin@edunova-demo.local</p>
        </div>
        <dl className="preview-dashboard__account-facts">
          <div>
            <dt>Compte</dt>
            <dd>Actif</dd>
          </div>
          <div>
            <dt>Deux facteurs</dt>
            <dd>Non activés</dd>
          </div>
        </dl>
        <div className="preview-dashboard__demo-info">
          <p>Ces données sont fictives et ne correspondent à aucune session réelle.</p>
          <Link to="/login" className="preview-dashboard__cta">
            Accéder à l&apos;authentification
          </Link>
        </div>
      </section>
    </section>
  )
}

export default PreviewDashboard
