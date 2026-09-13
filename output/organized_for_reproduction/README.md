# Reproduction-Ready Organization for Tuwaiq + SATR (1479 items)

**Research basis:** Sanity Content Modeling Best Practices (don't conflate page with content, use references not embedding, Portable Text, GROQ) + Moodle/Open edX LMS taxonomy (Category → Subcategory → Course, Bloom's levels, consistent structure) — validated via `sanity.io/content-modeling-foundations`, `sanity.io/docs/developer-guides/deciding-fields-and-relationships`, `docs.moodle.org/Course_categories`.

## Why this organization is best for reproduction

1. **Content vs Page separation (Sanity):** Tuwaiq bootcamps were pages with embedded strings (`initiativeCategoryName: "معسكر"`). We normalized to `category`/`scope`/`location` documents + `reference` fields. This avoids duplication, enables filtering (`*[_type=="bootcamp" && category._ref=="ac411..."]`), and lets you reuse the same Category/Location across 1297 items. Follows Sanity's "hunt for nouns, model meaning not presentation."

2. **LMS taxonomy (Moodle):** Courses organized by *Category* (معسكر/برنامج/لقاء/ويبينار) with optional subcategories, plus *Scope* as topic track (8: تطوير البرمجيات...). This mirrors Moodle's `course_categories` (`parent`, `name`, `description`, `visible`) and lets you do "Science → Biology" style nesting. SATR's `learningPath` (20) groups `course` (162) via `courses: array<reference<course>>` — exactly how Moodle/Coursera bundle courses into tracks.

3. **Headless CMS flexibility:** Sanity NDJSON uses `_id`/`_type` + `_ref` so you can import to Sanity, Strapi, or any SQL (see `generic/*.json` for Prisma-ready). Portable Text for `descriptionAr` preserves RTL Arabic and allows rich text (headings, lists, goals) without HTML blobs. GROQ can reshape without remodeling.

4. **Arabic & RTL:** Field names `titleAr`, `descriptionAr` + Sanity `language: ar`, frontend `dir=rtl` + `IBM Plex Sans Arabic` (from `design-tokens.json`). No auto-translation, original Arabic preserved (`ensure_ascii=False`).

5. **Pricing, scheduling, outcomes as structured data:** `isPaid, price, vat, dates{start,end,registrationEnd}, learningOutcomes[]` are separate fields, not free text — enables filtering "open paid bootcamps in Riyadh starting next month" and SCORM/xAPI later if needed (not required for simple reproduction).

6. **Publishing workflow:** All docs have `sourceId` + `url` (e.g. `https://tuwaiq.edu.sa/bootcamp/kx9ya9Kd/view`) for audit, plus `isOpen` for visibility — maps to Sanity `Content Releases` (preview entire release, schedule).

## What we built (exhaustive → normalized)

- **Source exhaustive:** `output/exhaustive/` — 1297 Tuwaiq bootcamps (full `GetInitiativePublishBySlug` details, 5.9MB), 20 SATR paths + 162 courses (each `/public` detail), 8 scopes, 4 categories, stats — all via `api/GetInitiativePublishesShorten` + `api.satr.codes` with rate-limit.

- **Normalized generic (any platform):** `generic/`
  - `categories.json` (4, id + titleAr/titleEn + slug)
  - `scopes.json` (8, image CDN https://cdn.tuwaiq.edu.sa/initiatives_admin/...)
  - `locations.json` (4, الرياض etc. + initiativesCount)
  - `bootcamps_normalized.json` (1297, with `category: {_ref: id}`, `scope: {_ref}`, `location: {_ref}`, `dates`, `media`, `learningOutcomes[]`, `url`)
  - `learningPaths_normalized.json` (20, with `courses: [_ref]`, `learningGoals[]`, `totalDuration` seconds)
  - `courses_normalized.json` (162, with `level`, `duration`, `image`)
  - `flat_normalized.json` (1479 flat, `platform` + `contentType` for simple import)

- **Sanity-ready:** `sanity/schemas/*.ts` (6 `defineType` with `reference`, `slug`, `array of block`, validation) + `sanity/data/*.ndjson` (one JSON per line, import order matters: categories→scopes→locations→courses→paths→bootcamps). See `sanity/README_SANITY.md`.

- **Alternative SQL (Prisma):** Map directly:
  ```prisma
  model Category { id String @id; titleAr String; titleEn String?; slug String @unique }
  model Scope { id String @id; titleAr String; image String?; description String? }
  model Location { id String @id; titleAr String }
  model Bootcamp { id String @id; slug String @unique; titleAr String; descriptionAr String; categoryId String; scopeId String?; locationId String?; level String; isPaid Boolean; price Float?; startDate DateTime; category Category @relation(fields: [categoryId], references: [id]) }
  // Path/Course similar with many-to-many via join table
  ```

## How to reproduce

1. **Sanity:** `npx sanity@latest init` → copy `sanity/schemas` → `sanity.config.ts` `schema: {types: schemaTypes}` → `sanity dataset import ./sanity/data/*.ndjson production` in order.
2. **Strapi/SQL:** Import `generic/*.json` via script, e.g. `for doc in bootcamps_normalized.json: prisma.bootcamp.create({data: {...category: {connect: {id: doc.category._ref}}}})`
3. **Frontend:** Use `design-tokens.json` (palette #4f29b7 primary, `f9f7ff` bg, IBM Plex Sans Arabic) + `dir=rtl` for visual parity. Query with GROQ: `*[_type=="bootcamp"]{titleAr, category->, scope->, dates}`.

## File map

- `output/exhaustive/` — raw exhaustive API dumps (reference)
- `output/organized_for_reproduction/generic/` — normalized JSON for any DB
- `output/organized_for_reproduction/sanity/` — schemas + NDJSON for Sanity Content Lake
- `output/design-tokens.json` + `output/style-guide.md` — visual system (separate)

All Arabic preserved, references deduped, ready for `sanity dataset import` or `prisma db push`.
