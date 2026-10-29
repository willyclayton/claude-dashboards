"""Omni Content Validator: create a scratch dashboard on the Sales topic, rename a measure it uses on a throwaway branch,
and ask the validator what would break. Nothing is merged; the branch is deleted and the dashboard moved to Trash."""
import json, subprocess, sys, time
P = sys.argv[1] if len(sys.argv) > 1 else "willyc"
M = "f014a03c-efda-4326-8e20-476e3d6882d3"; T = "analytics_prod_ecomm__sales"; OI = "analytics_prod_ecomm__sales__order_items"
FIELD = "total_revenue"
def omni(*a): return subprocess.run(["omni", "-p", P, *a], capture_output=True, text=True).stdout
doc = None; name = f"claude-impact-{int(time.time())}"
try:
    body = {"modelId": M, "name": "ZZ claude validator test (safe to delete)", "queryPresentations": [{
        "name": "Revenue by status", "topicName": T, "prefersChart": False, "visType": "basic",
        "fields": [f"{OI}.status", f"{OI}.{FIELD}"],
        "query": {"table": OI, "fields": [f"{OI}.status", f"{OI}.{FIELD}"], "limit": 20, "join_paths_from_topic_name": T}, "config": {}}]}
    doc = json.loads(omni("documents", "create", "--body", json.dumps(body)))
    ident = doc.get("identifier") or doc.get("dashboard", {}).get("identifier") or doc.get("document", {}).get("identifier") or (doc.get("dashboardId")); print("created:", json.dumps(doc)[:200])
    base = json.loads(omni("models", "content-validator-get", M, "--include-personal-folders", "true", "--find-type", "FIELD", "--find", f"{OI}.{FIELD}"))
    print("documents using the field on main:", [c.get("name") for c in base.get("content", [])])
    y = json.loads(omni("models", "yaml-get", M, "--filename", f"{T}.topic"))["files"][f"{T}.topic"]
    old = f"      {FIELD}:\n"; assert y.count(old) == 1
    t0 = time.time(); br = json.loads(omni("models", "create-branch", M, "--name", name))["model"]["id"]
    omni("models", "yaml-create", M, "--body", json.dumps({"fileName": f"{T}.topic", "yaml": y.replace(old, f"      {FIELD}_renamed:\n"), "mode": "extension", "branchId": br, "commitMessage": "rename"}))
    r = json.loads(omni("models", "content-validator-get", M, "--branch-id", br, "--include-personal-folders", "true", "--content-filter-mode", "ALL"))
    print("documents the validator evaluated on the branch:", [(c.get("name"), len([i for q in c.get("queries_and_issues", []) for i in q.get("issues", [])])) for c in r.get("content", [])])
    r["content"] = [c for c in r.get("content", []) if any(q.get("issues") for q in c.get("queries_and_issues", []))]
    print("seconds from rename to impact report: %.1f" % (time.time() - t0))
    for c in r.get("content", []):
        print("BROKEN:", json.dumps({k: c.get(k) for k in ("name", "identifier", "type")}), "| issues:", json.dumps({k: v for k, v in c.items() if k not in ("name", "identifier", "type")})[:500])
    if not r.get("content"): print("validator reported nothing:", json.dumps(r)[:300])
finally:
    print("delete branch:", omni("models", "delete-branch", M, name).strip().replace("\n", " ")[:50])
    if doc:
        for rec in json.loads(omni("documents", "list")).get("records", []):
            if rec.get("name", "").startswith("ZZ claude validator test"):
                print("delete scratch dashboard:", omni("documents", "delete", rec["identifier"]).strip().replace("\n", " ")[:60])
