"""Path 3: viewer / analyst / admin groups on the sales view (Cube production mode, port 4001)."""
import json, os, time, urllib.parse, urllib.request, urllib.error, jwt
API = "http://localhost:4001/cubejs-api/v1/load"
def tok(**c): return jwt.encode({"exp": int(time.time()) + 600, **c}, os.environ["CUBEJS_API_SECRET"], algorithm="HS256")
def call(token, q):
    url = f"{API}?query={urllib.parse.quote(json.dumps(q))}"
    for _ in range(60):
        try: r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": token}), timeout=120))
        except urllib.error.HTTPError as e: return f"HTTP {e.code}: {e.read().decode()[:110]}"
        if r.get("error") == "Continue wait": time.sleep(1); continue
        if "data" not in r: return str(r.get("error"))[:110]
        return {k: round(float(v), 2) if v and v.replace('.', '', 1).replace('-', '', 1).isdigit() else v for k, v in r["data"][0].items()} if len(r["data"]) == 1 else {d.get("sales.users_country", i): round(float(list(d.values())[-1]), 2) for i, d in enumerate(r["data"])}
by_country = {"measures": ["sales.total_revenue"], "dimensions": ["sales.users_country"]}
margin = {"measures": ["sales.avg_margin"]}
email = {"measures": ["sales.total_orders"], "dimensions": ["sales.users_email"], "limit": 1}
who = {"admin (UK)": tok(groups=["admin"], country="UK"), "analyst (UK)": tok(groups=["analyst"], country="UK"),
       "viewer (UK)": tok(groups=["viewer"], country="UK"), "viewer, no country": tok(groups=["viewer"]), "no group claim": tok(country="UK")}
for name, t in who.items():
    print(f"{name:20} revenue by country -> {call(t, by_country)}")
    print(f"{'':20} avg_margin         -> {call(t, margin)}")
    print(f"{'':20} customer email     -> {str(call(t, email))[:110]}")
