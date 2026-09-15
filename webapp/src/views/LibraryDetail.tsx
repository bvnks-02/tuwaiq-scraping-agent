import { useParams } from 'react-router-dom'
import DOMPurify from 'dompurify'
import DetailShell from '../components/DetailShell'

export default function LibraryDetail() {
  const { id } = useParams()
  return (
    <DetailShell ref_={id ? `/data/details/library/${id}.json` : undefined}>
      {(d: any) => {
        const clean = d.contentHtml ? DOMPurify.sanitize(d.contentHtml, { ALLOWED_TAGS: ['h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','a','img','br','span','blockquote','table','thead','tbody','tr','th','td','colgroup','col','code','pre','hr','div'], ALLOWED_ATTR: ['href','src','alt','style','class'] }) : ''
        return (
          <>
            <div className="container detail-hero">
              <div className="detail-badges">
                <span className="badge">مكتبة طويق</span>
                {d.sourceType && <span className="badge muted">{d.sourceType === 'ARTICLE' ? 'مقال' : d.sourceType === 'PUBLICATION' ? 'إصدار' : 'مجلة'}</span>}
                {d.keywords?.map((k: string) => <span key={k} className="badge muted">{k}</span>)}
              </div>
              <h1 className="detail-title">{d.titleAr}</h1>
              {d.descriptionAr && <p className="detail-desc">{d.descriptionAr}</p>}
            </div>
            <div className="container" style={{ paddingBottom: 48, maxWidth: 860 }}>
              {d.externalPdf
                ? <div className="panel" style={{ position: 'static', alignItems: 'center' }}>
                    <p>هذا المحتوى متاح كملف PDF:</p>
                    <a className="btn-primary" href={d.externalPdf} target="_blank" rel="noreferrer">فتح الملف ↗</a>
                    <iframe src={d.externalPdf} style={{ width: '100%', height: 520, border: 0, borderRadius: 12 }} title={d.titleAr} />
                  </div>
                : d.logoUrl && <img src={d.logoUrl} alt="" style={{ maxHeight: 300, borderRadius: 12, margin: '0 auto 20px' }} />}
              {clean && <div className="prose-rtl" dangerouslySetInnerHTML={{ __html: clean }} />}
              {d.url && <a className="btn-secondary" href={d.url} target="_blank" rel="noreferrer" style={{ marginTop: 20 }}>المصدر ↗</a>}
            </div>
          </>
        )
      }}
    </DetailShell>
  )
}
