# Sanity Import

These NDJSON files are Sanity Content Lake import-ready (reference integrity preserved).

```bash
# Import in dependency order (references first)
sanity dataset import ./sanity/data/categories.ndjson production
sanity dataset import ./sanity/data/scopes.ndjson production
sanity dataset import ./sanity/data/locations.ndjson production
sanity dataset import ./sanity/data/courses.ndjson production
sanity dataset import ./sanity/data/learningPaths.ndjson production
sanity dataset import ./sanity/data/bootcamps.ndjson production
```

- `_type` + `_id` are set (e.g. `bootcamp-kx9ya9Kd`, `category-ac411...`)
- References use `_ref` to `category`/`scope`/`location` IDs — no duplication.
- `descriptionAr` as Portable Text `array of block` in schema (currently string excerpt, convert via `@portabletext/block-tools` if needed).
- Arabic preserved (`ensure_ascii=False`), RTL handled in frontend (`dir=rtl`, `IBM Plex Sans Arabic` from design-tokens).
- Preview via GROQ: `*[_type=="bootcamp" && category._ref=="ac411..."] | order(dates.start asc)`

Add `sanity.config.ts` -> `schema: {types: schemaTypes}`.
