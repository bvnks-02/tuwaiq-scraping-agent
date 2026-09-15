# Tuwaiq Academy — Exhaustive Scraping & Reproduction-Ready Dataset

**Source:** https://tuwaiq.edu.sa (Arabic, RTL) + https://satr.tuwaiq.edu.sa  
**Method:** `scrapling` StealthyFetcher (Patchright, solve_cloudflare, network_idle, locale ar-SA) → API discovery via XHR capture → exhaustive `Fetcher(impersonate=chrome)` with rate-limit.

## Outputs

- **Visual System:** `output/design-tokens.json` (palette #4f29b7 primary, IBM Plex Sans Arabic, RTL) + `output/design-tokens.yaml` + `output/style-guide.md` (216 lines, getComputedStyle on nav/hero/buttons/cards/footer)
- **Exhaustive Educational Content (1538 items):** `output/exhaustive/`
  - Tuwaiq: 1297 bootcamps/programs/meetups/webinars (4 categories, 8 scopes, 4 locations) via `api/GetInitiativePublishesShorten` + `GetInitiativePublishBySlug` (each detail with title, description, goals, dates, price, location, video)
  - SATR: 20 paths + 162 courses via `api.satr.codes/path|landing-guest`, each `/public` detail
- **Organized for Reproduction** (`output/organized_for_reproduction/` — 8 Sanity document types, `_id`/`_type` NDJSON): `output/organized_for_reproduction/`
  - Sanity schemas (`sanity/schemas/*.ts` defineType with reference, Portable Text) + NDJSON (`sanity/data/*.ndjson`) ready for `sanity dataset import`
  - Generic normalized JSON (`generic/*.json`) for Strapi/Prisma/SQL
  - Flat CMS-ready (`flat_normalized.json` 1538 records)

## Quick Start (Reproduce)

```bash
# Sanity
npx sanity@latest init
cp -r output/organized_for_reproduction/sanity/schemas ./schemas
# then in sanity.config.ts: schema: {types: schemaTypes}
sanity dataset import ./output/organized_for_reproduction/sanity/data/categories.ndjson production
sanity dataset import ./output/organized_for_reproduction/sanity/data/scopes.ndjson production
sanity dataset import ./output/organized_for_reproduction/sanity/data/courses.ndjson production
# ... etc in order
```

See `output/exhaustive/README.md` and `output/organized_for_reproduction/README.md` for full schema rationale (Sanity best practices + Moodle taxonomy).

## Scripts

- `tuwaiq_scraper.py` — visual + academic via StealthyFetcher
- `tuwaiq_exhaustive.py` — exhaustive 1297 Tuwaiq via APIs
- `satr_exhaustive_fix.py` — exhaustive SATR 20+162 via api.satr.codes
- `tuwaiq_fixup.py` / `tuwaiq_visual_v2.py` — offline parsers & visual fixups

## Compliance

- `robots.txt` Allow: / respected, avoided `/signin`, rate-limited 0.2-0.3s, preserved Arabic RTL, no auto-translation.

Generated 2026-09-13.
