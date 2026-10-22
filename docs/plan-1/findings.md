# Plan 1 Findings: gaps, tests and evidence

*Run 2026-10-20. Paper trail for the scoring matrix. Everything here was run, not asserted, unless tagged otherwise. Raw data and scripts are in [`bakeoff/`](../../Plan%201/bakeoff).*

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
| G3 | Restricted-user security test not run | Cube dev and production mode; Snowflake guardrail check | Closed for routes 1 and 2. **Omni attempted, blocked:** impersonation needs an Organization API key; our CLI login is an OAuth user token (section 11) |
| G4 | "Adding a metric" test undefined | Defined and timed on Cube and on Omni (throwaway branch): one metric, three dashboard queries | Closed for both tools' modeler path. **Open:** business-user UI path in Omni (Documented, not driven) |
| G5 | Total cost unmeasured | Per-answer model cost and time captured | Partial. Per-answer cost done; hours, licence, hosting open |
| G6 | Omni auditability unverified | Omni agent shows SQL and field definitions in its answer | Partial. Change history is Documented, not tested |
| G5b | Warehouse compute per answer unmeasured | Snowflake query history attributed to routes 1 and 2 (section 11) | Closed for routes 1 and 2; Omni's queries not separable |
| G7 | Non-technical-user task test | Needs a person | **Open** |
| G8 | Bake-off size (slide says 25-50) | Ran 10 | **Open** |
| G9 | Route 4 (Omni UI AI) | Cannot be driven from here | **Open** |
| G10 | Route 2 beyond Cube (Snowflake SV, MetricFlow) | Not built | **Open** |
| G11 | Hours logged per route and role | Needs a time log | **Open** |
| G12 | Two independent scorers; messier dataset | Process | **Open** |
| G13 *(new)* | Overlapping Omni topics give different revenue | Found during Omni run | Found, needs the data team |
| G14 *(new)* | Definitions differ between Omni topics (revenue, return rate) | Found during Omni run | Found, needs the data team |

## 3. Method and conditions

- **Questions:** 10 plain-English questions ([`bakeoff/questions.py`](../../Plan%201/bakeoff/questions.py)): 6 simple counts and rates, 4 that depend on the governed definition of revenue (Q4, Q5, Q6, Q9). The questions do **not** state the rules.
- **Answer key:** hand-written Snowflake SQL ([`results/answer_key.json`](../../Plan%201/bakeoff/results/answer_key.json)), computed the same day. The definition is the ported Omni `analytics_prod_ecomm__sales` topic: revenue = `SALE_PRICE * 0.5`, excluding Cancelled and Returned. It matched the Desktop dashboard's totals exactly ($1,319,165.62 for Apr-Sep 2026).
- **Routes and how each was driven:** each question ran 3 times per route through headless Claude Code (`claude -p`, CLI 2.1.303, model `claude-sonnet-5-5`), restricted to one set of tools.

| Route | Tools Claude was allowed |
|---|---|
| 1. Claude on its own | Snowflake `execute_sql` (SELECT only) |
| 2. Claude + 3rd-party layer | Cube MCP (`describe_data`, `query_data`) |
| 3. Claude + Omni (agent picks the topic) | Omni MCP (`askOmni`, `checkStatus`) |
| 3b. Claude + Omni, pointed at the Sales topic | Same, with the topic named in the prompt |

- **Scoring:** a run is correct if it matches the key within 0.5% (rows must match label-for-label). Consistency counts a question as consistent when all 3 runs agree with each other, whether or not they are right.
- **Data:** live Snowflake, so numbers drift: distinct orders were 252,701 on 2026-10-16 and 254,271 on 2026-10-20.
- **Rate limits:** 7 Omni runs hit HTTP 429 because I ran 6 in parallel. They were re-run one at a time and replaced ([`runs_retry.jsonl`](../../Plan%201/bakeoff/results/runs_retry.jsonl)); originals are kept in `runs.jsonl`.

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

**Measured (Cube, [`results/change_metric_test.txt`](../../Plan%201/bakeoff/results/change_metric_test.txt)):** one change to `total_revenue` (exclude Cancelled and Returned) took **1 file, 1 block, 3.4 s** from edit to verified, and **3 of 3** dashboard-style queries changed. Reverted cleanly.

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
# round 2: omni_metric_change_test.py, omni_latency_test.py (need pyarrow and the omni CLI), latency_scale_test.py
../cube-claude-lab/.venv/bin/python security_test.py         # Cube dev mode + Snowflake guardrails
../cube-claude-lab/.venv/bin/python change_metric_test.py    # metric change timing
```

Files (all in `Plan 1/bakeoff/`): `questions.py`, `answer_key.py`, `run_bakeoff.py`, `score.py`, `security_test.py`, `security_prod_test.py`, `change_metric_test.py`; results in `bakeoff/results/` (`runs.jsonl`, `runs_retry.jsonl`, `scores.json`, `answer_key.json`, `security_test.txt`, `security_prod_test.txt`, `change_metric_test.txt`).

## 10. Questions for the data team

1. Is `SALE_PRICE * 0.5` intended? Two Omni topics disagree on it.
2. Which topic is authoritative for revenue, and can the other be retired or hidden from the AI?
3. What is the correct return-rate denominator?
4. Should "exclude Cancelled and Returned" be built into the revenue measure rather than left as AI guidance?

## 11. Round 2 (2026-10-20): the "Not tested" cells in the success criteria grid

The grid ([success-criteria-grid.xlsx](success-criteria-grid.xlsx)) was re-filled. Everything below was run or looked up on 2026-10-20; scripts and raw output are in `Plan 1/bakeoff/`.

### 11.1 Omni: change one metric (Tested)

[`omni_metric_change_test.py`](../../Plan%201/bakeoff/omni_metric_change_test.py), output in [`results/omni_metric_change_test.txt`](../../Plan%201/bakeoff/results/omni_metric_change_test.txt). On a throwaway branch of the Omni model (never merged, deleted afterwards), `total_revenue` in the Sales topic was changed to exclude Cancelled and Returned.

| | Cube | Omni |
|---|---|---|
| Files / blocks edited | 1 / 1 | 1 / 1 |
| Edit to verified | 3.4 s | 5.6 s (branch created in 0.6 s) |
| Validation | n/a | `models validate`: no errors |
| Dashboard-style queries changed | 3 of 3 | 3 of 3 |
| Production untouched | yes (reverted) | yes (branch deleted) |
| Total after the change | 5,754,404.54 | 5,754,404.54 |

The two tools agree to the cent after the same change. This is the **modeler** path via the Omni CLI. The business-user path in Omni's UI (create a metric, open it for review, promote it) is Documented in Omni's branch-mode docs and was not driven. Omni's git integration is not configured on this model.

### 11.2 Latency, concurrency, scale (Tested)

[`latency_scale_test.py`](../../Plan%201/bakeoff/latency_scale_test.py), [`omni_latency_test.py`](../../Plan%201/bakeoff/omni_latency_test.py).

| Measure | Result |
|---|---|
| Snowflake direct, result cache off, median of 5 | 0.26 s |
| Snowflake direct, result cache on, median of 5 | 0.18 s |
| Cube REST, cold (5 distinct queries), median | 0.37 s |
| Cube REST, cached, median of 5 | 0.015 s |
| Omni semantic query, median of 5 (all cache MISS) | 1.76 s |
| Cube, 20 concurrent users with their own tokens | 0.66 s wall (same query, so cache-served) |
| Omni, 10 concurrent queries | 3.0 s wall, max 3.0 s |
| Minting 100 user tokens | 2 ms (identity and SSO are separate work) |
| End to end through Claude, per answer | 14.9 s (route 1), 9.0 s (Cube), 34.2 s and 37.0 s (Omni) |

Cube adds overhead on a cold query (0.37 s against 0.26 s direct) and wins on repeats (15 ms). The end-to-end times are dominated by Claude's own time, not the query engine.

### 11.3 Warehouse compute per answer (Tested, partial)

Attributed from Snowflake query history by user and query shape during the bake-off (the routes ran at the same time, so attribution is by shape, not by time window):

| Route | Warehouse queries for 30 answers | Total elapsed | Per answer |
|---|---|---|---|
| 1. Claude on its own | 63 | 41.5 s | 2.1 queries, 1.4 s |
| 2. Cube | 32 | 3.7 s | 1.1 queries, 0.12 s |
| 3/4. Omni | not separable | n/a | Omni's queries run under shared connection users with other demos |

Elapsed time is a proxy: on an X-Small warehouse with auto-suspend, billed credits are dominated by resume and the 60-second minimum, so these numbers show relative load, not credits. Claude on its own re-queries the warehouse about twice per answer; Cube issues about one and caches repeats.

### 11.4 Traceability and observability (Tested for Cube and Snowflake)

- **Git trace:** `git log -S` found the commit, author and date for an `ai_context` change in 0.08 s. It works only for someone who can use Git.
- **Cube Core logs:** the container logged 4,269 query lines during this work, with no usage analytics, popular-question or failed-question views. Cube Cloud adds query history (1 day on Free, 7 days on Premium, per cube.dev/pricing).
- **Snowflake query history** shows every SQL statement but not the user's question or any rating.
- **Omni (Documented):** AI Hub (Quality, Usage, Overview), Analytics > AI logs and Evals cover question logs and failed or low-rated answers; no dedicated popular-questions ranking (docs.omni.co/administration/ai-hub, /administration/analytics, /ai/evals).

### 11.5 Sharing Claude Dashboards: a real constraint for Route 2 (Tested + third-party)

- **Observed:** our dashboard's Cube queries showed "This query isn't refreshing automatically" in the side panel. The Cube MCP server runs locally over stdio.
- **Third-party coverage (tabulareditor.com, not Anthropic):** live dashboards need a connector whose MCP server is **hosted remotely**; a local server can only feed extracts while you build; viewers' queries run with their own connection and permissions; datasets cap at 8 MB; the page can only be changed by Claude. Treat as Asserted until checked against Anthropic's own docs, which a search did not surface.
- **Consequence:** to share a live Cube-backed dashboard, the Cube MCP must be hosted (a tunnel or Cube Cloud's MCP). Omni's connector is already remote, so this doesn't apply to routes 3 and 4.

### 11.6 Omni security: attempted, blocked

Omni's docs say a query can run as another user only with an **Organization API key** passing `userId` ("a PAT cannot impersonate another user"). Our CLI profile uses an OAuth user login and the CLI exposes no `userId` option, so the restricted-user test could not be run without creating an API key and a test user. Per the docs: MCP queries run under the signed-in user's permissions; access filters use user attributes; AI queries respect permitted topics. **Still open.**

### 11.7 Omni findings from the docs

- **Topic overlap may be fixable at the connector:** Omni's MCP can be scoped to a model and topic through setup headers (docs.omni.co/ai/mcp). Not tried; likely closes the unguided accuracy gap (36.7%).
- **MCP is not guaranteed to equal the in-app chat:** both use Omni's AI pipeline, but the docs do not promise identical answers. The Omni (route 4) column therefore uses the MCP runs as a proxy, labelled as such.
- **Pricing:** the docs give no platform price. AI use is credit-based, with overage at $1.00 per credit after an admin accepts it (docs.omni.co/ai/settings/usage). Cube Cloud: Free $0, Starter $40 per developer per month, Premium $80 per developer per month plus Explorer $40 and Viewer $20 per user (cube.dev/pricing).
- **Sharing:** five documented routes: Share dialog with Viewer/Editor/Manager/Owner roles, folder permissions, scheduled deliveries, PDF/CSV download, and embed.

### 11.8 Still not tested, and why

| Cell | Blocker |
|---|---|
| Ease of use (non-technical user) | needs a person; no trial run |
| Modularity on a finished Claude dashboard | not tried |
| Opportunity cost, setup hours, weekly upkeep | need a time log over weeks |
| Omni restricted-user security | needs an Organization API key and a test user |
| Omni in-app chat (route 4) accuracy, consistency, cost | not driven; MCP used as proxy |
| Omni platform licence cost | not public |

## 12. Round 3 (2026-10-22): building the Cube layer out end to end, and breaking it

Goal: run Cube as a stand-in for a BI semantic layer, add what a real build needs, and record every gap. The walkthrough is in [cube-demo-guide.md](cube-demo-guide.md) and the extra criteria in [additional-criteria.md](additional-criteria.md). Scripts: [`cube_buildout_tests.py`](../../Plan%201/bakeoff/cube_buildout_tests.py), [`omni_broken_field_test.py`](../../Plan%201/bakeoff/omni_broken_field_test.py), [`ai_behavior_test.py`](../../Plan%201/bakeoff/ai_behavior_test.py). Raw output in `Plan 1/bakeoff/results/` (`cube_buildout_tests.json`, `omni_broken_field_test.txt`, `ai_behavior.json`, `security_prod_access_policy_test.txt`).

### 12.1 What we added to the Cube model (Tested)

| Addition | Edit to queryable | Check |
|---|---|---|
| `returned_revenue` (new metric) | 0.8 s | 55,459.10, equals the status-filter query exactly |
| `net_revenue` (exclusion rule inside the measure) | 2.3 s | $1,319,165.62 for Apr-Sep, equals the answer key to the cent |
| `rolling_30d_revenue` | 1.6 s | six daily values returned |
| `complete_only` segment | 2.6 s | equals `total_revenue_completed` (5,702,974.52) |
| Pre-aggregation (revenue by day and status) | 1.4 s until used | repeat queries 9-25 ms; Cube Store ships in the image. Not kept in the model |

The four metrics and the segment are kept in `model/cubes/order_items.yml`; the 6 golden tests still pass. `net_revenue` closes finding 5 (the exclusion rule was advisory text): it is now enforceable inside a measure.

### 12.2 Security: the right pattern, and the MCP gap (Tested)

- **Native `access_policy` fails closed.** In production mode, no token and a forged token get 403; a `country=UK` token sees UK only; a token with no country claim sees **nothing** (empty). `queryRewrite` (what we had) returns **everything** for a missing claim. In Cube 1.8.8 the policy needs `group: "*"` (`role` is rejected).
- **The MCP wrapper had no identity.** We added `CUBE_SECURITY_CONTEXT`: Claude through a UK-scoped wrapper returned only UK ($1,004,479.13) and flagged the filter it had not asked for. Unscoped, it returned USA ($4,766,188.15) and UK.
- **Remote transport works, with no auth.** The wrapper runs as a Streamable HTTP MCP and Claude connected by URL with the UK identity applied. An unauthenticated `initialize` request got HTTP 200. Identity is per server process, not per caller. We kept it on localhost.

### 12.3 What happens when a definition breaks (Tested on both)

| | Cube | Omni |
|---|---|---|
| Measure points at a missing column or field | Model loads; `/meta` fine; other metrics fine; the broken metric fails at query time with a raw Snowflake error ("invalid identifier"), 1.9 s | `validate` returned a not-found error with the YAML path and an auto-fix suggestion in 1.5 s; a query on the branch failed at the planning stage; main stayed healthy |

The two tests are not identical (a missing warehouse column in Cube, a missing model field in Omni). Both show when you find out. Omni's branch was deleted and nothing was merged.

### 12.4 AI behavior across routes (Tested, 1 run each)

| Question | Cube | Omni (Sales topic) | Claude alone |
|---|---|---|---|
| "Customer NPS last quarter?" (not in data) | Refused; "won't invent a definition"; offered proxies | Refused; searched wider, found nothing | Refused after searching every table |
| "Show me sales." (ambiguous) | Monthly net revenue table | All-time overview | Used an undocumented `MONTHLY_SALES_OVERVIEW` table |
| "Revenue last quarter?" (today 2026-10-22) | **$698,416.89** | **$698,416.89** | About **$1.40M** (raw price, Complete only) |

No route asked a clarifying question. One run per cell, so treat as illustration, not a rate.

### 12.5 Still untested from the 40 criteria

Time zones, fiscal calendars, semi-additive metrics, column masking, SSO, hostile prompts, multi-turn follow-ups, the SQL API, drill-down, scheduling, embedding and dashboard collaboration. See [additional-criteria.md](additional-criteria.md).
