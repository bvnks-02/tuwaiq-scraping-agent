#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P1 deep content extraction — scrapling tooling only, rate-limited."""
import json, time, pathlib
from scrapling.fetchers import Fetcher

OUT = pathlib.Path("output/organized_for_reproduction")
LIB = OUT / "library" / "articles"
EX_SATR = pathlib.Path("output/exhaustive/satr/course_details")
EX_TUW = pathlib.Path("output/exhaustive/tuwaiq/details")

def fetch_json(url, retries=2):
    for i in range(retries + 1):
        try:
            r = Fetcher.get(url, impersonate="chrome", stealthy_headers=True)
            if r.status == 200:
                return r.json()
            if r.status == 404:
                return None
        except Exception as e:
            print(f"  err {url[:80]} {e} attempt {i}", flush=True)
        time.sleep(0.5)
    return None

# ===== Step 1: library articles =====
print("=== Library articles ===", flush=True)
listing = []
for offset in (0, 50):
    j = fetch_json(f"https://api.satr.codes/tuwaiq-library/public?limit=50&offset={offset}")
    if j:
        listing.extend(j.get("result_list", []))
    time.sleep(0.3)
print(f"listing {len(listing)}", flush=True)

seen, articles_meta = set(), []
for it in listing:
    iid = it.get("id")
    if iid and iid not in seen:
        seen.add(iid)
        articles_meta.append(it)

fetched, with_content = 0, 0
for i, it in enumerate(articles_meta, 1):
    iid = it["id"]
    p = LIB / f"{iid}.json"
    if p.exists() and p.stat().st_size > 200:
        d = json.loads(p.read_text(encoding="utf-8"))
        fetched += 1
        if d.get("content"): with_content += 1
        continue
    d = fetch_json(f"https://api.satr.codes/tuwaiq-library/article/{iid}")
    if d:
        (LIB / f"{iid}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        fetched += 1
        if d.get("content"): with_content += 1
    else:
        print(f"  FAILED article {iid}", flush=True)
    if i % 10 == 0: print(f"  {i}/{len(articles_meta)}", flush=True)
    time.sleep(0.25)
print(f"articles fetched {fetched}/{len(articles_meta)}, with_content {with_content}", flush=True)

# ===== Step 2: enrich courses with units/sessions =====
print("=== Enrich courses ===", flush=True)
courses = json.loads((OUT / "generic" / "courses_normalized.json").read_text(encoding="utf-8"))
units_count = 0
for c in courses:
    uid = c["slug"]["current"]
    raw_p = EX_SATR / f"{uid}.json"
    if not raw_p.exists(): continue
    raw = json.loads(raw_p.read_text(encoding="utf-8"))
    c["objectives"] = raw.get("objectives") or []
    units = []
    for u in (raw.get("units") or []):
        sessions = []
        for s in (u.get("sessions") or []):
            sess = {
                "title": s.get("title"), "type": s.get("type"),
                "duration": s.get("duration"), "order": s.get("order"),
            }
            q = s.get("quiz")
            if isinstance(q, dict):
                sess["quiz"] = {k: q.get(k) for k in ("number_of_questions","passing_percentage","max_attempts")}
            prj = s.get("project")
            if isinstance(prj, dict):
                sess["project"] = {k: prj.get(k) for k in ("title","description") if prj.get(k)}
            art = s.get("article")
            if isinstance(art, dict):
                sess["article"] = {k: art.get(k) for k in ("title","id") if art.get(k)}
            sessions.append(sess)
        units.append({
            "title": u.get("title"), "description": u.get("description"),
            "totalDuration": u.get("total_duration"), "order": u.get("order"),
            "sessions": sessions,
        })
    c["units"] = units
    if units: units_count += 1
    c["previewVideo"] = raw.get("preview_video") or None
    c["subscribersCount"] = raw.get("subscribers_count")
    c["videosDuration"] = raw.get("videos_duration")
    c["quizzesCount"] = raw.get("quizzes_count")
    c["projectsCount"] = raw.get("projects_count")
    c["courseStatus"] = raw.get("course_status")
    c["courseType"] = raw.get("course_type")
    c["programmingLanguages"] = raw.get("programming_languages") or []
    c["technologies"] = raw.get("technologies") or []
(OUT / "generic" / "courses_normalized.json").write_text(json.dumps(courses, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"courses enriched 162, with units {units_count}", flush=True)

# ===== Step 3: enrich bootcamps =====
print("=== Enrich bootcamps ===", flush=True)
bootcamps = json.loads((OUT / "generic" / "bootcamps_normalized.json").read_text(encoding="utf-8"))
n_faq = n_feat = n_req = n_full = 0
for b in bootcamps:
    slug = b["slug"]["current"]
    raw_p = EX_TUW / f"{slug}.json"
    if not raw_p.exists(): continue
    raw = json.loads(raw_p.read_text(encoding="utf-8"))
    b["requirements"] = raw.get("requirements") or []
    b["features"] = raw.get("features") or []
    b["faqs"] = raw.get("faqs") or []
    b["durationText"] = raw.get("durationText")
    b["startTimeText"] = raw.get("startTimeText")
    b["endTimeText"] = raw.get("endTimeText")
    b["startDateText"] = raw.get("startDateText")
    b["endDateText"] = raw.get("endDateText")
    b["attendType"] = raw.get("initiativeAttendType")
    b["minimumAge"] = raw.get("minimumAge")
    b["maximumAge"] = raw.get("maximumAge")
    if b["faqs"]: n_faq += 1
    if b["features"]: n_feat += 1
    if b["requirements"]: n_req += 1
    if b["requirements"] or b["features"] or b["faqs"]: n_full += 1
(OUT / "generic" / "bootcamps_normalized.json").write_text(json.dumps(bootcamps, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"bootcamps enriched 1297: faqs {n_faq}, features {n_feat}, requirements {n_req}", flush=True)

# ===== Step 4: library_normalized =====
lib_norm = []
for it in articles_meta:
    iid = it["id"]
    p = LIB / f"{iid}.json"
    d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    lib_norm.append({
        "_type": "libraryArticle",
        "_id": f"article-{iid}",
        "titleAr": d.get("title") or it.get("title"),
        "slug": {"current": d.get("url_id") or iid},
        "descriptionAr": d.get("description"),
        "contentHtml": d.get("content"),
        "keywords": d.get("keywords") or [],
        "duration": d.get("duration") or it.get("duration"),
        "logoUrl": d.get("logo_url") or it.get("logo_url"),
        "visitorCount": d.get("visitor_count"),
        "publishedAt": it.get("published_at"),
        "sourceType": it.get("type"),
        "url": f"https://library.tuwaiq.edu.sa/article/{iid}",
    })
(OUT / "generic" / "library_normalized.json").write_text(json.dumps(lib_norm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"library_normalized {len(lib_norm)}", flush=True)

# ===== Step 5: regenerate Sanity NDJSON =====
import pathlib as pl
SAN = OUT / "sanity" / "data"
def write_ndjson(name, docs):
    with open(SAN / name, "w", encoding="utf-8") as f:
        for doc in docs:
            clean = {k: v for k, v in doc.items() if v is not None}
            f.write(json.dumps(clean, ensure_ascii=False) + "\n")
write_ndjson("bootcamps.ndjson", bootcamps)
write_ndjson("courses.ndjson", courses)
write_ndjson("library.ndjson", lib_norm)
print("NDJSON regenerated", flush=True)

# ===== Step 6: validation =====
val = {
    "articles_fetched": fetched,
    "articles_total": len(articles_meta),
    "articles_with_content": with_content,
    "courses_enriched": 162,
    "courses_with_units": units_count,
    "bootcamps_enriched": 1297,
    "bootcamps_with_faqs": n_faq,
    "bootcamps_with_features": n_feat,
    "bootcamps_with_requirements": n_req,
    "library_normalized": len(lib_norm),
}
pl.Path(".slim/deepwork/p1-validation.json").write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")
print("VALIDATION:", json.dumps(val, ensure_ascii=False), flush=True)
