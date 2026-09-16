import { useParams } from 'react-router-dom'
import { fmtDuration } from '../lib/data'
import DetailShell from '../components/DetailShell'

const TYPE_AR: Record<string, string> = { video: 'فيديو', quiz: 'اختبار', article: 'مقال', project: 'مشروع', challenge: 'تحدي', session: 'جلسة', lesson: 'درس' }

export default function CourseDetail() {
  const { id } = useParams()
  return (
    <DetailShell ref_={id ? `/data/details/satr/course-${id}.json` : undefined}>
      {(d: any) => {
        const units = d.units || []
        const sessCount = units.reduce((a: number, u: any) => a + (u.sessions?.length || 0), 0)
        return (
          <>
            <div className="container detail-hero">
              <div className="detail-badges">
                <span className="badge">دورة</span>
                {d.level && <span className="badge muted">{d.level === 'JUNIOR' ? 'ناشئين' : d.level === 'MIDDLE' ? 'متوسط' : d.level}</span>}
                {d.duration ? <span className="badge muted">{fmtDuration(d.duration)}</span> : null}
                {sessCount > 0 && <span className="badge muted">{sessCount} جلسة</span>}
                {d.subscribersCount ? <span className="badge muted">{d.subscribersCount.toLocaleString('en-US')} مشترك</span> : null}
                {(d.programmingLanguages || []).map((l: any) => <span key={l.name || l} className="badge muted">{l.name || l}</span>)}
              </div>
              <h1 className="detail-title">{d.titleAr}</h1>
              <p className="detail-desc">{d.descriptionAr}</p>
              {d.previewVideo?.video_id && (
                <div style={{ marginTop: 18, aspectRatio: '16/9' }}>
                  <iframe src={`https://player.vimeo.com/video/${d.previewVideo.video_id}`} style={{ width: '100%', height: '100%', border: 0, borderRadius: 12 }} allowFullScreen title={d.titleAr} />
                </div>)}
            </div>
            <div className="container detail-grid">
              <div>
                {!!d.objectives?.length && <section style={{ marginBottom: 24 }}><h3 className="section-title" style={{ fontSize: 20 }}>أهداف الدورة</h3>
                  <ul className="list-tick">{d.objectives.map((o: string, i: number) => <li key={i}><span className="tick">✓</span>{o}</li>)}</ul></section>}
                <section><h3 className="section-title" style={{ fontSize: 20 }}>المحتوى</h3>
                  <div className="units">
                    {[...units].sort((a: any, b: any) => (a.order ?? 0) - (b.order ?? 0)).map((u: any, i: number) => (
                      <details key={u.id || i} className="unit" open={i === 0}>
                        <summary className="unit-head">
                          <b>{u.title}</b>
                          <span className="muted">{u.sessions?.length || 0} جلسة · {u.totalDuration ? fmtDuration(u.totalDuration) : ''}</span>
                        </summary>
                        <div className="sessions">
                          {[...(u.sessions || [])].sort((a: any, b: any) => (a.order ?? 0) - (b.order ?? 0)).map((s: any, j: number) => (
                            <div key={s.id || j} className="session">
                              <span className="badge type">{TYPE_AR[s.type] || s.type}</span>
                              <div style={{ flex: 1 }}><b style={{ fontSize: 14 }}>{s.title}</b>{s.description && <div className="muted" style={{ fontSize: 13 }}>{s.description}</div>}</div>
                              {s.duration ? <span className="dur">{fmtDuration(s.duration)}</span> : null}
                              {s.quiz && <span className="badge muted">{s.quiz.number_of_questions} أسئلة · نجاح {s.quiz.passing_percentage}%</span>}
                            </div>))}
                        </div>
                      </details>))}
                </div>
              </section>
            </div>
            <aside className="panel">
              <a className="btn-primary" href={d.url} target="_blank" rel="noreferrer">افتح الدورة على سطر ↗</a>
              {!!d.technologies?.length && <div className="kv"><b>تقنيات</b><span>{d.technologies.map((t: any) => t.name || t).join('، ')}</span></div>}
            </aside>
            </div>
          </>
        )
      }}
    </DetailShell>
  )
}
