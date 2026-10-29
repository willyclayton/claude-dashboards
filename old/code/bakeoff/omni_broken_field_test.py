"""Omni: what happens when a measure points at a column that doesn't exist? Throwaway branch, never merged, deleted after."""
import json, subprocess, sys, time
P = sys.argv[1] if len(sys.argv) > 1 else "willyc"
M = "f014a03c-efda-4326-8e20-476e3d6882d3"; T = "analytics_prod_ecomm__sales"; OI = "analytics_prod_ecomm__sales__order_items"
def omni(*a): return subprocess.run(["omni", "-p", P, *a], capture_output=True, text=True).stdout
y = json.loads(omni("models", "yaml-get", M, "--filename", f"{T}.topic"))["files"][f"{T}.topic"]
anchor = "      total_revenue:\n"; assert y.count(anchor) == 1
bad = (f"      broken_metric:\n        sql: SUM(${{{OI}.sale_price_renamed}})\n        description: points at a field that does not exist\n\n")
name = f"claude-broken-field-{int(time.time())}"
br = json.loads(omni("models", "create-branch", M, "--name", name))["model"]["id"]
try:
    t = time.time()
    print("yaml-create:", json.loads(omni("models", "yaml-create", M, "--body", json.dumps({"fileName": f"{T}.topic", "yaml": y.replace(anchor, bad + anchor),
          "mode": "extension", "branchId": br, "commitMessage": "add broken metric"})))) 
    val = omni("models", "validate", M, "--branchid", br)
    issues = json.loads(val) if val.strip().startswith("[") else val
    errs = [i for i in issues if not i.get("is_warning")] if isinstance(issues, list) else issues
    print("seconds to validate:", round(time.time() - t, 1))
    print("validation errors:", json.dumps(errs)[:600] if errs else "none")
    q = omni("query", "run", "--body", json.dumps({"query": {"modelId": M, "table": OI, "fields": [f"{OI}.broken_metric"], "limit": 1, "join_paths_from_topic_name": T}, "branchId": br}))
    print("querying the broken metric:", q.strip()[:300])
    print("main still healthy:", "job_id" in omni("query", "run", "--body", json.dumps({"query": {"modelId": M, "table": OI, "fields": [f"{OI}.total_orders"], "limit": 1, "join_paths_from_topic_name": T}})))
finally:
    print("delete branch:", omni("models", "delete-branch", M, name).strip()[:60])
