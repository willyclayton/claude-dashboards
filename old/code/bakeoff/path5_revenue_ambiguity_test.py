import json, subprocess
from concurrent.futures import ThreadPoolExecutor
Q = "What was revenue last quarter? Today is 2026-10-22. Reply under 50 words: the number, the dates and the measure you used."
ARMS = {"cube": (["--mcp-config","cube-all.json","--strict-mcp-config","--allowedTools","mcp__cube__describe_data,mcp__cube__query_data"], "Use only the cube MCP tools."),
        "omni": (["--allowedTools","mcp__claude_ai_Omni_Analytics__askOmni,mcp__claude_ai_Omni_Analytics__checkStatus,mcp__claude_ai_Omni_Analytics__pickModel,mcp__claude_ai_Omni_Analytics__pickTopic"], "Use only the Omni tools (askOmni, then checkStatus). Use the topic analytics_prod_ecomm__sales.")}
def run(job):
    arm, n = job; flags, how = ARMS[arm]
    p = subprocess.run(["claude","-p",f"{how}\n{Q}"]+flags+["--output-format","json","--max-turns","20"],capture_output=True,text=True)
    try: return arm, n, json.loads(p.stdout).get("result","")
    except Exception as e: return arm, n, "ERR "+str(e)[:80]
with ThreadPoolExecutor(2) as ex: res = list(ex.map(run, [(a,n) for n in (1,2,3) for a in ARMS]))
json.dump(res, open("ambiguity.json","w"), indent=1)
for a,n,r in sorted(res): print(f"\n## {a} run {n}\n{r[:330]}")
