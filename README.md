# Tuwaiq Academy — Content Explorer & Reproduction Dataset

An interactive, Arabic-RTL web viewer + structured dataset scraped from **https://tuwaiq.edu.sa** and **https://satr.tuwaiq.edu.sa** (منصة سطر / مكتبة طويق) — reproduced as a public "same as the original, minus auth" experience.

**Live viewer:** see *Deploy* below. **Items: 1538** (1296 bootcamps/programs/meetups/webinars · 20 learning paths · 165 courses · 51 library articles/publications/magazines · 6 practical projects).

## 🖥️ Webapp (flagship deliverable)

`webapp/` — Vite + React (TypeScript) SPA, Arabic RTL, IBM Plex Sans Arabic, design tokens extracted from the live site (`output/design-tokens.json`). Client-side fuzzy search (MiniSearch), filters (category/scope/level/paid/platform), and full detail views:

- `/bootcamp/:slug` — goals, requirements, features, FAQs, price/dates, merged instances, video embed
- `/path/:id` — resolved course list per learning path
- `/course/:id` — units → sessions timeline (types, durations, quiz metadata, lesson descriptions)
- `/library/:id` — full article HTML (sanitized, tables & code preserved); magazines/publications link their PDF
- `/project/:id` — practical project summaries

```bash
cd webapp
npm install
npm run dev        # dev server
npm run build      # static build → webapp/dist (data included)
npm run preview    # serve the build
```

**Deploy note (SPA fallback):** any static host must rewrite unmatched paths to `/index.html` (deep links like `/course/APjgdQqVWR` are client routes). `webapp/vercel.json` does this for Vercel; for nginx use `try_files $uri /index.html;`. `vite preview` handles it automatically in dev.

## Dataset & Reproduction

- `webapp/public/data/` — serving payloads: light `index.json` (1538 rows) + lazy per-detail chunks (1538 files) + `meta.json`
- `output/organized_for_reproduction/` — 8 Sanity document types (`sanity/schemas/*.ts`) + import-ready NDJSON (`sanity/data/*.ndjson`, `_id`/`_type`/references), plus normalized generic JSON for Strapi/Prisma/SQL (`generic/`)
- `output/exhaustive/` — raw API dumps (Tuwaiq 1297 detail JSONs, SATR paths/courses/projects)
- `output/design-tokens.json` + `output/style-guide.md` — extracted visual system (palette #4f29b7, IBM Plex Sans Arabic, RTL rules)

Import to Sanity: `sanity dataset import ./output/organized_for_reproduction/sanity/data/categories.ndjson production` then the rest in dependency order (see `sanity/README_SANITY.md`).

## Scripts (extraction pipeline)

| Script | Purpose |
|---|---|
| `tuwaiq_scraper.py` | initial StealthyFetcher pass (visual + academic) |
| `tuwaiq_visual_v2.py` | computed-style visual extraction (design tokens) |
| `tuwaiq_exhaustive.py` | all 1297 Tuwaiq initiatives + details via official APIs |
| `satr_exhaustive_fix.py` | all SATR paths/courses + `/public` details |
| `deep_content_extract.py` | library articles/publications/magazines + course/bootcamp enrichment |
| `remediate_p1.py` | gate-1 remediation merges (session descriptions, taxonomy, provenance) |
| `build_webapp_data.py` | normalized → webapp payloads (denormalized index + chunks) |

## Deploy

```bash
cd webapp
npx vercel --prod   # or connect the GitHub repo in the Vercel dashboard (root dir: webapp)
```

## Compliance & content rights

- Scraping respected `robots.txt` (Allow: /), rate-limited (0.2–0.3s), no auth bypass — quiz questions are auth-gated upstream and remain so.
- **Content ownership:** all Arabic text, media, and course material belongs to **Tuwaiq Academy** (and its partners/ sub-academies). This repo is an independent, non-affiliated educational/technical reproduction; per-item `sourceId`/`url` fields preserve original attribution. For any takedown or correction request, open an issue or contact the academy.
- Arabic content preserved verbatim (RTL); no auto-translation.

Generated 2026-09-13 → 2026-09-16. Deepwork log: `.slim/deepwork/` (local).
