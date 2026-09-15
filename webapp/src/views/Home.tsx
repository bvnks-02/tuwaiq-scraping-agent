import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchIndex, fetchMeta, fmtDuration } from '../lib/data'
import { useMeta } from '../App'
import type { IndexRow } from '../lib/types'
import RowGrid from '../components/RowGrid'

export default function Home() {
  const [rows, setRows] = useState<IndexRow[]>([])
  const meta = useMeta()
  useEffect(() => { fetchIndex().then(setRows).catch(() => {}) }, [])
  const byType = (t: string, n = 8) => rows.filter(r => r.type === t).slice(0, n)
  const stats = meta ? [
    { n: meta.totals.bootcamp, l: 'معسكر وبرنامج ولقاء' },
    { n: meta.totals.course, l: 'دورة تعليمية' },
    { n: meta.totals.learningPath, l: 'مسار تعليمي' },
    { n: meta.totals.libraryArticle, l: 'محتوى مقروء' },
  ] : []
  return (
    <>
      <section className="hero">
        <div className="container">
          <h1>تعلم تقنيات المستقبل<br />في مكانٍ واحد</h1>
          <p>مستكشف شامل لمحتوى أكاديمية طويق: المعسكرات والبرامج واللقاءات، ومنصة سَطر ومساراتها ودوراتها، ومكتبة طويق — بكل التفاصيل.</p>
          <Link to="/browse" className="btn-primary">ابدأ ←</Link>
        </div>
      </section>
      <div className="container">
        {stats.length > 0 && (
          <div className="stats">
            {stats.map(s => <div key={s.l} className="stat-card"><div className="stat-num">{s.n.toLocaleString('en-US')}</div><div className="stat-label">{s.l}</div></div>)}
          </div>
        )}
        {([['bootcamp', 'المعسكرات والبرامج', '/browse?type=bootcamp'],
           ['learningPath', 'مسارات منصة سَطر', '/browse?type=learningPath'],
           ['course', 'أحدث الدورات', '/browse?type=course'],
           ['libraryArticle', 'مكتبة طويق', '/browse?type=libraryArticle']] as const).map(([t, label, to]) => (
          <section className="section" key={t}>
            <div className="section-head">
              <h2 className="section-title" style={{ marginBottom: 0 }}>{label}</h2>
              <Link className="btn-secondary" to={to}>عرض المزيد</Link>
            </div>
            <RowGrid rows={byType(t)} />
          </section>
        ))}
      </div>
    </>
  )
}
