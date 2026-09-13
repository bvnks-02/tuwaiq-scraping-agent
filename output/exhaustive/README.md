# Tuwaiq Academy — Exhaustive Educational Content (Organized)

**Generated:** 2026-09-13  **Source:** https://tuwaiq.edu.sa + https://satr.tuwaiq.edu.sa  
**Method:** API discovery via StealthyFetcher XHR capture (`/api/GetInitiativePublishesShorten`, `/api/GetInitiativePublishBySlug`, `api.satr.codes/path|landing-guest`), then exhaustive `Fetcher(impersonate=chrome)` with 0.25s rate-limit. Preserved Arabic RTL, respected `Allow: /`.

## Totals

- **Tuwaiq:** 1297 initiatives indexed, 1297 details fetched
  - برنامج: 620, لقاء: 330, معسكر: 204, ويبينار: 129, لقاءات رمضانية: 13, تحدي: 1
  - Scopes: 8 (تطوير البرمجيات, حوسبة سحابية, علم البيانات...)
  - Categories: 4
- **SATR:** 20 paths + 162 courses = 182 (each with `/public` detail)
- **Grand total educational items:** 1479
- **Visual system:** `output/design-tokens.json` (palette #4f29b7 primary, IBM Plex Sans Arabic, RTL)

## Structure

```
output/
├── design-tokens.json / .yaml (visual system, computed styles)
├── style-guide.md (216 lines)
├── exhaustive/
│   ├── SUMMARY.json
│   ├── ORGANIZED_ALL.json (tuwaiq + satr nested, CMS-ready)
│   ├── FLAT_CMS_READY.json (1479 flat records)
│   ├── tuwaiq/
│   │   ├── categories.json (4)
│   │   ├── scopes.json (8)
│   │   ├── statistics.json
│   │   ├── bootcamps_index.json (1297)
│   │   ├── bootcamps_details_all.json (5.9M)
│   │   ├── master_index.json (2.2M)
│   │   ├── by_category_*.json (6 files)
│   │   └── details/{slug}.json (1297 files)
│   └── satr/
│       ├── landing_guest.json
│       ├── seed.json
│       ├── banner.json
│       ├── paths_index.json (20)
│       ├── courses_index.json (162)
│       ├── path_details/ (20)
│       └── course_details/ (162)
```

## Key Fields

**Tuwaiq bootcamp detail** (`details/{slug}.json`): `id, initiativeId, title, description, goals[], startDate, endDate, registrationEndDate, isOpen, isPaid, price, vat, locationName, initiativeScopeName, initiativeCategoryName, initiativeAgeName (كبار/ناشئين), language, academyType, logo/outerImage/innerImage, video (vimeo), slug, url`

**SATR path** (`paths_index.json` + `path_details`): `url_id, title, description, level (MIDDLE/JUNIOR), total_duration (seconds), courses_count, learning_goals[]`

**SATR course** (`courses_index.json` + `course_details`): `url_id, title, description, level, total_duration, image` + `/public` includes videos, lessons.

## Usage for CMS

- Flat: `FLAT_CMS_READY.json` — one JSON array, each record has `platform` (tuwaiq/satr), `type`, `title`, `slug`, `url`, `description` (Arabic preserved)
- Nested: `ORGANIZED_ALL.json` — grouped by platform/category, ready to import
- Visual: `design-tokens.json` + `style-guide.md`

## Rate-limit & Compliance

- `Fetcher` with `stealthy_headers` + `impersonate=chrome`, 0.25s delay, no `/signin`, only public APIs, `Allow: /`.

## Verification

- Tuwaiq total 1297 matches API pagination `total:1297`, details 0 failures
- SATR paths 20/20, courses 162/162, all details fetched
- Arabic preserved (ensure_ascii=False), RTL `dir=rtl`, `IBM Plex Sans Arabic`
