"""Runs Q1-Q8 against the Cube API and compares with the independent Snowflake answer key (key.json).
Usage: set -a && . ./.env && set +a && .venv/bin/python tests/run_questions.py"""
import json, os, sys, time
import httpx, jwt

URL = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
SECRET = os.environ["CUBEJS_API_SECRET"]
KEY = json.load(open(os.path.join(os.path.dirname(__file__), "key.json")))

def load(q):
    h = {"Authorization": jwt.encode({"exp": int(time.time()) + 300}, SECRET, algorithm="HS256")}
    for _ in range(60):
        r = httpx.get(f"{URL}/load", headers=h, params={"query": json.dumps(q)}, timeout=120).json()
        if r.get("error") == "Continue wait":
            time.sleep(1); continue
        if "data" not in r: raise RuntimeError(r)
        return r["data"]

def one(m): return float(load({"measures": [m]})[0][m])

year = KEY["q2_year"]
got = {
 "q1_net_revenue": one("sales.net_revenue"),
 "q2_orders": float(load({"measures": ["sales.orders"], "timeDimensions": [{"dimension": "sales.created_at", "dateRange": [f"{year}-01-01", f"{year}-12-31"]}]})[0]["sales.orders"]),
 "q3_aov": one("sales.avg_order_value"),
 "q4_margin_pct": one("sales.margin_pct"),
 "q5_return_rate": one("sales.return_rate"),
 "q7_repeat_share": one("sales.repeat_share"),
}
top = load({"measures": ["sales.net_revenue"], "dimensions": ["sales.category"], "order": {"sales.net_revenue": "desc"}, "limit": 5})
got["q6_top5"] = "; ".join(f"{r['sales.category']} {float(r['sales.net_revenue']):.2f}" for r in top)
src = load({"measures": ["sales.net_revenue"], "dimensions": ["sales.traffic_source"], "order": {"sales.net_revenue": "desc"}, "limit": 2})
got["q8_top_sources"] = "; ".join(f"{r['sales.traffic_source']} {float(r['sales.net_revenue']):.2f}" for r in src)

bad = 0
for k, v in got.items():
    exp = KEY[k]
    ok = (abs(v - exp) <= 0.006 if isinstance(v, float) else v == exp)  # expected answers are given to 2 decimals
    bad += not ok
    print(("PASS" if ok else "FAIL"), k, "cube=", v, "snowflake=", exp)
sys.exit(1 if bad else 0)
