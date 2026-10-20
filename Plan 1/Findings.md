# Plan 1 Findings: gaps, tests and evidence

*Run 2026-10-20. Paper trail for the scoring matrix. Everything here was run, not asserted, unless tagged otherwise. Raw data and scripts are in [`bakeoff/`](bakeoff/).*

## 1. Headline

1. **Governed layers beat Claude on its own on definition questions, and Cube and Omni tie on structure.** With a governed definition in play, Claude on its own was wrong on all four definition-dependent questions (0/12 runs correct). It was *consistently* wrong, so consistency alone hides the problem.
2. **Cube answered 30/30 correctly and identically. Omni answered 28/30 when pointed at the right topic, and only 11/30 when left to choose.** Omni's agent picked a different topic (`analytics_prod_ecomm__order_items_sv`) that does not halve revenue. Two Omni topics over the same table disagree by 2x on revenue.
3. **Security in the Cube lab fails as configured.** The container runs in dev mode, which accepts no token and forged tokens. In production mode auth is enforced and the country filter works, but a token with no `country` claim sees everything, and our MCP wrapper mints exactly that kind of token.
4. **Changing a metric in Cube is quick for an engineer (one edit, 3.4 s, three dashboard queries changed) but needs an engineer.** The business-user path (request, engineer edit, push) was not run end to end. It is the lens that separates the tools, see section 6.
5. **Per answer, Cube was cheapest and fastest** ($0.048 and 9 s, against about $0.16 and 35 s for Omni).

## 2. Gap analysis: what was missing, and what closed it

| # | Gap in the scoring matrix | Closed by | Status |
|---|---|---|---|
| G1 | Accuracy unmeasured for routes 1, 3, 4 | Bake-off, 10 questions x 3 runs, answer key from Snowflake SQL | Closed (routes 1, 2, 3). Route 4 shares route 3's engine, not tested separately |
| G2 | Consistency unmeasured | Each question run 3 times per route | Closed |
| G3 | Restricted-user security test not run | Cube dev and production mode; Snowflake guardrail check | Closed for routes 1 and 2. **Open for Omni** (needs an Omni restricted test user) |
| G4 | "Adding a metric" test undefined | Defined and timed on Cube: one metric, three dashboard queries | Closed for Cube mechanics. **Open:** business-user flow in Omni (writes to Omni; not run) |
| G5 | Total cost unmeasured | Per-answer model cost and time captured | Partial. Per-answer cost done; hours, licence, hosting open |
| G6 | Omni auditability unverified | Omni agent shows SQL and field definitions in its answer | Partial. Change history is Documented, not tested |
| G7 | Non-technical-user task test | Needs a person | **Open** |
| G8 | Bake-off size (slide says 25-50) | Ran 10 | **Open** |
| G9 | Route 4 (Omni UI AI) | Cannot be driven from here | **Open** |
| G10 | Route 2 beyond Cube (Snowflake SV, MetricFlow) | Not built | **Open** |
| G11 | Hours logged per route and role | Needs a time log | **Open** |
| G12 | Two independent scorers; messier dataset | Process | **Open** |
| G13 *(new)* | Overlapping Omni topics give different revenue | Found during Omni run | Found, needs the data team |
| G14 *(new)* | Definitions differ between Omni topics (revenue, return rate) | Found during Omni run | Found, needs the data team |

## 3. Method and conditions

- **Questions:** 10 plain-English questions ([`bakeoff/questions.py`](bakeoff/questions.py)): 6 simple counts and rates, 4 that depend on the governed definition of revenue (Q4, Q5, Q6, Q9). The questions do **not** state the rules.
- **Answer key:** hand-written Snowflake SQL ([`results/answer_key.json`](bakeoff/results/answer_key.json)), computed the same day. The definition is the ported Omni `analytics_prod_ecomm__sales` topic: revenue = `SALE_PRICE * 0.5`, excluding Cancelled and Returned. It matched the Desktop dashboard's totals exactly ($1,319,165.62 for Apr-Sep 2026).
- **Routes and how each was driven:** each question ran 3 times per route through headless Claude Code (`claude -p`, CLI 2.1.303, model `claude-sonnet-5-5`), restricted to one set of tools.

| Route | Tools Claude was allowed |
|---|---|
| 1. Claude on its own | Snowflake `execute_sql` (SELECT only) |
| 2. Claude + 3rd-party layer | Cube MCP (`describe_data`, `query_data`) |
| 3. Claude + Omni (agent picks the topic) | Omni MCP (`askOmni`, `checkStatus`) |
| 3b. Claude + Omni, pointed at the Sales topic | Same, with the topic named in the prompt |

- **Scoring:** a run is correct if it matches the key within 0.5% (rows must match label-for-label). Consistency counts a question as consistent when all 3 runs agree with each other, whether or not they are right.
- **Data:** live Snowflake, so numbers drift: distinct orders were 252,701 on 2026-10-16 and 254,271 on 2026-10-20.
- **Rate limits:** 7 Omni runs hit HTTP 429 because I ran 6 in parallel. They were re-run one at a time and replaced ([`runs_retry.jsonl`](bakeoff/results/runs_retry.jsonl)); originals are kept in `runs.jsonl`.

## 4. Results: accuracy, consistency, cost

| Route | Runs | Accuracy | Consistency | $ per answer | Seconds | Turns |
|---|---|---|---|---|---|---|
| 1. Claude on its own | 30 | **60.0%** | 100% | $0.123 | 14.9 | 4.1 |
| 2. Claude + Cube | 30 | **100%** | 100% | $0.048 | 9.0 | 4.0 |
| 3. Claude + Omni (agent picks topic) | 30 | **36.7%** | 90% | $0.158 | 34.2 | 7.7 |
| 3b. Claude + Omni (Sales topic named) | 30 | **93.3%** | 90% | $0.159 | 37.0 | 7.7 |

Correct runs out of 3, per question (`*` = all 3 runs identical):

| Q | Question (short) | 1 | 2 | 3 | 3b |
|---|---|---|---|---|---|
| Q1 | Distinct orders | 3* | 3* | 3* | 3* |
| Q2 | Distinct customers | 3* | 3* | 0* | 3* |
| Q3 | Items sold | 3* | 3* | 0* | 3* |
| Q4 | Revenue Apr-Sep | **0*** | 3* | 0* | 3* |
| Q5 | Revenue by month | **0*** | 3* | 0* | 3* |
| Q6 | Revenue by country | **0*** | 3* | 0* | 3* |
| Q7 | Return rate % | 3* | 3* | 2 | 1 |
| Q8 | Avg days to ship | 3* | 3* | 3* | 3* |
| Q9 | Avg sale price | **0*** | 3* | 0* | 3* |
| Q10 | Items by status | 3* | 3* | 3* | 3* |

Cost is the model cost of answering one question (Claude Code list price), not the total cost of ownership.

### What the misses were

- **Route 1 (Claude on its own):** every miss is a definition question. It used the raw table price: Q4 was $2,638,331.24 against the governed $1,319,165.62, exactly 2x. The six non-definition questions were all right. It gave the same wrong answer every run, which is why consistency reads 100%.
- **Route 3 (Omni, agent picks):** the agent chose topic `analytics_prod_ecomm__order_items_sv`. Its revenue measure is `SUM(sale_price)` with no 0.5 factor, and it excludes Cancelled and Returned from counts too: Q3 = 249,145, short of the key by exactly 11,768 (9,283 cancelled + 2,485 returned). Q2 is also lower (125,736 against 129,158). Observed directly: [chat transcript](https://willyc.omniapp.co/chat/021bc0c7-3ba7-412c-89bb-7e9bcebd0f3d).
- **Route 3b (topic named):** all correct except **Q7 (return rate)**. Omni returned about 1.00 where the key says 0.95. The key divides returned items by all items (the ported definition). Omni's value differs, so the live model's return-rate definition is not the one we ported. This is a definition disagreement, not an Omni computation error.
- **Route 2 (Cube):** no misses. The Cube model is a port of the key's own definition, so a match is expected. It shows the port is faithful, not that Cube is "better" than Omni.

## 5. Security results

| Check | Route | Result |
|---|---|---|
| No token | Cube, as configured (dev mode) | **HTTP 200, all data** |
| Forged token (wrong secret) with `country=UK` | Cube, dev mode | **Returned all data**, country filter not applied |
| `CUBEJS_DEV_MODE` | Cube lab container | `true` |
| No token / forged token | Cube, production mode | **HTTP 403** both |
| Valid token `country=UK` | Cube, production mode | Only UK ($1,045,428.08) |
| Valid token with **no** `country` claim | Cube, production mode | **All countries** (fail-open) |
| UK token asking for USA | Cube | Empty result (filters stack) |
| MCP wrapper identity | `mcp/server.py` | Mints one token with no `country` claim, so Claude through the wrapper always sees everything |
| Row access / masking policies on `ECOMM` | Snowflake (route 1) | **None** (0 rows each) |
| Role used | Snowflake | `DBT_DEMO_ROLE`, `OWNERSHIP` on `ORDER_ITEMS`, 71 schemas visible |
| Omni (routes 3 and 4) | Omni | **Not tested.** Docs say MCP queries run under the signed-in user's permissions and access filters apply; needs a restricted Omni user to verify |

Sources for the Omni claims: docs.omni.co/ai/mcp/authentication, docs.omni.co/ai/security. The production-mode test used a throwaway container on port 4001 with `CUBEJS_DEV_MODE=false` and `CUBEJS_CACHE_AND_QUEUE_DRIVER=memory`, since removed.

## 6. Changing a metric: the persona lens

**Measured (Cube, [`results/change_metric_test.txt`](bakeoff/results/change_metric_test.txt)):** one change to `total_revenue` (exclude Cancelled and Returned) took **1 file, 1 block, 3.4 s** from edit to verified, and **3 of 3** dashboard-style queries changed. Reverted cleanly.

That is the data engineer's seat. The question the business asks is who has to be involved:

| Seat | Route 1: Claude alone | Route 2: Cube | Routes 3 and 4: Omni |
|---|---|---|---|
| Business user | No place to define a metric; re-prompts, definitions drift | Cannot edit YAML. Submits a request to data engineering | Can create a metric and promote it through a reviewed change (Documented) |
| Data engineer | Not involved, but nothing is governed | Edits YAML, tests, pushes, deploys | Reviews the change rather than writing it |
| Modeler | n/a | Does not exist as a role; it is the engineer | Owns the governed model, branch review (Documented) |
| Claude admin | Warehouse access per user | Owns the MCP wrapper, token minting, hosting | Owns the connector and OAuth |

The request-to-live path in Cube (ticket, engineer, push, deploy) is the stated team process and **was not timed here**. The Omni business-user path is **Documented** (docs.omni.co/content/develop/branch-mode), not tested. Both are open (G4).

## 7. Interpretation

- **Accuracy is not the whole contest.** Where a definition exists, both governed layers return it deterministically. The differences that showed up were not arithmetic: they were *which definition was used* (Omni topic choice, return-rate denominator, the unconfirmed 0.5 factor). That is a governance finding, and it favors a tool that makes one definition authoritative and visible.
- **Omni's risk is topic overlap, not hallucination.** The same instance holds topics that disagree. Curating which topics the AI may use (`ai_chat_topics`, per the Omni docs) and retiring the duplicate is the likely fix; not tried. Until then an unguided question can land on the wrong one.
- **Claude on its own is wrong in a stable way.** It is consistent and unaudited. That is the strongest argument against route 1.
- **Where Omni leads on evidence:** adding a metric (business-user seat), auditability (change history, visible definitions), security (documented, untested), and self-service. **Where it does not lead:** per-answer cost and speed (Cube is faster and cheaper), and accuracy and consistency in this run (Cube 100%/100%, Omni 93%/90% when pinned).

## 8. Caveats

- **Questions asked through headless Claude Code, not Claude Desktop or Claude Dashboards.** Same model and tools, different front end.
- **10 questions x 3 runs.** The slide calls for 25-50. Small numbers; a single miss moves a route by 3 points.
- **One scorer, one date, one dataset** (synthetic). Sections 4, 5 and the Cube part of 6 are Tested; anything marked Documented comes from Omni's docs and was not run by us.
- **Answer key follows the ported topic.** The business has not confirmed the 0.5 factor or the return-rate definition.
- **Routes 3 and 4 share an engine** (Omni's agent). Route 4's UI was not driven.
- **Omni was pointed at the topic in 3b;** a real user would not know to do that.

## 9. Reproduce

```bash
cd "Plan 1/cube-claude-lab" && set -a && . ./.env && set +a && cd ../bakeoff
../cube-claude-lab/.venv/bin/python answer_key.py          # answer key from Snowflake
python3 run_bakeoff.py 3 r1,r2,r3,r3b                        # 3 runs per question per route (WORKERS=2 avoids Omni rate limits)
python3 score.py                                             # accuracy, consistency, cost
../cube-claude-lab/.venv/bin/python security_test.py         # Cube dev mode + Snowflake guardrails
../cube-claude-lab/.venv/bin/python change_metric_test.py    # metric change timing
```

Files: `bakeoff/questions.py`, `answer_key.py`, `run_bakeoff.py`, `score.py`, `security_test.py`, `security_prod_test.py`, `change_metric_test.py`; results in `bakeoff/results/` (`runs.jsonl`, `runs_retry.jsonl`, `scores.json`, `answer_key.json`, `security_test.txt`, `security_prod_test.txt`, `change_metric_test.txt`).

## 10. Questions for the data team

1. Is `SALE_PRICE * 0.5` intended? Two Omni topics disagree on it.
2. Which topic is authoritative for revenue, and can the other be retired or hidden from the AI?
3. What is the correct return-rate denominator?
4. Should "exclude Cancelled and Returned" be built into the revenue measure rather than left as AI guidance?
