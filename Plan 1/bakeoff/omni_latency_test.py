"""Omni: query latency (median of 5, cache-busted) and 10 concurrent queries.
Not done: a restricted-user test. Omni docs say only an Organization API key can impersonate (userId); our CLI login is an OAuth user token."""
import base64, json, os, statistics as st, subprocess, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
P = sys.argv[1] if len(sys.argv) > 1 else "willyc"
M = "f014a03c-efda-4326-8e20-476e3d6882d3"; OI = "analytics_prod_ecomm__sales__order_items"; US = "analytics_prod_ecomm__sales__users"
def run(limit):
    body = {"query": {"modelId": M, "table": OI, "fields": [f"{US}.country", f"{OI}.total_revenue"], "limit": limit,
            "join_paths_from_topic_name": "analytics_prod_ecomm__sales"}}
    t = time.time(); out = subprocess.run(["omni", "-p", P, "query", "run", "--body", json.dumps(body)], capture_output=True, text=True).stdout
    dt = time.time() - t; cache = "?"
    for l in out.splitlines():
        if l.startswith('{"job_id"'): cache = json.loads(l)["summary"].get("cache_type")
    return dt, cache
res = [run(500 + i) for i in range(5)]
print("omni_query_median_s", round(st.median(r[0] for r in res), 2), "cache types", [r[1] for r in res])
with ThreadPoolExecutor(10) as ex:
    t = time.time(); r = list(ex.map(run, range(600, 610))); wall = time.time() - t
print("omni_10_concurrent wall_s", round(wall, 2), "p50", round(st.median(x[0] for x in r), 2), "max", round(max(x[0] for x in r), 2))
