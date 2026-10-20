"""Route 2 (Cube) restricted-user test + Route 1 (Snowflake) guardrail check. Read-only."""
import json, os, time, urllib.parse, urllib.request, urllib.error
import jwt
import snowflake.connector

API = "http://localhost:4000/cubejs-api/v1/load"
def load(token, query):
    url = f"{API}?query={urllib.parse.quote(json.dumps(query))}"
    for _ in range(40):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": token}), timeout=120))
        except urllib.error.HTTPError as e:
            return {"http": e.code, "body": e.read().decode()[:120]}
        if r.get("error") == "Continue wait":
            time.sleep(1); continue
        return r
def tok(secret=None, **claims):
    return jwt.encode({"exp": int(time.time()) + 600, **claims}, secret or os.environ["CUBEJS_API_SECRET"], algorithm="HS256")
def countries(r):
    return {x["sales.users_country"]: round(float(x["sales.total_revenue"]), 2) for x in r["data"]} if "data" in r else r
q = {"measures": ["sales.total_revenue"], "dimensions": ["sales.users_country"]}
out = {}
out["token_country_UK"] = countries(load(tok(country="UK"), q))
out["token_country_USA"] = countries(load(tok(country="USA"), q))
out["token_no_country"] = countries(load(tok(), q))
out["UK_token_asks_for_USA"] = countries(load(tok(country="UK"), {**q, "filters": [{"member": "sales.users_country", "operator": "equals", "values": ["USA"]}]}))
out["UK_token_total_no_dimension"] = round(float(load(tok(country="UK"), {"measures": ["sales.total_revenue"]})["data"][0]["sales.total_revenue"]), 2)
out["wrong_secret"] = load(tok(secret="not-the-secret", country="UK"), q)
print(json.dumps(out, indent=1))

c = snowflake.connector.connect(account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"], user=os.environ["CUBEJS_DB_USER"],
    password=os.environ["CUBEJS_DB_PASS"], warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"], role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"])
cur = c.cursor()
print("current_role:", cur.execute("select current_role()").fetchone()[0])
for sql in ["show row access policies in schema ANALYTICS_PROD.ECOMM",
            "show masking policies in schema ANALYTICS_PROD.ECOMM",
            "show schemas in database ANALYTICS_PROD"]:
    rows = cur.execute(sql).fetchall()
    print(sql, "->", len(rows), "rows", [r[1] for r in rows][:12])
print("privileges on ORDER_ITEMS for current role:",
      sorted({r[1] for r in cur.execute("show grants on table ANALYTICS_PROD.ECOMM.ORDER_ITEMS").fetchall()})[:15])
c.close()
