"""Build out and break the Cube model on purpose. Each experiment patches model YAML, waits for the hot reload,
queries, records the result and time, then reverts the file. Run from Plan 1/cube-claude-lab with .env loaded.
Usage: python ../bakeoff/cube_buildout_tests.py [E1,E2,...]
Note: E1-E4 were kept in the model afterwards, so rerunning them collides on names; E5-E7 can be rerun.
E5 needs `group: "*"` (not `role`) in Cube 1.8.8."""
import json, os, shutil, sys, time, urllib.parse, urllib.request, urllib.error, jwt

API = "http://localhost:4000/cubejs-api/v1"
OI, SALES = "model/cubes/order_items.yml", "model/views/sales.yml"
def tok(**c): return jwt.encode({"exp": int(time.time()) + 600, **c}, os.environ["CUBEJS_API_SECRET"], algorithm="HS256")
def load(q, token=None, path="load"):
    url = f"{API}/{path}?query={urllib.parse.quote(json.dumps(q))}"
    for _ in range(90):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": token or tok()}), timeout=120))
        except urllib.error.HTTPError as e:
            return {"error": e.read().decode()[:300], "http": e.code}
        if r.get("error") == "Continue wait": time.sleep(0.5); continue
        return r
def patch(path, old, new):
    s = open(path).read(); assert s.count(old) == 1, (path, old[:40]); open(path, "w").write(s.replace(old, new))
def settle(q, ok, limit=45):
    """Poll until ok(result) is true (hot reload done) or the limit passes; return (seconds, last result)."""
    t = time.time(); r = None
    while time.time() - t < limit:
        r = load(q)
        if ok(r): return round(time.time() - t, 1), r
        time.sleep(1)
    return round(time.time() - t, 1), r
def val(r, m): return float(r["data"][0][m]) if r and "data" in r and r["data"] else None
def bak(p): shutil.copy(p, p + ".bak")
def restore(p): shutil.move(p + ".bak", p)
MEAS = "      - name: total_items_sold\n"   # anchor: first measure in order_items
WIN = ["2026-04-01", "2026-09-30"]
RES = {}

def E1():  # brand-new metric from scratch (not already in the model)
    exp = val(load({"measures": ["sales.total_revenue"], "filters": [{"member": "sales.status", "operator": "equals", "values": ["Returned"]}]}), "sales.total_revenue")
    bak(OI)
    try:
        patch(OI, MEAS, '''      - name: returned_revenue
        sql: "{sale_price}"
        type: sum
        filters:
          - sql: "{CUBE}.STATUS = 'Returned'"
        description: "Revenue on items that were returned."
        meta:
          synonyms: [refunded revenue, returns value]

''' + MEAS)
        s, r = settle({"measures": ["sales.returned_revenue"]}, lambda r: r and "data" in r)
        return {"seconds_edit_to_queryable": s, "value": val(r, "sales.returned_revenue"), "expected_via_status_filter": exp,
                "match": abs(val(r, "sales.returned_revenue") - exp) < 1e-6}
    finally: restore(OI)

def E2():  # exclusion rule built into a measure
    bak(OI)
    try:
        patch(OI, MEAS, '''      - name: net_revenue
        sql: "{sale_price}"
        type: sum
        filters:
          - sql: "{CUBE}.STATUS NOT IN ('Cancelled','Returned')"
        description: "Revenue excluding Cancelled and Returned orders."

''' + MEAS)
        q = {"measures": ["sales.net_revenue"], "timeDimensions": [{"dimension": "sales.created_at", "dateRange": WIN}]}
        s, r = settle(q, lambda r: r and "data" in r)
        return {"seconds_edit_to_queryable": s, "net_revenue_apr_sep": val(r, "sales.net_revenue"), "answer_key_Q4": 1319165.6198219657}
    finally: restore(OI)

def E3():  # rolling window
    bak(OI)
    try:
        patch(OI, MEAS, '''      - name: rolling_30d_revenue
        sql: "{sale_price}"
        type: sum
        rolling_window:
          trailing: 30 day
        description: "Revenue over the trailing 30 days."

''' + MEAS)
        q = {"measures": ["sales.rolling_30d_revenue"], "timeDimensions": [{"dimension": "sales.created_at", "granularity": "day", "dateRange": ["2026-09-25", "2026-09-30"]}]}
        s, r = settle(q, lambda r: r and "data" in r)
        return {"seconds_edit_to_queryable": s, "rows": [(d["sales.created_at.day"][:10], round(float(d["sales.rolling_30d_revenue"] or 0), 2)) for d in r["data"]]}
    finally: restore(OI)

def E4():  # segment
    bak(OI)
    try:
        s_ = open(OI).read()
        assert "    segments:" not in s_
        patch(OI, "    measures:\n", '''    segments:
      - name: complete_only
        sql: "{CUBE}.STATUS = 'Complete'"

    measures:
''')
        q = {"measures": ["sales.total_revenue"], "segments": ["sales.complete_only"]}
        s, r = settle(q, lambda r: r and "data" in r)
        comp = val(load({"measures": ["sales.total_revenue_completed"]}), "sales.total_revenue_completed")
        return {"seconds_edit_to_queryable": s, "segment_revenue": val(r, "sales.total_revenue"), "total_revenue_completed": comp}
    finally: restore(OI)

def E5():  # native access policy on the view (row level by country claim)
    bak(SALES)
    try:
        patch(SALES, "    cubes:\n", '''    access_policy:
      - group: "*"
        row_level:
          filters:
            - member: users_country
              operator: equals
              values: ["{ securityContext.country }"]

    cubes:
''')
        q = {"measures": ["sales.total_revenue"], "dimensions": ["sales.users_country"]}
        out = {}
        time.sleep(4)
        for name, t in [("country=UK", tok(country="UK")), ("no country claim", tok()), ("country=USA", tok(country="USA"))]:
            r = load(q, t)
            out[name] = ({d["sales.users_country"]: round(float(d["sales.total_revenue"]), 2) for d in r["data"]} if "data" in r else r.get("error", r)[:160] if isinstance(r.get("error", ""), str) else r)
        return out
    finally: restore(SALES)

def E6():  # upstream column breaks: bad column in a measure
    bak(OI)
    try:
        patch(OI, MEAS, '''      - name: broken_metric
        sql: SALE_PRICE_RENAMED
        type: sum

''' + MEAS)
        t = time.time(); meta = load({}, path="meta")  # does Cube reject the model?
        r = load({"measures": ["sales.broken_metric"]})
        ok_other = load({"measures": ["sales.total_orders"]})
        return {"meta_endpoint_ok": isinstance(meta, dict) and "cubes" in meta,
                "other_metrics_still_work": "data" in ok_other,
                "broken_query_error": (r.get("error") or "")[:220], "seconds_to_see_error": round(time.time() - t, 1)}
    finally: restore(OI)

def E7():  # pre-aggregation (needs Cube Store, which ships in the image)
    bak(OI)
    try:
        patch(OI, "    measures:\n", '''    pre_aggregations:
      - name: rev_by_day_status
        measures: [total_revenue, total_orders]
        dimensions: [status]
        time_dimension: created_at
        granularity: day
        refresh_key:
          every: 1 hour

    measures:
''')
        q = {"measures": ["sales.total_revenue"], "dimensions": ["sales.status"], "timeDimensions": [{"dimension": "sales.created_at", "granularity": "month", "dateRange": WIN}]}
        t = time.time(); r = None
        for _ in range(60):
            r = load(q)
            if r and "usedPreAggregations" in r and r["usedPreAggregations"]: break
            time.sleep(3)
        warm = []
        for _ in range(3):
            t1 = time.time(); load(q); warm.append(round(time.time() - t1, 3))
        return {"seconds_until_preagg_used": round(time.time() - t, 1), "used": list((r or {}).get("usedPreAggregations", {}).keys()),
                "error": (r or {}).get("error"), "repeat_query_s": warm}
    finally: restore(OI)

if __name__ == "__main__":
    pick = sys.argv[1].split(",") if len(sys.argv) > 1 else ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
    for name in pick:
        try: RES[name] = globals()[name]()
        except Exception as e: RES[name] = {"exception": f"{type(e).__name__}: {e}"[:300]}
        print(name, json.dumps(RES[name])[:600], flush=True)
        time.sleep(6)
    json.dump(RES, open("../bakeoff/results/cube_buildout_tests.json", "w"), indent=1)
