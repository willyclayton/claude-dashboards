import json, subprocess, sys
Q={"out_of_scope":"What was our customer NPS last quarter?",
   "ambiguous":"Show me sales.",
   "relative_time":"What was revenue last quarter? Today is 2026-10-22. Reply briefly with the number and the dates you used."}
ARMS={"cube":("--mcp-config cube-all.json --strict-mcp-config --allowedTools mcp__cube__describe_data,mcp__cube__query_data","Use only the cube MCP tools."),
      "omni":("--allowedTools mcp__claude_ai_Omni_Analytics__askOmni,mcp__claude_ai_Omni_Analytics__checkStatus,mcp__claude_ai_Omni_Analytics__pickModel,mcp__claude_ai_Omni_Analytics__pickTopic","Use only the Omni tools (askOmni, then checkStatus until finished). Use the topic analytics_prod_ecomm__sales."),
      "claude_alone":("--allowedTools mcp__claude_ai_Snowflake_demo__execute_sql","Use only the Snowflake execute_sql tool (SELECT only). Data is in ANALYTICS_PROD.ECOMM.")}
out={}
for arm,(flags,how) in ARMS.items():
    for k,q in Q.items():
        p=subprocess.run(["claude","-p",f"{how}\n{q}\nKeep the answer under 80 words."]+flags.split()+["--output-format","json","--max-turns","20"],capture_output=True,text=True)
        try: d=json.loads(p.stdout); out[f"{arm}/{k}"]={"result":d.get("result"),"cost":d.get("total_cost_usd")}
        except Exception as e: out[f"{arm}/{k}"]={"error":str(e)[:100]}
        print(arm,k,flush=True)
json.dump(out,open("ai_behavior.json","w"),indent=1)
