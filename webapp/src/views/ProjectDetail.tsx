import { useParams } from 'react-router-dom'
import DetailShell from '../components/DetailShell'
export default function ProjectDetail() {
  const { id } = useParams()
  return (
    <DetailShell ref_={id ? `/data/details/satr/project-${id}.json` : undefined}>
      {(d: any) => (
        <div className="container detail-hero">
          <div className="detail-badges"><span className="badge">مشروع تطبيقي</span></div>
          <h1 className="detail-title">{d.titleAr}</h1>
          <p className="detail-desc" style={{ whiteSpace: 'pre-wrap' }}>{d.descriptionAr}</p>
          {(d.programmingLanguages?.length || d.technologies?.length) && (
            <div className="detail-badges" style={{ marginTop: 14 }}>
              {(d.programmingLanguages || []).map((l: any) => <span key={l.name || l} className="badge muted">{l.name || l}</span>)}
              {(d.technologies || []).map((t: any) => <span key={t.name || t} className="badge muted">{t.name || t}</span>)}
            </div>)}
        </div>
      )}
    </DetailShell>
  )
}
