"""Omni: change one metric on a throwaway branch, validate, query three dashboard-style queries before and after,
then delete the branch. Never merges. Needs the omni CLI and a profile (default: willyc). Requires pyarrow."""
import base64, json, subprocess, sys, time, io
import pyarrow as pa

PROFILE = sys.argv[1] if len(sys.argv) > 1 else "willyc"
MODEL = "f014a03c-efda-4326-8e20-476e3d6882d3"   # Will's Snowflake Connection
TOPIC = "analytics_prod_ecomm__sales"
OI = "analytics_prod_ecomm__sales__order_items"
US = "analytics_prod_ecomm__sales__users"
def omni(*a):
    p = subprocess.run(["omni", "-p", PROFILE, *a], capture_output=True, text=True)
    return p.stdout
def run_query(fields, branch=None):
    body = {"query": {"modelId": MODEL, "table": OI, "fields": fields, "limit": 1000,
                      "join_paths_from_topic_name": TOPIC}}
    if branch: body["branchId"] = branch
    out = omni("query", "run", "--body", json.dumps(body))
    for line in out.splitlines():
        if line.startswith('{"job_id"'):
            d = json.loads(line); b = base64.b64decode(d["result"])
            t = pa.ipc.open_stream(io.BytesIO(b)).read_all().to_pandas() if False else pa.ipc.open_stream(io.BytesIO(b)).read_all()
            return t.to_pydict(), d["summary"].get("display_sql", "")
    raise RuntimeError(out[:300])
def total(d, field): return round(sum(float(x) for x in d[field]), 2)

TILES = {"kpi": [f"{OI}.total_revenue"],
         "by_country": [f"{US}.country", f"{OI}.total_revenue"],
         "by_status": [f"{OI}.status", f"{OI}.total_revenue"]}
def snap(branch=None):
    return {k: total(run_query(f, branch)[0], f"{OI}.total_revenue") for k, f in TILES.items()}

t0 = time.time()
before = snap(); print("before", before)
topic = json.load(open("/dev/stdin")) if False else None
y = json.loads(omni("models", "yaml-get", MODEL, "--filename", f"{TOPIC}.topic"))["files"][f"{TOPIC}.topic"]
old = f"      total_revenue:\n        sql: SUM(${{{OI}.sale_price}})\n"
assert y.count(old) == 1, "total_revenue block not found"
new = (f"      total_revenue:\n        sql: SUM(CASE WHEN ${{{OI}.status}} NOT IN ('Cancelled','Returned') "
       f"THEN ${{{OI}.sale_price}} ELSE 0 END)\n")
y2 = y.replace(old, new)
t_branch = time.time()
br = json.loads(omni("models", "create-branch", MODEL, "--name", f"claude-metric-test-{int(t0)}"))["model"]["id"]
print("branch", br, "created in", round(time.time() - t_branch, 1), "s")
t_edit = time.time()
res = omni("models", "yaml-create", MODEL, "--body", json.dumps({"fileName": f"{TOPIC}.topic", "yaml": y2,
        "mode": "extension", "branchId": br, "commitMessage": "Exclude Cancelled and Returned from total_revenue"}))
print("yaml-create:", res.strip()[:120])
val = omni("models", "validate", MODEL, "--branchid", br)
errs = [i for i in json.loads(val) if not i.get("is_warning")] if val.strip().startswith("[") else val[:200]
print("validate errors:", errs if errs else "none")
after = snap(br); print("after ", after)
elapsed = round(time.time() - t_edit, 1)
print("edit-to-verified seconds:", elapsed, "| files edited: 1 | blocks edited: 1 | tiles changed:", sum(after[k] != before[k] for k in before), "of 3")
print("main unchanged:", snap() == before)
print("delete branch:", omni("models", "delete-branch", MODEL, f"claude-metric-test-{int(t0)}").strip()[:100])
