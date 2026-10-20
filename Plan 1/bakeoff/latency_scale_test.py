"""Latency (median of 5), 20-user concurrency, token minting, and traceability timing. Read-only."""
import json, os, statistics as st, subprocess, time, urllib.parse, urllib.request, jwt, snowflake.connector
from concurrent.futures import ThreadPoolExecutor
API = "http://localhost:4000/cubejs-api/v1/load"
def tok(**c): return jwt.encode({"exp": int(time.time()) + 600, **c}, os.environ["CUBEJS_API_SECRET"], algorithm="HS256")
def cube(q, token):
    url = f"{API}?query={urllib.parse.quote(json.dumps(q))}"; t = time.time()
    while True:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": token}), timeout=120))
        if r.get("error") != "Continue wait": return time.time() - t
        time.sleep(0.5)
Q = {"measures": ["sales.total_revenue"], "dimensions": ["sales.users_country"],
     "timeDimensions": [{"dimension": "sales.created_at", "dateRange": ["2026-04-01", "2026-09-30"]}]}
T = tok()
out = {}
cold = []
for i in range(5):  # distinct date ranges defeat Cube's cache
    q = json.loads(json.dumps(Q)); q["timeDimensions"][0]["dateRange"] = ["2026-04-01", f"2026-09-{20+i}"]
    cold.append(cube(q, T))
out["cube_cold_median_s"] = round(st.median(cold), 3)
out["cube_cached_median_s"] = round(st.median([cube(Q, T) for _ in range(5)]), 3)
c = snowflake.connector.connect(account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"], user=os.environ["CUBEJS_DB_USER"], password=os.environ["CUBEJS_DB_PASS"], warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"], role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"])
cur = c.cursor(); cur.execute("alter session set use_cached_result=false")
sql = "SELECT u.COUNTRY, SUM(o.SALE_PRICE*0.5) FROM ANALYTICS_PROD.ECOMM.ORDER_ITEMS o JOIN ANALYTICS_PROD.ECOMM.USERS u ON u.ID=o.USER_ID WHERE o.CREATED_AT >= '2026-04-01' AND o.CREATED_AT < '2026-10-01' AND (o.STATUS NOT IN ('Cancelled','Returned') OR o.STATUS IS NULL) GROUP BY 1"
ts = []
for _ in range(5):
    t = time.time(); cur.execute(sql).fetchall(); ts.append(time.time() - t)
out["snowflake_direct_no_result_cache_median_s"] = round(st.median(ts), 3)
cur.execute("alter session set use_cached_result=true"); ts = []
for _ in range(5):
    t = time.time(); cur.execute(sql).fetchall(); ts.append(time.time() - t)
out["snowflake_direct_result_cache_median_s"] = round(st.median(ts), 3)
# 20 concurrent users, each with own token (country alternates)
tokens = [tok(country=["USA", "UK"][i % 2], user=f"u{i}") for i in range(20)]
t = time.time(); toks = [tok(country="USA", user=f"u{i}") for i in range(100)]; out["mint_100_tokens_s"] = round(time.time() - t, 4)
with ThreadPoolExecutor(20) as ex:
    t = time.time(); lat = list(ex.map(lambda tk: cube(Q, tk), tokens)); wall = time.time() - t
out["cube_20_concurrent_users"] = {"wall_s": round(wall, 2), "p50_s": round(st.median(lat), 2), "max_s": round(max(lat), 2)}
# traceability: find who/when changed the ai_context line in Git
t = time.time()
log = subprocess.run(["git", "log", "--format=%h|%an|%ad|%s", "--date=short", "-S", "ai_context", "--", "Plan 1/cube-claude-lab/model/views/sales.yml"], capture_output=True, text=True, cwd="../..").stdout.strip().splitlines()
out["git_trace_seconds"] = round(time.time() - t, 3); out["git_trace_result"] = log[-1] if log else None
print(json.dumps(out, indent=1))
