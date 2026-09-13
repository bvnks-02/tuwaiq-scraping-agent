#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exhaustive Tuwaiq + SATR courses extraction
- Tuwaiq: via api/GetInitiativePublishesShorten paginated + GetInitiativePublishBySlug detail
- SATR: via api.satr.codes/path/course pagination + /public detail
Organized output in output/exhaustive/
"""
import json, time, pathlib, re
from urllib.parse import urljoin
from scrapling.fetchers import Fetcher

BASE = "https://tuwaiq.edu.sa"
SATR_API = "https://api.satr.codes"
OUT = pathlib.Path("/home/bvnks/scraping_agent/output/exhaustive")
OUT.mkdir(parents=True, exist_ok=True)
(TUW := OUT / "tuwaiq").mkdir(parents=True, exist_ok=True)
(SATR := OUT / "satr").mkdir(parents=True, exist_ok=True)
(TUW / "details").mkdir(parents=True, exist_ok=True)
(SATR / "path_details").mkdir(parents=True, exist_ok=True)
(SATR / "course_details").mkdir(parents=True, exist_ok=True)

def log(m): print(m, flush=True)

def fetch_json(url, retries=2):
    for attempt in range(retries+1):
        try:
            r = Fetcher.get(url, impersonate="chrome", stealthy_headers=True)
            if r.status == 200:
                try:
                    return r.json()
                except:
                    # try text
                    if len(r.text) < 5:
                        return None
                    return json.loads(r.text)
            else:
                log(f"  {url} status {r.status}")
                if r.status == 404:
                    return None
        except Exception as e:
            log(f"  fetch {url} err {e} attempt {attempt}")
            if attempt == retries:
                return None
        time.sleep(0.4)
    return None

# ========== TUWAIQ EXHAUSTIVE ==========
log("=== TUWAIQ: Fetching categories, scopes, locations, stats ===")
cats = fetch_json(f"{BASE}/api/GetInitiativeCategories") or []
scopes = fetch_json(f"{BASE}/api/GetInitiativeScopes") or []
locs = fetch_json(f"{BASE}/api/GetLocationsWithInitiatives") or []
stats = fetch_json(f"{BASE}/Api/GetStatistics") or {}
with open(TUW / "categories.json","w",encoding="utf-8") as f: json.dump(cats, f, ensure_ascii=False, indent=2)
with open(TUW / "scopes.json","w",encoding="utf-8") as f: json.dump(scopes, f, ensure_ascii=False, indent=2)
with open(TUW / "locations.json","w",encoding="utf-8") as f: json.dump(locs, f, ensure_ascii=False, indent=2)
with open(TUW / "statistics.json","w",encoding="utf-8") as f: json.dump(stats, f, ensure_ascii=False, indent=2)
log(f"cats {len(cats)} scopes {len(scopes)} locs {len(locs)} stats {stats}")

# Also fetch news/releases
news = fetch_json(f"{BASE}/Api/GetNews/6/1/") or []
releases = fetch_json(f"{BASE}/Api/GetReleases?page=1&pageSize=70") or {}
releases_home = fetch_json(f"{BASE}/Api/GetReleasesForHomePage") or {}
with open(TUW / "news.json","w",encoding="utf-8") as f: json.dump(news, f, ensure_ascii=False, indent=2)
with open(TUW / "releases.json","w",encoding="utf-8") as f: json.dump(releases, f, ensure_ascii=False, indent=2)
with open(TUW / "releases_home.json","w",encoding="utf-8") as f: json.dump(releases_home, f, ensure_ascii=False, indent=2)

# Exhaustive initiatives: try all without filter, paginated 100 per page
log("\n=== TUWAIQ: Exhaustive initiatives via GetInitiativePublishesShorten ===")
all_initiatives = []
seen_ids = set()
page = 1
pageSize = 100
total = None
while True:
    url = f"{BASE}/api/GetInitiativePublishesShorten/{pageSize}/{page}"
    j = fetch_json(url)
    if not j:
        log(f"  page {page} no data, break")
        break
    data = j.get("data", [])
    pagination = j.get("pagination", {})
    if total is None:
        total = pagination.get("total", 0)
        log(f"  total {total} pages {pagination.get('totalPages')}")
    if not data:
        log(f"  page {page} empty, break")
        break
    for it in data:
        if it["id"] not in seen_ids:
            seen_ids.add(it["id"])
            all_initiatives.append(it)
    log(f"  page {page} got {len(data)} total collected {len(all_initiatives)}/{total}")
    if len(all_initiatives) >= total or page >= pagination.get("totalPages", 999):
        break
    page += 1
    time.sleep(0.3)

# Also try per-category to ensure we didn't miss filtered ones? The all fetch should cover all, but verify by also fetching per-category and merging
log(f"\nCollected {len(all_initiatives)} initiatives via all query, total reported {total}")
# Save index
with open(TUW / "bootcamps_index.json","w",encoding="utf-8") as f: json.dump(all_initiatives, f, ensure_ascii=False, indent=2)

# Now fetch details for each initiative via slug
log(f"\n=== Fetching details for {len(all_initiatives)} initiatives via GetInitiativePublishBySlug ===")
details = []
failures = []
for idx, it in enumerate(all_initiatives, 1):
    slug = it.get("slug")
    if not slug:
        continue
    url = f"{BASE}/api/GetInitiativePublishBySlug/{slug}"
    j = fetch_json(url)
    if j:
        # Save individual
        with open(TUW / "details" / f"{slug}.json","w",encoding="utf-8") as f: json.dump(j, f, ensure_ascii=False, indent=2)
        details.append(j)
    else:
        failures.append(slug)
        log(f"  failed {slug}")
    if idx % 50 == 0:
        log(f"  {idx}/{len(all_initiatives)} done, failures {len(failures)}")
    time.sleep(0.25)

log(f"Details fetched {len(details)} failures {len(failures)}")
with open(TUW / "bootcamps_details_all.json","w",encoding="utf-8") as f: json.dump(details, f, ensure_ascii=False, indent=2)
if failures:
    with open(TUW / "failures.json","w",encoding="utf-8") as f: json.dump(failures, f, ensure_ascii=False, indent=2)

# Organize by category and type
by_cat = {}
for d in details:
    cat = d.get("initiativeCategoryName") or d.get("initiativeCategoryId") or "unknown"
    by_cat.setdefault(cat, []).append(d)
for cat, lst in by_cat.items():
    fname = re.sub(r'[^\w\-_]', '_', cat)[:40]
    with open(TUW / f"by_category_{fname}.json","w",encoding="utf-8") as f: json.dump(lst, f, ensure_ascii=False, indent=2)
log(f"By category: { {k: len(v) for k,v in by_cat.items()} }")

# Also create a clean master index with key fields only
master = []
for d in details:
    master.append({
        "title": d.get("title"),
        "slug": d.get("slug"),
        "category": d.get("initiativeCategoryName"),
        "category_id": d.get("initiativeCategoryId"),
        "scope": d.get("initiativeScopeName"),
        "scope_id": d.get("initiativeScopeId"),
        "scope_image": d.get("initiativeScopeImage"),
        "location": d.get("locationName"),
        "age": d.get("initiativeAgeName"),
        "isOpen": d.get("isOpen"),
        "isPaid": d.get("isPaid"),
        "price": d.get("price"),
        "startDate": d.get("startDate"),
        "endDate": d.get("endDate"),
        "registrationEndDate": d.get("registrationEndDate"),
        "language": d.get("language"),
        "academyType": d.get("academyType",{}).get("name") if isinstance(d.get("academyType"), dict) else d.get("academyType"),
        "logo": urljoin("https://cdn.tuwaiq.edu.sa/initiatives_admin/", d.get("outerImage") or d.get("logo") or ""),
        "description": d.get("description","")[:300],
        "goals": d.get("goals", [])[:5],
        "url": f"{BASE}/bootcamp/{d.get('slug')}/view"
    })
with open(TUW / "master_index.json","w",encoding="utf-8") as f: json.dump(master, f, ensure_ascii=False, indent=2)
log(f"Master index {len(master)}")

# ========== SATR EXHAUSTIVE ==========
log("\n=== SATR: Fetching landing, seed, banner ===")
landing = fetch_json(f"{SATR_API}/landing-guest") or {}
seed = fetch_json(f"{SATR_API}/seed") or {}
banner = fetch_json(f"{SATR_API}/banner/public?platform=WEB") or {}
with open(SATR / "landing_guest.json","w",encoding="utf-8") as f: json.dump(landing, f, ensure_ascii=False, indent=2)
with open(SATR / "seed.json","w",encoding="utf-8") as f: json.dump(seed, f, ensure_ascii=False, indent=2)
with open(SATR / "banner.json","w",encoding="utf-8") as f: json.dump(banner, f, ensure_ascii=False, indent=2)
log(f"landing paths {len(landing.get('paths',[]))} courses {len(landing.get('courses',[]))} seed langs {len(seed.get('programming_languages',[]))}")

# Paginate paths and courses
def paginate_satr(endpoint, limit=15):
    all_items = []
    offset = 0
    total = None
    while True:
        url = f"{SATR_API}/{endpoint}?limit={limit}&offset={offset}"
        j = fetch_json(url)
        if not j:
            break
        result = j.get("result_list", [])
        if total is None:
            total = j.get("total_count") or j.get("max_count") or 0
        if not result:
            break
        all_items.extend(result)
        log(f"  {endpoint} offset {offset} got {len(result)} total {len(all_items)}/{total}")
        if len(all_items) >= total:
            break
        offset += limit
        time.sleep(0.3)
    return all_items

log("\n=== SATR: Paginating paths ===")
paths_all = paginate_satr("path/path-content", 15)
with open(SATR / "paths_index.json","w",encoding="utf-8") as f: json.dump(paths_all, f, ensure_ascii=False, indent=2)
log(f"Paths total {len(paths_all)}")

log("\n=== SATR: Paginating courses ===")
courses_all = paginate_satr("course/course-content", 15)
with open(SATR / "courses_index.json","w",encoding="utf-8") as f: json.dump(courses_all, f, ensure_ascii=False, indent=2)
log(f"Courses total {len(courses_all)}")

# Fetch details for each path/course via /public
log("\n=== SATR: Fetching path details ===")
path_details = []
for p in paths_all:
    url_id = p.get("url_id") or p.get("id")
    if not url_id:
        continue
    j = fetch_json(f"{SATR_API}/path/{url_id}/public")
    if j:
        with open(SATR / "path_details" / f"{url_id}.json","w",encoding="utf-8") as f: json.dump(j, f, ensure_ascii=False, indent=2)
        path_details.append(j)
    time.sleep(0.2)
    if len(path_details) % 10 == 0:
        log(f"  path details {len(path_details)}/{len(paths_all)}")

log("\n=== SATR: Fetching course details ===")
course_details = []
for c in courses_all:
    url_id = c.get("url_id") or c.get("id")
    if not url_id:
        continue
    j = fetch_json(f"{SATR_API}/course/{url_id}/public")
    if j:
        with open(SATR / "course_details" / f"{url_id}.json","w",encoding="utf-8") as f: json.dump(j, f, ensure_ascii=False, indent=2)
        course_details.append(j)
    time.sleep(0.2)
    if len(course_details) % 20 == 0:
        log(f"  course details {len(course_details)}/{len(courses_all)}")

log(f"SATR details: paths {len(path_details)} courses {len(course_details)}")

# Create master satr organized file
# Try to also get articles/projects from landing
articles = landing.get("articles", []) if isinstance(landing, dict) else []
projects = landing.get("practical_projects", []) if isinstance(landing, dict) else []
with open(SATR / "articles.json","w",encoding="utf-8") as f: json.dump(articles, f, ensure_ascii=False, indent=2)
with open(SATR / "projects.json","w",encoding="utf-8") as f: json.dump(projects, f, ensure_ascii=False, indent=2)

# Summary
summary = {
    "tuwaiq": {
        "total_initiatives_indexed": len(all_initiatives),
        "total_details_fetched": len(details),
        "by_category": {k: len(v) for k,v in by_cat.items()},
        "categories": [c["text"] for c in cats],
        "scopes": [s["name"] for s in scopes],
        "failures": len(failures)
    },
    "satr": {
        "paths_total": len(paths_all),
        "courses_total": len(courses_all),
        "path_details": len(path_details),
        "course_details": len(course_details),
        "articles": len(articles),
        "projects": len(projects),
        "statistics": landing.get("statistics", {}) if isinstance(landing, dict) else {}
    }
}
with open(OUT / "summary.json","w",encoding="utf-8") as f: json.dump(summary, f, ensure_ascii=False, indent=2)
log(f"\n=== SUMMARY ===\n{json.dumps(summary, ensure_ascii=False, indent=2)}")

