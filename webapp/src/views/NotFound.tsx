import { Link } from 'react-router-dom'
export default function NotFound() {
  return (
    <div className="container" style={{ textAlign: 'center', padding: '80px 0' }}>
      <h1 style={{ fontSize: 40, color: 'var(--bp-accent)' }}>404</h1>
      <p className="muted">الصفحة غير موجودة</p>
      <Link className="btn-primary" to="/" style={{ marginTop: 16 }}>العودة للرئيسية</Link>
    </div>
  )
}
