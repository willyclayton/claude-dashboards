# Plan 1: Can Claude + Cube replace Omni's semantic layer?

*Last updated 2026-10-16. Owner: Will Clayton.*

## 1. The one-minute version

**Question.** Can Claude plus a free, open-source semantic layer (Cube) answer business questions as accurately as Omni's semantic layer, and at what cost in effort and upkeep?

**Why it matters.** A semantic layer is the one place where "revenue" or "return rate" is defined once, so every chart and every AI answer uses the same math. Omni sells this as a core feature. If a free tool can do the same job, we need a sharper answer to "what does Omni add?". If it can't, we learn exactly where Omni earns its keep.

**Status: Green on build, Yellow on verdict.** The Cube model is built, live on real Snowflake data, and passes all 6 accuracy tests. The tests that decide the verdict (does Claude pick the right metric, do dashboards use it, what does upkeep cost) have not been run.

| | |
|---|---|
| Cube model built from Omni's sales topic | Done (24 measures, 46 fields) |
| Connected to live Snowflake data | Done (2026-10-16) |
| Accuracy tests, Cube vs hand-written SQL | **6 of 6 pass** |
| Claude asking questions through Cube | Not started |
| Same questions through Omni, scored side by side | Not started |
| Cost and upkeep comparison | Not started |

**Bottom line today.** Don't cite this as "Cube is as good as Omni." What is proven: the semantic layer ports easily and its numbers match the warehouse exactly. What is open: whether Claude uses it correctly, and what it costs to run and maintain.

## 2. How it works

```
 Question  ->  Claude  ->  MCP tool  ->  Cube (semantic layer)  ->  Snowflake
 "revenue      (AI)       (the bridge)   metrics defined once      ANALYTICS_PROD.ECOMM
  by country"                            in YAML, writes the SQL   (same data Omni reads)

 Comparison arm:  Question -> Claude -> Omni MCP -> Omni model -> same Snowflake data
```

- **Same data on both sides.** Omni and Cube both read Snowflake `ANALYTICS_PROD.ECOMM` (order items, users, inventory, products), so any difference in answers comes from the semantic layer, not the data.
- **Cube writes the SQL.** Claude doesn't invent queries. It asks for named metrics and Cube generates the SQL from the definitions. The same question gives the same query.
- **Gold standard.** Six hand-written SQL queries against the raw tables act as ground truth.

## 3. Progress

| # | Step | Status | Evidence |
|---|---|---|---|
| 1 | Align Omni and Snowflake onto the same data | Done | Both read `ANALYTICS_PROD.ECOMM` |
| 2 | Port Omni's `analytics_prod_ecomm__sales` topic to Cube YAML | Done | 5 files, about 570 lines, compiles |
| 3 | Connect Cube to Snowflake | **Done 2026-10-16** | Query returned 259,301 items and 252,701 orders |
| 4 | Golden accuracy tests | **Done, 6/6 pass** | See section 4 |
| 5 | Connect Claude (local MCP wrapper or Cube Cloud MCP) | Next | `mcp/server.py` written, not yet run |
| 6 | Run 10-15 questions three ways: Claude alone, Claude + Cube, Claude + Omni | Not started | Question set not written |
| 7 | Definition-change test: change one metric in Cube and in Omni, time both | Not started | |
| 8 | Findings write-up for the data team | Not started | |

### How step 3 got unblocked
The original plan needed a Snowflake key-pair, which requires an admin. Instead, Cube now logs in with a **programmatic access token (PAT)** you can create yourself in Snowsight. Two things were learned:
- The first token was scoped to `AR_PROD_ALL_R`, which has **no access** to the `ECOMM` schema. Cube authenticated but every query failed with "not authorized".
- `SHOW GRANTS ON SCHEMA` showed only `DBT_DEMO_ROLE` (your default role, and the schema owner) has access among your roles. A new token scoped to that role fixed it.
- Trade-off: `DBT_DEMO_ROLE` can write and drop, more than Cube needs. Acceptable for a local lab. A true read-only setup needs an admin to grant `SELECT` to a read role.

## 4. Evidence: accuracy tests

Each test compares Cube's answer to hand-written SQL run directly on Snowflake.

| Test | What it checks | Result |
|---|---|---|
| Total items sold | Basic count | Pass |
| Total orders (distinct) | Distinct-count logic | Pass |
| Completed revenue | The `sale_price = SALE_PRICE * 0.5` definition | Pass |
| Items by status | Grouping | Pass |
| Revenue by customer country | Join fan-out (no double counting) | Pass |
| Return rate (0-100) | Ratio math and units | Pass |

Run with: `cd cube-claude-lab && set -a && . ./.env && set +a && .venv/bin/python tests/run_golden.py`

## 5. Scorecard: Cube vs Omni so far

| Area | Where it stands | Verdict |
|---|---|---|
| Defining metrics once | Omni's topic ported in about one session, mostly mechanical | **Close** |
| Deterministic SQL | Cube generates SQL from definitions | **Close** |
| Numbers match the warehouse | 6 of 6 golden tests pass on live data | **Proven** |
| Claude picks the right metric | Descriptions and synonyms carried over; untested with real questions | Unproven |
| Changing a definition | Cube: edit YAML, test, merge. Omni: modeling tool with branches. Not timed | Unproven |
| Dashboards | Do Claude Dashboards' charts go through the Cube tool or write their own SQL? Most important open test | Unknown |
| Who is asking (permissions) | Cube can filter rows by user, but needs per-person sign-in. Local setup uses one shared login | Gap |
| Ease for non-engineers | Omni has a visual modeler. Cube is YAML in Git | Gap |
| Running it | Omni is managed. Cube Core means we own hosting, auth, upgrades, monitoring | Gap, cost to quantify |
| Cost | Cube Core is free; people-time is not. Cube Cloud pricing unverified | Unknown |

## 6. Findings so far

1. **Revenue is half the raw table.** Omni defines `sale_price` as `SALE_PRICE * 0.5`. This is exactly the gap between raw data and defined metrics that a semantic layer handles. Unclear if intentional; worth asking the data team.
2. **Definition conflicts with instruction.** `total_revenue` includes all statuses, but the topic's AI instructions say to exclude cancelled and returned orders.
3. **Omni's simple `ecommerce_sales` topic is bare** (no descriptions or revenue measures). The prod topics built from Snowflake semantic views carry the real definitions.
4. **Faster path to access.** A PAT replaces the admin-gated key-pair for a lab; role scoping on the token is the thing to get right.

## 7. Tools and what each one does

| Tool | Role in the project | Cost | In use now |
|---|---|---|---|
| Snowflake | Warehouse holding the data | Existing, paid (credits) | Yes |
| Omni | The product being compared against | Existing, paid | Yes (source of the model) |
| Cube Core | Open-source semantic layer, runs locally | Free | Yes |
| Docker Desktop | Runs Cube locally | Free for personal/small business; check company eligibility | Yes |
| Python 3.12 | Test runner and MCP wrapper | Free | Yes |
| Claude Code | Built the model, config and tests | Existing | Yes |
| Git / GitHub (private) | Code and notes | Free | Yes |
| Claude + Claude Dashboards | The AI and dashboard front end being tested | Existing; plan details unverified | Next |
| MCP wrapper (`mcp/server.py`) | Bridge letting Claude call Cube | Free (our code) | Next |
| Cloudflare quick tunnel | Public URL so claude.ai can reach the local MCP | Free (lab data only) | Planned |
| Cube Cloud | Hosted Cube with hosted MCP and OAuth | Free tier or paid; limits unverified | Evaluating |

11 tools in total: 7 in use, 2 next, 1 planned, 1 under evaluation. Only Snowflake and Omni cost money, and both already existed.

## 8. Risks and decisions needed

| Item | Why it matters | Owner |
|---|---|---|
| `DBT_DEMO_ROLE` is broader than needed | Write access for a read-only tool | Ask an admin for a read-only role on `ECOMM` |
| Tokens were pasted into chat | Treat them as exposed; they live in gitignored `.env` | Delete old `will-cube-testing` token; rotate after the lab |
| Dashboards may bypass Cube | If charts write their own SQL, the semantic layer isn't doing its job there | Test in step 6 |
| Cube Cloud limits unknown | Decides whether hosted OAuth is viable | Click Create Deployment to see plan limits |
| Question set not written | Accuracy scoring can't start without it | Draft 10-15 questions: clean, ambiguous, out of scope |

## 9. Next steps (in order)

1. Write the 10-15 question set with expected answers.
2. Start the MCP wrapper and ask Claude the questions through Cube.
3. Run the same questions through Omni and score all three arms.
4. Time a definition change in both tools.
5. Write up accuracy, hours, cost and upkeep for the data team.

## 10. Hours

| Phase | Done | Remaining |
|---|---|---|
| Align Omni and Snowflake data | about 1 h | none |
| Build and compile Cube model | about 1 h (Claude-built) | none |
| Docker, Python, Cube Cloud setup | about 1 h | none |
| Snowflake access | about 1 h (token workaround, role discovery) | none |
| Golden tests | about 0.5 h | none |
| Connect Claude | none | 1-2 h |
| Question set and scoring | none | 3-4 h |
| Definition-change test (both tools) | none | 1-2 h |
| Findings write-up | none | 2-3 h |

Estimates; replace with measured numbers. The data team will ask what build and upkeep cost.

## 11. Reproduce it

1. `cd cube-claude-lab && cp .env.example .env`
2. In `.env`: set `CUBEJS_API_SECRET` (`openssl rand -hex 32`) and `CUBEJS_DB_PASS` to a Snowflake PAT scoped to `DBT_DEMO_ROLE` (Snowsight > Profile > Authentication > Generate token)
3. `docker compose up -d`, then query `http://localhost:4000/cubejs-api/v1/load`
4. Run the golden tests (command in section 4)

## 12. Files
- `cube-claude-lab/`: Cube model (`model/`), MCP wrapper (`mcp/`), tests (`tests/`), `docker-compose.yml`
- `omni-source/`: the Omni topic the Cube model was converted from
- `Cube Core + Claude_ hands-on lab.md`: original lab guide
