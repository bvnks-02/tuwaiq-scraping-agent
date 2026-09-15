import React, { createContext, useContext, useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { fetchMeta } from './lib/data'
import type { Meta } from './lib/types'

const MetaCtx = createContext<Meta | null>(null)
export const useMeta = () => useContext(MetaCtx)

const NAV = [
  { to: '/', label: 'الرئيسية' },
  { to: '/browse?type=bootcamp', label: 'المعسكرات والبرامج' },
  { to: '/browse?type=course', label: 'منصة سطر' },
  { to: '/browse?type=libraryArticle', label: 'مكتبة طويق' },
]

export default function App({ children }: { children: React.ReactNode }) {
  const [meta, setMeta] = useState<Meta | null>(null)
  const { pathname } = useLocation()
  useEffect(() => { fetchMeta().then(setMeta).catch(() => setMeta(null)) }, [])
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return (
    <MetaCtx.Provider value={meta}>
      <header className="nav">
        <div className="container nav-inner">
          <Link to="/" className="brand">
            <span className="brand-mark">ط</span>
            <span>أكاديمية طويق</span>
            <span className="brand-sub">مستكشف المحتوى</span>
          </Link>
          <nav className="nav-links">
            {NAV.map(n => <Link key={n.to} to={n.to} className="nav-link">{n.label}</Link>)}
          </nav>
        </div>
      </header>
      <main>{children}</main>
      <footer className="footer">
        <div className="container footer-inner">
          <div className="footer-brand">
            <span className="brand-mark">ط</span> أكاديمية طويق
            <p className="muted">مستكشف تعليمي غير رسمي — نسخة عامة من محتوى tuwaiq.edu.sa و satr.tuwaiq.edu.sa</p>
          </div>
          <div className="footer-links">
            <a href="https://tuwaiq.edu.sa" target="_blank" rel="noreferrer">الموقع الرسمي</a>
            <a href="https://satr.tuwaiq.edu.sa" target="_blank" rel="noreferrer">منصة سطر</a>
            <a href="https://library.tuwaiq.edu.sa" target="_blank" rel="noreferrer">مكتبة طويق</a>
            <Link to="/browse">المستكشف</Link>
          </div>
        </div>
      </footer>
    </MetaCtx.Provider>
  )
}
