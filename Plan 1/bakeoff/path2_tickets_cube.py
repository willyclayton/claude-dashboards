"""Path 2: a data engineer (Claude Code, headless) takes a change request, edits the Cube model, tests it, and we re-ask the question.
Run from Plan 1/cube-claude-lab with .env loaded. Reverts the model after each ticket and saves the diff."""
import json, os, subprocess, time
SC = "/private/tmp/claude-501/-Users-will-Desktop-Claude-Claude-Dashboards/ff0fcbc3-9ba2-484b-9bf0-4d7702bd1f6e/scratchpad"
ASK = ['claude', '-p', None, '--mcp-config', f'{SC}/cube-all.json', '--strict-mcp-config', '--allowedTools', 'mcp__cube__describe_data,mcp__cube__query_data', '--output-format', 'json', '--max-turns', '12']
def ask(q):
    cmd = list(ASK); cmd[2] = q + " Answer in under 60 words and say which measure you used."
    t = time.time(); p = subprocess.run(cmd, capture_output=True, text=True)
    d = json.loads(p.stdout); return {"answer": d.get("result"), "seconds": round(time.time() - t, 1), "cost": d.get("total_cost_usd")}
def ticket(text):
    cmd = ['claude', '-p', text, '--permission-mode', 'acceptEdits', '--allowedTools', 'Read,Edit,Glob,Grep,Bash(.venv/bin/python:*),Bash(git diff:*),Bash(git status:*)', '--output-format', 'json', '--max-turns', '40']
    t = time.time(); p = subprocess.run(cmd, capture_output=True, text=True)
    d = json.loads(p.stdout)
    diff = subprocess.run(['git', 'diff', '--', 'model'], capture_output=True, text=True).stdout
    return {"seconds": round(time.time() - t, 1), "cost": d.get("total_cost_usd"), "turns": d.get("num_turns"), "summary": d.get("result"), "diff": diff}
RULES = ("You are the data engineer for this Cube semantic layer (repo: Plan 1/cube-claude-lab). Only edit files under model/. Cube runs at http://localhost:4000 and hot-reloads; "
         "to query it, mint a token with `.venv/bin/python tests/mint_token.py` and call /cubejs-api/v1/load. Test your change against the running Cube and compare with hand-checked numbers. Do not commit. "
         "Finish with a short summary of what you changed and the value you verified.\n\nRequest from an analyst: ")
CASES = {
 "T1_aov_fix": {"ask": "What was AOV (average order value) in Q3 2026, July 1 to September 30?",
   "ticket": RULES + "\"When I ask Claude for AOV it gives me average item price. AOV should be net revenue per order, excluding cancelled and returned orders. Please make the semantic layer understand AOV properly.\" Verify for Q3 2026 (2026-07-01 to 2026-09-30).",
   "truth": "net revenue / distinct orders = 698,416.89 / 29,465 = 23.70"},
 "T2_repeat_rate": {"ask": "What share of customers who ordered in Q3 2026 (July 1 to September 30) placed 2 or more orders ever? Use the semantic layer.",
   "ticket": RULES + "\"I need a repeat customer rate: the percentage of customers with 2 or more distinct orders. Please add it so Claude can answer it.\" Verify all-time.",
   "truth": "see SQL in results"},
}
out = {}
for name, c in CASES.items():
    print("==", name, flush=True)
    before = ask(c["ask"]); print("before:", before["answer"][:160].replace("\n", " "), flush=True)
    tk = ticket(c["ticket"]); print("ticket seconds", tk["seconds"], "cost", tk["cost"], "turns", tk["turns"], flush=True)
    time.sleep(6)
    after = ask(c["ask"]); print("after:", after["answer"][:200].replace("\n", " "), flush=True)
    out[name] = {"truth": c["truth"], "before": before, "ticket": tk, "after": after}
    subprocess.run(["git", "checkout", "--", "model"])
    time.sleep(6)
json.dump(out, open("../bakeoff/results/path2_tickets_cube.json", "w"), indent=1)
