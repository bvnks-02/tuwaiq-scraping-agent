import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import MiniSearch from 'minisearch'
import { fetchIndex } from '../lib/data'
import { useMeta } from '../App'
import RowGrid from '../components/RowGrid'
import type { IndexRow, Meta } from '../lib/types'

const TYPE_LABEL: Record<string, string> = {
  bootcamp: 'المعسكرات والبرامج', learningPath: 'المسارات', course: 'الدورات',
  libraryArticle: 'مكتبة طويق', practicalProject: 'مشاريع تطبيقية', newsItem: 'الأخبار',
}
const PAGE = 24

export default function Browse() {
  const [rows, setRows] = useState<IndexRow[]>([])
  const [query, setQuery] = useState('')
  const [visible, setVisible] = useState(PAGE)
  const [sp, setSp] = useSearchParams()
  const meta = useMeta() as Meta | null
  const fType = sp.get('type') || ''
  const fCat = sp.get('cat') || ''
  const fLevel = sp.get('level') || ''
  const fPaid = sp.get('paid') || ''

  useEffect(() => { fetchIndex().then(setRows).catch(() => {}) }, [])

  const ms = useMemo(() => {
    const m = new MiniSearch({ fields: ['title', 'excerpt', 'category', 'scope'], storeFields: ['id'], searchOptions: { prefix: true, fuzzy: 0.2 } })
    if (rows.length) m.addAll(rows)
    return m
  }, [rows])

  const filtered = useMemo(() => {
    let out = rows
    if (query.trim()) {
      const hits = new Set(ms.search(query).map((h: any) => h.id as string))
      out = out.filter(r => hits.has(r.id))
    }
    if (fType) out = out.filter(r => r.type === fType)
    if (fCat) out = out.filter(r => r.category === fCat)
    if (fLevel) out = out.filter(r => r.level === fLevel)
    if (fPaid) out = out.filter(r => fPaid === 'paid' ? !!r.isPaid : !r.isPaid)
    return out
  }, [rows, ms, query, fType, fCat, fLevel, fPaid])

  useEffect(() => { setVisible(PAGE) }, [query, fType, fCat, fLevel, fPaid])
  const setP = (k: string, v: string) => { const cur = sp.get(k); const n = new URLSearchParams(sp); if (v && cur !== v) n.set(k, v); else n.delete(k); setSp(n) }

  return (
    <div className="container">
      <div className="toolbar">
        <div className="searchbox"><input className="search-box" placeholder="ابحث…" value={query} onChange={e => setQuery(e.target.value)} /></div>
      </div>
      <div className="filters">
        <button className={`chip ${fType === '' ? 'on' : ''}`} onClick={() => { const n = new URLSearchParams(sp); n.delete('type'); setSp(n) }}>الكل</button>
        {Object.entries(TYPE_LABEL).map(([t, l]) => (
          <button key={t} className={`chip ${fType === t ? 'on' : ''}`} onClick={() => setP('type', t)}>{l}</button>
        ))}
      </div>
      <div className="filters">{meta?.categories.map(c => (
        <button key={c} className={`chip ${fCat === c ? 'on' : ''}`} onClick={() => { const n = new URLSearchParams(sp); fCat === c ? n.delete('cat') : n.set('cat', c); setSp(n) }}>{c}</button>
      ))}</div>
      {(!fType || fType === 'bootcamp' || fType === 'learningPath' || fType === 'course') && (
        <div className="filters">{meta?.levels.map(l => (
          <button key={l} className={`chip ${fLevel === l ? 'on' : ''}`} onClick={() => { const n = new URLSearchParams(sp); fLevel === l ? n.delete('level') : n.set('level', l); setSp(n) }}>{l}</button>
        ))}</div>
      )}
      {fType === 'bootcamp' && (
        <div className="filters">
          <button className={`chip ${fPaid === 'paid' ? 'on' : ''}`} onClick={() => setP('paid', 'paid')}>مدفوع</button>
          <button className={`chip ${fPaid === 'free' ? 'on' : ''}`} onClick={() => setP('paid', 'free')}>مجاني</button>
        </div>
      )}
      <div className="section-head" style={{ marginTop: 8 }}>
        <h2 className="section-title" style={{ marginBottom: 0 }}>{filtered.length.toLocaleString('en-US')} نتيجة</h2>
      </div>
      <RowGrid rows={filtered.slice(0, visible)} />
      {filtered.length > visible && (
        <div style={{ textAlign: 'center', margin: '28px 0' }}>
          <button className="btn-secondary" onClick={() => setVisible(v => v + PAGE)}>عرض المزيد</button>
        </div>
      )}
    </div>
  )
}
