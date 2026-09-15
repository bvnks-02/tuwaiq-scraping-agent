#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild webapp payloads: light denormalized index + per-detail chunks (gate-1 remediated sources)."""
import json, pathlib

ORG = pathlib.Path("output/organized_for_reproduction/generic")
W = pathlib.Path("webapp/public/data")
for sub in ("tuwaiq", "satr", "library"):
    (W / "details" / sub).mkdir(parents=True, exist_ok=True)

bootcamps = json.loads((ORG / "bootcamps_normalized.json").read_text(encoding="utf-8"))
courses = json.loads((ORG / "courses_normalized.json").read_text(encoding="utf-8"))
paths = json.loads((ORG / "learningPaths_normalized.json").read_text(encoding="utf-8"))
library = json.loads((ORG / "library_normalized.json").read_text(encoding="utf-8"))
projects = json.loads((ORG / "practical_projects.json").read_text(encoding="utf-8"))
cats = json.loads((ORG / "categories.json").read_text(encoding="utf-8"))
scopes = json.loads((ORG / "scopes.json").read_text(encoding="utf-8"))
locs = json.loads((ORG / "locations.json").read_text(encoding="utf-8"))
academies = json.loads((ORG / "academies.json").read_text(encoding="utf-8"))
cat_by = {c["id"]: c["titleAr"] for c in cats}
scope_by = {s["id"]: s["titleAr"] for s in scopes}
loc_by = {l["id"]: l["titleAr"] for l in locs}
course_by = {c["slug"]["current"]: c for c in courses}

index = []

# Tuwaiq bootcamps
for b in bootcamps:
    slug = b["slug"]["current"]
    chunk = {**b,
        "categoryName": cat_by.get((b.get("category") or {}).get("_ref")),
        "scopeName": scope_by.get((b.get("scope") or {}).get("_ref")),
        "locationName": loc_by.get((b.get("location") or {}).get("_ref"))}
    index.append({
        "id": f"tuwaiq:{slug}", "type": "bootcamp", "platform": "tuwaiq",
        "title": b.get("titleAr"), "excerpt": b.get("excerpt", "")[:200],
        "level": b.get("level"), "language": b.get("language"),
        "category": chunk["categoryName"],
        "scope": chunk["scopeName"],
        "location": chunk["locationName"],
        "isPaid": b.get("isPaid"), "price": b.get("price"),
        "dateStart": (b.get("dates") or {}).get("start"),
        "image": (b.get("media") or {}).get("outerImage"),
        "url": b.get("url"), "ref": f"/data/details/tuwaiq/{slug}.json",
    })
    (W / "details" / "tuwaiq" / f"{slug}.json").write_text(json.dumps(chunk, ensure_ascii=False), encoding="utf-8")

# SATR paths — resolve course refs into embedded summaries at build time
for p in paths:
    uid = p["slug"]["current"]
    resolved, dangling = [], []
    for ref in (p.get("courses") or []):
        rid = (ref.get("_ref") or "").replace("course-", "")
        c = course_by.get(rid)
        if c:
            resolved.append({"url_id": rid, "title": c.get("titleAr"),
                             "level": c.get("level"), "duration": c.get("duration")})
        else:
            dangling.append(rid)
    index.append({
        "id": f"satr-path:{uid}", "type": "learningPath", "platform": "satr",
        "title": p.get("titleAr"), "excerpt": (p.get("descriptionAr") or "")[:200],
        "level": p.get("level"), "coursesCount": p.get("coursesCount"),
        "totalDuration": p.get("totalDuration"),
        "url": p.get("url"), "ref": f"/data/details/satr/path-{uid}.json",
    })
    chunk = {**p, "resolvedCourses": resolved}
    if dangling:
        chunk["danglingCourseRefs"] = dangling
    (W / "details" / "satr" / f"path-{uid}.json").write_text(json.dumps(chunk, ensure_ascii=False), encoding="utf-8")

# SATR courses
for c in courses:
    uid = c["slug"]["current"]
    index.append({
        "id": f"satr-course:{uid}", "type": "course", "platform": "satr",
        "title": c.get("titleAr"), "excerpt": c.get("excerpt", "")[:200],
        "level": c.get("level"), "duration": c.get("duration"),
        "image": c.get("image") or None,
        "url": c.get("url"), "ref": f"/data/details/satr/course-{uid}.json",
    })
    (W / "details" / "satr" / f"course-{uid}.json").write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")

# Library
for a in library:
    iid = a["_id"].replace("article-", "")
    index.append({
        "id": f"library:{iid}", "type": "libraryArticle", "platform": "library",
        "title": a.get("titleAr"), "excerpt": a.get("excerpt") or (a.get("descriptionAr") or "")[:200],
        "sourceType": a.get("sourceType"), "publishedAt": a.get("publishedAt"),
        "hasExternalPdf": bool(a.get("externalPdf")),
        "image": a.get("logoUrl"), "url": a.get("url"),
        "ref": f"/data/details/library/{iid}.json",
    })
    (W / "details" / "library" / f"{iid}.json").write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")

# Practical projects (6 public samples of 193)
for p in projects:
    uid = p.get("url_id") or p.get("id")
    doc = {"_type": "practicalProject", "_id": f"project-{uid}", "titleAr": p.get("title"),
           "slug": {"current": uid}, "descriptionAr": p.get("description"),
           "programmingLanguages": p.get("programming_languages") or [],
           "technologies": p.get("technologies") or []}
    (W / "details" / "satr" / f"project-{uid}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    index.append({
        "id": f"satr-project:{uid}", "type": "practicalProject", "platform": "satr",
        "title": p.get("title"), "excerpt": (p.get("description") or "")[:200],
        "url": f"https://satr.tuwaiq.edu.sa/project/{uid}/view",
        "ref": f"/data/details/satr/project-{uid}.json",
    })

meta = {
    "generatedAt": "2026-09-15",
    "totals": {
        "all": len(index),
        "bootcamp": sum(1 for i in index if i["type"] == "bootcamp"),
        "learningPath": sum(1 for i in index if i["type"] == "learningPath"),
        "course": sum(1 for i in index if i["type"] == "course"),
        "libraryArticle": sum(1 for i in index if i["type"] == "libraryArticle"),
        "practicalProject": sum(1 for i in index if i["type"] == "practicalProject"),
    },
    "categories": [c["titleAr"] for c in cats],
    "scopes": [s["titleAr"] for s in scopes],
    "locations": [l["titleAr"] for l in locs],
    "academies": [a.get("titleAr") for a in academies],
    "levels": sorted({str(i.get("level")) for i in index if i.get("level")}),
    "platforms": ["tuwaiq", "satr", "library"],
    "projectsKnownTotal": 193,
    "notes": "6/193 practical projects publicly listed; Unity course details summary-level (public detail empty).",
}
(W / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
(W / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
print(f"index rows {len(index)} totals {meta['totals']}")
