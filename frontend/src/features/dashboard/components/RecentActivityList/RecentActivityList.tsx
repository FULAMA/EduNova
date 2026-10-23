import type { RecentActivity } from '../../types/recent-activity.types'

import './RecentActivityList.css'

type RecentActivityListProps = {
  activities: RecentActivity[]
}

export function RecentActivityList({
  activities,
}: RecentActivityListProps) {
  return (
    <section className="recent-activity">
      <header className="recent-activity__header">
        <h2 className="recent-activity__title">
          Activité récente
        </h2>
      </header>

      {activities.length === 0 ? (
        <div className="recent-activity__empty">
          <p className="recent-activity__empty-title">
            Aucune activité récente
          </p>

          <p className="recent-activity__empty-description">
            Les nouvelles activités de l’établissement apparaîtront ici.
          </p>
        </div>
      ) : (
        <div className="recent-activity__list">
          {activities.map((activity) => (
            <article
              className="recent-activity__item"
              key={activity.id}
            >
              <div className="recent-activity__content">
                <h3 className="recent-activity__item-title">
                  {activity.title}
                </h3>

                <p className="recent-activity__description">
                  {activity.description}
                </p>
              </div>

              <time className="recent-activity__time">
                {activity.occurredAt}
              </time>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
