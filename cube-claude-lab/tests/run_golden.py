import json
import os
import sys
import time
import urllib.parse
import urllib.request

import jwt
import snowflake.connector

API = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
TOKEN = jwt.encode(
    {"exp": int(time.time()) + 3600}, os.environ["CUBEJS_API_SECRET"], algorithm="HS256"
)

# Ground truth is hand-written SQL against the raw tables. The semantic layer's
# sale_price is SALE_PRICE * 0.5, so revenue checks apply the same factor here.
T = "ANALYTICS_PROD.ECOMM"


def cube(query):
    url = f"{API}/load?query={urllib.parse.quote(json.dumps(query))}"
    for _ in range(60):
        req = urllib.request.Request(url, headers={"Authorization": TOKEN})
        body = json.load(urllib.request.urlopen(req, timeout=120))
        if body.get("error") == "Continue wait":
            time.sleep(2)
            continue
        return body["data"]
    raise RuntimeError("Cube kept answering 'Continue wait'")


_conn = None


def sf(sql):
    global _conn
    if _conn is None:
        _conn = snowflake.connector.connect(
            account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"],
            user=os.environ["CUBEJS_DB_USER"],
            private_key_file=os.path.join(
                os.path.dirname(__file__), "..", "secrets", "snowflake_key.p8"
            ),
            warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"],
            role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"],
        )
    return _conn.cursor().execute(sql).fetchall()


def scalar(member):
    return lambda rows: float(rows[0][member])


def grouped(dim, member):
    return lambda rows: {r[dim]: float(r[member]) for r in rows}


CASES = [
    {
        "name": "total items sold",
        "cube": {"measures": ["sales.total_items_sold"]},
        "sql": f"SELECT COUNT(*) FROM {T}.ORDER_ITEMS",
        "cube_value": scalar("sales.total_items_sold"),
        "sql_value": lambda r: float(r[0][0]),
    },
    {
        "name": "total orders (distinct)",
        "cube": {"measures": ["sales.total_orders"]},
        "sql": f"SELECT COUNT(DISTINCT ORDER_ID) FROM {T}.ORDER_ITEMS",
        "cube_value": scalar("sales.total_orders"),
        "sql_value": lambda r: float(r[0][0]),
    },
    {
        "name": "completed revenue (sale_price is SALE_PRICE * 0.5)",
        "cube": {"measures": ["sales.total_revenue_completed"]},
        "sql": f"SELECT SUM(SALE_PRICE * 0.5) FROM {T}.ORDER_ITEMS WHERE STATUS = 'Complete'",
        "cube_value": scalar("sales.total_revenue_completed"),
        "sql_value": lambda r: float(r[0][0]),
    },
    {
        "name": "items by status",
        "cube": {"measures": ["sales.total_items_sold"], "dimensions": ["sales.status"]},
        "sql": f"SELECT STATUS, COUNT(*) FROM {T}.ORDER_ITEMS GROUP BY STATUS",
        "cube_value": grouped("sales.status", "sales.total_items_sold"),
        "sql_value": lambda r: {s: float(n) for s, n in r},
    },
    {
        "name": "revenue by customer country (join fan-out check)",
        "cube": {"measures": ["sales.total_revenue"], "dimensions": ["sales.users_country"]},
        "sql": (
            f"SELECT u.COUNTRY, SUM(o.SALE_PRICE * 0.5) FROM {T}.ORDER_ITEMS o "
            f"JOIN {T}.USERS u ON u.ID = o.USER_ID GROUP BY u.COUNTRY"
        ),
        "cube_value": grouped("sales.users_country", "sales.total_revenue"),
        "sql_value": lambda r: {c: float(v) for c, v in r},
    },
    {
        "name": "return rate (percent, 0-100)",
        "cube": {"measures": ["sales.return_rate"]},
        "sql": f"SELECT 100.0 * COUNT_IF(IS_RETURNED) / COUNT(*) FROM {T}.ORDER_ITEMS",
        "cube_value": scalar("sales.return_rate"),
        "sql_value": lambda r: float(r[0][0]),
    },
]


def close(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    return abs(a - b) <= 1e-4 * max(1.0, abs(b))


failed = 0
for case in CASES:
    got = case["cube_value"](cube(case["cube"]))
    want = case["sql_value"](sf(case["sql"]))
    ok = close(got, want)
    print(f"{'PASS' if ok else 'FAIL'}  {case['name']}")
    if not ok:
        failed += 1
        print(f"      cube: {got}\n      sql:  {want}")

sys.exit(1 if failed else 0)
