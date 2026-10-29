"""Change one metric (total_revenue) once in Cube YAML; confirm three dashboard-style queries all change. Reverts after."""
import json, subprocess, time, urllib.parse, urllib.request, jwt, os, shutil
API="http://localhost:4000/cubejs-api/v1/load"
tok=jwt.encode({"exp":int(time.time())+600},os.environ["CUBEJS_API_SECRET"],algorithm="HS256")
def load(q):
    url=f"{API}?query={urllib.parse.quote(json.dumps(q))}"
    for _ in range(60):
        r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"Authorization":tok}),timeout=120))
        if r.get("error")!="Continue wait": return r
        time.sleep(1)
TILES={"tile_kpi":{"measures":["sales.total_revenue"]},
       "tile_by_month":{"measures":["sales.total_revenue"],"timeDimensions":[{"dimension":"sales.created_at","granularity":"year","dateRange":["2026-01-01","2026-12-31"]}]},
       "tile_by_country":{"measures":["sales.total_revenue"],"dimensions":["sales.users_country"]}}
def snap():
    return {k:sum(float(r["sales.total_revenue"]) for r in load(q)["data"]) for k,q in TILES.items()}
P="model/cubes/order_items.yml"; bak=P+".bak"
before=snap(); print("before",before)
shutil.copy(P,bak); s=open(P).read()
old='''      - name: total_revenue
        sql: "{sale_price}"
        type: sum
'''
assert s.count(old)==1
t0=time.time()
s=s.replace(old,old+'''        filters:
          - sql: "{CUBE}.STATUS NOT IN ('Cancelled','Returned')"
''')
open(P,"w").write(s)          # the ONE edit
after=None
for _ in range(60):
    time.sleep(1); a=snap()
    if a!=before: after=a; break
elapsed=round(time.time()-t0,1)
print("after",after); print("edit-to-verified seconds",elapsed,"| files edited: 1 | blocks edited: 1 | tiles changed:",sum(after[k]!=before[k] for k in before),"of 3")
shutil.move(bak,P)            # revert
time.sleep(6); print("reverted",snap()==before)
