"""Score results/runs.jsonl against results/answer_key.json. Writes results/scores.json and prints a table."""
import json, re, collections, statistics
from questions import QUESTIONS

key = json.load(open("results/answer_key.json"))["answers"]
KIND = {q["id"]: q["kind"] for q in QUESTIONS}
TOL = 0.005  # 0.5% relative, which also absorbs rounding to 2 decimals

def parse(text):
    if not text: return None
    m = re.search(r"\{.*\}", text, re.S)
    try:
        d = json.loads(m.group(0)) if m else None
    except Exception:
        return None
    if not isinstance(d, dict): return None
    if "value" in d:
        try: return float(d["value"])
        except Exception: return None
    if "rows" in d:
        try: return {str(a).strip().lower(): float(b) for a, b in d["rows"]}
        except Exception: return None
    return None

def close(a, b):
    return abs(a - b) <= TOL * max(abs(b), 0.01) or abs(a - b) <= 0.011

def same(a, b):
    if a is None or b is None: return False
    if isinstance(a, dict) != isinstance(b, dict): return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    return close(a, b)

def norm_key(q):
    k = key[q]
    return {s.lower(): v for s, v in k.items()} if isinstance(k, dict) else k

runs = [json.loads(l) for l in open("results/runs.jsonl")]
import os
if os.path.exists("results/runs_retry.jsonl"):  # reruns of rate-limited (HTTP 429) runs replace the original
    retry = {(r["route"], r["q"], r["run"]): r for r in map(json.loads, open("results/runs_retry.jsonl"))}
    runs = [retry.get((r["route"], r["q"], r["run"]), r) for r in runs]
by = collections.defaultdict(list)
for r in runs:
    r["parsed"] = parse(r.get("result"))
    r["correct"] = same(r["parsed"], norm_key(r["q"]))
    by[(r["route"], r["q"])].append(r)

out = {}
for route in sorted({r["route"] for r in runs}):
    qs = [q["id"] for q in QUESTIONS]
    rr = [r for r in runs if r["route"] == route]
    consistent = 0; per_q = {}
    for q in qs:
        g = by[(route, q)]
        allsame = len(g) > 1 and all(same(g[0]["parsed"], x["parsed"]) for x in g[1:])
        consistent += allsame
        per_q[q] = {"correct": sum(x["correct"] for x in g), "n": len(g), "all_runs_agree": allsame}
    out[route] = {
        "runs": len(rr), "errors": sum(1 for r in rr if r["parsed"] is None),
        "accuracy_pct": round(100 * sum(r["correct"] for r in rr) / len(rr), 1),
        "consistency_pct": round(100 * consistent / len(qs), 1),
        "avg_cost_usd": round(statistics.mean(r["cost_usd"] or 0 for r in rr), 4),
        "avg_seconds": round(statistics.mean(r["seconds"] for r in rr), 1),
        "avg_turns": round(statistics.mean(r.get("turns") or 0 for r in rr), 1),
        "per_question": per_q}
json.dump(out, open("results/scores.json", "w"), indent=1)
print(f"{'route':6} {'runs':>4} {'acc%':>6} {'consist%':>9} {'$/run':>7} {'sec':>6} {'turns':>6} errors")
for k, v in out.items():
    print(f"{k:6} {v['runs']:>4} {v['accuracy_pct']:>6} {v['consistency_pct']:>9} {v['avg_cost_usd']:>7} {v['avg_seconds']:>6} {v['avg_turns']:>6} {v['errors']}")
print("\ncorrect runs per question (of N):")
print("q    " + "  ".join(f"{k:>6}" for k in out))
for q in [x["id"] for x in QUESTIONS]:
    print(f"{q:4} " + "  ".join(f"{out[k]['per_question'][q]['correct']}/{out[k]['per_question'][q]['n']}{'*' if out[k]['per_question'][q]['all_runs_agree'] else ' '}".rjust(6) for k in out))
print("(* = all runs gave the same answer)")
