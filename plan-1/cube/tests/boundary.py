"""Boundary checks: what an end user (anyone with a Cube token) can and cannot reach."""
import json, os, time, httpx, jwt
URL = "http://localhost:4000/cubejs-api/v1"
H = {"Authorization": jwt.encode({"exp": int(time.time()) + 300}, os.environ["CUBEJS_API_SECRET"], algorithm="HS256")}
def get(p, q=None):
    r = httpx.get(URL + p, headers=H, params={"query": json.dumps(q)} if q else None, timeout=60)
    return r.status_code, r.text[:140]
meta = httpx.get(URL + "/meta", headers=H).json()["cubes"]
names = {m["name"] for c in meta for m in c["measures"] + c["dimensions"]}
print("cubes visible:", [c["name"] for c in meta])
pii = [n for n in names if any(w in n.lower() for w in ["email", "first_name", "last_name", "gender", "zip", "latitude", "longitude", "city", "state", "age"]) and "age_band" not in n]
print("PII members in meta:", pii or "none")
for label, q in [("raw cube order_items.net_revenue", {"measures": ["order_items.net_revenue"]}),
                 ("customers.id (non-public cube)", {"dimensions": ["customers.id"]}),
                 ("sales.email (does not exist)", {"dimensions": ["sales.email"]}),
                 ("no token", None)]:
    if label == "no token":
        r = httpx.get(URL + "/meta", timeout=30); print(label, "->", r.status_code)
    else:
        print(label, "->", *get("/load", q))
