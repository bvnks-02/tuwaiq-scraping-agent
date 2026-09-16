import { useParams } from 'react-router-dom'
import DOMPurify from 'dompurify'
import { fmtDate } from '../lib/data'
import { useMeta } from '../App'
import DetailShell from '../components/DetailShell'

export default function BootcampDetail() {
  const { slug } = useParams()
  const meta = useMeta()
  return (
    <DetailShell ref_={slug ? `/data/details/tuwaiq/${slug}.json` : undefined}>
      {(d: any) => {
        const media = d.media || {}
        const faqList = Array.isArray(d.faqs) ? d.faqs : Object.entries(d.faqs || {}).map(([question, answer]) => ({ question, answer: String(answer) }))
        return (
          <>
            <div className="container detail-hero">
              {media.outerImage && <img src={media.outerImage} alt="" style={{ width: '100%', maxHeight: 320, objectFit: 'cover', borderRadius: 16 }} />}
              <div className="detail-badges">
                {[d.categoryName, d.scopeName, d.level, d.academyName, d.durationText].filter(Boolean).map((b: string) => <span key={b} className="badge">{b}</span>)}
                {d.locationName && <span className="badge muted">{d.locationName}</span>}
              </div>
              <h1 className="detail-title">{d.titleAr}</h1>
              <p className="detail-desc">{d.descriptionAr}</p>
            </div>
            <div className="container detail-grid">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {media.video && <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(media.video, { ALLOWED_TAGS: ['div','iframe'], ALLOWED_ATTR: ['src','allow','frameborder','allowfullscreen','style','class','title'] }) }} />}
                {!!d.learningOutcomes?.length && (
                  <section><h3 className="section-title" style={{ fontSize: 20 }}>أهداف التدريب</h3>
                    <ul className="list-tick">{d.learningOutcomes.map((g: any, i: number) => <li key={i}><span className="tick">✓</span>{g.textAr}</li>)}</ul>
                  </section>)}
                {!!d.requirements?.length && (
                  <section><h3 className="section-title" style={{ fontSize: 20 }}>متطلبات الانضمام</h3>
                    <ul className="list-tick">{d.requirements.map((r: string, i: number) => <li key={i}><span className="tick">•</span>{r}</li>)}</ul>
                  </section>)}
                {!!d.features?.length && (
                  <section><h3 className="section-title" style={{ fontSize: 20 }}>مميزات البرنامج</h3>
                    <ul className="list-tick">{d.features.map((f: string, i: number) => <li key={i}><span className="tick">•</span>{f}</li>)}</ul>
                  </section>)}
                {!!faqList.length && (
                  <section><h3 className="section-title" style={{ fontSize: 20 }}>الأسئلة الشائعة</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {faqList.map((f: any, i: number) => (
                        <details key={i} className="accordion"><summary>{f.question}</summary><div>{f.answer}</div></details>))}
                    </div>
                  </section>)}
              </div>
              <aside className="panel">
                <div className="kv"><b>السعر</b><span>{d.isPaid ? `${(d.price ?? 0).toLocaleString('en-US')} ريال` : 'مجاني'}</span></div>
                {(d.dates?.start) && <div className="kv"><b>البداية</b><span>{fmtDate(d.dates.start)}</span></div>}
                {(d.dates?.end) && <div className="kv"><b>النهاية</b><span>{fmtDate(d.dates.end)}</span></div>}
                {(d.dates?.registrationEnd) && <div className="kv"><b>إغلاق التسجيل</b><span>{fmtDate(d.dates.registrationEnd)}</span></div>}
                {d.durationText && <div className="kv"><b>المدة</b><span>{d.durationText}</span></div>}
                {d.language && <div className="kv"><b>اللغة</b><span>{d.language === 'ar' ? 'العربية' : d.language}</span></div>}
                {d.url && <a className="btn-primary" href={d.url} target="_blank" rel="noreferrer">الصفحة الأصلية ↗</a>}
                {!!d.mergedPublishes?.length && (
                  <details><summary style={{ cursor: 'pointer', fontWeight: 600 }}>مواعيد بديلة ({d.mergedPublishes.length})</summary>
                    <ul style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {d.mergedPublishes.map((m: any, i: number) => <li key={i} style={{ fontSize: 13, color: 'var(--bp-ink-soft)' }}>{fmtDate(m.startDate)} — {m.locationName || ''}</li>)}
                    </ul></details>)}
              </aside>
            </div>
          </>
        )
      }}
    </DetailShell>
  )
}
