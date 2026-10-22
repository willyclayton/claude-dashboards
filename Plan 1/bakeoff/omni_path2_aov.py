"""Path 2 on Omni: same AOV change request as the Cube ticket, on a throwaway branch (never merged, deleted after).
Asks Omni's agent the question before (main) and after (branch)."""
import json, subprocess, sys, time
P = sys.argv[1] if len(sys.argv) > 1 else "willyc"
M = "f014a03c-efda-4326-8e20-476e3d6882d3"; T = "analytics_prod_ecomm__sales"; OI = "analytics_prod_ecomm__sales__order_items"
Q = "What was AOV (average order value) in Q3 2026, July 1 to September 30? Say which measure you used."
def omni(*a): return subprocess.run(["omni", "-p", P, *a], capture_output=True, text=True).stdout
def ask(branch=None):
    args = ["ai", "job-submit", M, Q, "--topic-name", T] + (["--branch-id", branch] if branch else [])
    t = time.time(); j = json.loads(omni(*args)); jid = j.get("jobId") or j.get("id")
    for _ in range(90):
        st = json.loads(omni("ai", "job-status", jid))
        if str(st.get("state") or st.get("status")).upper() in ("COMPLETE", "COMPLETED", "FAILED", "ERROR"): break
        time.sleep(2)
    r = json.loads(omni("ai", "job-result", jid)); return round(time.time() - t, 1), (r.get("resultSummary") or r.get("message") or json.dumps(r))[:700]
s0, before = ask(); print("BEFORE (main) %.1fs:" % s0, before.replace("\n", " "))
y = json.loads(omni("models", "yaml-get", M, "--filename", f"{T}.topic"))["files"][f"{T}.topic"]
old_syn = "synonyms: [ aov, average order value, average transaction, avg price, mean price ]"
anchor = "      average_sale_price:\n"; assert y.count(old_syn) == 1 and y.count(anchor) == 1
excl = f"${{{OI}.status}} NOT IN ('Cancelled','Returned')"
new_measure = (f"      average_order_value:\n        sql: SUM(CASE WHEN {excl} THEN ${{{OI}.sale_price}} ELSE 0 END) / NULLIF(COUNT(DISTINCT CASE WHEN {excl} THEN ${{{OI}.order_id}} END), 0)\n"
               "        description: Average order value. Net revenue per order, excluding Cancelled and Returned items. Not the same as average_sale_price, which is per item.\n"
               "        synonyms: [ aov, average order value, average basket value, revenue per order, net revenue per order ]\n\n")
y2 = y.replace(old_syn, "synonyms: [ average item price, avg price, mean price, price per item ]").replace(anchor, new_measure + anchor)
name = f"claude-aov-ticket-{int(time.time())}"
t0 = time.time(); br = json.loads(omni("models", "create-branch", M, "--name", name))["model"]["id"]
try:
    r = json.loads(omni("models", "yaml-create", M, "--body", json.dumps({"fileName": f"{T}.topic", "yaml": y2, "mode": "extension", "branchId": br, "commitMessage": "Add average_order_value; fix AOV synonym"})))
    val = omni("models", "validate", M, "--branchid", br); issues = json.loads(val) if val.strip().startswith("[") else []
    errs = [i for i in issues if not i.get("is_warning")]
    print("edit + validate seconds: %.1f | validation errors: %s" % (time.time() - t0, json.dumps(errs)[:300] if errs else "none"))
    s1, after = ask(br); print("AFTER (branch) %.1fs:" % s1, after.replace("\n", " "))
    print("total change-to-answer seconds: %.1f" % (time.time() - t0))
finally:
    print("delete branch:", omni("models", "delete-branch", M, name).strip().replace("\n", " ")[:60])
