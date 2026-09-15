# Sanity Import

NDJSON files are Content-Lake import-ready (`_id` + `_type` set; references use `_ref` to document `_id`s).

```bash
# Import in dependency order (referenced docs first)
sanity dataset import ./sanity/data/categories.ndjson production
sanity dataset import ./sanity/data/academies.ndjson production
sanity dataset import ./sanity/data/scopes.ndjson production
sanity dataset import ./sanity/data/locations.ndjson production
sanity dataset import ./sanity/data/courses.ndjson production
sanity dataset import ./sanity/data/learningPaths.ndjson production
sanity dataset import ./sanity/data/bootcamps.ndjson production
sanity dataset import ./sanity/data/library.ndjson production
```

Schema: 8 types registered in `schema.ts` (category, academy, scope, location, bootcamp, learningPath, course, libraryArticle).

- `bootcamp`: full enrichment — faqs (array of {question, answer}), features, requirements, durationText/times, attendType, ages, academyName, mergedPublishes.
- `course`: units→sessions with per-session description + quiz metadata (questions auth-gated upstream), objectives, previewVideo, subscribers/quizzes counts. `duration` is numeric seconds.
- `libraryArticle`: contentHtml as Portable Text (`content` field); 12 items have `externalPdf` (magazines/publications) — link/embed instead of content; `sourceType` ∈ {ARTICLE 39, PUBLICATION 8, MAGAZINE 4}.
- Path→course references: 3 Unity courses (`RduPyTHWvD/CzeUdJXjme/onKKLSYMOj`) have summary-level records only (public detail endpoint returns empty) — flagged `detailSource: path-embedded-summary`.
- Arabic preserved (UTF-8, RTL). GROQ example: `*[_type=="bootcamp" && category._ref=="ac41152d-f228-8af4-8406-e0cda6df6c35"]{titleAr, dates}`
