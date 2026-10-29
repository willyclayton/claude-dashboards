"""Same restricted-user checks against Cube in production mode (CUBEJS_DEV_MODE=false), port 4001."""
import json, os, time, urllib.parse, urllib.request, urllib.error, jwt
API="http://localhost:4001/cubejs-api/v1/load"
q={"measures":["sales.total_revenue"],"dimensions":["sales.users_country"]}
def call(token):
    url=f"{API}?query={urllib.parse.quote(json.dumps(q))}"
    h={"Authorization":token} if token else {}
    for _ in range(60):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=120))
        except urllib.error.HTTPError as e:
            return f"HTTP {e.code}: {e.read().decode()[:80]}"
        if r.get("error")=="Continue wait": time.sleep(1); continue
        return {x["sales.users_country"]:round(float(x["sales.total_revenue"]),2) for x in r["data"]}
t=lambda secret=os.environ["CUBEJS_API_SECRET"],**c: jwt.encode({"exp":int(time.time())+600,**c},secret,algorithm="HS256")
for name,tok in [("no token",None),("forged token (wrong secret)",t("nope",country="UK")),
                 ("valid token, country=UK",t(country="UK")),("valid token, no country claim",t())]:
    print(f"{name:32} ->",call(tok))
