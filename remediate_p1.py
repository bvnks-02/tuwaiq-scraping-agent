#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate-1 remediation: one bounded pass over all material findings + nits."""
import json, re, pathlib, html as htmllib
from urllib.parse import urljoin

ORG = pathlib.Path("output/organized_for_reproduction")
GEN = ORG / "generic"
SAN = ORG / "sanity"
EX_SATR = pathlib.Path("output/exhaustive/satr")
EX_TUW = pathlib.Path("output/exhaustive/tuwaiq/details")
def W(p, o): p.write_text(json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")
def RL(p): return json.loads(p.read_text(encoding="utf-8"))

# ---- F1: session descriptions into courses_normalized ----
courses = RL(GEN / "courses_normalized.json")
desc_count = 0
for c in courses:
    uid = c["slug"]["current"]
    raw = EX_SATR / "course_details" / f"{uid}.json"
    if not raw.exists(): continue
    rd = RL(raw)
    for u_n, u_r in zip(c.get("units") or [], rd.get("units") or []):
        for s_n, s_r in zip(u_n.get("sessions") or [], u_r.get("sessions") or []):
            d = s_r.get("description")
            if d:
                s_n["description"] = d; desc_count += 1
W(GEN / "courses_normalized.json", courses)
print(f"F1 session descriptions merged: {desc_count}")

# ---- F2a: 3 dangling Unity course refs -> minimal records from path-embedded summaries ----
unity = ["RduPyTHWvD", "CzeUdJXjme", "onKKLSYMOj"]
made = 0
path_detail = RL(EX_SATR / "path_details" / "QkAdKXTgYY.json")
for c in (path_detail.get("courses") or []):
    if c.get("url_id") in unity:
        uid = c["url_id"]
        doc = {
            "_type": "course", "_id": f"course-{uid}",
            "titleAr": c.get("title"), "slug": {"current": uid},
            "descriptionAr": c.get("description") or "",
            "excerpt": (c.get("description") or "")[:160],
            "level": c.get("level") or "", "duration": c.get("total_duration") or 0,
            "units": [], "detailSource": "path-embedded-summary (public detail returns empty)",
            "url": f"https://satr.tuwaiq.edu.sa/course/{uid}/view", "sourceId": c.get("id"),
        }
        (EX_SATR / "course_details" / f"{uid}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        if not any(x["slug"]["current"] == uid for x in courses):
            courses.append({**doc, "excerpt": (doc["descriptionAr"] or "")[:160], "image": "", "video": None, "prerequisites": [], "learningOutcomes": [], "url": doc["url"], "sourceId": doc["sourceId"]})
            made += 1
W(GEN / "courses_normalized.json", courses)
print(f"F2a unity courses: embedded {len(unity)}, added to normalized {made}, total courses {len(courses)}")

# ---- F2b: recover missing categories + locations + academies from raw dumps ----
cats = RL(GEN / "categories.json")
locs = RL(GEN / "locations.json")
known_cat = {c["id"]: c for c in cats}
known_loc = {l["id"]: l for l in locs}
missing_cat, missing_loc = {}, {}
academies = {}
bootcamps = RL(GEN / "bootcamps_normalized.json")
for b in bootcamps:
    slug = b["slug"]["current"]
    rawp = EX_TUW / f"{slug}.json"
    if not rawp.exists(): continue
    raw = RL(rawp)
    cid, cname = raw.get("initiativeCategoryId"), raw.get("initiativeCategoryName")
    if cid and cname and cid not in known_cat and cid not in missing_cat:
        missing_cat[cid] = {"id": cid, "titleAr": cname}
    lid, lname = raw.get("locationId"), raw.get("locationName")
    if lid and lname and lid not in known_loc and lid not in missing_loc:
        missing_loc[lid] = {"id": lid, "titleAr": lname, "initiativesCount": 0}
    at = raw.get("academyType")
    if isinstance(at, dict) and at.get("id") and at["id"] not in academies:
        academies[at["id"]] = {"_type": "academy", "_id": at["id"], "titleAr": at.get("name"),
                               "titleEn": at.get("nameEn"), "code": at.get("code"),
                               "logo": f"https://cdn.tuwaiq.edu.sa/initiatives_admin/{at.get('logo')}" if at.get("logo") else None}
cats += list(missing_cat.values()); locs += list(missing_loc.values())
W(GEN / "categories.json", cats); W(GEN / "locations.json", locs)
W(GEN / "academies.json", list(academies.values()))
print(f"F2b taxonomy: cats {len(cats)} (+{len(missing_cat)}), locs {len(locs)} (+{len(missing_loc)}), academies {len(academies)}")

# ---- F2c: denormalize academy string on bootcamps (keep ref too) ----
for b in bootcamps:
    aid = (b.get("academy") or {}).get("_ref")
    if aid and aid in academies:
        b["academyName"] = academies[aid]["titleAr"]
W(GEN / "bootcamps_normalized.json", bootcamps)
print("F2c academyName denormalized")

# ---- F7: mergedPublishes into bootcamps ----
mp_count = 0
for b in bootcamps:
    rawp = EX_TUW / f"{b['slug']['current']}.json"
    if not rawp.exists(): continue
    mp = RL(rawp).get("mergedPublishes")
    if mp:
        b["mergedPublishes"] = [{"slug": m.get("slug"), "title": m.get("title"),
                                 "startDate": m.get("startDate"), "endDate": m.get("endDate"),
                                 "locationName": m.get("locationName")}
                                for m in mp if isinstance(m, dict)][:10]
        mp_count += 1
W(GEN / "bootcamps_normalized.json", bootcamps)
print(f"F7 mergedPublishes captured on {mp_count} bootcamps")

# ---- F5: library sourceType provenance + F6 excerpts + magazine bare-PDF flag ----
library = RL(GEN / "library_normalized.json")
# recover provenance from the webapp detail files saved per type earlier? Use listing meta:
listing = []
for off in (0, 50):
    try:
        from scrapling.fetchers import Fetcher
        r = Fetcher.get(f"https://api.satr.codes/tuwaiq-library/public?limit=50&offset={off}", impersonate="chrome", stealthy_headers=True)
        listing += r.json().get("result_list", [])
    except Exception: pass
    time.sleep(0.3)
listing_types = {it["id"]: it.get("type", "ARTICLE") for it in listing}
strip_re = re.compile(r"<[^>]+>")
excerpt_count, pdf_flag = 0, 0
for a in library:
    iid = a["_id"].replace("article-", "")
    a["sourceType"] = listing_types.get(iid, a.get("sourceType", "ARTICLE"))
    htmlc = a.get("contentHtml") or ""
    if len(htmlc) < 150 and htmlc.strip().lower().startswith(("http://", "https://")):
        a["contentHtml"] = None
        a["externalPdf"] = htmlc.strip(); a["excerpt"] = a.get("titleAr"); pdf_flag += 1
    else:
        txt = strip_re.sub(" ", htmlc)
        txt = re.sub(r"\s+", " ", txt).strip()
        if not a.get("descriptionAr"):
            a["descriptionAr"] = txt[:300] or None
        a["excerpt"] = txt[:160]
    excerpt_count += 1
W(GEN / "library_normalized.json", library)
print(f"F5/F6 library provenance fixed {excerpt_count}, externalPdf flagged {pdf_flag}")

# ---- N4: dedupe flat_normalized + fix validation wording ----
flat = RL(GEN / "flat_normalized.json")
seen, dedup = set(), []
for r_ in flat:
    k = r_.get("_id") or r_.get("slug", {}).get("current")
    if k in seen: continue
    seen.add(k); dedup.append(r_)
W(GEN / "flat_normalized.json", dedup)
val = RL(pathlib.Path(".slim/deepwork/p1-validation.json"))
val["bootcamps_enriched"] = len(dedup)
val["bootcamps_unique_note"] = "1297 upstream rows; 1296 unique after removing true duplicate 3Rr1XKA8"
val["session_descriptions_merged"] = desc_count
val["categories_total"] = len(cats)
val["locations_total"] = len(locs)
val["academies"] = len(academies)
val["mergedPublishes_bootcamps"] = mp_count
val["courses_total"] = len(courses)
pathlib.Path(".slim/deepwork/p1-validation.json").write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"N4 flat deduped {len(flat)} -> {len(dedup)}; validation updated")
