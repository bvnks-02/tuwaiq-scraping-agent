import { useParams } from 'react-router-dom'
import DOMPurify from 'dompurify'
import { fmtDate } from '../lib/data'
import DetailShell from '../components/DetailShell'

export default function NewsDetail() {
  const { id } = useParams()
  return (
    <DetailShell ref_={id ? `/data/details/tuwaiq/news-${id}.json` : undefined}>
      {(d: any) => {
        const clean = d.descriptionHtml ? DOMPurify.sanitize(d.descriptionHtml, { ALLOWED_TAGS: ['h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','a','img','br','span','blockquote','table','thead','tbody','tr','th','td','colgroup','col','code','pre','hr','div'], ALLOWED_ATTR: ['href','src','alt','style','class'] }) : ''
        return (
          <>
            <div className="container detail-hero">
              <div className="detail-badges">
                <span className="badge">خبر</span>
                {(d.newsCategory?.name || d.newsCategory) && <span className="badge muted">{d.newsCategory?.name || d.newsCategory}</span>}
                {d.publishDate && <span className="badge muted">{fmtDate(d.publishDate)}</span>}
              </div>
              <h1 className="detail-title">{d.titleAr}</h1>
            </div>
            <div className="container" style={{ paddingBottom: 48, maxWidth: 860 }}>
              {d.image && <img src={d.image} alt="" style={{ maxHeight: 340, width: '100%', objectFit: 'cover', borderRadius: 12, marginBottom: 20 }} />}
              {clean && <div className="prose-rtl" dangerouslySetInnerHTML={{ __html: clean }} />}
              {d.url && <a className="btn-secondary" href={d.url} target="_blank" rel="noreferrer" style={{ marginTop: 20 }}>المصدر ↗</a>}
            </div>
          </>
        )
      }}
    </DetailShell>
  )
}
