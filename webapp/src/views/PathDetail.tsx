import { Link, useParams } from 'react-router-dom'
import { fmtDuration } from '../lib/data'
import DetailShell from '../components/DetailShell'

export default function PathDetail() {
  const { id } = useParams()
  return (
    <DetailShell ref_={id ? `/data/details/satr/path-${id}.json` : undefined}>
      {(d: any) => (
        <>
          <div className="container detail-hero">
            <div className="detail-badges">
              <span className="badge">مسار</span>
              {d.level && <span className="badge muted">{d.level === 'JUNIOR' ? 'ناشئين' : d.level === 'MIDDLE' ? 'متوسط' : d.level}</span>}
              {d.coursesCount && <span className="badge muted">{d.coursesCount} دورة</span>}
              {d.totalDuration ? <span className="badge muted">{fmtDuration(d.totalDuration)}</span> : null}
            </div>
            <h1 className="detail-title">{d.titleAr}</h1>
            <p className="detail-desc">{d.descriptionAr}</p>
          </div>
          <div className="container detail-grid">
            <div>
              {!!d.learningGoals?.length && <section style={{ marginBottom: 24 }}><h3 className="section-title" style={{ fontSize: 20 }}>أهداف التعلم</h3>
                <ul className="list-tick">{d.learningGoals.map((g: any, i: number) => <li key={i}><span className="tick">✓</span>{g.textAr}</li>)}</ul></section>}
              <section><h3 className="section-title" style={{ fontSize: 20 }}>دورات المسار</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {(d.resolvedCourses || []).map((c: any) => (
                    <Link key={c.url_id} to={`/course/${c.url_id}`} className="session">
                      <span className="badge">{c.level === 'JUNIOR' ? 'ناشئ' : c.level === 'MIDDLE' ? 'متوسط' : c.level || 'دورة'}</span>
                      <b style={{ flex: 1 }}>{c.title}</b>
                      {c.duration ? <span className="dur">{fmtDuration(c.duration)}</span> : null}
                    </Link>))}
                </div>
                {!!d.danglingCourseRefs?.length && <p className="muted" style={{ marginTop: 8, fontSize: 13 }}>ملاحظة: {d.danglingCourseRefs.length} دورة بدون تفاصيل عامة.</p>}
              </section>
            </div>
            <aside className="panel">
              <a className="btn-primary" href={d.url} target="_blank" rel="noreferrer">افتح المسار على سطر ↗</a>
            </aside>
          </div>
        </>
      )}
    </DetailShell>
  )
}
