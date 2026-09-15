import RowCard from './RowCard'
import type { IndexRow } from '../lib/types'
export default function RowGrid({ rows }: { rows: IndexRow[] }) {
  if (!rows.length) return null
  return <div className="grid">{rows.map(r => <RowCard key={r.id} row={r} />)}</div>
}
