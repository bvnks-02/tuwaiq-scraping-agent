import { useEffect, useState } from 'react'
import { fetchDetail } from '../lib/data'
export default function DetailShell({ ref_, children }: { ref_?: string; children: (d: any) => React.ReactNode }) {
  const [d, setD] = useState<any>(null)
  const [err, setErr] = useState('')
  useEffect(() => {
    if (!ref_) { setErr('لا يوجد محتوى'); return }
    setD(null); setErr('')
    fetchDetail(ref_).then(setD).catch(e => setErr(String(e)))
  }, [ref_])
  if (err) return <div className="container err">تعذر تحميل المحتوى: {err}</div>
  if (!d) return <div className="loading container">جارٍ التحميل…</div>
  return <>{children(d)}</>
}
