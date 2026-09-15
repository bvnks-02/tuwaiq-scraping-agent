import { Link } from 'react-router-dom'
import { fmtDuration } from '../lib/data'
import type { IndexRow } from '../lib/types'

const TYPE_LABEL: Record<string, string> = {
  bootcamp: 'برنامج/معسكر', learningPath: 'مسار', course: 'دورة',
  libraryArticle: 'مكتبة', practicalProject: 'مشروع تطبيقي',
}
const ROUTE: Record<string, string> = {
  bootcamp: '/bootcamp/', learningPath: '/path/', course: '/course/',
  libraryArticle: '/library/', practicalProject: '/project/',
}
export function rowHref(r: IndexRow): string {
  return ROUTE[r.type] + r.id.split(':')[1]
}
export default function RowCard({ row }: { row: IndexRow }) {
  return (
    <Link className="card" to={rowHref(row)}>
      {row.image && <img className="cover" src={row.image} alt="" loading="lazy" />}
      <div className="card-body">
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <span className="badge">{TYPE_LABEL[row.type] || row.type}</span>
          {row.level && <span className="badge muted">{row.level}</span>}
          {row.isPaid && <span className="badge muted">مدفوع</span>}
        </div>
        <div className="card-title">{row.title}</div>
        {row.excerpt && <div className="card-excerpt">{row.excerpt}</div>}
        <div className="card-excerpt" style={{ marginTop: 'auto' }}>
          {[row.category, row.scope, row.location].filter(Boolean).join(' · ')}
          {row.totalDuration ? ` · ${fmtDuration(row.totalDuration)}` : ''}
        </div>
      </div>
    </Link>
  )
}
