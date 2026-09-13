#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, time, pathlib
from scrapling.fetchers import Fetcher

SATR_API = "https://api.satr.codes"
OUT = pathlib.Path("/home/bvnks/scraping_agent/output/exhaustive/satr")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "path_details").mkdir(parents=True, exist_ok=True)
(OUT / "course_details").mkdir(parents=True, exist_ok=True)

def log(m): print(m, flush=True)
def fetch_json(url):
    try:
        r = Fetcher.get(url, impersonate="chrome", stealthy_headers=True)
        if r.status == 200:
            try:
                return r.json()
            except:
                return None
    except Exception as e:
        log(f"err {url} {e}")
    return None

# Paginate courses if not already done
# Check existing paths_index
paths_index = json.loads((OUT / "paths_index.json").read_text(encoding="utf-8")) if (OUT / "paths_index.json").exists() else None
if paths_index:
    log(f"Existing paths {len(paths_index)}")
else:
    log("No paths_index, fetching")
    # This shouldn't happen, but fetch
    all_paths=[]
    offset=0
    limit=15
    while True:
        j = fetch_json(f"{SATR_API}/path/path-content?limit={limit}&offset={offset}")
        if not j or not j.get("result_list"):
            break
        all_paths.extend(j["result_list"])
        log(f"paths offset {offset} got {len(j['result_list'])} total {len(all_paths)}")
        if len(all_paths) >= j.get("total_count", 999):
            break
        offset+=limit
        time.sleep(0.3)
    with open(OUT / "paths_index.json","w",encoding="utf-8") as f: json.dump(all_paths, f, ensure_ascii=False, indent=2)
    paths_index = all_paths

# Now courses
courses_path = OUT / "courses_index.json"
if courses_path.exists():
    log(f"courses_index exists? checking size")
    try:
        c = json.loads(courses_path.read_text(encoding="utf-8"))
        log(f"existing courses {len(c)}")
        if len(c) >= 160:
            log("courses already complete, skipping pagination")
            courses_all = c
        else:
            raise ValueError("incomplete")
    except Exception as e:
        log(f"need to refetch courses: {e}")
        courses_all = None
else:
    courses_all = None

if not courses_all or len(courses_all) < 160:
    log("Fetching satr courses pagination...")
    all_courses=[]
    offset=0
    limit=15
    total=None
    while True:
        j = fetch_json(f"{SATR_API}/course/course-content?limit={limit}&offset={offset}")
        if not j:
            log(f"offset {offset} no data")
            break
        result = j.get("result_list", [])
        if total is None:
            total = j.get("total_count") or 0
            log(f"total {total}")
        if not result:
            log(f"offset {offset} empty")
            break
        all_courses.extend(result)
        log(f"offset {offset} got {len(result)} total {len(all_courses)}/{total}")
        if len(all_courses) >= total:
            break
        offset+=limit
        time.sleep(0.3)
    with open(courses_path,"w",encoding="utf-8") as f: json.dump(all_courses, f, ensure_ascii=False, indent=2)
    courses_all = all_courses
    log(f"Saved courses {len(all_courses)}")

# Now fetch details for paths
log(f"\nFetching path details for {len(paths_index)} paths")
for idx, p in enumerate(paths_index, 1):
    url_id = p.get("url_id") or p.get("id")
    out_file = OUT / "path_details" / f"{url_id}.json"
    if out_file.exists() and out_file.stat().st_size > 100:
        continue
    j = fetch_json(f"{SATR_API}/path/{url_id}/public")
    if j:
        with open(out_file,"w",encoding="utf-8") as f: json.dump(j, f, ensure_ascii=False, indent=2)
    if idx % 10 == 0:
        log(f"  paths {idx}/{len(paths_index)}")
    time.sleep(0.2)

# Fetch course details
log(f"\nFetching course details for {len(courses_all)} courses")
for idx, c in enumerate(courses_all, 1):
    url_id = c.get("url_id") or c.get("id")
    out_file = OUT / "course_details" / f"{url_id}.json"
    if out_file.exists() and out_file.stat().st_size > 100:
        continue
    j = fetch_json(f"{SATR_API}/course/{url_id}/public")
    if j:
        with open(out_file,"w",encoding="utf-8") as f: json.dump(j, f, ensure_ascii=False, indent=2)
    if idx % 20 == 0:
        log(f"  courses {idx}/{len(courses_all)}")
    time.sleep(0.2)

# Verify counts
import pathlib as pl
log(f"Done. Path details {len(list((OUT / 'path_details').glob('*.json')))} Course details {len(list((OUT / 'course_details').glob('*.json')))}")
# Create summary snippet
import json as js
summary = {
    "paths_total": len(paths_index),
    "courses_total": len(courses_all),
    "path_details": len(list((OUT / "path_details").glob("*.json"))),
    "course_details": len(list((OUT / "course_details").glob("*.json")))
}
print(js.dumps(summary, ensure_ascii=False, indent=2))
