export interface IndexRow {
  id: string; type: string; platform: string; title: string; excerpt?: string
  level?: string; language?: string; category?: string; scope?: string; location?: string
  isPaid?: boolean; price?: number | null; dateStart?: string
  image?: string | null; url?: string; ref?: string
  sourceType?: string; publishedAt?: string; coursesCount?: number; totalDuration?: number
  hasExternalPdf?: boolean
}
export interface Meta {
  totals: Record<string, number>
  categories: string[]; scopes: string[]; locations: string[]; academies: string[]
  levels: string[]; platforms: string[]
}
