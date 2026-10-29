"""Run each question N times per route through headless Claude Code and log raw results.
Usage: python run_bakeoff.py [runs=3] [routes=r1,r2,r3]
Routes: r1 Claude -> Snowflake SQL | r2 Claude -> Cube MCP | r3 Claude -> Omni MCP (agent picks topic) | r3b same, pointed at the Sales topic
Needs: CUBEJS_API_SECRET in env (for r2). Output: results/runs.jsonl"""
import json, os, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from questions import QUESTIONS

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
ROUTES = (sys.argv[2] if len(sys.argv) > 2 else "r1,r2,r3").split(",")
HOME = os.path.expanduser("~")

FORMAT = ('Reply with ONLY a JSON object and nothing else. For a single number: {"value": 123.45}. '
          'For a breakdown: {"rows": [["label", 123.45], ...]}. Round to 2 decimals. Never modify data.')
ARMS = {
    "r1": {"tools": "mcp__claude_ai_Snowflake_demo__execute_sql",
           "how": "Use only the Snowflake execute_sql tool (SELECT only). The data is in ANALYTICS_PROD.ECOMM."},
    "r2": {"tools": "mcp__cube__describe_data,mcp__cube__query_data",
           "how": "Use only the cube MCP tools (describe_data first, then query_data)."},
    "r3": {"tools": "mcp__claude_ai_Omni_Analytics__askOmni,mcp__claude_ai_Omni_Analytics__checkStatus,"
                    "mcp__claude_ai_Omni_Analytics__pickModel,mcp__claude_ai_Omni_Analytics__pickTopic",
           "how": "Use only the Omni tools (askOmni, then checkStatus until the job finishes)."},
    "r3b": {"tools": "mcp__claude_ai_Omni_Analytics__askOmni,mcp__claude_ai_Omni_Analytics__checkStatus,"
                     "mcp__claude_ai_Omni_Analytics__pickModel,mcp__claude_ai_Omni_Analytics__pickTopic",
            "how": "Use only the Omni tools (askOmni, then checkStatus until the job finishes). "
                   "Use the Omni topic analytics_prod_ecomm__sales (the Sales topic)."},
}
cfg = os.path.join(tempfile.gettempdir(), "bakeoff-cube-mcp.json")
json.dump({"mcpServers": {"cube": {"command": f"{HOME}/.cube-mcp/.venv/bin/python",
           "args": [f"{HOME}/.cube-mcp/server.py"],
           "env": {"CUBEJS_API_SECRET": os.environ.get("CUBEJS_API_SECRET", ""), "MCP_TRANSPORT": "stdio"}}}},
          open(cfg, "w"))
os.chmod(cfg, 0o600)

def run(job):
    route, q, n = job
    arm = ARMS[route]
    prompt = f"{arm['how']}\nQuestion: {q['text']}\n{FORMAT}"
    cmd = ["claude", "-p", prompt, "--allowedTools", arm["tools"], "--output-format", "json", "--max-turns", "25"]
    if route == "r2":
        cmd += ["--mcp-config", cfg, "--strict-mcp-config"]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=tempfile.gettempdir())
        d = json.loads(p.stdout)
        rec = {"result": d.get("result"), "cost_usd": d.get("total_cost_usd"), "turns": d.get("num_turns"),
               "denials": len(d.get("permission_denials") or [])}
    except Exception as e:
        rec = {"result": None, "error": str(e)[:300]}
    rec.update(route=route, q=q["id"], run=n, seconds=round(time.time() - t, 1),
               ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
    with open(os.environ.get("OUT", "results/runs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(route, q["id"], n, rec.get("seconds"), flush=True)

jobs = [(r, q, n) for n in range(1, RUNS + 1) for q in QUESTIONS for r in ROUTES]
if os.environ.get("ONLY"):  # retry list, e.g. ONLY="r3b:Q5:2,r3:Q9:2"
    want = {tuple(x.split(":")[:2]) + (int(x.split(":")[2]),) for x in os.environ["ONLY"].split(",")}
    jobs = [j for j in jobs if (j[0], j[1]["id"], j[2]) in want]
with ThreadPoolExecutor(max_workers=int(os.environ.get("WORKERS", 6))) as ex:
    list(ex.map(run, jobs))
print("done", len(jobs))
