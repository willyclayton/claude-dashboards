# Claude Dashboards + Cube vs Omni: Project Plan

## Why the fuck do I care?

**The question:** can Claude plus a free semantic layer (Cube) do what Omni's semantic layer does? If yes, "what does Omni add?" gets a much harder question. If no, we'll know exactly where Omni earns its keep.

*Plain English: a semantic layer is the one place where "revenue" or "return rate" is defined once, so every chart and every AI answer uses the same math.*

**Pulse check (as of this update): promising, but not proven.** One piece is built and looks right. The pieces that decide the verdict haven't been run yet.

### Am I getting close to Omni?

| Area | Where it stands | Verdict |
|---|---|---|
| Defining metrics once | Omni's sales topic was ported to Cube: 24 measures, 46 fields, descriptions and synonyms, including odd definitions like the halved `sale_price`. It compiles and generates correct-looking SQL. This took about one session, mostly mechanical. | **Close** |
| Deterministic SQL | Cube writes the SQL from the definitions, so the same question gives the same query. Checked on the SQL only, not yet on real data. | **Close, unproven** |
| Numbers match the warehouse and Omni | Six golden tests are written. They can't run until Cube can log in to Snowflake. | **Unproven** |
| Claude picks the right metric | Descriptions and synonyms carry over, but only through my small wrapper. It hasn't been tested with real questions. | **Unproven** |
| Changing a definition | Cube: edit a YAML file, test, merge. Omni: edit in its modeling tool with branches. Nobody has timed either. | **Unproven** |
| Dashboards | Unknown whether Claude Dashboards' charts actually go through the Cube tool or write their own SQL. This is the most important test. | **Unknown** |
| Who is asking (permissions) | Cube can filter rows by user. A real rollout needs per-person sign-in. Cube Cloud's hosted option offers it. My local setup uses one shared login. | **Gap** |
| Ease for non-engineers | Omni has a visual modeling tool. Cube is YAML in Git, which is fine for engineers and harder for analysts. | **Gap** |
| Running it | Omni is managed. With Cube Core, we own hosting, auth, upgrades and monitoring. | **Gap, cost to quantify** |
| Cost | Cube Core is free, but the people-time isn't. Cube Cloud pricing and limits are unverified. | **Unknown** |

### Why it could get there
- Porting a real Omni model into Cube was fast, so the modeling layer isn't the hard part.
- Cube generates the SQL itself, which is exactly the "almost deterministic SQL" idea.
- Cube Cloud ships a hosted MCP server with OAuth, which covers some of the identity gap.

### Why it might not
- Everything that decides the verdict (accuracy on real questions, dashboards, upkeep) hasn't been run.
- Omni bundles modeling UI, permissions, hosting and AI context. Replicating that is a lot of surrounding work.
- The Snowflake key is still blocked on an admin, so nothing has run on live data.

**Bottom line for the team:** don't cite this as "Cube is as good as Omni." What's true: the semantic layer itself ports easily. What's open: whether Claude uses it correctly and what it costs to run and maintain.

## Goal
Test, honestly and as a devil's advocate to Omni, whether Claude Dashboards plus a free, open-source semantic layer (Cube) is a viable alternative to Omni's semantic layer. Report findings to the central data team on: **answer accuracy, setup effort, upkeep (how definitions change), and cost.**

Same data for both sides: Snowflake `ANALYTICS_PROD.ECOMM` (order items, users, inventory, products).

## The plan
1. **Align the data.** Omni and Snowflake must read the same database. Done.
2. **Build the Cube model.** Convert Omni's `analytics_prod_ecomm__sales` topic into Cube YAML. Done; it compiles.
3. **Connect Cube to Snowflake.** Blocked on a Snowflake key (needs an admin).
4. **Golden tests.** Six checks compare Cube's answers to hand-written SQL.
5. **Connect Claude.** Either my small local MCP server or Cube Cloud's hosted MCP.
6. **Run the same 10-15 questions** through Claude alone, Claude + Cube, and Claude + Omni. Score accuracy.
7. **Change test.** Change one definition in Cube and in Omni. Time both.
8. **Write up findings** for the data team (accuracy, hours, cost, upkeep).

## Findings so far
- Omni's `sale_price` is defined as `SALE_PRICE * 0.5` in the semantic layer, so revenue is half the raw table. This is the definition-vs-raw-table gap a semantic layer exists to handle. It's unclear whether it's intentional.
- `total_revenue` includes all statuses, but the topic's AI instructions say to exclude cancelled and returned orders. The definition and the instruction conflict.
- The simple `ecommerce_sales` topic in Omni is bare (no descriptions or revenue measures). The prod topics from Snowflake semantic views carry the real definitions.

## Tools: free vs paid
| Tool | Used for | Cost |
|---|---|---|
| Cube Core (open source) | Semantic layer, runs locally | Free |
| Cube Cloud | Hosted Cube, hosted MCP with OAuth | Free tier or paid; plan limits unverified |
| Docker Desktop | Runs Cube locally | Free for personal and small-business use; check company eligibility |
| Python 3.12 + uv | MCP wrapper, tests | Free |
| Cloudflare quick tunnel | Public URL so claude.ai can reach local MCP | Free (lab data only) |
| Snowflake | Data, queries | Existing, paid (warehouse credits) |
| Omni | The comparison | Existing, paid |
| Claude + Dashboards | The AI and dashboards front end | Existing; plan details unverified |
| GitHub (private repo) | Code and notes | Free |

## What you have to set up
- **Snowflake key** for Cube. Needs an admin: your roles can't attach a key to your own user. Prefer a read-only service user (e.g. `CUBE_SVC` with `AR_PROD_ALL_R`).
- **`.env`** in `cube-claude-lab/` (copy `.env.example`, add a generated API secret).
- **Cube Cloud:** click Create Deployment to see plan limits and data sources (optional).
- **Question set:** 10-15 questions (some clean, some ambiguous, some out of scope) with expected answers.

## Manual steps done so far
- Signed in to `willyc.omniapp.co` in the browser for the Omni CLI (OAuth).
- Installed Docker Desktop (drag to Applications, approved admin prompt).
- Tried to attach a key to your Snowflake user in Snowsight. Failed: no admin role.
- Created a Cube Cloud account and opened its MCP Server page.

## Man hours (estimates; replace with measured numbers)
| Phase | Done so far | Remaining |
|---|---|---|
| Align Omni and Snowflake data | about 1 h | none |
| Build and compile Cube model | about 1 h (Claude-built) | none |
| Docker, Python, Cube Cloud setup | about 1 h (you) | none |
| Snowflake access (admin wait) | about 0.5 h | about 0.5 h plus wait time |
| Golden tests, connect Claude | none | 1-2 h |
| Question set and scoring | none | 3-4 h |
| Definition-change test (both tools) | none | 1-2 h |
| Findings write-up | none | 2-3 h |

Track real hours in this table as you go. The data team will ask what the build and upkeep cost.

## Files
- `cube-claude-lab/`: Cube model (`model/`), MCP wrapper (`mcp/`), tests (`tests/`), `docker-compose.yml`
- `omni-source/`: the Omni topic the Cube model was converted from
- `Cube Core + Claude_ hands-on lab.md`: original lab guide
