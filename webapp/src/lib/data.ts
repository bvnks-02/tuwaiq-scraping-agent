import type { IndexRow, Meta } from './types'

const API = import.meta.env.BASE_URL ?? '/'
export async function fetchIndex(): Promise<IndexRow[]> {
  const r = await fetch(`${API}data/index.json`)
  if (!r.ok) throw new Error(`index ${r.status}`)
  return r.json()
}
export async function fetchMeta() {
  const r = await fetch(`${API}data/meta.json`)
  if (!r.ok) throw new Error(`meta ${r.status}`)
  return r.json()
}
export async function fetchDetail(ref: string): Promise<any> {
  const path = ref.replace(/^\//, '')
  const r = await fetch(`${API}${path}`)
  if (!r.ok) throw new Error(`detail ${ref} ${r.status}`)
  return r.json()
}
export function fmtDuration(sec?: number | null): string {
  if (!sec && sec !== 0) return ''
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60
  return [h, m, s].map(v => String(v).padStart(2, '0')).join(':')
}
export function fmtDate(iso?: string | null): string {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString('ar-SA', { year: 'numeric', month: 'long', day: 'numeric' }) } catch { return iso.slice(0, 10) }
}
